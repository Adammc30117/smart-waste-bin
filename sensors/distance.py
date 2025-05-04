# --- Bin Fill Sensor Script (distance.py) ---
# This script measures the distance from the ultrasonic sensor to the trash surface, calculates the fill level,
# and updates the database accordingly. An LED is used to indicate when the bin is considered full (≥80%).
#
# 📚 Sources of Learning and Reference:
# - HC-SR04 with Raspberry Pi (Pi My Life Up): https://pimylifeup.com/raspberry-pi-distance-sensor/
# - The Pi Hut HC-SR04 Guide: https://thepihut.com/blogs/raspberry-pi-tutorials/hc-sr04-ultrasonic-range-sensor-on-the-raspberry-pi
# - YouTube (Sensor Wiring & Logic Reference): https://www.youtube.com/watch?v=C02oB1n7rcg
#
# This code was developed by Adam McLoughlin as part of the Smart Waste Bin project.

import lgpio  # High-precision GPIO library for Raspberry Pi
from gpiozero import LED  # Simpler GPIO LED control
import mysql.connector  # MySQL database connector
from time import sleep, time  # For timing and delays
from datetime import datetime  # For timestamp logging

# --- GPIO Pin Setup ---
TRIG = 23  # Trigger pin for HC-SR04
ECHO = 24  # Echo pin for HC-SR04
LED_PIN = 25  # LED pin to indicate full bin

# --- Physical Bin Configuration ---
BIN_HEIGHT_CM = 34.5  # Actual height from sensor to bin base

# --- GPIO Initialization ---
h = lgpio.gpiochip_open(0)  # Open GPIO chip
lgpio.gpio_claim_output(h, TRIG)  # Set trigger pin as output
lgpio.gpio_claim_input(h, ECHO)   # Set echo pin as input

# --- LED Setup ---
led = LED(LED_PIN)  # LED on GPIO 25

# --- Database Connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Limerick3011.",  # Your MySQL password
        database="smart_bins"
    )

# --- Update bin_data table with latest fill level and status ---
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
        status = "Full" if fill_percent >= 80 else "Normal"  # Business logic: full if ≥ 80%
        cursor.execute("""
            UPDATE bin_data
            SET fill_percent = %s, status = %s
            WHERE id = %s
        """, (fill_percent, status, bin_id))
        conn.commit()
    cursor.close()
    conn.close()
    print(f"[{datetime.now()}] Fill: {fill_percent}% | Status: {status}")

# --- Raw Distance Measurement (returns cm) ---
def measure_distance():
    # Send 10µs pulse to trigger pin
    lgpio.gpio_write(h, TRIG, 0)
    sleep(0.05)
    lgpio.gpio_write(h, TRIG, 1)
    sleep(0.00001)
    lgpio.gpio_write(h, TRIG, 0)

    start_time = time()
    timeout_start = start_time

    # Wait for echo to go high
    while lgpio.gpio_read(h, ECHO) == 0:
        start_time = time()
        if start_time - timeout_start > 0.1:
            return 100  # Timeout: return large distance

    stop_time = time()
    timeout_start = stop_time

    # Wait for echo to go low
    while lgpio.gpio_read(h, ECHO) == 1:
        stop_time = time()
        if stop_time - timeout_start > 0.1:
            return 100  # Timeout again

    # Calculate duration and convert to cm (speed of sound = 34300 cm/s)
    elapsed = stop_time - start_time
    distance = elapsed * 17150  # Half the round-trip time
    return round(distance, 2)

# --- Smooth Distance Readings + Spike Filtering ---
def get_smoothed_distance(previous_distance):
    readings = []
    for _ in range(7):  # Take 7 samples
        dist = measure_distance()
        if dist < 100:  # Ignore outliers/timeouts
            readings.append(dist)
        sleep(0.1)

    if readings:
        avg_distance = sum(readings) / len(readings)
    else:
        avg_distance = 100  # Default fallback

    # Simple spike rejection (ignore sudden jumps > 10 cm)
    if previous_distance is not None and abs(avg_distance - previous_distance) > 10:
        print(f"Spike detected: {avg_distance:.2f} cm (holding previous {previous_distance:.2f} cm)")
        return previous_distance

    return round(avg_distance, 2)

# --- Main Sensor Loop ---
if __name__ == "__main__":
    print("Distance Measurement In Progress...")
    previous_distance = None
    try:
        while True:
            distance = get_smoothed_distance(previous_distance)
            previous_distance = distance

            # Convert to fill percentage
            fill_level = BIN_HEIGHT_CM - distance
            fill_percent = max(0, min((fill_level / BIN_HEIGHT_CM) * 100, 100))

            print(f"Distance: {distance:.2f} cm | Fill: {fill_percent:.1f}%")

            update_fill_status(round(fill_percent, 1))

            # Control LED based on fill level
            if fill_percent >= 80:
                led.on()
            else:
                led.off()

            sleep(5)  # Wait before next reading
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        lgpio.gpiochip_close(h)  # Clean up GPIO
