import os
from typing import List
import azure.functions as func
from helpers import convert_and_add_message, send_to_delta_table

# Will apply this jsonpath query, if specified
json_path_query = os.getenv("EVENTHUB_JSONPATH_QUERY")

# Handles _batches_ of Event Hubs messages. Expects each message in a batch to be a string (with either JSON or XML)
def main(events: List[func.EventHubEvent]):
     
    result = []

    for event in events:
        convert_and_add_message(event.get_body().decode('utf-8'), json_path_query, result)

    send_to_delta_table(result)
