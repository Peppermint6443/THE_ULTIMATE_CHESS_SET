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

for i in range(10):
    

    step_count = SPR
    delay = .0001
    print(1)
    # this is the code to complete one full turn 
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)

    print(2)
    # switch direction
    sleep(2)
    GPIO.output(DIR,GPIO.HIGH)

    # add a random comment to test this out
    # add a second random comment, I think I got it figured out this time... I needed to pull the updated version of the repository to this branch, otherwise it was editing what the repository contained when the project first started

    # run the same code as before, but this time backwards
    for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)


    print(3)
    GPIO.output(DIR, GPIO.LOW)
    sleep(1)
    
    
    
GPIO.cleanup()
