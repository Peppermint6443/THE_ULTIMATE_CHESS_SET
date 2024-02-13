from gpiozero import Button
from time import sleep
import RPi.GPIO as GPIO
import numpy as np
import threading

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

    # Configure Limit Switch pins
    xSwitchPin = 21
    ySwitchPin = 20

    # Configure electromagnet pin
    magPin = 26
    
    #----- General Variables
    CW  = GPIO.HIGH  # Clockwise rotation
    CCW = GPIO.LOW   # Counter-clockwise rotation
    
    
    def __init__(self, origin, squareSize = 1.75, beltPitch = 2, \
        teethPerRev = 20, stepsPerRev = 1600, motDelay = 0.0001):
        """
        Initializes a real board object. 
        Inputs: 
            origin =  tuple in the form (x,y) marking the real-world coordinates of the bottom-left edge of the board relative to the zeroed point (inches)
            squareSize = edge length of a square on the board (inches)
            beltPitch = distance between belt teeth (in MILLIMETERS)
            teethPerRev = number of teeth per full motor revolution
            stepsPerRev = number of steps the motor makes per revolution
            motDelay = # of seconds to wait between motor impulses.
                - Reducing this number increases motor speed, but also increases
                  the risk of skipping steps.

        Sets the dimensions of the board so that the chessToReal function can do its job
        """
        s = self
        s.squareSize = squareSize #inches
        motDelay = 0.00025
        s.motDelay   = motDelay
        
        #----- Set Dimensions
        mmPerRev = beltPitch*teethPerRev
        inchPerRev = mmPerRev/25.4 #This is an exception: this is inches in the CoreXY plane
        s.stepsPerInch = stepsPerRev/inchPerRev
        s.inchPerStep = 1/s.stepsPerInch
        print(s.inchPerStep*25.4*1600, "mm per revolution")

        s.xOrigin = origin[0] #inches
        s.yOrigin = origin[1] #inches

        #----- Set Boundaries
        tolerance = 0.5 #inches, extra padding to avoid edges
        s.xLoBound = s.xOrigin-s.squareSize*2  + tolerance #inches
        s.xHiBound = s.xOrigin+s.squareSize*10 - tolerance #inches
        s.yLoBound = s.yOrigin-s.squareSize*1  + tolerance #inches
        s.yHiBound = s.yOrigin+s.squareSize*9  - tolerance #inches

        #----- Set Raspberry Pi pins to GPIO ready
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

        #Configure limit switches
        s.xLimitSwitch = Button(s.xSwitchPin)
        s.yLimitSwitch = Button(s.ySwitchPin)
        
        #Configure magPin as output
        GPIO.setup(s.magPin, GPIO.OUT)
        
        #----- Calibration
        self.calibrate()
        
    def calibrate(self):
        """
        Calibrates the x axis, then the y axis.
        """
        s = self
        
        # Calibrate y first
        while s.yLimitSwitch.is_pressed == False:
            
            s.moveSteps(s.coreXY((0,-1)))
        s.zeroY = 0
        s.currentY = 0
        
        # Calibrate x second
        while s.xLimitSwitch.is_pressed == False:
            s.moveSteps(s.coreXY((-1,0)))
        s.zeroX = 0
        s.currentX = 0

        #Move Gantry to the center of square a1
        s.moveInches(s.getSquareCoords(0))
    
    def moveSteps(self, coords):
        """
        Moves the motors a given number of steps. 
        Inputs:
            coords: 2-element tuple with: 
                coords[0] = # of left-motor steps
                coords[1] = # of right-motor steps
                - ^^ These can be computed using the coreXY function

        NOTE: this function can only move along cartesian x or y lines or along diagonals.
        WARNING: there is no error checking or position updating written into this function to ensure no boundary crossing. 
            - Normally, the moveInches function should be called instead (this has error checking).
        """
        s = self

        lSteps, rSteps = int(coords[0]), int(coords[1])
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
        if lSteps == 0:
            if rSteps == 0:
                #Neither moves
                return None
            else: 
                #Right moves, left doesn't
                for step in range(abs(rSteps)):
                    GPIO.output(s.STEP_2, GPIO.HIGH)
                    sleep(s.motDelay)
                    GPIO.output(s.STEP_2, GPIO.LOW)
                    sleep(s.motDelay)
        elif rSteps == 0: 
            #Left moves, right doesn't
            for step in range(abs(lSteps)):
                GPIO.output(s.STEP_1, GPIO.HIGH)
                sleep(s.motDelay)
                GPIO.output(s.STEP_1, GPIO.LOW)
                sleep(s.motDelay)
        elif abs(lSteps) != abs(rSteps):
            #If unequal step dimensions, move sequentially. 
            #Move the left motor first
            for step in range(abs(lSteps)):
                GPIO.output(s.STEP_1, GPIO.HIGH)
                sleep(s.motDelay)
                GPIO.output(s.STEP_1, GPIO.LOW)
                sleep(s.motDelay)
            #Then right motor second
            for step in range(abs(rSteps)):
                    GPIO.output(s.STEP_2, GPIO.HIGH)
                    sleep(s.motDelay)
                    GPIO.output(s.STEP_2, GPIO.LOW)
                    sleep(s.motDelay)
            
                
                #Old error catcher:
            #raise NameError(f"Invalid Move: the function 'moveGantry' can only perform \
            #                moves along the cartesian x or y directions, or along diagonals. \
            #                Data: \
            #                    currentX = {s.currentX} inches \
            #                    currentY = {s.currentY} inches \
            #                    Attempted to move {lSteps} steps left and \
            #                                      {rSteps} steps right.")
            return None
        else:
            #Make simultaneous move
            for step in range(abs(lSteps)):
                GPIO.output(s.STEP_1, GPIO.HIGH)
                GPIO.output(s.STEP_2, GPIO.HIGH)
                sleep(s.motDelay)
                GPIO.output(s.STEP_1, GPIO.LOW)
                GPIO.output(s.STEP_2, GPIO.LOW)
                sleep(s.motDelay)

    def coreXY(self, xy):
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
        m1 = -x - y
        m2 = -x + y
        return np.array([m1,m2])
    
    def moveInches(self, deltas):
        """ 
        Moves the gantry. 
        Inputs:
            deltas: 2 element tuple with:
            deltas[0]: delta x. inches in the x direction to move
            deltas[1]: delta y: inches in the y direction to move

        NOTE: this function can only move along cartesian x or y lines or along diagonals.
        """
        #NOTE: this code must involve:
            #1) checking to make sure the bounds haven't been exceeded. 
            #2) updating self.currentX and self.currentY
        
        s = self

        delx = deltas[0]
        dely = deltas[1]

        #----- Confirm move remains in boundaries
        newX = s.currentX + delx
        newY = s.currentY + dely
        b1 = newX < s.xHiBound
        b2 = newY < s.yHiBound
        b3 = newX > s.xLoBound
        b4 = newY > s.yLoBound
        if b1 and b2 and b3 and b4:
            #Move gantry
            xStepsCoreXY = delx*s.stepsPerInch#*np.sqrt(2)
            yStepsCoreXY = dely*s.stepsPerInch#*np.sqrt(2)
            move = s.coreXY((xStepsCoreXY, yStepsCoreXY))
            print(move)
            s.moveSteps(move)

            #Update gantry location
            s.currentX = newX
            s.currentY = newY
        else:
            raise RuntimeError(f"""Attempted to move outside of boundary. Data:
            current X = {s.currentX}
            current Y = {s.currentY}
            Attempted delX = {delx}
            Attempted delY = {dely}""")

    def turnMagnetOn(self):
        GPIO.output(self.magPin, GPIO.HIGH)

    def turnMagnetOff(self):
        GPIO.output(self.magPin, GPIO.LOW)
    
    def getSquareCoords(self, square):
        """
        Translates a chess move to real coordinates (units: steps from the origin)
        Inputs: 
            square: numerical index of piece's square (0-63)
        Outputs:
            coord: tuple with the absolute coordinates of the center of the square (units: inches) 
                - Ranks and columns range from 0 to 6
                - Rank 0 = 1, Rank 1 = 2, etc.
                - File 0 = a, File 1 = b, etc.
        """
        #JWP TO DO: handle capture bank. Easiest would be use negative numbers
        rank = (square // 8)
        col  = (square %  8)

        x = (col  + 0.5)*self.squareSize + self.xOrigin #inches
        y = (rank + 0.5)*self.squareSize + self.yOrigin #inches
        print(f"getSquareCoords({square}) = {(x, y)}") #DDEBUGGING
        return (x, y)

    def moveToSquare(self, square):
        """
        Moves the gantry to the inputted square (0-63)
        """
        s = self
        coords = s.getSquareCoords(square)

        delx = coords[0] - s.currentX
        dely = coords[1] - s.currentY
        deltas = (delx, dely)
        print(f"moveToSquare deltas = {deltas}") #DEBUGGING
        print(f"CurrentX = {s.currentX}, currentY = {s.currentY}")
        s.moveInches(deltas)
        print(f"Successfully moved to square {square}")

    def movePiece(self, startSquare, endSquare, movingPiece, isCapture, capturedPiece):
        """
        Moves a piece based off the following inputs: 
            startSquare    = starting square (0-63)
            endSquare      = ending square   (0-63)
            movingPiece    = symbol of the piece that's being moved
            isCapture      = notes that the move involves capturing a piece
            capturedPiece  = which piece was captured, for correct storage in the piece bank
        """
        s = self
        
        #PIECE BANK: negative indices are white's piece bank off to the left. 
        # indices greater than 63 are black's piece bank off to the right. 
        
        if isCapture:
            #s.movePiece(endSquare, #PIECEBANK#, "x", False, capturedPiece)
            pass
        else:
        
            # Move to starting square
            s.moveToSquare(startSquare)
            
            #To keep the magnet on while moving the gantry, we use threading:
            pieceIsMoving = True
            try:
                while pieceIsMoving:
                    magnet_thread = threading.Thread(target=s.turnMagnetOn())
                    magnet_thread.start()
                    
                    if movingPiece.lower() == "n":
                        #Knight routine
                        coords = s.getSquareCoords(endSquare)
                        delx = coords[0] - s.currentX
                        dely = coords[1] - s.currentY 
                        if delx>dely:
                            #move 1/2 square y
                            s.moveInches((0, dely/2))
                            #move delx
                            s.moveInches((delx, 0))
                            #move 1/2 square y
                            s.moveInches((0,dely/2))
                            
                        elif dely>delx:
                            #move 1.2 square x
                            s.moveInches((delx/2,0))
                            #move dely
                            s.moveInches((0,dely))
                            #move 1.2 squre x
                            s.moveInches((delx/2))
                        else:
                            raise RuntimeError("Knight movement error")
                            
                    else: 
                        s.moveToSquare(endSquare)
                    
                    pieceIsMoving = False
                    magnet_thread.join()
                    s.turnMagnetOff()
            except KeyboardInterupt:
                s.turnMagnetOff()
                print("Movement aborted")
                GPIO.cleanup()
