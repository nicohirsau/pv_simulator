from datetime import datetime
import json
import sys
import time
import random

from pvsimulator.queueclient import QueueClient

def simulate_household_output():
    meter = QueueClient(queue_name = 'pv_simulation')
    meter.connect()
    while True:
        message = json.dumps(
            {
                "timestamp": str(datetime.utcnow()),
                "watt_value": random.randint(0, 9000)
            }
        )
        meter.publish_message(message)
        time.sleep(1)

def main(args=None):
    try:
        simulate_household_output()
    except KeyboardInterrupt:
        print("Execution was interrupted by the user!")
        exit(0)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
