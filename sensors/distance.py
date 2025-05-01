import lgpio
from gpiozero import LED
import mysql.connector
from time import sleep, time
from datetime import datetime

# GPIO pin setup
TRIG = 23
ECHO = 24
LED_PIN = 25

# Bin height
BIN_HEIGHT_CM = 34.5

# Initialize GPIO chip
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, TRIG)
lgpio.gpio_claim_input(h, ECHO)

# Initialize LED
led = LED(LED_PIN)

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Limerick3011.",
        database="smart_bins"
    )

def update_fill_status(fill_percent):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM bin_data
        WHERE bin_id = 'TUS_Moylish'
        ORDER BY timestamp DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        bin_id = result[0]
        status = "Full" if fill_percent >= 80 else "Normal"
        cursor.execute("""
            UPDATE bin_data
            SET fill_percent = %s, status = %s
            WHERE id = %s
        """, (fill_percent, status, bin_id))
        conn.commit()
    cursor.close()
    conn.close()
    print(f"[{datetime.now()}] Fill: {fill_percent}% | Status: {status}")

def measure_distance():
    lgpio.gpio_write(h, TRIG, 0)
    sleep(0.05)
    lgpio.gpio_write(h, TRIG, 1)
    sleep(0.00001)
    lgpio.gpio_write(h, TRIG, 0)

    start_time = time()
    timeout_start = start_time

    while lgpio.gpio_read(h, ECHO) == 0:
        start_time = time()
        if start_time - timeout_start > 0.1:
            return 100  # Timeout

    stop_time = time()
    timeout_start = stop_time

    while lgpio.gpio_read(h, ECHO) == 1:
        stop_time = time()
        if stop_time - timeout_start > 0.1:
            return 100  # Timeout

    elapsed = stop_time - start_time
    distance = elapsed * 17150
    return round(distance, 2)

# New: Smoothing with spike filtering
def get_smoothed_distance(previous_distance):
    readings = []
    for _ in range(7):  # 7 samples
        dist = measure_distance()
        if dist < 100:  # Ignore max distance errors
            readings.append(dist)
        sleep(0.1)

    if readings:
        avg_distance = sum(readings) / len(readings)
    else:
        avg_distance = 100  # Default if all readings fail

    # Spike filtering: Ignore if jump >10cm from previous
    if previous_distance is not None and abs(avg_distance - previous_distance) > 10:
        print(f"Spike detected: {avg_distance:.2f} cm (holding previous {previous_distance:.2f} cm)")
        return previous_distance

    return round(avg_distance, 2)

# Main loop
if __name__ == "__main__":
    print("Distance Measurement In Progress...")
    previous_distance = None
    try:
        while True:
            distance = get_smoothed_distance(previous_distance)
            previous_distance = distance

            fill_level = BIN_HEIGHT_CM - distance
            fill_percent = max(0, min((fill_level / BIN_HEIGHT_CM) * 100, 100))

            print(f"Distance: {distance:.2f} cm | Fill: {fill_percent:.1f}%")

            update_fill_status(round(fill_percent, 1))

            if fill_percent >= 80:
                led.on()
            else:
                led.off()

            sleep(5)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        lgpio.gpiochip_close(h)
