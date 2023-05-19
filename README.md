# 2D Plotter Image Converter/Arduino Controller
This program processes an inputted image and converts it into controls for a connected Arduino. It consists of two parts: Python code for image processing and conversion, and Arduino code for controlling the stepper motors and servo motor.

# Python Code
Dependencies
* cv2
* matplotlib
* numpy
* sys
* math
* serial
* json
* time
# Usage
* Provide the path to the input image (drawing_image.png) 
* Enter a scaling factor to reduce the size of the image.
* Enter the dimensions of the canvas in inches.
* Preview the image graph.
* Adjust the Arduino code accordingly with the initial position of the stepper motors.
* Connect Arduino to COM3 port. Use a 9600 baud rate.
* Run the program to send the points to the Arduino.
# Arduino Code
Dependencies
* AccelStepper
* AFMotor
* ArduinoJson
* Servo
# Usage
* Upload the Arduino code to your Arduino board.
* Connect the stepper motors and servo motor to the appropriate ports on a L293D Motor Driver Board.
* Make sure the baud rate in the Arduino code matches the baud rate set in the Python code (9600).
* Run the Python code to send the points to the Arduino.
