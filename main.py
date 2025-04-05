from gpiozero import LED
from signal import pause

red = LED(24)

red.blink()

pause()