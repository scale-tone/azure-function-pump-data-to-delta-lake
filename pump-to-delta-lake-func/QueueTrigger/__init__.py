import os
import tempfile
import time
import fcntl
from typing import List
import azure.functions as func
from helpers import convert_and_add_message, send_to_delta_table

batch_size = 100
# waiting max 3 seconds
max_wait_count = 60

bufDir = os.path.join(tempfile.gettempdir(), "pump-to-delta-lake-func-buf")
os.mkdir(bufDir)


def main(event: func.QueueMessage) -> None:

    fileName = os.path.join(bufDir, event.id + '.json')
    with open(fileName, 'w') as f:
        f.write(event.get_body().decode('utf-8'))

    allFiles = [f for f in os.listdir(bufDir) if os.path.isfile(os.path.join(bufDir, f))]

    i = 0
    while (len(allFiles) < batch_size) and (i < max_wait_count):

        if len(allFiles) == 0:
            return

        i = i + 1
        time.sleep(0.05)

        allFiles = [f for f in os.listdir(bufDir) if os.path.isfile(os.path.join(bufDir, f))]


    result = []

    for f in allFiles:
        filePath = os.path.join(bufDir, f)

        try:

            fcntl.flock(filePath, fcntl.LOCK_EX)

            with open(filePath) as f:
                convert_and_add_message(f.read(), result)

        except OSError:
            continue

    print(f">> sending {len(result)} events...")

    send_to_delta_table(result)

    print(f">> {len(result)} events successfully sent")

    for f in allFiles:
        try:
            os.remove(os.path.join(bufDir, f))
        except OSError:
            pass
