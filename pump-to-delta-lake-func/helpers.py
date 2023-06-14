import os
import json
import xmltodict

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

def send_to_delta_table(msgs):

    frame = spark.createDataFrame(msgs)

    # Appending records to OUTPUT_TABLE_NAME
    frame.write.format("delta").mode("append").saveAsTable(os.environ["OUTPUT_TABLE_NAME"])


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

def convert_and_add_message(msg_string, json_path, output_container):

    # supporting both XML and JSON
    if msg_string.startswith("<"):
        json_objects = xmltodict.parse(msg_string, attr_prefix="")
        json_objects = list(json_objects.values())[0]
    else:
        json_objects = json.loads(msg_string)

    # converting to array, if it is not yet
    if type(json_objects) != list:
        json_objects = [json_objects]

    for json_object in json_objects:

        # Applying jsonpath query, if specified
        if json_path:
            json_object = apply_jsonpath(json_object, json_path)

        output_container.append(json_object)
