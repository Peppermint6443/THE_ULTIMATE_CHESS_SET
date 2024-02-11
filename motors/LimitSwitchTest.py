from gpiozero import Button

buttonPin = 21

button = Button(buttonPin)

while True:
	if button.is_pressed:
		print("Button was pressed")
	else: 
		print("Button not pressed")
