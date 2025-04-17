# sensors/ultrasonic.py

import RPi.GPIO as GPIO
import time

TRIG = 23  # GPIO pin for Trig
ECHO = 24  # GPIO pin for Echo

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

def get_distance_cm():
    GPIO.output(TRIG, False)
    time.sleep(0.5)

    # Send trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo to start
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound / 2
    return round(distance, 2)

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup()
        while True:
            dist = get_distance_cm()
            print(f"Distance: {dist} cm")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopping sensor.")
    finally:
        cleanup()
