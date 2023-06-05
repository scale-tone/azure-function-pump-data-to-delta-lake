from typing import List
import azure.functions as func
from helpers import convert_and_add_message, send_to_delta_table

def main(events: List[func.QueueMessage]) -> None:

    result = []

    for event in events:
        convert_and_add_message(event.get_body().decode('utf-8'), result)

    send_to_delta_table(result)