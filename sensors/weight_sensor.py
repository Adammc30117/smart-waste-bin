
# sensors/weight_sensor.py

import sys
import time
import mysql.connector
from datetime import datetime

sys.path.append("/home/adammc3011/DFRobot_HX711_I2C/python/raspberrypi/")
from DFRobot_HX711_I2C import *

IIC_MODE = 0x01
IIC_ADDRESS = 0x64
hx711 = DFRobot_HX711_I2C(IIC_MODE, IIC_ADDRESS)

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Limerick3011.",  # update if needed
        database="smart_bins"
    )

def insert_weight(weight):
    conn = get_connection()
    cursor = conn.cursor()
    status = "Full" if weight > 5.0 else "Normal"  # example threshold
    query = "INSERT INTO bin_data (bin_id, fill_percent, weight_kg, status) VALUES (%s, %s, %s, %s)"
    values = ("TUS_Moylish", 0, weight, status)  # fill_percent set to 0 for now
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[{datetime.now()}] Weight logged: {weight} kg")

if __name__ == "__main__":
    hx711.begin()
    hx711.set_calibration(2210.0)
    hx711.peel()
    print("Starting weight sensor...")

    try:
        while True:
            data = hx711.read_weight(10)
            print("Weight: %.2f g" % data)
            insert_weight(round(data / 1000, 2))  # convert to kg
            time.sleep(5)
    except KeyboardInterrupt:
        print("Exiting...")
