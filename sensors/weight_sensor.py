# sensors/weight_sensor.py

import time
from hx711 import HX711

def setup():
    hx = HX711(dout_pin=5, pd_sck_pin=6)  # Connect DT to GPIO 5, SCK to GPIO 6
    hx.set_scale_ratio(200)  # You’ll calibrate this number later
    return hx

def get_weight(hx):
    return round(hx.get_weight_mean(20), 2)  # Average over 20 readings

if __name__ == "__main__":
    try:
        hx = setup()
        while True:
            weight = get_weight(hx)
            print(f"Weight: {weight} kg")
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        print("Exiting...")
