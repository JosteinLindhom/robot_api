import threading
import time
import api

VARIABLE = "T_ROB1/TTBmain/waiting"
VARIABLE_2 = "T_ROB1/TTBmain/Sval"

def on_message(api: api.Robot, value):
        if value == 'TRUE':
            print("Robot stopped while waiting for signal from Python")
            print("Continuing in 5 seconds")
            for x in range(4, -1, -1):
                time.sleep(1)
                print(x, "...")
            print("Continuing")
            api.set_rapid_variable(VARIABLE, False)

rob = api.Robot(ip='127.0.0.1', port=80, user='Admin')
rob.subscribe(VARIABLE, on_message=on_message)

