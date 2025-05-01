# --- Waste Facility Dashboard (waste_facility.py) ---
import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Waste Facility Manager", layout="centered")

# --- Database Connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Limerick3011.",
        database="smart_bins"
    )

# --- Fetch pickups ---
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

# --- UI ---
st.title("🏭 Waste Facility Dashboard")
df = fetch_scheduled_pickups()

if df.empty:
    st.info("No pickups scheduled yet.")
else:
    # --- Status Pie Chart ---
    st.subheader("📊 Pickup Status Distribution")
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig = px.pie(status_counts, names='Status', values='Count', title='Pickup Status')
    st.plotly_chart(fig)

    # --- Activity Log ---
    st.subheader("📄 Recent Pickup Activity")
    st.table(df[['scheduled_time', 'bin_id', 'status']].head(10))

    # --- Action Buttons ---
    st.subheader("🚚 Manage Pickups")
    for index, row in df.iterrows():
        with st.container():
            st.write(f"📍 **Bin ID**: {row['bin_id']}")
            st.write(f"🕒 Scheduled At: {row['scheduled_time']}")
            status_badge = f":red[Pending]" if row['status'] == "Pending" else f":orange[In Progress]" if row['status'] == "In Progress" else f":green[Completed]"
            st.write(f"🚚 Status: {status_badge}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Mark In Progress", key=f"in_progress_{row['id']}"):
                    update_pickup_status(row['id'], "In Progress")
                    st.rerun()
            with col2:
                if st.button("Mark Completed", key=f"completed_{row['id']}"):
                    update_pickup_status(row['id'], "Completed")
                    st.rerun()
