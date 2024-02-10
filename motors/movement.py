from gpiozero import Button

class realBoard():
    #####
    #STANDARDS:
    # All lengths are in inches, unless otherwise specified
    # Coordinate convention is (x,y)
    #####

    magnetState = False #False means off, True means on
    currentX = None
    currentY = None
    zeroX    = None
    zeroY    = None
    
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
        mmPerRev = beltPitch*teethPerRev
        inchPerRev = mmPerRev/25.4
        self.stepsPerInch = int(stepsPerRev/inchPerRev)
        self.stepsPerSquare = int(self.stepsPerInch*squareSize)

        self.xOrigin = int(origin[0]*stepsPerInch)
        self.yOrigin = int(origin[1]*stepsPerInch)

        self.calibrate()

    def calibrate(self):
        """
        Calibrates the x axis, then the y axis.
        """
        s = self
        while s.zeroY == None:
            # Calibrate y first
            s.moveGantry(0,-1)
            if s.limitSwitchIsPressed("y"):
                s.zeroY = 0
                s.currentY = 0
        while s.zeroX ==  None:
            #Calibrate x second
            s.moveGantry(-1,0)
            if s.limitSwitchIsPressed("x"):
                s.zeroX = 0
                s.currentX = 0

    def limitSwitchIsPressed(self, switch):
        # Reference about Pi's buttons: https://gpiozero.readthedocs.io/en/stable/recipes.html#button
        xSwitchPin = #SET THESE
        ySwitchPin = #SET THESE
        
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

    def moveGantry(self, delx, dely):
        """
        Moves the gantry. 
        Inputs:
            delx: number of steps in the x direction to move
            dely: number of steps in the y direction to move 
        """

        #NOTE: this code must involve:
            #1) checking to make sure the bounds haven't been exceeded. 
            #2) updating self.currentX and self.currentY
        
        s = self
        if dely != 0 and delx != 0:
            #Move diagonally
            ##### CODE GOES HERE
        if dely == 0 and delx != 0:
            #Only move in the x direction
            ##### CODE GOES HERE
        if dely != 0 and delx == 0:
            #Only move in the y direction
            ##### CODE GOES HERE
    
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

    def movePiece(self, startSquare, endSquare):
        """
        Moves the electromagnet to the piece's square
        """

    