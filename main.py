# Program: 2D Plotter Image Converter/ Arduino Controller
# Programmer: Eric Brooks
# Date: 5/19/2023
# Description: Program processes an inputted image and converts it into controls for a connected arduino.




import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys
import math
import serial
import json
import time

# Load the input image
original_image = cv2.imread('drawing_image.png')

downsizeFactor = int(input("To reduce the size of your image, enter a scaling factor: "))

# Grabs the dimensions of the original image and sets them to the new image
width = int(original_image.shape[1]) / downsizeFactor
height = int(original_image.shape[0]) / downsizeFactor

# Gives the user the height to width ratio, to help determine the dimensions of the canvas
height_to_width_ratio = round((height / width), 1)
print("Your image height to width ratio is: {} ".format(height_to_width_ratio))

# Asks for the height and width of the actual canvas to use in later calculations
canvas_height = int(input("How tall is your canvas in inches? "))
canvas_width = int(input("How wide is your canvas in inches? "))


# Creates a scaling factor to convert pixel distance to physical distance
scaling_factor = canvas_height / height

# Resize the image (Possible unnecessary anymore)
resized_image = cv2.resize(original_image, (int(width), int(height)))

# Convert the image to grayscale
grayscale_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to the grayscale image
blurred_image = cv2.GaussianBlur(grayscale_image, (5, 5), 0)

# Apply Canny edge detection to the blurred image. Takes the image, and a lower and upper threshold find the edges of
# the image. Increase the thresholds to allow more "noise", decrease to remove noise.
edged_image = cv2.Canny(blurred_image, 100, 100)

# Save binary image
cv2.imwrite('edged_image.png', edged_image)

# Asks the user if they want to continue with the program (allows the user to check if the processed image is good or
# not before preforming main bulk of program
exit_while_statement = False
while exit_while_statement == False:
    break_or_continue = input("Would you like to continue? (y/n) ")
    if break_or_continue == "y":
        exit_while_statement = True
        pass
    elif break_or_continue == "n":
        sys.exit()
    else:
        pass

print("Processing Image, this may take awhile. If taking too long, consider downsizing your image")

# Convert the binary image into an array
binary_image = np.array(edged_image)

# Create a list to store the drawing path
unsorted_path = []

# Embedded for loop to put any pixels that are white into the unsorted_path array
for x in range(binary_image.shape[0]):
    for y in range(binary_image.shape[1]):
        if binary_image[x, y] == 255:
            unsorted_path.append((y, x))

# Stores the length of the original list, used later on to calculate program completion
original_length = len(unsorted_path)

# An array to contain the order of which path the robot will follow to draw image
path = []


# Move the first entry of the unsorted_path list to the path list
path.append(unsorted_path[0])
del unsorted_path[0]

# While loop will preform a distance calculation between the path point and every unsorted_point to find the closest
# point, then appends point to path list and repeats until unsorted_path is empty
while len(unsorted_path) >= 1:
    # Used to make the first distance recorded the "shortest distance"
    shortest_distance = 10000000000000000000000000000

    # If the last entry in the path list is a travel marker, look at the second to last entry
    if path[-1][0] == 8888:
        for i in range(len(unsorted_path)):
            # Access x and y of path point
            x1 = path[-2][0]
            y1 = path[-2][1]
            # Access x and y of unsorted point
            x2 = unsorted_path[i][0]
            y2 = unsorted_path[i][1]

            # Distance formula
            distance = ((y1 - y2) ** 2 + (x1 - x2) ** 2) ** (1 / 2)

            # If the distance is smaller than the smallest distance, its point's index will be recorded
            if distance <= shortest_distance:
                shortest_distance = distance
                closest_point_index = i
            else:
                pass
    else:
        for i in range(len(unsorted_path)):
            # Access x and y of path point
            x1 = path[-1][0]
            y1 = path[-1][1]
            # Access x and y of unsorted point
            x2 = unsorted_path[i][0]
            y2 = unsorted_path[i][1]

            # Distance formula
            distance = ((y1 - y2) ** 2 + (x1 - x2) ** 2) ** (1 / 2)

            # If the distance is smaller than the smallest distance, its point's index will be recorded
            if distance <= shortest_distance:
                shortest_distance = distance
                closest_point_index = i
            else:
                pass

    # If the distance to the next point is greater than 3 pixels, append a "travel marker" around the next point
    if shortest_distance > 3:
        # Markers to signal the robot to lift the pen
        path.append([9999, 9999])
        # The point with the shortest distance will then be added to the path list and removed from the unsorted_path list
        path.append(unsorted_path[closest_point_index])
        del unsorted_path[closest_point_index]
        # Markers to signal the robot to put down the pen
        path.append([8888, 8888])
    else:
        # The point with the shortest distance will then be added to the path list and removed from the unsorted_path list
        path.append(unsorted_path[closest_point_index])
        del unsorted_path[closest_point_index]

# Scaling constant to convert the cable length to the number of steps for the stepper motor
steps_per_inch = 125

# Lists to store the x and y value of the points to then be graphed with matplot
y_path = []
x_path = []

# Array of stepper motor commands to send to the arduino
points = []

# Converts the x,y coordinates into cable lengths where cable1 and cable2 are the left and right cables respectively
for i in range(len(path)):
    # Attaching pen commands to points list
    if path[i][0] == 9999:
        points.append(9999)
        points.append(9999)
    elif path[i][0] == 8888:
        points.append(8888)
        points.append(8888)
    else:
        x = path[i][0] + 1
        x2 = width - x + 1
        y = path[i][1] + 1
        angle1 = np.arctan2(y, (x + 1))
        angle2 = np.arctan2(y, (x2 + 1))
        cable_length_1 = (y * (1 / np.sin(angle1))) * scaling_factor * steps_per_inch
        cable_length_2 = (y * (1 / np.sin(angle2))) * scaling_factor * steps_per_inch
        step_length_1 = int(round(cable_length_1, 0))
        step_length_2 = int(round(cable_length_2, 0))

        points.append(step_length_1)
        points.append(step_length_2)

        x_path.append(x)
        y_path.append(y)

# Plots a graph for the user to preview their image. Travel lines will be shown, but they won't be drawn
plt.plot(x_path, y_path)
plt.gca().invert_yaxis()
plt.show()

# Gives the initial position of the stepper motors, adjust arduino code accordingly
IntitPos = (canvas_width / 2) * steps_per_inch
print("Stepper initial position =", IntitPos)
input("Ready to continue?")

# Open connection with Arduino
ser = serial.Serial("COM3", 9600)

# Allow some time to connect
time.sleep(2)

# How many points are sent at a time **Must be even** If too large, will be too much for arduino
packageSize = 100

# A for loop that sends the points list in "packages" equal to the packageSize var and waits until the Arduino responds
# to send another "package"
for i in range(math.ceil(len(points) / packageSize)):
    # give time for arduino
    time.sleep(0.5)
    package = []

    try:  # Store points into package until index error
        for j in range(packageSize):
            package.append(points[(i * packageSize) + j])
    except IndexError:
        pass
    print("Package to be sent:")
    print(package)
    JSONpoints = json.dumps(package)
    ser.write(JSONpoints.encode())
    print("Python: Package Sent")

    # Waits for arduino response to send next package
    while True:
        line = ser.readline().decode().strip()
        if line == "Serial: Finished Package":
            print(line)
            break
        else:
            print(line)

# End statement and close connection with arduino
print("Python: All points sent")
ser.close()
