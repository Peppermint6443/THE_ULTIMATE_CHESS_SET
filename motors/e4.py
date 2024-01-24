# import needed packages
from time import sleep
import RPi.GPIO as GPIO
import numpy as np

# initialize constants based on your setup
DIR_1 = 23 # add the number corresponding to the direction pin on the driver
STEP_1 = 24 # add the number corresponding to the step pin on the driver
EN_1 = 25
DIR_2 = 17
STEP_2 = 27
EN_2 = 22
CW = 1 # this is for a clockwise rotation
CCW = 0 # this is for a counter-clockwise rotation
SPR = 1600 # this is the number of steps per revolution, from the driver information sheet

# initialize the driver pins
GPIO.setmode(GPIO.BCM)

# open encode mode
GPIO.setup(EN_1,GPIO.OUT)
GPIO.setup(EN_2,GPIO.OUT)

# deactivate
GPIO.output(EN_1,GPIO.HIGH)
GPIO.output(EN_2,GPIO.HIGH)

# initialize direction and step pins
GPIO.setup(DIR_1,GPIO.OUT)
GPIO.setup(STEP_1, GPIO.OUT)
GPIO.setup(DIR_2,GPIO.OUT)
GPIO.setup(STEP_2,GPIO.OUT)

# intialize the direction and step pins to low
GPIO.output(DIR_1, GPIO.LOW)
GPIO.output(STEP_1, GPIO.LOW)
GPIO.output(DIR_2,GPIO.LOW)
GPIO.output(STEP_2,GPIO.LOW)

# reactivate
GPIO.output(EN_1,GPIO.LOW)
GPIO.output(EN_2,GPIO.LOW)


# functions to move the gantry
def coord(x):
    x1,x2 = x
    y1 = x1 - x2
    y2 = x1 + x2
    y = np.array([y1,y2])
    return y


# # the stuff for creating a window that will create buttons
import tkinter as tk

# Function to send commands to the robot based on button clicks
def send_command(direction):
    if direction == "Forward":
        move = coord([0,1])
    elif direction == "Backward":
        move = coord([0,-1])
    elif direction == "Left":
        move = coord([-1,0])
    elif direction =="Right":
        move = coord([1,0])
    
    if move[0] > 0:
        GPIO.output(DIR_1,GPIO.HIGH)
    else:
        GPIO.output(DIR_1,GPIO.LOW)
    if move[1] > 0:
        GPIO.output(DIR_2,GPIO.HIGH)
    else:
        GPIO.output(DIR_2,GPIO.LOW)
    
    # move left motor
    SC_1 = move[0] * SPR
    delay = .0001
    # this is the code to complete one full turn 
    for x in range(abs(SC_1)):
        GPIO.output(STEP_1, GPIO.HIGH)
        GPIO.output(STEP_2, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP_1, GPIO.LOW)
        GPIO.output(STEP_2,GPIO.LOW)
        sleep(delay)

# Hello there eThAn, this is a GitHub test

# hello there Ja-red, this is a second github test!

#    # move right motor
 #   SC_2 = move[1] * SPR
  #  delay = .0001
    # this is the code to complete one full turn 
   # for x in range(abs(SC_2)):
    #    GPIO.output(STEP_2, GPIO.HIGH)
     #   sleep(delay)
      #  GPIO.output(STEP_2, GPIO.LOW)
       # sleep(delay)

# Create the main GUI window
root = tk.Tk()
root.title("Robot Controller")

# Function to create buttons and bind them to the send_command function
def create_button(direction):
    button = tk.Button(root, text=direction, command=lambda: send_command(direction))
    button.pack(side=tk.LEFT, padx=10, pady=10)

# Create buttons for each direction
create_button("Forward")
create_button("Backward")
create_button("Left")
create_button("Right")

# Start the GUI event loop
root.mainloop()

GPIO.cleanup()
