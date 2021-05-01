import json
import math
import random
import sys
import time
from datetime import datetime

from pvsimulator import filewriter
from pvsimulator.queueclient import QueueClient
from pvsimulator.timemath import *


def get_normalized_pv_value(t):
    """
    Expects a value between 0 and 1 (0 -> 00:00:00 || 1 -> 24:00:00) and returns the normalized
    simulated photovoltaic output at that time, according to the graph on the challenge paper.

    The formula can be examinated on https://www.desmos.com/calculator
    The formula used is this one: 
    \max\left(-\frac{\left(x-7\right)^{2}}{10}+1,\ -\frac{\left(x-6.3\right)^{2}}{100}+.2\right)
    It tries to mimic the Graph as normalized values.
    
    f(0) = photovoltaic output at 00:00:00
    f(PI*4) = photovoltaic output at 24:00:00
    """
    x = t * math.pi * 4
    normalized_photovoltaic_value = max(
        -(math.pow(x - 7  , 2) / 10 ) + 1,
        -(math.pow(x - 6.3, 2) / 100) + 2
    )
    return normalized_photovoltaic_value

class PV_Simulator(QueueClient):
    def __init__(
            self, 
            host = 'localhost', 
            username = 'guest', 
            password = 'guest', 
            queue_name = 'queue',
            consuming_timeout = 0.25
        ):
        super().__init__(host, username, password, queue_name, consuming_timeout)
    
    def _on_message_received_callback(self, method_body):
        print("Received: ", method_body)
        method_body_json = json.loads(method_body)

        timestamp_value = int(method_body_json["timestamp"])
        normalized_daytime = get_normalized_daytime(timestamp_value)
        normalized_pv_power_value = get_normalized_pv_value(normalized_daytime)
        random_absolute_pv_power_value = normalized_pv_power_value * 3250 + random.randint(-50, 50)
        random_absolute_pv_power_value = max(random_absolute_pv_power_value, 0)
        
        combined_power_value = random_absolute_pv_power_value + method_body_json["meter_power_value_watt"]
        
        method_body_json["combined_power_value_watt"] = combined_power_value
        method_body_json["photovoltaic_power_value_watt"] = random_absolute_pv_power_value
        output = [
            method_body_json["timestamp"],
            method_body_json["meter_power_value_watt"],
            method_body_json["photovoltaic_power_value_watt"],
            method_body_json["combined_power_value_watt"],
        ]
        filewriter.file_append("output.csv", output)

def simulate_photovoltaic_consumer():
    pv = PV_Simulator(queue_name = 'pv_simulation', consuming_timeout = 0)
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

