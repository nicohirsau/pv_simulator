# PV_Simulator

This project is a implementation of the `PV Simulator Challenge`.  

> In this little challenge, we will request you to build an application which, among other tasks, generates simulated PV (photovoltaic) power values (in kW).
>
> <cite>The Mobility House GmbH</cite>

</br>
</br>

# Setup
## Prerequisites
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

# Usage
> Not completely defined yet!