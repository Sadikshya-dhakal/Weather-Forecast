// File: project/backend/static/script.js

function getWeatherIcon(label) {
  const icons = {
    sunny: "☀️",
    sun: "☀️",
    clear: "☀️",
    rain: "🌧️",
    rainy: "🌧️",
    drizzle: "🌦️",
    cloudy: "☁️",
    overcast: "☁️",
    fog: "🌫️",
    thunderstorm: "⛈️",
    snow: "❄️"
  };
  label = label.toLowerCase();
  for (let key in icons) {
    if (label.includes(key)) return icons[key];
  }
  return "❓";
}

function fetchForecast() {
  const city = document.getElementById("cityInput").value.trim();
  if (!city) {
    alert("Please enter a city name.");
    return;
  }

  fetch(`/predict?city=${encodeURIComponent(city)}`)
    .then(resp => resp.json())
    .then(data => {
      console.log("RAW JSON:", data);  // <--- Check that avgtemp & precipitation appear here
      const forecastDiv = document.getElementById("forecast");
      forecastDiv.innerHTML = "";

      if (data.error) {
        forecastDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        return;
      }

      data.predictions.forEach(item => {
        const card = document.createElement("div");
        card.className = "day-card";

        const icon = getWeatherIcon(item.predicted);
        card.innerHTML = `
          <div class="date">${item.date}</div>
          <div class="icon">${icon}</div>
          <div class="label">${item.predicted}</div>
          <div class="details">
            Avg Temp: ${item.avgtemp.toFixed(1)}°C<br>
            Precipitation: ${item.precipitation.toFixed(1)} mm
          </div>
        `;
        forecastDiv.appendChild(card);
      });
    })
    .catch(err => {
      alert("Failed to fetch forecast: " + err);
    });
}

document.getElementById("getForecastBtn")
        .addEventListener("click", fetchForecast);
