# PV_Simulator

This project is a implementation of the `PV Simulator Challenge`.  

> In this little challenge, we will request you to build an application which, among other tasks, generates simulated PV (photovoltaic) power values (in kW).
>
> <cite>The Mobility House GmbH</cite>

</br>
</br>

# Setup
To run this simulation, some prerequisites have to be made.

### 1. Setup a RabbitMQ instance
The RabbitMQ service is used to establish a communication between the systems.  
For information about how to setup an instance, visit https://www.rabbitmq.com/download.html  
> If its your first time using RabbitMQ, I would recommend to user the docker version.  
> It requires no special setup, just Docker has to be installed.

</br>

### 2. Clone the project (and `cd` into it)
Obvious step.  
For your clipboard:  
```
git clone https://github.com/nicohirsau/pv_simulator && cd pv_simulator
```

</br>

### 3. Install the required packages
This project uses some third-party pip packages.  
To install all of them at once just use:  
```
pip install -r requirements.txt
```

> I would recommend using a virtual environment.  
> (For example, one managed with this fine piece of software: https://virtualenvwrapper.readthedocs.io/en/latest/)

</br>

### 4. Install the project as a local pip package
This project assumes to be installed as local pip egg.  
To do this, you have at least these <del>3</del> 2 choices:  

1. Install it through pip: 
```
pip install -e .
```
2. Use the setup.py: 
```
python setup.py install
```

</br>

### 5. Setup a configuration file <strong><em>(optional)</em></strong>
The simulation will connect to a RabbitMQ instance.  
For this to work, it needs some basic informations like:
- The hostname of the instance
- A login name and password
- A name for the queue, that's going to be used

As default, these informations are defined as followed:  
```
host = localhost  
username = guest  
password = guest  
queue_name = pv_simulation  
```
When you start the simulation, you are able to pass a 
filepath to a configuration file, to change these values.  
One example configuration file can be found under
`pvsimulator/simulations/example.conf`.
It's content looks like this:
```
[simulation-config]
host = localhost
username = guest
password = guest
queue_name = pv_simulation
```
If you choose to use custom values, you should copy this file and 
edit the content of the copy.  
So, the changes are not tracked by git.  
How to pass the config filepath is shown further below.

</br>

# Simulation information
The simulation consists of 2 parts:
- The Meter, simulating an average household power consumption
- The Photovoltaic System, simulating an average photovoltaic power generation

The Meter will publish the usage values with timestamps over the RabbitMQ instance.  
The Photovoltaic System will consume these messages, calculate the power generation at the time of the timestamp and write all the information into an csv formatted file.  
  
Since these 2 simulate seperate systems, you have to start both seperately to run the simulation.  
Both scripts can be found under `pvsimulator/simulations/`, one named `meter.py` and the other `photovoltaic.py`.

</br>

## The Meter
```
Usage: python meter.py [OPTIONS]

Options:
  -m, --mode [oneday|endless]  The kind of simulation that should be run. (default: 'oneday')
  -t, --timestep INTEGER       The amount of seconds to wait between each message. (default: '1')

  -c, --config TEXT            The filepath to an optional configuration file. (default: 'None')
  --help                       Show this message and exit.
```

> With each run, the meter will first purge the queue to start with a clean state.

## --mode
The Meter simulation can be executed in 2 modes:
### oneday
This mode will simulate one day of consumption and then exit.  
It simulates the Jul 9, 2009 from 00:00:00 to 24:00:00.
### endless
This mode will simulate a live meter, using the current time.  
It runs until stopped by the user `(Ctrl+C)`.

> After the end of each meter simulation, a `STOP_SIMULATION` message will be published.  
> This will stop the photovoltaic simulation when it receives it.

</br>

## Photovoltaic
```
Usage: python photovoltaic.py [OPTIONS]

Options:
  -o, --output TEXT     The file, to which the output will be written to (default: 'output.csv')
  -i, --idletime FLOAT  The time, the consumer should idle between each queue access (default: '0.0')

  -c, --config TEXT     The filepath to an optional configuration file. (default: 'None')
  --help                Show this message and exit.
```
The Photovoltaic simulation runs until stopped by the user `(Ctrl+C)` or the receiving of the `STOP_SIMULATION` message.

</br>

# Example Usage

In one terminal start the meter simulation with:
```
python pvsimulator/simulations/meter.py -t 10 -c ./myconfig.conf
```
To simulate one day of power consumption and then exit.  
  
In another terminal start the photovoltaic simulation with:
```
python pvsimulator/simulations/photovoltaic.py -o ./myoutput.csv -c ./myconfig.conf
```
To let it consume and process all messages from the Meter.  
It will exit, when it received the `STOP_SIMULATION` message or is cancelled by the user. 

</br>

# The output
I chose to use the csv format for the output file.  
It allows me to just append more information row by row without, for example in the json format, parsing the whole file at each write.  
  
The csv filecontent could look like this:
```
1247097600,1805.0,5252.075,7057.075
1247097601,1806.4555296646004,5256.1345586732195,7062.59008833782
1247097602,1828.9110567851385,5176.194115971431,7005.105172756569
1247097603,1849.3665813560292,5197.253671894631,7046.62025325066
1247097604,1769.8221033716889,5230.313226442823,7000.135329814512
```
where the comma seperated colums mean the following:  
`timestamp|meter_power_value|photovoltaic_power_value|combined_power_value`  
> The timestamp is a `seconds since epoch` timestamp.  
> All power values are in `Watt`.

</br>

# Tests
For demonstration purposes, I implemented a few automated test cases with the `pytest` framework (https://docs.pytest.org/en/6.2.x/).  
  
Since they are not part of the implementation logic itself, I did not put the `pytest` pip requirement in the `requirements.txt`-file.    
So, to run them first install pytest through
```
pip install pytest
```
and then simply run
```
pytest
```
in the root directory of this project.  
  
> It has to be run from the root directory, so that the relative path to the `./tests/test.conf`-file matches.  
> In this config file, you can setup your RabbitMQ settings for the test runs.