from enum import Enum
import cv2
import math
import socket
import asyncio
import argparse

from modules.Camera import Cam
from modules.Point import Point
from modules.Calibrator import Calibrator

# setting up constants
EPSON_ROBOT_IP = "192.168.1.2"


# Initialize calibrator
calibrator = Calibrator()

class EpsonController:

    class Action(Enum):
        G1 = "g1"
        PRESS_RED_BLUE_RED = "go_pressRedBlueRed"
        PRESS_RED = "go_pressRedOnly"
        PRESS_BLUE = "go_pressBlueOnly"

        BALL_MAZE_1 = "go_ballMaze1"
        BALL_MAZE_2 = "go_ballMaze2"

        SWIPE_UP_A = "go_swipeUpA"
        SWIPE_UP_B = "go_swipeUpB"
        SWIPE_AB = "go_swipeAB"
        SWIPE_BA = "go_swipeBA"
        SWIPE_AG = "go_swipeABackground"
        SWIPE_BG = "go_swipeBBackground"
        SWIPE_GA = "go_swipeBackgroundA" 
        SWIPE_GB = "go_swipeBackgroundB"
        
        LONG_PRESS_A = "go_longA"
        LONG_PRESS_B = "go_longB"
        LONG_PRESS_G = "go_longG"

        TAP_A = "go_tapA"
        TAP_B = "go_tapB"
        TAP_G = "go_tapBackground"
        DTAP_A = "go_doubletapA"
        DTAP_B = "go_doubletapB"
        DTAP_G = "go_doubletapBackground"

        PEN_PLACE = "go_penPlace"
        PEN_PICK = "go_penPick"

        SCREEN_CAMERA = "go_screenCamera"

        DRAW_CIRCLE = "go_drawCircle"
        DRAW_TRIANGLE = "go_drawTriangle"
        DRAW_SQUARE = "go_drawSquare"
        
        DO_PRESS_RBR = "do_pressRBR"
        DO_MAZE1 = "do_Maze1"
        DO_MAZE2 = "do_Maze2"      
        STYLUSREADY = "stylusReady"
        MAGNETREADY = "magnetReady"
        PENPICK = "penPick"
        PENPLACE = "penPlace"
        ARMREADY = "armReady"  

       
    def __init__(self):

        # setting up socket
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((EPSON_ROBOT_IP, 2001))
        self.clientSocket.settimeout(60) 

        # set up calibrator
        self.calibrator = Calibrator()
        self.isPerformingAction = False
        
        # EPSON STATE
        self.history = []


    def goto(self, x=None, y=None, z=None, u=0):
        # Single source of truth for the location of the arm 
        # if x, y, or z are not provided, the robot will stay in the same position
        if x == None:
            x = self.robot_x
        if y == None:
            y = self.robot_y
        if z == None:
            z = self.robot_z
        

        coordinates = f"GO {x} {y} {z} {u}\r\n"
        print(f"Sending to position {x}, {y}")
        self.clientSocket.send(coordinates.encode())
        try:
            confirmation = self.clientSocket.recv(1023)
            print("result:", confirmation)
        except:
            pass


        # after the robot has moved, we need to update the robot's position
        self.robot_x = x
        self.robot_y = y
        self.robot_z = z


    def setLocalFrame(self, pointA: Point, pointB: Point):
        print(f"Setting a new local frame\n pointA: {str(pointA)}\n pointB: {str(pointB)}")
        command= f"local {pointA.x:.2f} {pointA.y:.2f} {pointB.x:.2f} {pointB.y:.2f}\r\n"
        print("command:", command)
        self.clientSocket.send(command.encode())
        try:
            confirmation = self.clientSocket.recv(1023)
            print("result:", confirmation)
        except:
            pass

    
    def getWorldCoordinates(self, point: Point):
        # self.calibrator.rotate(90)
        x_world, y_world = self.calibrator.predict({'x':point.x, 'y': point.y})
        print(str(point))
        return Point(x_world, y_world)

    
    def getLocation(self):
        print(f"x: {self.robot_x}, y: {self.robot_y}, z: {self.robot_z}")
    

    async def executeTask(self, action) -> bool:
        if self.isPerformingAction:
            # if the epson is already performing an action then do nothing
            print("EPSON already performing an action, IGNORING NEW ACTION")
            return False
        
        self.isPerformingAction = True
        if isinstance(action, self.Action):
            command = f"{action.value}\r\n"
            print(f"Sending command: {command.strip()}")

            def blocking_send_recv():
                try:
                    self.clientSocket.send(command.encode())
                    confirmation = self.clientSocket.recv(1023)
                    print("result:", confirmation)
                    self.isPerformingAction = False
                    return True if confirmation else False
                except Exception as e:
                    print(f"Error during send/recv: {e}")
                    self.isPerformingAction = False
                    return False

            actionComplete = await asyncio.to_thread(blocking_send_recv)
            return actionComplete
        
        else:
            print("Invalid action provided.")
            return False




