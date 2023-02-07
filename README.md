# Robot Communication

## Introduction

This repository contains code for communicating with an ABB robot using Robot Web Services (RWS). The code is written in Python and is intended to be used to control the robot from a web application.

The provided code in `robcomm.py` is a wrapper around the RWS API. It provides a simple interface for sending commands to the robot and receiving data from it. The code is written in Python 3 and uses the `requests` library for sending HTTP requests to the robot. The code is tested on an ABB CRB 15000 robot in a virtual environment.

## Installation

Requirements:

- Python 3
- requests
- dacite
- ws4py
- urllib3

To install the requirements, run the following command:

        pip install -r requirements.txt

## Usage

To connect to a robot, create a `Robot` object and pass the robot's IP address and port number to the constructor. The port number depends on the robot's configuration. To configure the port used for virtual controllers in RobotStudio, refer to [Configuring RobotStudio ports.](#configuring-robotstudio-ports)

```python
    robot = Robot('127.0.0.1', 80)
```

### Subscribing to persistent variables

To subscribe to a persistent variable, call the `subscribe` method of the `Robot` object. The method takes a list of persistent variables to subscribe to. The persistent variables are specified as a string in the format `[TASK]/[MODULE]/[VARIABLE]`, e.g. `T_ROB1/Module1/Var1`.

```python
    robot.subscribe(['T_ROB1/Module1/Var1', 'T_ROB1/Module1/Var2'])
```

`subscribe` takes an optional `on_message` parameter. This parameter is a callback function that is called when a message is received from the robot. The callback function takes three parameters:

- `robot`: The `Robot` object that received the message.
- `variable_url`: The URL of the persistent variable that was updated.
- `value`: The new value of the persistent variable.

```python
    def on_message(robot, variable_url, value):
        print(f'Received message from {robot.ip} on {variable_url}: {value}')
    
    robot.subscribe(['T_ROB1/Module1/Var1', 'T_ROB1/Module1/Var2'], on_message)

    # Example output:
    # Received message from 127.0.0.1 on /rw/rapid/symbol/RAPID/T_ROB1/Module1/Var1: 1
```

### Updating a persistent variable

To update a persistent variable, call the `set_rapid_variable` method of the `Robot` object. The method takes a persistent variable to update. The persistent variables are specified as a string in the format `[TASK]/[MODULE]/[VARIABLE]`, e.g. `T_ROB1/Module1/Var1`. The value of the persistent variable is specified as a string.

```python
    robot.set_rapid_variable('T_ROB1/Module1/Var1', '2')

    # Updating an array variable
    robot.set_rapid_variable('T_ROB1/Module1/Var2', '[1, 2, 3]')
```

### Reading a persistent variable

To read a persistent variable, call the `get_rapid_variable` method of the `Robot` object. The method takes either an URL or a persistent variable. The persistent variables are specified as a string in the format `[TASK]/[MODULE]/[VARIABLE]`, e.g. `T_ROB1/Module1/Var1`. The method returns the value of the persistent variable as a string.

```python
    value = robot.get_rapid_variable(variable='T_ROB1/Module1/Var1')
    print(value) # 2

    # Alternatively, the URL of the variable can be specified. 
    # Your "on_message" callback function will receive the URL of the updated variable each time a message is received.
    value = robot.get_rapid_variable(url='/rw/rapid/symbol/RAPID/T_ROB1/Module1/Var1')
    print(value) # 2
```

An example of how to use communicate with a robot is provided in `example.py`. The example code is intended to be used in conjunction with the provided RobotStudio project, `example.rspag`.

## Configuring RobotStudio ports

Read [this](https://forums.robotstudio.com/discussion/12177/how-to-change-the-listening-port-of-the-virtual-controller-robotware-6-x-and-7-x) before changing the ports, as it outlines any potential issues that may arise. The following instructions are based on the instructions provided in the link above.

Virtual controllers in RobotStudio listen on port 80 by default. In the event that this port is already in use, it will try to use one of the following ports:

    5466
    9403
    9805
    11622
    19985
    31015
    34250
    40129
    45003

If the controller is unavailable on all of these ports, you may need to configure the port manually. This can be done by editing the `appweb.conf` file found at either of the following locations, depending on the version of RobotWare you are using:

    C:\Users\<USERNAME>\AppData\Local\ABB\RobotWare\RobotControl_<VERSION_NUMBER>\system\appweb.conf

or

    C:\Users\<USERNAME>\AppData\Local\ABB\RobotWare\RobotWare_<VERSION NUMBER>\system\appweb.conf

In the `appweb.conf` file you will find the following lines (ports may vary):

```python
    # Listen -1
    ListenSecure -1
```

You may change the port number to some other unused port. For example, to use port 8080, change the lines to:

```python
    # Listen -1
    ListenSecure 8080
```

After making the changes, restart RobotStudio and the virtual controller should be available on the new port.
