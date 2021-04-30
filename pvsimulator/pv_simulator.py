from datetime import datetime
import json
import sys
import time
import random

from pvsimulator.receiver import Receiver

class PV_Simulator(Receiver):
    def __init__(
            self, 
            host = 'localhost', 
            username = 'guest', 
            password = 'guest', 
            queue_name = 'queue'
        ):
        super().__init__(host, username, password, queue_name)
    
    def _on_message_received_callback(self, method_body):
        print(method_body)

def simulate_photovoltaic_consumer():
    pv = PV_Simulator(queue_name = 'pv_simulation')
    pv.connect()
    pv.start_consuming_blocking()

def main(args=None):
    try:
        simulate_photovoltaic_consumer()
    except KeyboardInterrupt:
        print("Execution was cancelled by user!")
        exit(0)
    except Exception:
        exit(0)

if __name__ == "__main__":
    sys.exit(main())

