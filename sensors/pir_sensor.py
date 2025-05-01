import lgpio
import time
import mysql.connector
from datetime import datetime

PIR_PIN = 17  # GPIO 17 (pin 11)

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(h, PIR_PIN)

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Limerick3011.",
        database="smart_bins"
    )

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

if __name__ == "__main__":
    print("PIR Sensor Monitoring (Debounce 3 sec, Detection Window 15 sec). Press Ctrl+C to stop.")

    try:
        motion_times = []
        last_trigger_time = 0

        while True:
            if lgpio.gpio_read(h, PIR_PIN):
                now = time.time()

                # Debounce: Only one detection every 3 seconds
                if now - last_trigger_time > 3:
                    last_trigger_time = now
                    motion_times.append(now)
                    print(f"Motion detected at {datetime.now()}")

                    # Clean up triggers older than 15 seconds
                    motion_times = [t for t in motion_times if now - t <= 20]

                    # If 3 detections within 15 seconds, log hesitation
                    if len(motion_times) >= 3:
                        log_hesitation_event()
                        motion_times.clear()
                        print("Cooldown: Pausing detection for 10 seconds...")
                        time.sleep(10)  # Cooldown after logging

                time.sleep(0.2)
            else:
                time.sleep(0.2)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        lgpio.gpiochip_close(h)
