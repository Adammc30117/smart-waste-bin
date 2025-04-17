import RPi.GPIO as GPIO
import time
import mysql.connector
from datetime import datetime

# GPIO pin the PIR sensor is connected to
PIR_PIN = 18  # GPIO 18 (physical pin 12)

# Setup GPIO
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="smart_bins"
    )

# Insert hesitation event into MySQL
def log_hesitation_event():
    conn = get_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO hesitation_events (bin_id, detected_time)
    VALUES (%s, %s)
    """
    cur.execute(query, ("TUS_Moylish", datetime.now()))
    conn.commit()

    cur.close()
    conn.close()
    print(f"[{datetime.now()}] Motion detected and logged.")

# Main loop
if __name__ == "__main__":
    setup_gpio()
    print("PIR Sensor Monitoring started. Press Ctrl+C to stop.")

    try:
        while True:
            if GPIO.input(PIR_PIN):
                log_hesitation_event()
                time.sleep(5)  # prevent spamming multiple logs
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()
