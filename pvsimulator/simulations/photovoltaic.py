import click
import json
import math
import random
import sys
import time
from datetime import datetime

from pvsimulator import filewriter
from pvsimulator.queueclient import QueueClient
from pvsimulator.timemath import *
from pvsimulator.simulations import configuration


def get_normalized_pv_value(t):
    """
    Expects a value between 0 and 1 (0 -> 00:00:00 || 1 -> 24:00:00) and returns the normalized
    simulated photovoltaic output at that time, according to the graph on the challenge paper.

    The formula can be examinated on https://www.desmos.com/calculator
    The formula used is this one: 
    \max\left(\max\left(-\frac{\left(x-7\right)^{2}}{10}+1,\ -\frac{\left(x-6.3\right)^{2}}{100}+.2\right),\ 0\right)
    It tries to mimic the Graph as normalized values.
    
    f(0) = photovoltaic output at 00:00:00
    f(PI*4) = photovoltaic output at 24:00:00
    """
    x = t * math.pi * 4
    normalized_photovoltaic_value = max(
        -(math.pow(x - 7  , 2) / 10 ) + 1,
        -(math.pow(x - 6.3, 2) / 100) + 2
    )
    normalized_photovoltaic_value = max(
        normalized_photovoltaic_value,
        0
    )
    return normalized_photovoltaic_value

class PV_Simulator(QueueClient):
    def __init__(
            self, 
            host = 'localhost', 
            username = 'guest', 
            password = 'guest', 
            queue_name = 'queue',
            consuming_timeout = 0.25,
            output_filepath = 'output.csv'
        ):
        self._output_filepath = output_filepath
        super().__init__(host, username, password, queue_name, consuming_timeout)
    
    def _on_message_received_callback(self, message_body):
        # Check, if the simulation should be stopped
        if message_body == "STOP_SIMULATION":
            self.stop_consuming()
            return
        
        print("Received: ", message_body)
        message_body_json = json.loads(message_body)

        # Generate the pseudo random photovoltaic power value
        timestamp_value = int(message_body_json["timestamp"])
        normalized_daytime = get_normalized_daytime(timestamp_value)
        normalized_pv_power_value = get_normalized_pv_value(normalized_daytime)
        random_absolute_pv_power_value = normalized_pv_power_value * 3250 + random.randint(-50, 50)
        
        # Calculate the combined power value
        combined_power_value = random_absolute_pv_power_value + message_body_json["meter_power_value_watt"]
        
        # Generate the new csv output row
        output = [
            message_body_json["timestamp"],
            message_body_json["meter_power_value_watt"],
            random_absolute_pv_power_value,
            combined_power_value,
        ]
        # Append the row to the output file
        filewriter.file_append(self._output_filepath, output)

def simulate_photovoltaic_consumer(output, idletime):
    '''
    Start the photovoltaic simulation while blocking the Thread.
    '''
    pv = PV_Simulator(
        host = configuration.CONFIGURATION['host'],
        username = configuration.CONFIGURATION['username'],
        password = configuration.CONFIGURATION['password'],
        queue_name = configuration.CONFIGURATION['queue_name'], 
        consuming_timeout = idletime,
        output_filepath = output
    )
    pv.connect()
    pv.start_consuming_blocking()

@click.command()
@click.option(
    '--output', '-o', default='output.csv', type=click.STRING,
    help='The file, to which the output will be written to (default: \'output.csv\')'
)
@click.option(
    '--idletime', '-i', default=0, type=click.FLOAT,
    help='The time in seconds, the consumer should idle between each queue access (default: \'0.0\')'
)
@click.option(
    '--config', '-c', default=None, type=click.STRING,
    help='The filepath to an optional configuration file. (default: \'None\')'
)
def main(output, idletime, config):
    # If the config filepath was passed, try to load it
    if config:
        configuration.read_config_file(config)

    # Run the simulation until it stops or is cancelled
    try:
        simulate_photovoltaic_consumer(output, idletime)
    except KeyboardInterrupt:
        print("Execution was cancelled by user!")
        exit(0)
    except Exception as e:
        print(e)
        exit(0)

if __name__ == "__main__":
    sys.exit(main())

