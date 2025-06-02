from flask import Flask, render_template, request, jsonify
import requests
import numpy as np
import pandas as pd
import pickle
from tensorflow.keras.models import load_model
import webbrowser
import threading

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)

# ─── Load the trained LSTM model and MinMaxScaler ─────────────────────────────
MODEL_PATH = 'lstm_model.keras'
SCALER_PATH = 'scaler.pkl'

model = load_model(MODEL_PATH)
with open(SCALER_PATH, 'rb') as f:
    scaler = pickle.load(f)

# ─── WeatherAPI configuration ────────────────────────────────────────────────
API_KEY = '10e86b291c2642739fe45616252505'
API_URL = 'http://api.weatherapi.com/v1/forecast.json'

# ─── Map from model output index to human-readable labels ─────────────────────
LABEL_MAP = ['drizzle', 'fog', 'rain', 'snow', 'sun', 'cloudy']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict')
def predict():
    city = request.args.get('city', '').strip()
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400

    # 1) Fetch 7-day forecast from WeatherAPI
    params = {
        'key': API_KEY,
        'q': city,
        'days': 7,
        'aqi': 'no',
        'alerts': 'no'
    }
    try:
        resp = requests.get(API_URL, params=params)
        resp.raise_for_status()
    except requests.RequestException as e:
        return jsonify({'error': f'WeatherAPI request failed: {e}'}), 500

    data = resp.json()
    forecast_days = data.get('forecast', {}).get('forecastday', [])
    if len(forecast_days) != 7:
        return jsonify({'error': 'Expected 7 days of forecast data'}), 500

    # 2) Extract the four features for each day
    daily_features = []
    for day in forecast_days:
        d = day['day']
        feat = [
            d['totalprecip_mm'],
            d['maxtemp_c'],
            d['mintemp_c'],
            d['maxwind_kph']
        ]
        daily_features.append(feat)

    # 3) Scale the features
    df = pd.DataFrame(
        daily_features,
        columns=['precipitation', 'temp_max', 'temp_min', 'wind']
    )
    scaled = scaler.transform(df.values)   # shape = (7, 4)

    # 4) Predict weather and collect avgtemp and precipitation
    predictions = []
    for i, day in enumerate(forecast_days):
        single_day = scaled[i].reshape((1, 4, 1))  # (batch=1, timesteps=4, features=1)
        probs = model.predict(single_day)
        idx = np.argmax(probs, axis=1)[0]
        label = LABEL_MAP[idx] if idx < len(LABEL_MAP) else 'unknown'

        d = day['day']
        avgtemp = d['avgtemp_c']
        precip = d['totalprecip_mm']
        date = day['date']

        predictions.append({
            'date': date,
            'avgtemp': avgtemp,
            'precipitation': precip,
            'predicted': label
        })

    return jsonify({'predictions': predictions})

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    print(">>> Starting Flask server: http://127.0.0.1:5000")
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
