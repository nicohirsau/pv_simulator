from datetime import datetime
import json
import sys
import time
import random

from pvsimulator.queueclient import QueueClient

class PV_Simulator(QueueClient):
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
    pv.start_consuming_async()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pv.stop_consuming_async()
        print("Execution was cancelled by user!")
        exit(0)
    except Exception:
        exit(0)

def main(args=None):
    simulate_photovoltaic_consumer()
    

if __name__ == "__main__":
    sys.exit(main())

