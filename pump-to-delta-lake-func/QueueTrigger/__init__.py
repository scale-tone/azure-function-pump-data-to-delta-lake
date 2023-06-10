import logging
import os
import tempfile
import time
import fcntl
from typing import List
import azure.functions as func
from helpers import convert_and_add_message, send_to_delta_table

batch_size = 10
max_wait_count = 10

bufDir = os.path.join(tempfile.gettempdir(), "pump-to-delta-lake-func-buf")
os.makedirs(bufDir, exist_ok=True)

def main(event: func.QueueMessage) -> None:

    logging.warning(f">> got event {event.id}")

    fileName = os.path.join(bufDir, event.id + '.json')
    with open(fileName, 'w') as f:
        f.write(event.get_body().decode('utf-8'))

    logging.warning(f">> saved to {fileName}")

    allFiles = [f for f in os.listdir(bufDir) if os.path.isfile(os.path.join(bufDir, f))]

    i = 0
    while (len(allFiles) < batch_size) and (i < max_wait_count):

        if len(allFiles) == 0:
            return

        i = i + 1
        time.sleep(0.05)

        allFiles = [f for f in os.listdir(bufDir) if os.path.isfile(os.path.join(bufDir, f))]


    result = []

    try:

        with open(os.path.join(bufDir, "lock.lock"), "x"):

            for f in allFiles:
                fileName = os.path.join(bufDir, f)

                with open(fileName) as f:
                    convert_and_add_message(f.read(), result)

            logging.warning(f">> sending {len(result)} events...")

            send_to_delta_table(result)

            logging.warning(f">> {len(result)} events successfully sent")

            for f in allFiles:
                os.remove(os.path.join(bufDir, f))

        os.remove(os.path.join(bufDir, "lock.lock"))

    except FileExistsError:
        logging.warning(">>> failed to get lock")
        pass