async def main():
    parser = argparse.ArgumentParser(description="Control the Epson robot from the command line.")
    parser.add_argument("--goto", nargs="+", type=float, metavar="N", help="Move the robot to the specified X, Y, Z coordinates.")
    parser.add_argument("-d", type=str, help="Pick a direction to move the robot, x, y, z, xy, yz, xz, xyz.")
    parser.add_argument("--home", action="store_true", help="Move the robot to the home position.")
    parser.add_argument("--loc", action="store_true", help="Print out the current location of the robot")
    parser.add_argument("--train", type=int, help="Trains points for the epson robot to remember, you can specify the number of points to train.")
    parser.add_argument("--point_control", action="store_true", help="Control the robot using the mouse to select points on the screen.")
    parser.add_argument("--goCamera", action="store_true", help="Go to camera position.")
    parser.add_argument("--execute_task", type=str, help="Execute a taskboard pattern on the robot.")

    args = parser.parse_args()
    epson = EpsonController()

    if args.goto:
        if args.d: 
            try:
                if args.d == "x":
                    epson.goto(x=args.goto[0])
                elif args.d == "y":
                    epson.goto(y=args.goto[0])
                elif args.d == "z":
                    epson.goto(z=args.goto[0])
                elif args.d == "xy":
                    epson.goto(x=args.goto[0], y=args.goto[1])
                elif args.d == "yz":
                    epson.goto(y=args.goto[0], z=args.goto[1])
                elif args.d == "xz":
                    epson.goto(x=args.goto[0], z=args.goto[1])
                elif args.d == "xyz":
                    epson.goto(x=args.goto[0], y=args.goto[1], z=args.goto[2])
                else: 
                    print("Invalid direction provided. Use --help for usage information.")
            except:
                print("Invalid coordinates provided. Use --help for usage information.")
        else:
            print("No direction provided. Use -d to specify a direction")

    elif args.point_control:
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                font = cv2.FONT_HERSHEY_SIMPLEX
                color = (255, 0, 0)  # white color in BGR format
                copy = param["image"]

                # Get the size of the text
                text_size, _ = cv2.getTextSize(f"{x}{y}", font, 1, 2)

                # Draw a circle around the point on the image copy
                cv2.circle(copy, (x, y), 10, (255, 0, 0), 2)
                # Put the text on the image
                cv2.putText(
                    copy, f"{math.ceil(x)}, {math.ceil(y)}", (x, y - 10), font, 0.5, color, 2)

                # Display the image with circles
                cv2.imshow('point', copy)

                # Go to position
                point = epson.getWorldCoordinates(Point(x=x, y=y))
                epson.goto(x=point.x, y=point.y)

        cam = Cam(0)
        cam.take_picture(filename="./point_control.png")
        img = cv2.imread("./point_control.png")
        cv2.imshow("point", img)
        cv2.setMouseCallback('point', mouse_callback, {"image": img})
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    elif args.home:
        epson.goHome()
    elif args.goCamera:
        epson.goCamera()
    elif args.loc: 
        epson.getLocation()
    elif args.train:
        # first we need to take a picture
        cam = Cam(0)
        # take a picture
        cam.take_picture(filename="output/train.png")
        # show the image
        img = cv2.imread("output/train.png")
        cv2.imshow("point", img)
        # pick a point on the picture
        if args.train < cam.getCount():
            cv2.setMouseCallback('point', cam.point, {"image": img})
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            cam.release()
    elif args.execute_task:
        await epson.executeTask(EpsonController.Action[args.execute_task.upper()])
    else:
        print("No valid command provided. Use --help for usage information.")

if __name__ == "__main__":
    asyncio.run(main())
