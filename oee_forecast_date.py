import pandas as pd
import numpy as np
import mysql.connector
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import os
import pickle
import sys
from datetime import timedelta

try:
    # Path to saved model and scaler
    MODEL_PATH = r"C:\Users\Si E Yang\Desktop\fyp2\oee_forecast_model.keras"
    SCALER_PATH = r"C:\Users\Si E Yang\Desktop\fyp2\oee_scaler.pkl"
    
    # Check if model and scaler files exist
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"Scaler file not found at {SCALER_PATH}")
    
    # 1. Load the saved model
    loaded_model = load_model(MODEL_PATH)
    print("Model loaded successfully")
    
    # 2. Load the saved scaler
    with open(SCALER_PATH, 'rb') as file:
        loaded_scaler = pickle.load(file)
    print("Scaler loaded successfully")
    
    # 3. Connect to MySQL
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="cookies"
        )
        print("Database connection successful")
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        sys.exit(1)
    
    # 4. Create a cursor and extract data from MySQL
    cursor = conn.cursor()
    query = "SELECT * FROM cookies_production"
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    
    # Check if we got any data
    if not data:
        raise ValueError("No data returned from the database query")
    
    df = pd.DataFrame(data, columns=columns)
    df["StartDateTime"] = pd.to_datetime(df["StartDateTime"], dayfirst=True)
    df["Date"] = df["StartDateTime"].dt.date
    
    # Calculate weighted OEE
    df['Weighted_OEE'] = df['OEE_net'] * df['Net_Time']
    
    # Group by date and compute daily weighted OEE
    daily_oee = df.groupby('Date').apply(
        lambda x: x['Weighted_OEE'].sum() / x['Net_Time'].sum()
    ).reset_index(name='OEE_net')
    
    daily_oee["Date"] = pd.to_datetime(daily_oee["Date"])
    daily_oee = daily_oee.sort_values("Date").set_index("Date")
    
    if len(daily_oee) < 7:
        raise ValueError(f"Insufficient data for prediction. Need at least 7 days, but got {len(daily_oee)}")
    
    # Forecasting function
    def forecast_next_week(input_data, model, scaler):
        input_array = np.array(input_data).reshape(-1, 1)
        scaled_input = scaler.transform(input_array)
        X = scaled_input.reshape(1, 7, 1)
        scaled_prediction = model.predict(X)
        prediction = scaler.inverse_transform(scaled_prediction.reshape(-1, 1))
        return prediction.flatten()
    
    # 5. Forecast next 7 days
    latest_week = daily_oee["OEE_net"].iloc[-7:].values
    future_forecast = forecast_next_week(latest_week, loaded_model, loaded_scaler)
    
    # Generate date labels for predictions
    last_date = daily_oee.index[-1]
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), periods=7)
    
    # Prepare DataFrame with dates and predictions
    pred_df = pd.DataFrame({
        "Date": forecast_dates,
        "OEE_net_predicted": future_forecast
    })
    
    # Display prediction
    print("\nPredicted OEE values for the next 7 days:")
    print(pred_df)
    
    # Update database
    try:
        cursor.execute("TRUNCATE TABLE predicted_oee")
        for i, row in pred_df.iterrows():
            cursor.execute(
                "INSERT INTO predicted_oee (date, OEE_net_predicted) VALUES (%s, %s)",
                (row["Date"].strftime("%Y-%m-%d"), float(row["OEE_net_predicted"]))
            )
        conn.commit()
        print("Database updated successfully with new predictions")
    except mysql.connector.Error as err:
        print(f"Error updating database: {err}")
        conn.rollback()
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("Database connection closed")
