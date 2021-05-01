import calendar
import json
import math
import random
import sys
import time
from datetime import datetime

from pvsimulator.queueclient import QueueClient
from pvsimulator.timemath import *


def get_normalized_meter_value(t):
    """
    Expects a value between 0 and 1 (0 -> 00:00:00 || 1 -> 24:00:00) and returns the normalized
    simulated household consumption at that time, according to this
    Graph: http://blog.abodit.com/images/uploads/2010/05/HomeEnergyConsumption.png

    The formula can be examinated on https://www.desmos.com/calculator
    The formula used is this one: 
    \frac{\left(\sin\left(x\right)\ +\ \frac{x}{2.5}\ \cdot\left(-e^{\frac{x}{12}}+2.85\right)+1\right)}{5}
    It tries to mimic the Graph as normalized values.
    
    f(0) = power consumption at 00:00:00
    f(PI*4) = power consumption at 24:00:00
    """
    x = t * math.pi * 4
    meter_value = math.sin(x) + (x/2.5) * (-math.pow(math.e, x / 12.0) + 2.85) + 1
    normalized_meter_value = meter_value / 5.0
    return normalized_meter_value

def simulate_one_day():
    meter = QueueClient(queue_name="pv_simulation")
    meter.connect()
    meter.purge_queue()

    t0 = calendar.timegm(
        time.strptime('Jul 9, 2009 @ 00:00:00 UTC', '%b %d, %Y @ %H:%M:%S UTC')
    )
    seconds_in_a_day = 86400

    for deltasecond in range(seconds_in_a_day):
        t_now = t0 + deltasecond
        normalized_daytime = get_normalized_daytime(t_now)
        normalized_meter_power_value = get_normalized_meter_value(normalized_daytime)
        random_absolute_meter_power_value = normalized_meter_power_value * 9000 + random.randint(-50, 50)

        message_body = json.dumps(
            {
                "timestamp": t_now,
                "meter_power_value_watt": random_absolute_meter_power_value
            }
        )

        meter.publish_message(
            message_body
        )
        print("Published: ", message_body)

def simulate_normal_operation():
    meter = QueueClient(queue_name="pv_simulation")
    meter.connect()
    meter.purge_queue()

    while True:
        t_now = int(time.time())
        normalized_daytime = get_normalized_daytime(t_now)
        normalized_meter_power_value = get_normalized_meter_value(normalized_daytime)
        random_absolute_meter_power_value = normalized_meter_power_value * 9000 + random.randint(-50, 50)

        message_body = json.dumps(
            {
                "timestamp": t_now,
                "meter_power_value_watt": random_absolute_meter_power_value
            }
        )

        meter.publish_message(
            message_body
        )
        print("Published: ", message_body)

def main(args=None):
    try:
        simulate_one_day()
    except KeyboardInterrupt:
        print("Execution was interrupted by the user!")
        exit(0)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
