# Test movement software

import movement as mvt
import RPi.GPIO as GPIO

board = mvt.realBoard((4,4))

GPIO.cleanup()
