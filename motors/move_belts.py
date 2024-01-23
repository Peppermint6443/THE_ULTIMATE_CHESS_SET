# import needed packages

from time import sleep
import RPi.GPIO as GPIO
import numpy as np

# initialize constants based on your setup
DIR = 23 # add the number corresponding to the direction pin on the driver
STEP = 24 # add the number corresponding to the step pin on the driver
EN = 25
CW = 1 # this is for a clockwise rotation
CCW = 0 # this is for a counter-clockwise rotation
SPR = 1600 # this is the number of steps per revolution, from the driver information sheet

# initialize the driver pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(EN,GPIO.OUT)
GPIO.output(EN,GPIO.HIGH)
GPIO.setup(DIR,GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(DIR, GPIO.LOW)
GPIO.output(STEP, GPIO.LOW)

# reactivate
GPIO.output(EN,GPIO.LOW)

# functions to move the gantry
def coord(xy):
    
    left = np.array([])
    right = np.array([])
    instructions = np.array([left,right])
    return instructions


# # the stuff for creating a window that will create buttons

import tkinter as tk

# Function to send commands to the robot based on button clicks
def send_command(direction):
    if direction == "Forward":
        print('forward')
    elif direction == "Backward":
        print('backward')
    elif direction == "Left":
        print('left')
    elif direction =="Right":
        print('right')

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

