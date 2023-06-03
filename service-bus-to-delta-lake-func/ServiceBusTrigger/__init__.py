import os
import json
import xmltodict

import azure.functions as func
from delta.tables import *
from pyspark.sql import SparkSession

from helpers import apply_jsonpath

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

# Will apply this jsonpath query, if specified
jsonPathQuery = os.getenv("JSONPATH_QUERY")

# Handles _batches_ of messages. Expects each message in a batch to be a string (with either JSON or XML)
def main(msgBatch: List[func.ServiceBusMessage]):

    # Converting messages from JSON to dataframe
    convertedMsgBatch = []

    for msg in msgBatch:

        msgString = msg.get_body().decode('utf-8')

        # supporting both XML and JSON
        if msgString.startswith("<"):
            jsonObjects = xmltodict.parse(msgString, attr_prefix="")
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

    dFrame = spark.createDataFrame(convertedMsgBatch)

    # Appending records to OUTPUT_TABLE_NAME
    dFrame.write.format("delta").mode("append").saveAsTable(os.environ["OUTPUT_TABLE_NAME"])
