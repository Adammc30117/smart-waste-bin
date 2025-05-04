# 🗑️ Smart Waste Bin Monitoring System (Proof-of-Concept)

This is the source code for my Smart Waste Bin project, developed for the **Technology Futures and Connected Living** module. The system monitors bin fullness using real sensors and provides real-time dashboards for campus and waste facility staff.

The application runs on a **Raspberry Pi** and collects data from:
- 📏 Ultrasonic Distance Sensor (HC-SR04)
- ⚖️ Weight Sensor (HX711 via I2C)
- 👀 PIR Motion Sensor (for hesitation detection)

It uses **MySQL** for data storage and **Streamlit** to render two real-time dashboards.

---

## 🔧 Requirements
- Python 3.10+
- Raspberry Pi OS (64-bit)
- MySQL Server (local or XAMPP)
- Streamlit
- Plotly
- `mysql-connector-python`
- `gpiozero`, `lgpio` for GPIO access

---

## 📁 Project Setup Instructions

### 1. Clone or Download This Repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-waste-bin.git
cd smart-waste-bin
```

### 2. Set Up Python Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up MySQL Database
- Use **phpMyAdmin** (from XAMPP) or the MySQL CLI.
- Create a database named: `smart_bins`
- Import the SQL schema from the provided file `database.txt`
- Update the password field in the sensor and dashboard Python files to match your local MySQL credentials:

```python
mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD_HERE",
    database="smart_bins"
)
```

---

## 🚀 Running the System

### Run the Sensors (one per terminal):

# Distance Sensor
python3 sensors/distance_sensor.py

# Weight Sensor
python3 sensors/weight_sensor.py

# PIR Sensor
python3 sensors/pir_sensor.py

### Launch Dashboards:

# App Dashboard for University Staff
streamlit run dashboard/app.py

# Waste Facility Manager Dashboard
streamlit run dashboard/waste_facility.py

---

## 💡 Key Features
- Real-time fill level and weight monitoring
- Full bin alerts with scheduled pickup functionality
- PIR-based hesitation detection for user behavior insight
- Role-based dashboards for TUS staff and waste management
- Pagination, charts, and live data visualization using Plotly + Streamlit

---

## 📚 Code Credits / Learning Sources
- Streamlit Docs: https://docs.streamlit.io/
- MySQL Connector: https://dev.mysql.com/doc/connector-python/en/
- Plotly Express: https://plotly.com/python/plotly-express/
- GPIO usage via `lgpio`: https://abyz.me.uk/lg/lgpio.html
- Ultrasonic Sensor setup: [Core Electronics Tutorial](https://core-electronics.com.au/tutorials/ultrasonic-distance-sensor-pi.html)
- PIR Motion Detection (Logic): [YouTube Guide](https://www.youtube.com/watch?v=za0Q8ZpWtnQ)
- HX711 Weight Sensor (DFRobot): https://wiki.dfrobot.com/HX711_Weight_Sensor_Kit_SKU_KIT0176

---

## 📬 Contact
If you have questions or issues setting up the project:
📧 **adammc3011@gmail.com**
