import logging
import datetime
import os
import tempfile
import shutil
import time
import math
import json
import xmltodict

import azure.functions as func


from delta.tables import *
from pyspark.sql import SparkSession
from jsonpath_ng import parse

# Saving DataBricks connection info into its config file
databricksConnectSettings = { \
    "host": os.environ["DATABRICKS_ADDRESS"], \
    "token": os.environ["DATABRICKS_API_TOKEN"], \
    "cluster_id": os.environ["DATABRICKS_CLUSTER_ID"], \
    "org_id": os.environ["DATABRICKS_ORG_ID"], \
    "port": "15001" \
}

with open('/root/.databricks-connect', 'w') as configFile:
    json.dump(databricksConnectSettings, configFile, ensure_ascii=False)

# Creating spark session
spark = SparkSession.builder.getOrCreate()

def send_to_delta_table_local(msgs):

    dFrame = spark.createDataFrame(msgs)

    # Appending records to OUTPUT_TABLE_NAME
    dFrame.write.format("delta").mode("append").saveAsTable(os.environ["OUTPUT_TABLE_NAME"])


def apply_jsonpath(msg, json_path):
    
    results = parse(json_path).find(msg)

    if len(results) == 1:
        # jsonpath produced an object - just returning it
        return results[0].value
    else:
        # jsonpath produced an array - trying to convert it back into object
        record = {}
        for res in results:
            record[res.path.fields[0]] = res.value

        return record


# Will apply this jsonpath query, if specified
jsonPathQuery = os.getenv("JSONPATH_QUERY")

def convert_and_add_message(msgString, convertedMsgBatch):

    # supporting both XML and JSON
    if msgString.startswith("<"):
        jsonObjects = xmltodict.parse(msgString, attr_prefix="")
        jsonObjects = list(jsonObjects.values())[0]
    else:
        jsonObjects = json.loads(msgString)

    # converting to array, if it is not yet
    if type(jsonObjects) != list:
        jsonObjects = [jsonObjects]

    for jsonObject in jsonObjects:

        # Applying jsonpath query, if specified
        if jsonPathQuery != None:
            jsonObject = apply_jsonpath(jsonObject, jsonPathQuery)

        convertedMsgBatch.append(jsonObject)




buf_dir = os.path.join(tempfile.gettempdir(), "pump-to-delta-lake-func-buf")
os.makedirs(buf_dir, exist_ok=True)

MAX_WAIT_IN_SECONDS = 300



# Storage Queue trigger does not support batching. So we'll need to handcraft it ourselves, using local temp folder as a buffer.
# The strategy below is as follows:
#   We store events in bucket folders, a separate folder _per every second_.
#   Then one of the handlers obtains an exclusive lock over that folder (by exclusively creating a dummy file)
#   and pushes all files from it to destination. Other handlers just wait until it happens.
#   If it doesn't happen within MAX_WAIT_IN_SECONDS, the handlers throw, causing their messages to be retried.
def main(event: func.QueueMessage) -> None:

    # Organizing a 1-second-long bucket folder
    now = datetime.datetime.now()
    str_time = now.strftime("%Y-%m-%d-%H-%M-") + str(math.floor(now.second / 10))

    batch_dir = os.path.join(buf_dir, str_time)
    os.makedirs(batch_dir, exist_ok=True)

    try:

        cur_event_file_path = os.path.join(batch_dir, event.id + '.txt')
        with open(cur_event_file_path, 'w') as f:
            f.write(event.get_body().decode('utf-8'))

        # Sleeping for 1 second, to ensure all events belonging to current bucket have arrived
        time.sleep(1)

        # Now one handler should do the job of sending events, others should just wait until it happens.
        # If that doesn't happen, then all handlers should throw (so that all events are retried)
        try:

            lock_file_name = os.path.join(buf_dir, str_time + ".lock")
            with open(lock_file_name, "x"):

                result = []

                # Reading all files in bucket folder
                event_files = [n for n in os.listdir(batch_dir) if os.path.isfile(os.path.join(batch_dir, n)) and n != lock_file_name]

                for event_file_name in event_files:

                    with open(os.path.join(batch_dir, event_file_name)) as f:
                        convert_and_add_message(f.read(), result)

                logging.warning(f">> sending {len(result)} events ({event.id})")

                # Sending batch to Delta Table
                send_to_delta_table_local(result)

                logging.warning(f">> successfully sent {len(result)} events ({event.id})")

                # Flushing bucket folder, but only if and when the entire batch is successfully sent
                shutil.rmtree(batch_dir, ignore_errors=True)

            os.remove(lock_file_name)
            return

        except (FileNotFoundError, FileExistsError):
            pass

        # Failed to obtain the lock, so just waiting till our file gets removed (which indicates that it was successfully sent by another handler)
        i = 0
        while os.path.isfile(cur_event_file_path) and i < MAX_WAIT_IN_SECONDS:
            time.sleep(1)
            i = i + 1

        if i == MAX_WAIT_IN_SECONDS:

            # removing event file and the entire bucket folder if empty
            try:
                os.remove(cur_event_file_path)
                os.rmdir(batch_dir)
            except:
                pass

            raise Exception(f"Event {event.id} failed to be sent")

    except Exception as ex:

        logging.error(ex)
        raise
