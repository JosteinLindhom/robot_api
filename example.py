import robcomm
import math
import random

ROBOT_POS = "T_ROB1/Module1/position"
ROBOT_IN_POSITION = "T_ROB1/Module1/in_position"

def uri_for_variable(variable) -> str:
    return f"/rw/rapid/symbol/RAPID/{variable}/data"

class Robot:
    IN_POSITION = uri_for_variable(ROBOT_IN_POSITION)
    POS = uri_for_variable(ROBOT_POS)

    position = [0, 0, 0]

    def on_message(self, robcomm: robcomm.Robot, variable: str, value):
        match variable:
            case Robot.IN_POSITION:
                    robcomm.set_rapid_variable(ROBOT_IN_POSITION, False)
                    self.position = [self.position[0] + 1, self.position[1] + 1, 0]
                    # x and y values are between 100 and 400
                    x = 100 + random.random() * 300
                    y = 100 + random.random() * 300
                    # Set the position variable in the robot
                    robcomm.set_rapid_variable(ROBOT_POS, f"[{x}, {y}, {self.position[2]}]")
            case Robot.POS:
                print(f"Position {variable} changed to {value}")

if __name__ == '__main__':
    # Port needs to be configured
    rob = robcomm.Robot(ip='127.0.0.1', port=9933)
    robot = Robot()
    rob.subscribe([ROBOT_IN_POSITION, ROBOT_POS], on_message=robot.on_message)
    

