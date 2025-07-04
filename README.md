# FYP-Degree


## Requirements
Make sure the following software are installed:

- [Node-RED v4.0.5](https://nodered.org/)
- [Power BI Desktop](https://powerbi.microsoft.com/)
- [XAMPP v3.3.0](https://www.apachefriends.org/)
- [MySQL Connector for .NET v9.3.0](https://dev.mysql.com/downloads/connector/net/)
- [Mosquitto MQTT Broker v2.0.21](https://mosquitto.org/download/)

---

## Installation & Setup

### 1. Node-RED

- Open Node-RED.
- Import the Node-RED flow.json file into Node-RED.
- Open the Inject node and paste the contents from DataToBeInject.json into it.

### 2. MySQL Database (via XAMPP)

- Start **MySQL** in XAMPP Control Panel.
- Open **phpMyAdmin**.
- Import the cookies.sql file into the MySQL database.

### 3. Python Forecast Script

- Save the oee_forecast_date.py file in a folder, e.g.:
  program/
  └── oee_forecast_date.py

- Install required Python libraries:
  pip install pandas
  pip install numpy
  pip install mysql-connector-python
  pip install scikit-learn
  pip install tensorflow

### 4. Configure Batch File

- Edit oee_forecast.bat:
  - Replace the path to your local python.exe.
  - Replace the path to oee_forecast_date.py.

### 5. Schedule Forecast Task

- Open Task Scheduler.
- Click Create Basic Task.
- Set the trigger schedule.
- In the Action step, select the oee_forecast.bat file.

---

## Power BI Dashboard

- Open connectMySQL.pbix in Power BI Desktop.
- Go to: Home > Transform Data > Data source settings.
- Update the server name and credentials if needed to match your local MySQL setup.

---
