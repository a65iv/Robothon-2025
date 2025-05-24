
# IMPORTS
import cv2
import time
import random
from Camera import Cam
from DetectedObjects import DetectedObjects
from TrashClassifier import TrashClassifier
from ArduinoController import ArduinoController
from EpsonController import EpsonController, HOMEX, HOMEY, HOMEZ, MAX_Y, MAX_X


# CONSTANTS
MIN_DISTANCE_SONAR = 5
SAFE_Z_DISTANCE = 350
MIN_HEIGHT_EPSON = 173
RAISE_HEIGHT_EPSON = 500
HOME_VIEW = "output/home_view.png"
DROP_VIEW = "output/drop_view.png"


def dropObject(object_type, epson: EpsonController, arduino: ArduinoController):
    drop_point = epson.getDropPoints(object_type) # get the trianed drop points for the object type
    if drop_point is not None:
        epson.goto(x=drop_point[0], y=drop_point[1]) # since we have already raised the object we can go to the drop point without any obstacles
        time.sleep(1)
        epson.goto(z=drop_point[2]) # go down to the drop point safely
        time.sleep(1)

    print(f"Item of type {object_type} dropped at {drop_point}")

    


def main():
    # INITIALIZE MODULES
    camera = Cam(0)
    epson = EpsonController()
    arduino = ArduinoController()
    trash_classifier = TrashClassifier()



    # LOOP CONDITION VARIABLE
    pickable_objects = [ None ]

    # STATUS VARIABLES
    count = 0
    empty_counter = 3

    while True: 
        arduino.talkToServo("g5")
        print("start of loop")
        # START PROGRAM LOOP 
        # while len(pickable_objects) != 0: # while there are still objects to pick up
        cam = camera.take_picture(filename=HOME_VIEW)
        # if not cam:
            # break

        print("TAKE PICTURE: DEBUG")
        home_view = cv2.imread(HOME_VIEW)
        print("READ PICTURE: DEBUG")

        cp_home_view = home_view.copy()


        # DETECT OBJECT CONTOURS
        detector = DetectedObjects(home_view)
        
        pickable_objects = detector.getPickableObjects()
        sorted_list = detector.sortDetectedObjects(pickable_objects, camera_point=epson.robot_camera_position) # this needs to be fixed --> it not only doesn't tell us that its is changing the object but the sorting is not right, (it should place items that are closest to the camera first i.e home point) TODO
        random.shuffle(sorted_list)
        print(len(sorted_list))
        if len(sorted_list) <= 0:
            empty_counter -= 1
            if empty_counter == 0:
                break
            time.sleep(2)
            continue

        object = sorted_list[0]
        count +=1
        # CLASSIFY OBJECTS
        (x, y) = object.center_point
        print(x, y, "center point")

        (width, height) = object.dimensions

        (box_x, box_y) = object.boundaries

        cropped_image = cp_home_view[(y - height):y+(int(height)), (x - width):x+(int(width))]
        if x - width < 0 or y - height < 0: # if the cropped image is out of bounds
            cropped_image = cp_home_view[(box_y):y+(int(height)), (box_x):x+(int(width))]
            
        object_type = trash_classifier.classify(cropped_image) # the classify function should return the type of object (paper, plastic, metal, glass), the conversion of the values from floats to strings should be done in the classify function  TODO
        # sorted list should already have the center point and dimensions of the object

        # MOVE EPSON TO THE TOP OF THE OBJECT
        world_x, world_y = epson.getWorldCoordinates(x, y)
        if (world_y >= MAX_Y or world_x <= MAX_X):
            epson.goHome()
            print('ignoring point, moving home')
            continue
        else:
            epson.goto(world_x, world_y)



        # MAKE SURE THE SERVO IS OPEN ---> might be redundant
        arduino.talkToServo("g5")

        # MOVE THE EPSON DOWN TO THE OBJECT
        epson.goto(z=SAFE_Z_DISTANCE)
        # arduino_distance = arduino.checkDistance()
        # arduino_collide = arduino.checkCollision()
        # try:
        while epson.robot_z > MIN_HEIGHT_EPSON: # TODO the predicate for checkDistance looks like it will run only once here, it should be updated while the robot is moving down
            # arduino_collide = arduino.checkCollision()
            # if arduino_collide: 
            #     break
            if epson.robot_z - 45 <= MIN_HEIGHT_EPSON:
                epson.goto(z=MIN_HEIGHT_EPSON)
            else:
                epson.goto(z = epson.robot_z - 45)

        # arduino.writeToSerial("e") # stop the sonar

        # MINIMUM HEIGHT REACHED, CLOSE THE SERVO
        arduino.talkToServo("g30")
        time.sleep(1)


        # RAISE THE EPSON, WHILE THE SERVO IS CLOSED
        epson.goto(z = RAISE_HEIGHT_EPSON)
        time.sleep(1)


        # MOVE TO THE DROP POINT AND DROP ----> this needs to be implemented TODO 
        drop_point = epson.getDropPoints(object_type) # get the trianed drop points for the object type
        if drop_point is not None:
            epson.goto(x=drop_point[0], y=drop_point[1]) # since we have already raised the object we can go to the drop point without any obstacles
            time.sleep(1)
            epson.goto(z=drop_point[2]) # go down to the drop point safely
            time.sleep(1)

        arduino.talkToServo("g5") # open the servo
        # arduino.talkToServo("g20") # open the servo
        time.sleep(1)


        # GO BACK TO THE HOME POSITION
        epson.goto(z=HOMEZ)
        time.sleep(1)


        epson.goHome()
        
    # main()




if __name__ == "__main__":
    main()