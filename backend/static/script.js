const icons = {
  "Sunny": "☀️",
  "Rainy": "🌧️",
  "Cloudy": "☁️",
  "Thunderstorm": "⛈️",
  "Unknown": "❓",
  "Partially Rainy": "🌦️",
  "Patchy Rain": "🌧️"
};

async function getWeather() {
  const city = document.getElementById('city').value.trim();
  if (!city) {
    alert('Please enter a city name');
    return;
  }

  try {
    const res = await fetch(`/predict?city=${encodeURIComponent(city)}`);
    if (!res.ok) throw new Error('Network response was not ok');
    const data = await res.json();

    if (data.error) {
      alert('Error: ' + data.error);
      return;
    }

    const forecastDiv = document.getElementById("forecast");
    forecastDiv.innerHTML = "";

    const icon = icons[data.predicted_condition] || "❓";

    const card = `
      <div class="card">
        <div class="weather-icon">${icon}</div>
        <div><strong>${data.predicted_condition}</strong></div>
        <div>Precipitation: ${data.input_features.precipitation.toFixed(2)} mm</div>
        <div>Max Temp: ${data.input_features.temp_max.toFixed(1)} °C</div>
        <div>Min Temp: ${data.input_features.temp_min.toFixed(1)} °C</div>
        <div>Wind Speed: ${data.input_features.wind.toFixed(1)} kph</div>
      </div>
    `;

    forecastDiv.innerHTML = card;

  } catch (error) {
    alert("Error fetching weather data: " + error.message);
  }
}
