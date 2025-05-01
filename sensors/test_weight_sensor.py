import RPi.GPIO as GPIO
from hx711 import HX711
import time

# Set GPIO pin numbers
DT = 5   # GPIO 5 (physical pin 29) — data pin (DT)
SCK = 6  # GPIO 6 (physical pin 31) — clock pin (SCK)

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Initialize the HX711
hx = HX711(DT, SCK)

# Optional: set reference unit (you can calibrate this later)
hx.set_reference_unit(1)

hx.reset()
hx.tare()  # Reset the scale to 0

print("Place an item on the scale...")

try:
    while True:
        weight = hx.get_weight(5)  # Read average of 5 readings
        print(f"Weight: {weight:.2f} g")
        hx.power_down()
        hx.power_up()
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")
    GPIO.cleanup()
