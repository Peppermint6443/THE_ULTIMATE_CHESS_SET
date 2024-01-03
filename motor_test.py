# import needed packages
from time import sleep
import RPi.GPIO as GPIO
import numpy as np

# initialize constants based on your setup
DIR = # add the number corresponding to the direction pin on the driver
STEP = # add the number corresponding to the step pin on the driver
CW = 1 # this is for a clockwise rotation
CCW = 0 # this is for a counter-clockwise rotation
SPR = 256 # this is the number of steps per revolution, from the driver information sheet

# initialize the driver pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR,GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(DIR, CW)

step_count = SPR
delay = .0208

# this is the code to complete one full turn 
for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)


# switch direction
sleep(.5)
GPIO.output(DIR,CCW)

# run the same code as before, but this time backwards
for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)