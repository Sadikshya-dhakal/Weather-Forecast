from flask import Flask, render_template, request, jsonify
import requests
import numpy as np
import pickle
import webbrowser
from tensorflow.keras.models import load_model

app = Flask(__name__)

# Load model and scaler
model = load_model("lstm_model.keras")
scaler = pickle.load(open("scaler.pkl", "rb"))

API_KEY = "10e86b291c2642739fe45616252505"
BASE_URL = "http://api.weatherapi.com/v1/history.json"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict")
def predict():
    city = request.args.get("city", "Kathmandu")
    sequence_length = 7

    features = []
    for i in range(sequence_length):
        day = f"2025-05-{25+i:02d}"
        url = f"{BASE_URL}?key={API_KEY}&q={city}&dt={day}"
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data"}), 500

        data = response.json()
        try:
            day_data = data["forecast"]["forecastday"][0]["day"]
            features.append([
                day_data["totalprecip_mm"],
                day_data["maxtemp_c"],
                day_data["mintemp_c"],
                day_data["maxwind_kph"]
            ])
        except:
            return jsonify({"error": "Invalid data format"}), 500

    features_scaled = scaler.transform(features)
    input_seq = np.array(features_scaled).reshape(1, sequence_length, 4)

    prediction = model.predict(input_seq)
    predicted_class = np.argmax(prediction)

    class_map = {
        0: "Sunny",
        1: "Rainy",
        2: "Cloudy"
    }
    label = class_map.get(predicted_class, "Unknown")

    return jsonify({"prediction": label})

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)
