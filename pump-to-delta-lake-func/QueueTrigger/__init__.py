import time
from typing import List
import azure.functions as func
from helpers import convert_and_add_message, send_to_delta_table

batch_size = 100
# waiting max 3 seconds
max_wait_count = 60
events = []

def main(event: func.QueueMessage) -> None:

    events.append(event)

    i = 0
    while (len(events) < batch_size) and (i < max_wait_count):

        if len(events) == 0:
            # if the batch got processed by another instance, just returning
            return

        i = i + 1
        time.sleep(0.05)

    result = []

    for event in events:
        convert_and_add_message(event.get_body().decode('utf-8'), result)

    send_to_delta_table(result)

    events.clear()
