import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# --- Connect to database ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="smart_bins"
    )

# --- Fetch all scheduled pickups ---
def fetch_scheduled_pickups():
    conn = get_connection()
    query = "SELECT * FROM scheduled_pickups ORDER BY scheduled_time DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Update pickup status ---
def update_pickup_status(pickup_id, new_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE scheduled_pickups SET status = %s WHERE id = %s", (new_status, pickup_id))
    conn.commit()
    cur.close()
    conn.close()

# --- Streamlit UI ---
st.set_page_config(page_title="Waste Facility Manager", layout="centered")
st.title("🏭 Waste Facility Dashboard")

df = fetch_scheduled_pickups()

if df.empty:
    st.info("No pickups scheduled yet.")
else:
    for index, row in df.iterrows():
        with st.container():
            st.write(f"📍 **Bin ID**: {row['bin_id']}")
            st.write(f"🕒 Scheduled At: {row['scheduled_time']}")
            st.write(f"🚚 Status: **{row['status']}**")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Mark In Progress", key=f"in_progress_{row['id']}"):
                    update_pickup_status(row['id'], "In Progress")
                    st.experimental_rerun()
            with col2:
                if st.button("Mark Completed", key=f"completed_{row['id']}"):
                    update_pickup_status(row['id'], "Completed")
                    st.experimental_rerun()
