# sensors/sensor_data_to_mysql.py

from ultrasonic import setup as us_setup, get_distance_cm, cleanup as us_cleanup
from weight_sensor import setup as weight_setup, get_weight
import mysql.connector
from datetime import datetime
import time

# Set your max bin height in cm (adjust based on bin)
MAX_HEIGHT_CM = 50

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="smart_bins"
    )

def insert_data(fill_percent, weight):
    status = "Full" if fill_percent >= 80 else "Normal"
    conn = get_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO bin_data (bin_id, fill_percent, weight_kg, status)
    VALUES (%s, %s, %s, %s)
    """
    values = ("TUS_Moylish", fill_percent, weight, status)
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()

    print(f"[{datetime.now()}] Inserted: Fill={fill_percent}%, Weight={weight} kg, Status={status}")

if __name__ == "__main__":
    try:
        us_setup()
        hx = weight_setup()

        while True:
            distance = get_distance_cm()
            fill_percent = max(0, min(100, round(100 - (distance / MAX_HEIGHT_CM) * 100)))
            weight = get_weight(hx)
            insert_data(fill_percent, weight)
            time.sleep(60)

    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        us_cleanup()
