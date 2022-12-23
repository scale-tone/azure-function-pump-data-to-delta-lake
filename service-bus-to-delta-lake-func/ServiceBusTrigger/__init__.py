import os
import json

import azure.functions as func
from delta.tables import *
from pyspark.sql import SparkSession

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

def main(msgBatch: List[func.ServiceBusMessage]):

    # Converting messages from JSON to dataframe
    convertedMsgBatch = []

    for msg in msgBatch:

        jsonString = msg.get_body().decode('utf-8')
        jsonObject = json.loads(jsonString)
        convertedMsgBatch.append(jsonObject)

    dFrame = spark.createDataFrame(convertedMsgBatch)

    # Appending records to OUTPUT_TABLE_NAME
    dFrame.write.format("delta").mode("append").saveAsTable(os.environ["OUTPUT_TABLE_NAME"])
