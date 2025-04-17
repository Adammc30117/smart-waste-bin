import random
import time
import mysql.connector
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",           # Change if different
        password="",           # Set if your MySQL has a password
        database="smart_bins"
    )

def simulate_data():
    return {
        "bin_id": "TUS_Moylish",
        "fill_percent": random.randint(20, 100),
        "weight_kg": round(random.uniform(1.0, 10.0), 2),
    }

def insert_data(data):
    data["status"] = "Full" if data["fill_percent"] >= 80 else "Normal"

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO bin_data (bin_id, fill_percent, weight_kg, status)
    VALUES (%s, %s, %s, %s)
    """
    values = (data["bin_id"], data["fill_percent"], data["weight_kg"], data["status"])
    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    print(f"[{datetime.now()}] Inserted: {data}")

if __name__ == "__main__":
    while True:
        data = simulate_data()
        insert_data(data)
        time.sleep(20)  # every 20 seconds
