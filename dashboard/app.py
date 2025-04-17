import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# --- Database Connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",            # adjust if needed
        password="",            # add password if your MySQL has one
        database="smart_bins"
    )

# --- Fetch latest bin reading ---
def get_latest_data():
    conn = get_connection()
    query = """
        SELECT * FROM bin_data 
        WHERE bin_id = 'TUS_Moylish' 
        ORDER BY timestamp DESC 
        LIMIT 1
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0] if not df.empty else None

# --- Fetch historical readings ---
def get_history():
    conn = get_connection()
    query = """
        SELECT * FROM bin_data 
        WHERE bin_id = 'TUS_Moylish' 
        ORDER BY timestamp DESC 
        LIMIT 20
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Schedule pickup ---
def schedule_pickup():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scheduled_pickups (bin_id, scheduled_time)
        VALUES (%s, %s)
    """, ("TUS_Moylish", datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

# --- Get upcoming pickups ---
def get_pickups():
    conn = get_connection()
    query = """
        SELECT * FROM scheduled_pickups 
        WHERE bin_id = 'TUS_Moylish' 
        ORDER BY scheduled_time DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Streamlit UI ---
st.set_page_config(page_title="Smart Waste Bin", layout="centered")
st.title("🗑️ TUS Moylish Bin Dashboard")

data = get_latest_data()

if data is not None:
    st.metric("📶 Fill Level (%)", f"{data['fill_percent']}%")
    st.metric("⚖️ Weight (kg)", f"{data['weight_kg']} kg")
    st.text(f"Last updated: {data['timestamp']}")

    if data['status'].strip().lower() == "full":
        st.error("⚠️ Bin is full! Schedule a pickup.")

        if st.button("📦 Schedule Pickup"):
            schedule_pickup()
            st.success("✅ Pickup has been scheduled.")
    else:
        st.success("✅ Bin is operating normally.")


    with st.expander("📈 View recent data history"):
        history = get_history()
        st.dataframe(history)

    with st.expander("📦 View scheduled pickups"):
        pickups = get_pickups()
        if not pickups.empty:
            st.dataframe(pickups)
        else:
            st.info("No pickups scheduled yet.")

else:
    st.warning("No sensor data found yet.")
