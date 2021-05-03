import calendar
import click
import json
import math
import random
import sys
import time
from datetime import datetime

from pvsimulator.queueclient import QueueClient
from pvsimulator.timemath import *
from pvsimulator.simulations import configuration


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

def construct_message_at_time(t):
    '''
    Constructs the message body at the time t.
    The value is based on the simulated output + a random value.

    Params:
        t: Seconds since epoch.
    '''
    # Generate the pseudo random meter value
    normalized_daytime = get_normalized_daytime(t)
    normalized_meter_power_value = get_normalized_meter_value(
        normalized_daytime
    )
    random_absolute_meter_power_value = normalized_meter_power_value * 8500 + random.randint(-50, 50)

    # Pack all values in one dict. Ready to be published.
    message_body = json.dumps(
        {
            "timestamp": t,
            "meter_power_value_watt": random_absolute_meter_power_value
        }
    )
    return message_body

def simulate_one_day(timestep):
    '''
    Runs the meter simulation for one simulated day.
    After finishing it, it will send the stop message and exit.

    Params:
        timestep: The amount of seconds to wait between each message.
    '''
    meter = QueueClient(
        host = configuration.CONFIGURATION['host'],
        username = configuration.CONFIGURATION['username'],
        password = configuration.CONFIGURATION['password'],
        queue_name = configuration.CONFIGURATION['queue_name']
    )
    meter.connect()
    meter.purge_queue()

    t0 = calendar.timegm(
        time.strptime('Jul 9, 2009 @ 00:00:00 UTC', '%b %d, %Y @ %H:%M:%S UTC')
    )
    seconds_in_a_day = 86400

    for deltasecond in range(0, seconds_in_a_day, timestep):
        t_now = t0 + deltasecond
        message_body = construct_message_at_time(t_now)

        meter.publish_message(
            message_body
        )
        print("Published: ", message_body)

    meter.publish_message("STOP_SIMULATION")

def simulate_normal_operation(timestep):
    '''
    Runs the simulation in a 'live' mode, using the current time.
    It will run, until it is stopped by the user.

    Params:
        timestep: The amount of seconds to wait between each message.
    '''
    meter = QueueClient(
        host = configuration.CONFIGURATION['host'],
        username = configuration.CONFIGURATION['username'],
        password = configuration.CONFIGURATION['password'],
        queue_name = configuration.CONFIGURATION['queue_name']
    )
    meter.connect()
    meter.purge_queue()

    try:
        while True:
            t_now = int(time.time())

            message_body = construct_message_at_time(t_now)

            meter.publish_message(
                message_body
            )
            print("Published: ", message_body)
            time.sleep(timestep)

    except KeyboardInterrupt:
        meter.publish_message("STOP_SIMULATION")
        print("Execution was cancelled by user!")
        return


@click.command()
@click.option(
    '--mode', '-m', default='oneday', type=click.Choice(['oneday', 'endless']), 
    help='The kind of simulation that should be run. (default: \'oneday\')'
)
@click.option(
    '--timestep', '-t', default=1, type=click.INT,
    help='The amount of seconds to wait between each message. (default: \'1\')'
)
@click.option(
    '--config', '-c', default=None, type=click.STRING,
    help='The filepath to an optional configuration file. (default: \'None\')'
)
def main(mode, timestep, config):
    if config:
        configuration.read_config_file(config)

    try:
        if mode is 'oneday':
            simulate_one_day(timestep)
        elif mode is 'endless':
            simulate_normal_operation(timestep)
    except KeyboardInterrupt:
        print("Execution was cancelled by user!")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
