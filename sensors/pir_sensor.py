# --- PIR Motion Sensor Script (pir_sensor.py) ---
# This script monitors a PIR motion sensor to detect hesitation events (i.e., people hovering near the bin).
# If motion is detected 3 times within 20 seconds, it logs a hesitation event to the database.
#
# 📚 Sources of Learning and Reference:
# - Raspberry Pi PIR Sensor Setup (Pi My Life Up): https://pimylifeup.com/raspberry-pi-motion-sensor/
# - YouTube Tutorial (Motion detection example with PIR sensor): https://youtu.be/Tw0mG4YtsZk?si=zTh8f5jqiGFgQdJ7
# - lgpio Library Documentation: https://abyz.me.uk/lg/lgpio.html
#
# Developed by Adam McLoughlin for Smart Waste Bin Monitoring System.

import lgpio  # For real-time GPIO input from the PIR sensor
import time  # For time tracking and delays
import mysql.connector  # To log hesitation events to MySQL database
from datetime import datetime  # For readable timestamps

# --- GPIO Pin Setup ---
PIR_PIN = 17  # GPIO 17 (physical pin 11)

# --- Initialize GPIO Chip ---
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(h, PIR_PIN)  # Set PIR_PIN as input

# --- Database Connection Function ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Limerick3011.",
        database="smart_bins"
    )

# --- Insert Hesitation Event into Database ---
def log_hesitation_event():
    conn = get_connection()
    cur = conn.cursor()
    query = """
    INSERT INTO hesitation_events (bin_id, detected_at)
    VALUES (%s, %s)
    """
    cur.execute(query, ("TUS_Moylish", datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
    print(f"[{datetime.now()}] Hesitation event logged.")

# --- Main Loop ---
if __name__ == "__main__":
    print("PIR Sensor Monitoring (Debounce 3 sec, Detection Window 15 sec). Press Ctrl+C to stop.")

    try:
        motion_times = []  # Stores timestamps of recent motions
        last_trigger_time = 0  # Time of last accepted detection

        while True:
            # If motion is detected (PIR sensor HIGH)
            if lgpio.gpio_read(h, PIR_PIN):
                now = time.time()

                # --- Debounce: avoid multiple triggers within 3 seconds ---
                if now - last_trigger_time > 3:
                    last_trigger_time = now
                    motion_times.append(now)
                    print(f"Motion detected at {datetime.now()}")

                    # Clean up old motion timestamps (older than 20 sec)
                    motion_times = [t for t in motion_times if now - t <= 20]

                    # --- Hesitation Detection Logic ---
                    # If 3 motions within 20 seconds → consider hesitation
                    if len(motion_times) >= 3:
                        log_hesitation_event()
                        motion_times.clear()
                        print("Cooldown: Pausing detection for 10 seconds...")
                        time.sleep(10)  # Cooldown to avoid spamming
                time.sleep(0.2)
            else:
                time.sleep(0.2)  # Sensor idle
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        lgpio.gpiochip_close(h)  # Always release GPIO pins
