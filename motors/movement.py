from gpiozero import Button
from time import sleep
import RPi.GPIO as GPIO
import numpy as np

class realBoard():
    ################
    #----- Notes about CoreXY:
    # When the left motor moves 1 step in the "positive" direction (CW, 
    # the gantry moves along the diagonal towards the left motor. 
    # When the right motor moves 1 step in the "positive" direction (CW), 
    # the gantry moves along the diagonal away from the right motor. 
    
    # This means if we tell the board to move 1 "step" along the left motor diagonal, 
    # it will move (-1/sqrt(2), -1/sqrt(2)) steps in the cartesian step grid.
    # Similarly, if we tell the board to move 1 "step" along the right motor diagonal, 
    # it will move (-1/sqrt(2),  1/sqrt(2)) steps in the cartesian step grid.
    # This means that if we tell the board to move 1 "step" in the (+) cartesian x, 
    # it will only move 1/sqrt(2) in that direction. 
    #
    # To avoid confusion, any dimension in inches works in the cartesian plane, 
    # and any dimension in "steps" works in the coreXY plane.
    ################

    magnetState = False #False means off, True means on
    currentX = None #inches
    currentY = None #inches
    zeroX    = None
    zeroY    = None

    #----- Set left motor (1) variables
    DIR_1 = 23       # RaspPi pin attached to DIR on motor 1
    STEP_1 = 24      # RaspPi pin attached to STEP on motor 1
    EN_1 = 25        # RaspPi pin attached to EN on motor 1

    #----- Set right motor (2) variables
    DIR_2 = 17       # RaspPi pin attached to DIR on motor 2
    STEP_2 = 27      # RaspPi pin attached to STEP on motor 2
    EN_2 = 22        # RaspPi pin attached to EN on motor 2

    #----- General Variables
    CW  = GPIO.HIGH  # Clockwise rotation
    CCW = GPIO.LOW   # Counter-clockwise rotation
    
    
    def __init__(self, origin, squareSize = 1.75, beltPitch = 2, teethPerRev = 20, stepsPerRev = 1600):
        """
        Initializes a real board object. 
        Inputs: 
            origin =  tuple in the form (x,y) marking the real-world coordinates of the bottom-left edge of the board relative to the zeroed point (inches)
            squareSize = edge length of a square on the board (inches)
            beltPitch = distance between belt teeth (in MILLIMETERS)
            teethPerRev = number of teeth per full motor revolution
            stepsPerRev = number of steps the motor makes per revolution

        Sets the dimensions of the board so that the chessToReal function can do its job
        """
        s = self
        s.squareSize = squareSize #inches
        
        #----- Set Dimensions
        mmPerRev = beltPitch*teethPerRev
        inchPerRev = mmPerRev/25.4 #This is an exception: this is inches in the CoreXY plane
        s.stepsPerInch = int(stepsPerRev/inchPerRev)
        s.inchPerStep = 1/s.stepsPerInch

        s.xOrigin = origin[0] #inches
        s.yOrigin = origin[1] #inches

        #----- Set Boundaries
        tolerance = 0.5 #inches, extra padding to avoid edges
        s.xLoBound = s.xOrigin-s.squareSize*2  + tolerance #inches
        s.xHiBound = s.xOrigin+s.squareSize*10 - tolerance #inches
        s.yLoBound = s.yOrigin-s.squareSize*1  + tolerance #inches
        s.yHiBound = s.yOrigin+s.squareSize*9  - tolerance #inches

        #----- Initialize driver pins
        GPIO.setmode(GPIO.BCM)

        # Open encode mode
        GPIO.setup(s.EN_1,GPIO.OUT)
        GPIO.setup(s.EN_2,GPIO.OUT)
        
        # Deactivate
        GPIO.output(s.EN_1,GPIO.HIGH)
        GPIO.output(s.EN_2,GPIO.HIGH)
        
        # Configure direction and step pins as outputs
        GPIO.setup(s.DIR_1,GPIO.OUT)
        GPIO.setup(s.DIR_2,GPIO.OUT)
        GPIO.setup(s.STEP_1, GPIO.OUT)
        GPIO.setup(s.STEP_2,GPIO.OUT)
        
        # Set the direction and step pins to low
        GPIO.output(s.DIR_1, GPIO.LOW)
        GPIO.output(s.DIR_2,GPIO.LOW)
        GPIO.output(s.STEP_1, GPIO.LOW)
        GPIO.output(s.STEP_2,GPIO.LOW)
        
        # Reactivate
        GPIO.output(s.EN_1,GPIO.LOW)
        GPIO.output(s.EN_2,GPIO.LOW)

        #----- Calibration
        self.calibrate()
        
    def calibrate(self):
        """
        Calibrates the x axis, then the y axis.
        """
        s = self
        while s.zeroY == None:
            # Calibrate y first
            s.moveSteps(s.coreXY(0,-1))
            if s.limitSwitchIsPressed("y"):
                s.zeroY = 0
                s.currentY = 0
        while s.zeroX ==  None:
            # Calibrate x second
            s.moveSteps(s.coreXY(-1,0))
            if s.limitSwitchIsPressed("x"):
                s.zeroX = 0
                s.currentX = 0

        #Move Gantry to the origin
        s.moveInches(s.xOrigin, s.yOrigin)
    
    def moveSteps(self, coords):
        """
        Moves the motors a given number of steps. 
        Inputs:
            coords: 2-element tuple with: 
                coords[0] = # of left-motor steps
                coords[1] = # of right-motor steps
                - ^^ These can be computed using the coreXY function

        NOTE: this function can only move along cartesian x or y lines or along diagonals.
        WARNING: there is no error checking written into this function to ensure no boundary crossing. Normally, the moveInches function should be called instead (this has error checking).
        """
        s = self

        #----- Set driver output pins
        if lSteps > 0:
            GPIO.output(s.DIR_1, s.CW)
        else:
            GPIO.output(s.DIR_1, s.CCW)
        if rSteps > 0:
            GPIO.output(s.DIR_2, s.CW)
        else:
            GPIO.output(s.DIR_2, s.CCW)
        
        #----- Make move
        lSteps, rSteps = int(coords[0]), int(coords[1])
        if lSteps == 0:
            if rSteps == 0:
                #Neither moves
                return None
            else: 
                #Right moves, left doesn't
                for step in range(abs(coords[1])):
                    GPIO.output(s.STEP_2, GPIO.HIGH)
                    sleep(0.0001)
                    GPIO.output(s.STEP_2, GPIO.LOW)
                    sleep(0.0001)
        elif rSteps == 0: 
            #Left moves, right doesn't
            for step in range(abs(coords[0])):
                GPIO.output(s.STEP_1, GPIO.HIGH)
                sleep(0.0001)
                GPIO.output(s.STEP_1, GPIO.LOW)
                sleep(0.0001)
        elif abs(lSteps) != abs(lSteps):
            #Check if both have the same number of steps before simultaneous move
            raise InvalidMoveError(f"The function 'moveGantry' can only perform moves along the cartesian x or y directions, or along diagonals. The move ({delx, dely}) is invalid.")
            return None
        else:
            #Make simultaneous move
            for step in range(abs(coords[0])):
                GPIO.output(s.STEP_1, GPIO.HIGH)
                GPIO.output(s.STEP_2, GPIO.HIGH)
                sleep(0.0001)
                GPIO.output(s.STEP_1, GPIO.LOW)
                GPIO.output(s.STEP_2, GPIO.LOW)
                sleep(0.0001)

    def coreXY(xy):
        """
        Translates coordinates from real world to coreXY motor inputs. 
        Inputs:
            xy: tuple with (moveInXDirection, moveInYDirection)
        Outputs: 
            m = 2-element numpy array:
                m[0]: number of steps the left motor should turn
                m[1]: number of steps the right motor should turn
                - If m[i] > 0, the rotation should be clockwise

        NOTE: if coreXY((1,1)) is called, the resulting motor instructions will lead
        to a movement of length 1 ALONG THE DIAGONAL. This means the net change in 
        cartesian coordinates will be delX = 1/sqrt(2) and delY = 1/sqrt(2)
            - To move a distance delX = delY = L in cartesian coordinates, 
            coreXY must be called as coreXY(sqrt(2)*L, sqrt(2)*L) 
        """
        x, y = xy #steps
        m1 = x - y
        m2 = x + y
        return np.array([m1,y2])

    def limitSwitchIsPressed(self, switch):
        # Reference about Pi's buttons: https://gpiozero.readthedocs.io/en/stable/recipes.html#button
        xSwitchPin = 21
        ySwitchPin = 20
        
        if switch == "x":
            button = Button(xSwitchPin)
        elif switch == "y":
            button = Button(ySwitchPin)
        else:
            raise SwitchError(f"Switch Direction {switch} is invalid. Valid values are 'x' and 'y'. ")

        if button.is_pressed:
            return True
        else: 
            return False
    
    def moveInches(self, delx, dely):
        """ 
        Moves the gantry. 
        Inputs:
            delx: inches in the x direction to move
            dely: inches in the y direction to move

        NOTE: this function can only move along cartesian x or y lines or along diagonals.
        """
        #NOTE: this code must involve:
            #1) checking to make sure the bounds haven't been exceeded. 
            #2) updating self.currentX and self.currentY
        
        s = self

        #----- Confirm move remains in boundaries
        newX = s.currentX + delx
        newY = s.currentY + dely
        b1 = newX < s.xHiBound
        b2 = newY < s.xHiBound
        b3 = newX > s.xLoBound
        b4 = newY > s.yLoBound
        if b1 and b2 and b3 and b4:
            #Move gantry
            xStepsCoreXY = delx*sqrt(2)*s.stepsPerInch
            yStepsCoreXY = dely*sqrt(2)*s.stepsPerInch
            move = s.coreXY((xStepsCoreXY, yStepsCoreXY))
            s.moveSteps(move)

            #Update gantry location
            s.currentX = newX
            s.currentY = newY
        else:
            raise BoundaryError(f"""Attempted to move outside of boundary. Data:
            current X = {s.currentX}
            current Y = {s.currentY}
            Attempted delX = {delx}
            Attempted delY = {dely}""")

    def chesstoReal(self, square):
        """
        Translates a chess move to real coordinates (units: steps from the origin)
        Inputs: 
            square: numerical index of piece's square (0-63)
        Outputs:
            coord: tuple with the coordinates of the center of the square (units: steps from the origin) 
        """
        rank = (square // 8) + 1
        col  = (square %  8) + 1

        x = (col  - 0.5)*self.stepsPerSquare
        y = (rank - 0.5)*self.stepsPerSquare
        return (int(x), int(y))
    