import time
import robcomm

VARIABLE = "T_ROB1/TTBmain/waiting"
VARIABLE_2 = "T_ROB1/TTBmain/Sval"

WAIT_TIME = 5

def on_message(robcomm: robcomm.Robot, value):
        if value == 'TRUE':
            print("Robot stopped while waiting for signal from Python")
            print(f'Continuing in {WAIT_TIME} seconds')
            for x in range(WAIT_TIME - 1, -1, -1):
                time.sleep(1)
                print(x, "...")
            print("Continuing")
            robcomm.set_rapid_variable(VARIABLE, False)

rob = robcomm.Robot(ip='152.94.0.228', port=443, user='Admin')
rob.subscribe(VARIABLE, on_message=on_message)
