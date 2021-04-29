"""Console script for pv_simulator."""
from datetime import datetime
import sys
import time

from pvsimulator.sender import Sender
from pvsimulator.receiver import Receiver

def main(args=None):
    meter = Sender('localhost', 'pv_simulation')
    pv = Receiver('localhost', 'pv_simulation')
    pv.start_consuming()
    while True:
        meter.send_message(str(datetime.utcnow()))
        time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
