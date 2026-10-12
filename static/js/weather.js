/**
 * HIDDEN VIRASAT — Live Weather Integration
 * Fetches and displays live meteorological conditions from Open-Meteo via Flask backend.
 */

const WEATHER_ICONS = {
  'sunny': '☀️',
  'partly-cloudy': '⛅',
  'cloudy': '☁️',
  'fog': '🌫️',
  'drizzle': '🌦️',
  'rain': '🌧️',
  'heavy-rain': '⛈️',
  'snow': '🌨️',
  'thunderstorm': '⚡'
};

async function loadLiveWeather(targetElementId, lat = 32.7266, lon = 74.8570, placeLabel = 'Jammu & Surrounds') {
  const container = document.getElementById(targetElementId);
  if (!container) return;

  // Show loading state
  container.innerHTML = `
    <div class="weather-loading" style="padding: 1rem; text-align: center; color: var(--mauve);">
      <span style="display: inline-block; animation: spin 1s infinite linear;">⏳</span>
      <span style="margin-left: 0.5rem; font-size: 0.9rem;">Gathering live meteorological conditions for ${placeLabel}...</span>
    </div>
  `;

  try {
    const res = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
    const data = await res.json();

    if (data.status === 'success') {
      renderWeatherSuccess(container, data, lat, lon, placeLabel);
    } else {
      renderWeatherError(container, data.message || 'Weather service currently unavailable', lat, lon, placeLabel);
    }
  } catch (err) {
    console.error('Weather fetch error:', err);
    renderWeatherError(container, 'Network connection to meteorological service interrupted', lat, lon, placeLabel);
  }
}

function renderWeatherSuccess(container, data, lat, lon, placeLabel) {
  const iconEmoji = WEATHER_ICONS[data.icon] || '🌤️';
  const temp = Math.round(data.temperature);
  const feelsLike = data.apparent_temperature !== undefined ? Math.round(data.apparent_temperature) : temp;

  container.innerHTML = `
    <div class="weather-header">
      <div class="weather-icon-circle" title="${data.condition}">
        <span>${iconEmoji}</span>
      </div>
      <div>
        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--mauve); font-weight: 700;">
          Live Atmosphere • ${placeLabel}
        </div>
        <div style="display: flex; align-items: baseline; gap: 0.6rem;">
          <span class="weather-temp-huge">${temp}°C</span>
          <span class="weather-condition-text">${data.condition}</span>
        </div>
        <div style="font-size: 0.82rem; color: #6D5E6F;">${data.condition_note || 'Fair weather conditions'}</div>
      </div>
    </div>
    
    <div class="weather-meta-pills">
      <div class="weather-meta-item" title="Apparent Temperature">
        <span>🌡️</span>
        <span>Feels: <strong>${feelsLike}°C</strong></span>
      </div>
      <div class="weather-meta-item" title="Relative Humidity">
        <span>💧</span>
        <span>Humidity: <strong>${data.relative_humidity}%</strong></span>
      </div>
      <div class="weather-meta-item" title="Wind Velocity">
        <span>💨</span>
        <span>Wind: <strong>${data.wind_speed} km/h</strong></span>
      </div>
      <button class="weather-refresh-btn" onclick="loadLiveWeather('${container.id}', ${lat}, ${lon}, '${placeLabel}')">
        🔄 Refresh
      </button>
    </div>
  `;
}

function renderWeatherError(container, message, lat, lon, placeLabel) {
  container.innerHTML = `
    <div style="padding: 1rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; width: 100%; flex-wrap: wrap;">
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 1.5rem;">⛅</span>
        <div>
          <div style="font-weight: 600; font-size: 0.9rem; color: var(--deep-plum);">Weather Data Temporarily Offline</div>
          <div style="font-size: 0.8rem; color: #7A6D7C;">${message} — Seasonal norms in Jammu range from 15°C to 28°C with clear hill skies.</div>
        </div>
      </div>
      <button class="weather-refresh-btn" onclick="loadLiveWeather('${container.id}', ${lat}, ${lon}, '${placeLabel}')">
        🔄 Retry Connection
      </button>
    </div>
  `;
}
