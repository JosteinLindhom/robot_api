# Robot Communication

## Introduction

This repository contains code for communicating with an ABB robot using Robot Web Services (RWS). The code is written in Python and is intended to be used to control the robot from a web application.

The provided code in `robcomm.py` is a wrapper around the RWS API. It provides a simple interface for sending commands to the robot and receiving data from it. The code is written in Python 3 and uses the `requests` library for sending HTTP requests to the robot. The code is tested on an ABB CRB 15000 robot in a virtual environment.

## Installation

Requirements:
    - Python 3
    - requests library
    - dacite library
    - ws4py library
    - urllib3 library

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
- `variable`: The full URI of the persistent variable that was updated.
- `value`: The new value of the persistent variable.

```python
    def on_message(robot, variable, value):
        print(f'Received message from {robot.ip} on {variable}: {value}')
    
    robot.subscribe(['T_ROB1/Module1/Var1', 'T_ROB1/Module1/Var2'], on_message)

    # Example output:
    # Received message from 127.0.0.1 on /rw/rapid/symbol/RAPID/T_ROB1/Module1/Var1: 1
```

An example of how to use communicate with a robot is provided in `example.py` . The example code may be used in conjunction with the provided RobotStudio project, `example.rspag`.

## Configuring RobotStudio ports
