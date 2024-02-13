# Test movement software

import movement as mvt
import RPi.GPIO as GPIO
from time import sleep

#board = mvt.realBoard((4,4))

origin = (0.5,2+9/16-1.15) # x,y inches
board = mvt.realBoard(origin)
sleep(10)
board.moveInches((2,0))

