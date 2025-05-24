import time
import serial
import argparse
SERVO_PORT = "/dev/cu.usbserial-140"


class ArduinoController:
    def __init__(self, port = SERVO_PORT):
        self.arduino = serial.Serial(port=port, timeout=5, baudrate=9600)
        self.port = port

    def talkToServo(self, command):
        try:
            time.sleep(2)
            self.arduino.write(str.encode(command + "\n" ))
            print(str.encode(command+ "\n") )
            # arduino.write(str.encode("\n"))
            print(f"Communicating with arduino: {command}")
            # if self.arduino.readable() > 0:  # check if there's data in the serial buffer
            #     data = self.arduino.read(size=4).decode().strip()  # read the data from the serial port and decode it as a string
            #     print("Received:", data)  # print the received data
            #     return data
        except:
            self.arduino = serial.Serial(port=self.port, timeout=5, baudrate=9600)
            self.talkToServo(command=command)


        
    def restart_serial_connection(self):
        # Close the current serial connection
        self.arduino.close()
        
        # Re-open the serial connection
        self.arduino.open()
        time.sleep(1) 
    
    def checkCollision(self):
        while True:
            if self.arduino.readable():
                data = self.arduino.read().strip()
                if data == b'1':
                    return True
                else:
                    return False

    def checkDistance(self):
        # self.restart_serial_connection()
        self.arduino.reset_input_buffer()
        self.arduino.write(str.encode("s\n"))
        time.sleep(1)
        print("buffering")
        while True:
            if self.arduino.readable():
                data = self.arduino.read(size=4).strip()
                print("DISTANCE gotten:", data)
                if data == b'':
                    return None
                distance = int(data)
                return distance
            else:
                print("Waiting for data")
                time.sleep(1)

    def writeToSerial(self, command):
        self.arduino.write(str.encode(command + "\n"))
        time.sleep(0.3)
        print(f"Sent: {command}")

    def test(self):
        for i in range(10):
            print(self.checkDistance())
            time.sleep(1)
            print("Next")
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="Control the Arduino from the command line.")
    parser.add_argument("--servo", type=str, help="Send a command to the arduino to control the servo motor. g0 to open and g40 to close")
    parser.add_argument("--echo", action="store_true", help="Get the distance from the ultrasonic sensor")
    parser.add_argument("--test", action="store_true", help="Calibrate the ultrasonic sensor")

    args = parser.parse_args()
    arduino = ArduinoController()

    if args.servo:
        arduino.talkToServo(args.servo)
    elif args.echo:
        arduino.checkDistance()
    elif args.test:
         for i in range(10):
            print(arduino.checkDistance())
            time.sleep(1)
            print("Next")
            time.sleep(1)

if __name__ == "__main__":
     main()