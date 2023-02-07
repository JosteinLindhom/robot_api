import robcomm
import random

ROBOT_POS = "T_ROB1/Module1/position"
ROBOT_IN_POSITION = "T_ROB1/Module1/in_position"

def url_for_variable(variable) -> str:
    return f"/rw/rapid/symbol/RAPID/{variable}/data"

class Example:
    IN_POSITION = url_for_variable(ROBOT_IN_POSITION)
    POS = url_for_variable(ROBOT_POS)

    # This function is called when a message is received for any of the subscribed variables
    def on_message(self, robcomm: robcomm.Robot, variable_url: str, value):
        match variable_url:
            case Example.IN_POSITION:
                if value == "FALSE":
                    # Ignore the message if the robot is not in position
                    print("Robot is moving")
                    return
                if value == "TRUE":
                    new_pos = robcomm.get_rapid_variable(variable=ROBOT_POS)
                    print(f"Robot is in position {new_pos}")
                
                # Create new random x, y and z values
                x = 100 + random.random() * 300
                y = 100 + random.random() * 300
                z = 0 + random.random() * 300

                # Set the updated position in the robot
                robcomm.set_rapid_variable(ROBOT_POS, f"[{x}, {y}, {z}]")
                
                # Signal that the robot is not in position
                robcomm.set_rapid_variable(ROBOT_IN_POSITION, False)
            case Example.POS:
                print(f"Position {variable_url} changed to {value}, {robcomm.ip}")

if __name__ == '__main__':
    # Create a connection to the robot
    robot = robcomm.Robot(ip='127.0.0.1', port=9933)
    # Create a local example object to handle the messages
    example = Example()
    # Subscribe to the in_position and position variables, and call the on_message function when a message is received
    robot.subscribe([ROBOT_IN_POSITION, ROBOT_POS], example.on_message)
    

