import os
import json
from typing import List
import xmltodict

import azure.functions as func

from helpers import apply_jsonpath, send_to_delta_table

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

    send_to_delta_table(convertedMsgBatch)