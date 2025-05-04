# --- Weight Sensor Script (weight_sensor.py) ---
# This script reads weight values from the DFRobot HX711 I2C load cell module and logs them into a MySQL database.
#
# 📚 Source Used for Development:
# - DFRobot HX711 I2C Weight Sensor Kit Tutorial: https://wiki.dfrobot.com/HX711_Weight_Sensor_Kit_SKU_KIT0176
# - Python driver library: https://github.com/DFRobot/DFRobot_HX711_I2C
#
# Much of the setup logic (like `begin()`, `set_calibration()`, `peel()`, and `read_weight(n)`) is taken from the DFRobot sample Python script.
# The script below follows the same pattern shown in the tutorial with small adjustments to insert the weight data into a MySQL database.
#
# Authored and adapted by Adam McLoughlin for the Smart Waste Bin Monitoring System.

import sys  # For appending library path
import time  # For sleeping between readings
import mysql.connector  # For database interaction
from datetime import datetime  # For logging timestamped data

# --- Add DFRobot HX711 I2C library path ---
# This path is where the Python driver from DFRobot is located on the Raspberry Pi.
# It allows the script to import and use the `DFRobot_HX711_I2C` class.
sys.path.append("/home/adammc3011/DFRobot_HX711_I2C/python/raspberrypi/")

# --- Import the DFRobot HX711 class ---
from DFRobot_HX711_I2C import *

# --- HX711 I2C configuration constants ---
IIC_MODE = 0x01  # Communication mode: I2C
IIC_ADDRESS = 0x64  # I2C address for the HX711 module

# --- Initialize HX711 instance with I2C mode and address ---
hx711 = DFRobot_HX711_I2C(IIC_MODE, IIC_ADDRESS)

# --- Function to connect to the database ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Limerick3011.",  # Replace if different
        database="smart_bins"
    )

# --- Insert weight reading into the database ---
def insert_weight(weight):
    conn = get_connection()
    cursor = conn.cursor()

    # Simple logic: if weight > 5kg, mark as full
    status = "Full" if weight > 5.0 else "Normal"

    # Insert into bin_data (fill_percent is 0 here; handled by ultrasonic separately)
    query = "INSERT INTO bin_data (bin_id, fill_percent, weight_kg, status) VALUES (%s, %s, %s, %s)"
    values = ("TUS_Moylish", 0, weight, status)
    cursor.execute(query, values)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"[{datetime.now()}] Weight logged: {weight} kg")

# --- Main loop ---
if __name__ == "__main__":
    # Start HX711 communication
    hx711.begin()

    # Calibration factor based on the load cell setup (value from DFRobot tutorial or custom calibrated)
    hx711.set_calibration(2210.0)

    # Tare the scale (i.e., zero it)
    hx711.peel()

    print("Starting weight sensor...")

    try:
        while True:
            # Read weight with 10 samples (smoothing)
            data = hx711.read_weight(10)  # Returns weight in grams
            print("Weight: %.2f g" % data)

            # Convert to kg and log
            insert_weight(round(data / 1000, 2))

            time.sleep(5)  # Delay before next reading
    except KeyboardInterrupt:
        print("Exiting...")
