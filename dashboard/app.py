# --- TUS Moylish Bin Dashboard (app.py) ---

# -------------------------
# Sources and References:
# - Streamlit Docs: https://docs.streamlit.io/
# - Streamlit Autorefresh: https://pypi.org/project/streamlit-autorefresh/
# - Plotly Docs: https://plotly.com/python/
# - MySQL Connector: https://dev.mysql.com/doc/connector-python/en/
# - Pandas Docs: https://pandas.pydata.org/docs/
# - Python datetime: https://docs.python.org/3/library/datetime.html
# -------------------------

import streamlit as st
from streamlit_autorefresh import st_autorefresh  # Source: streamlit-autorefresh module
import mysql.connector  # Source: MySQL Connector/Python docs
import pandas as pd
from datetime import datetime  # Source: Python datetime docs
import plotly.graph_objects as go  # Source: Plotly for Python

# --- Streamlit page config and auto-refresh ---
st.set_page_config(page_title="Smart Waste Bin", layout="centered")
st_autorefresh(interval=5000, limit=None, key="weight_data_refresh")

# --- Database Connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Limerick3011.",
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
    df = pd.read_sql(query, conn)  # Source: pandas.read_sql for MySQL query execution
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

# --- Fetch pickups ---
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

# --- Fetch hesitation events ---
def get_hesitations():
    conn = get_connection()
    query = """
        SELECT * FROM hesitation_events 
        WHERE bin_id = 'TUS_Moylish' 
        ORDER BY detected_at DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Schedule pickup ---
def schedule_pickup():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scheduled_pickups (bin_id, scheduled_time, status)
        VALUES (%s, %s, %s)
    """, ("TUS_Moylish", datetime.now(), "Pending"))
    conn.commit()
    cursor.close()
    conn.close()

# --- Streamlit UI rendering ---
st.title("🔑️ TUS Moylish Bin Dashboard")
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

    # --- Pickup Metrics ---
    pickups = get_pickups()
    total = len(pickups)
    completed = len(pickups[pickups['status'] == 'Completed'])
    in_progress = len(pickups[pickups['status'] == 'In Progress'])
    pending = total - completed - in_progress

    st.subheader("📊 Pickup Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total", total)
    col2.metric("✅ Completed", completed)
    col3.metric("🚚 In Progress", in_progress)
    col4.metric("⏳ Pending", pending)

    # --- History Chart with Plotly ---
    with st.expander("📈 View Fill & Weight History"):
        history = get_history()
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=history['timestamp'],
            y=history['fill_percent'],
            name="Fill Level (%)",
            yaxis="y1"
        ))

        fig.add_trace(go.Scatter(
            x=history['timestamp'],
            y=history['weight_kg'],
            name="Weight (kg)",
            yaxis="y2"
        ))

        fig.update_layout(
            yaxis=dict(title="Fill Level (%)", range=[0, 100]),
            yaxis2=dict(title="Weight (kg)", overlaying="y", side="right", range=[0, 2]),
            title="Fill Level & Weight Over Time",
            xaxis_title="Timestamp",
            legend_title="Metrics"
        )

        st.plotly_chart(fig, use_container_width=True)

    # --- Scheduled Pickups Table ---
    with st.expander("📦 View Scheduled Pickups"):
        if not pickups.empty:
            st.dataframe(pickups)
        else:
            st.info("No pickups scheduled yet.")

    # --- Hesitation Events ---
    hesitations = get_hesitations()
    st.subheader("🕵️‍♂️ Hesitation Events")
    st.metric("🔄 Total Hesitations Logged", len(hesitations))

    # --- Filter dropdown ---
    filter_option = st.selectbox("🔍 Filter Hesitations By", ["All Time", "Last 7 Days", "This Month"])

    if filter_option == "Last 7 Days":
        hesitations = hesitations[hesitations['detected_at'] > pd.Timestamp.now() - pd.Timedelta(days=7)]
    elif filter_option == "This Month":
        hesitations = hesitations[hesitations['detected_at'].dt.month == datetime.now().month]

    # --- Date Range Picker ---
    if not hesitations.empty:
        min_date = hesitations['detected_at'].min().date()
        max_date = hesitations['detected_at'].max().date()
        start_date, end_date = st.date_input("🗓️ Select Date Range:", [min_date, max_date])

        hesitations = hesitations[(hesitations['detected_at'].dt.date >= start_date) &
                                  (hesitations['detected_at'].dt.date <= end_date)]

        # --- Chart ---
        if not hesitations.empty:
            daily = hesitations['detected_at'].dt.date.value_counts().sort_index()
            chart = go.Figure(data=[go.Bar(x=daily.index, y=daily.values)])
            chart.update_layout(title="📅 Hesitations by Day", xaxis_title="Date", yaxis_title="Hesitations")
            st.plotly_chart(chart, use_container_width=True)

            with st.expander("📄 View Raw Hesitation Logs"):
                st.dataframe(hesitations)
        else:
            st.info("No hesitation events in selected date range.")
    else:
        st.info("No hesitation events found.")
else:
    st.warning("No sensor data found yet.")
