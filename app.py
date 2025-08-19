<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1024, height=600, initial-scale=1, maximum-scale=1, user-scalable=no" />
<title>Ballistics Wind Scope - Imperial Units & MOA</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  :root {
    --tactical-bg: #181d17;
    --tactical-panel: #1b231b;
    --tactical-surface: #222922;
    --tactical-accent: #d9ff62;
    --tactical-accent-dark: #2d5000;
    --tactical-danger: #ff4646;
    --text-main: #fff;
    --text-detail: #f8ffe9;
    --text-muted: #a3a3a3;
    --input-bg: #1e2a14;
    --input-border: #86b341;
    --input-focus: #d9ff62;
    --button-bg: var(--tactical-accent-dark);
    --button-hover: #557e29;
    --button-active: #557e29;
    --shadow: rgba(0,0,0,0.22);
  }
  html, body {
    margin: 0; padding: 0; height: 100%; width: 100%;
    background: var(--tactical-bg);
    font-family: system-ui, sans-serif;
    font-size: 15px;
    user-select: none;
    color: var(--text-main);
    overflow: hidden;
  }
  #container {
    display: grid;
    grid-template-columns: 210px 1fr 210px;
    grid-template-rows: 72px 1fr 72px;
    grid-template-areas:
      "topbar topbar topbar"
      "leftbar main rightbar"
      "bottombar bottombar bottombar";
    height: 100vh;
    width: 100vw;
    box-sizing: border-box;
    padding: 8px;
    gap: 6px;
    position: relative;
  }
  #topbar {
    grid-area: topbar;
    background: var(--tactical-panel);
    border-radius: 12px;
    padding: 6px 16px;
    display: flex;
    align-items: center;
    gap: 18px;
    justify-content: flex-start;
    box-shadow: 0 1px 9px var(--shadow);
    overflow-x: auto;
    font-size: 14px;
  }
  #topbar .input-group {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    min-width: 95px;
    max-width: 140px;
    flex: none;
  }
  #topbar label {
    font-weight: 700;
    color: var(--tactical-accent);
    font-size: 13px;
    user-select: none;
    margin-bottom: 4px;
  }
  #topbar input, #topbar select {
    font-size: 14px;
    border-radius: 6px;
    border: 2px solid var(--input-border);
    background: var(--input-bg);
    color: #d9ff62;
    padding: 6px 8px;
    width: 100%;
    outline: none;
    box-sizing: border-box;
    font-weight: 700;
    letter-spacing: 1px;
    text-align: center;
    transition: border-color 0.2s, color 0.3s;
  }
  #topbar input[type="number"]:focus, #topbar select:focus {
    border-color: var(--input-focus);
    color: #faffbd;
  }
  .unit-label {
    font-size: 11px;
    color: var(--tactical-accent);
    user-select: none;
    margin-top: 4px;
    text-align: center;
    letter-spacing: 1px;
  }
  #leftbar {
    grid-area: leftbar;
    background: var(--tactical-panel);
    border-radius: 12px;
    padding: 12px 10px 6px 10px;
    box-shadow: 0 1px 7px var(--shadow);
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 14px;
    font-size: 15px;
    color: var(--tactical-accent);
    font-weight: 700;
  }
  .slider-group {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    margin-bottom: 6px;
  }
  .slider-group label { margin-bottom:5px; font-weight:900; color:var(--tactical-accent);}
  .slider-group input[type="range"] {
    width: 100%;
    accent-color: var(--tactical-accent);
    background: var(--tactical-surface);
    border-radius: 8px;
  }
  .slider-group .slider-value {
    font-size: 15px; color: var(--tactical-accent); font-weight:900; text-align:center; margin-top: 2px;
    text-shadow: 0 1px 0 #111;
  }
  #leftbar button,
  #infoToggle,
  #topbar button,
  #set-btns button {
    background: var(--button-bg);
    color: var(--tactical-accent);
    border-radius: 9px;
    border: none;
    font-weight: 700;
    font-size: 15px;
    padding: 11px 10px;
    margin-bottom: 6px;
    cursor: pointer;
    user-select: none;
    transition: background .13s, color 0.2s;
    box-shadow: 0 3px 10px var(--shadow);
    letter-spacing: 1.2px;
    text-shadow: 0 1px 0 #000;
    min-width: 100%;
    text-align: center;
  }
  #leftbar button:active,
  #infoToggle:active,
  #topbar button:active,
  #set-btns button:active,
  #leftbar button:focus,
  #infoToggle:focus,
  #topbar button:focus,
  #set-btns button:focus {
    background: var(--button-active);
    color: #f0fff2;
  }
  #leftbar #calculateBtn {
    background: var(--tactical-accent-dark);
    color: #f0fff2;
    margin-bottom: 0;
  }
  #leftbar #downloadTilesBtn {
    background: var(--tactical-panel);
    color: var(--tactical-accent);
  }
  #map, #api-panel {
    grid-area: main;
    border-radius: 12px;
    background: #181d17;
    width: 100%;
    height: 100%;
    overflow: hidden;
  }
  #api-panel {
    background: #161a14;
    color: var(--tactical-accent);
    box-shadow: 0 2px 16px var(--shadow);
    padding: 20px 30px;
    font-family: 'system-ui', sans-serif;
    font-size: 15px;
    overflow-y: auto;
    display: none;
    position: relative;
  }
  #rightbar {
    grid-area: rightbar;
    background: var(--tactical-panel);
    border-radius: 12px;
    padding: 14px 12px 10px 12px;
    box-shadow: 0 1px 7px var(--shadow);
    display: flex;
    flex-direction: column;
    align-items: stretch;
    font-size: 14px;
    color: var(--tactical-accent);
    user-select: none;
    position: relative;
    min-width: 180px;
    min-height: 0;
    height: 100%;
    overflow-y: auto;
    font-weight: 800;
  }
  #instructions {
    display: none;
    margin-top: 6px;
    font-size: 14px;
    color: var(--tactical-accent);
    background: #1d2517;
    line-height: 1.3;
    padding: 15px 12px;
    border-radius: 12px;
    border: 2px solid var(--button-hover);
    box-shadow: 0 5px 20px var(--shadow);
    position: absolute;
    left: 0; top: 0; right: 0; bottom: 0;
    z-index: 20;
    box-sizing: border-box;
  }
  #right-panel-info {
    flex: 1 1 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
    z-index: 10;
  }
  #infoToggle {
    background: var(--button-bg);
    color: var(--tactical-accent);
    font-weight: 700;
    font-size: 15px;
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    cursor: pointer;
    user-select: none;
    margin-bottom: 10px;
    margin-top: 2px;
    align-self: flex-start;
    transition: background 0.13s, color 0.2s;
    box-shadow: 0 2px 10px var(--shadow);
    text-shadow: 0 1px 2px #000;
  }
  #infoToggle:focus, #infoToggle:active {
    background: var(--button-hover);
    color: #fff;
  }
  #bottombar {
    grid-area: bottombar;
    background: var(--tactical-surface);
    border-radius: 12px;
    padding: 6px 14px;
    box-shadow: 0 -1px 12px var(--shadow);
    display: flex;
    gap: 18px;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
    min-height: 72px;
    z-index: 10;
    color: var(--text-main);
    flex-wrap: wrap;
    font-weight: 900;
  }
  #coords {
    font-family: monospace;
    background: #263515;
    border-radius: 8px;
    padding: 6px 10px;
    color: #fff;
    white-space: nowrap;
    user-select: text;
    font-weight: 700;
    text-shadow: 0 1px 1px #000;
  }
  #set-btns {
    display: flex;
    gap: 14px;
  }
  #set-btns button {
    font-weight: 900;
    font-size: 16px;
    padding: 11px 16px;
    border-radius: 8px;
    border: 2px solid var(--tactical-accent);
    color: #fff;
    user-select: none;
    cursor: pointer;
    min-width: 130px;
    letter-spacing: 1px;
    background: var(--tactical-accent-dark);
    transition: background 0.13s, color 0.2s;
    text-shadow: 0 2px 2px #000;
  }
  #setShooterBtn.active,
  #setTargetBtn.active {
    box-shadow: 0 0 0 3px var(--tactical-accent);
    border-color: #fff;
    color: var(--tactical-accent);
    background: #222;
  }
  #setShooterBtn {
    background: var(--tactical-accent-dark);
  }
  #setTargetBtn {
    background: var(--tactical-danger);
  }
  #weatherSourceToggle label {
    font-size: 14px;
    color: var(--tactical-accent);
    font-weight: 700;
    user-select: none;
    display: block;
    margin-bottom: 3px;
    text-shadow: 0 1px 1px #000;
  }
  #weatherSourceToggle input[type="radio"] {
    margin-right: 9px;
    vertical-align: middle;
    cursor: pointer;
    accent-color: var(--tactical-accent);
  }
  .leaflet-control-zoom-in,
  .leaflet-control-zoom-out {
    font-size: 2rem !important;
    width: 44px !important;
    height: 44px !important;
    background: #141b0c !important;
    color: var(--tactical-accent) !important;
    border: 2px solid var(--tactical-accent) !important;
    border-radius: 6px !important;
    box-shadow: 0 0 6px #000;
  }
  #modeToggleBtn {
    background: var(--button-bg);
    color: var(--tactical-accent);
    border-radius: 9px;
    border: none;
    font-weight: 700;
    font-size: 15px;
    padding: 11px 14px;
    cursor: pointer;
    user-select: none;
    transition: background 0.13s, color 0.2s;
    box-shadow: 0 3px 10px var(--shadow);
    letter-spacing: 1.2px;
    text-shadow: 0 1px 0 #000;
    min-width: 110px;
  }
  #modeToggleBtn:active, #modeToggleBtn:focus {
    background: var(--button-active);
    color: #f0fff2;
  }
  #apiResults {
    color: #d9ff62;
    font-weight: 800;
    margin-top: 20px;
    line-height: 1.3;
    transition: font-size 0.3s ease;
  }
  #apiResults.expanded {
    font-size: 28px;
  }
  #solutionAge {
    margin-top: 8px;
    color: var(--tactical-accent);
    font-weight: 700;
    font-size: 16px;
    user-select: none;
}

/* Add this for red color when aging */
#solutionAge.red-text {
    color: red;
}
</style>
<body>
<div id="container" aria-label="Ballistics Wind Scope interface">
  <div id="topbar" role="region" aria-label="Ballistics inputs">
    <div class="input-group"><label for="bcG7">G7 BC</label><input type="number" step="0.0001" id="bcG7" value="0" min="0" /></div>
    <div class="input-group"><label for="velocity">Speed</label><input type="number" step="0.1" id="velocity" value="0" min="0" /><span class="unit-label">ft/s</span></div>
    <div class="input-group"><label for="pressure">Pressure</label><input type="number" step="0.01" id="pressure" value="0" min="25" max="32" /><span class="unit-label">inHg</span></div>
    <div class="input-group"><label for="temperature">Temp</label><input type="number" step="0.1" id="temperature" value="0" /><span class="unit-label">°F</span></div>
    <div class="input-group"><label for="windSpeed">Wind</label><input type="number" step="0.1" id="windSpeed" value="0" /><span class="unit-label">mph</span></div>
    <div class="input-group"><label for="windDirection">Wind Dir</label><input type="number" step="1" id="windDirection" value="0" min="0" max="360" /><span class="unit-label">°</span></div>
    <div class="input-group"><label for="rangeToTarget">Range</label><input type="number" id="rangeToTarget" value="0" min="0" /><span class="unit-label">yards</span></div>
  </div>
  <div id="leftbar" role="region" aria-label="Weather meter and main controls">
    <div class="slider-group">
      <label for="multiplier">Weather Meter Influence</label>
      <input type="range" min="0" max="2" value="1" step="0.01" id="multiplier" />
      <span class="slider-value" id="multiplierVal">1.00</span>
    </div>
    <button id="fetchWeatherBtn" aria-label="Fetch weather data">☁️ Fetch Weather</button>
    <button id="downloadTilesBtn" aria-label="Download map tiles for offline use">⬇️ Download Map</button>
    <button id="calculateBtn" aria-label="Calculate ballistics solutions">Calculate</button>
    <div id="weatherSourceToggle" aria-label="Select weather data source">
      <label><input type="radio" name="weatherSource" id="weatherExt" checked /> External API</label>
      <label><input type="radio" name="weatherSource" id="weatherLocal" /> Local LoRa Station</label>
    </div>
  </div>
  <div id="map" role="region" aria-label="Map showing shooter and target locations"></div>
  <div id="api-panel" role="region" aria-label="Wind and ballistics sensor dashboard" style="display:none;">
    <div id="apiResults"></div>
    <canvas id="trajectoryCanvas" width="330" height="180" style="background:#181d17; border-radius:10px; margin-top:25px;"></canvas>
  </div>
  <div id="rightbar" role="region" aria-label="Information panel and instructions">
    <button id="infoToggle" aria-pressed="false" aria-label="Show or hide instructions">❔ Info</button>
    <div id="instructions" role="region" aria-live="polite" tabindex="0" aria-hidden="true">
      <p>Tap <strong>Set Shooter</strong> or <strong>Set Target</strong>, then tap the map to place the marker.</p>
      <p>Markers can be dragged to fine-tune positions.</p>
      <p>Use the weather controls to fetch current weather data.</p>
      <p>Download map tiles for offline usage before heading into the field.</p>
    </div>
    <div id="right-panel-info" aria-live="polite">
      <div id="weatherStatus"></div>
      <div id="weatherPreview"></div>
    </div>
  </div>
  <div id="bottombar" role="region" aria-label="Ballistics results and controls">
    <button id="modeToggleBtn" aria-label="Toggle Map / API View">API Mode</button>
    <span id="coords" aria-live="polite">Shooter: <span id="shooterCoords" class="coord">Not Set</span>&nbsp;|&nbsp; Target: <span id="targetCoords" class="coord">Not Set</span></span>
    <span id="set-btns">
      <button id="setShooterBtn" aria-pressed="false" aria-label="Set shooter location">Set Shooter</button>
      <button id="setTargetBtn" aria-pressed="false" aria-label="Set target location">Set Target</button>
    </span>
  </div>
</div>
<script>
  const map = L.map('map', { zoomControl: true }).setView([40, -105], 8);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  let shooterMarker = null;
  let targetMarker = null;
  let setMode = null;

  function updateSetMode(mode) {
    setMode = mode;
    document.getElementById('setShooterBtn').classList.toggle('active', mode === 'shooter');
    document.getElementById('setTargetBtn').classList.toggle('active', mode === 'target');
    document.getElementById('setShooterBtn').setAttribute('aria-pressed', mode === 'shooter');
    document.getElementById('setTargetBtn').setAttribute('aria-pressed', mode === 'target');
  }
  document.getElementById('setShooterBtn').onclick = () => updateSetMode('shooter');
  document.getElementById('setTargetBtn').onclick = () => updateSetMode('target');

  function setCoords() {
    document.getElementById('shooterCoords').textContent =
      shooterMarker ? shooterMarker.getLatLng().lat.toFixed(4) + ', ' + shooterMarker.getLatLng().lng.toFixed(4) : 'Not Set';
    document.getElementById('targetCoords').textContent =
      targetMarker ? targetMarker.getLatLng().lat.toFixed(4) + ', ' + targetMarker.getLatLng().lng.toFixed(4) : 'Not Set';

    if (shooterMarker && targetMarker) {
      const R = 6371e3;
      let a = shooterMarker.getLatLng(),
          b = targetMarker.getLatLng();
      let dLat = (b.lat - a.lat) * Math.PI / 180;
      let dLon = (b.lng - a.lng) * Math.PI / 180;
      let lat1 = a.lat * Math.PI / 180;
      let lat2 = b.lat * Math.PI / 180;
      let x = dLon * Math.cos((lat1 + lat2) / 2);
      let y = dLat;
      let distanceMeters = Math.sqrt(x*x + y*y) * R;
      document.getElementById('rangeToTarget').value = Math.round(distanceMeters * 1.09361);
    }
  }

  map.on('click', e => {
    if (setMode === 'shooter') {
      if (shooterMarker) shooterMarker.setLatLng(e.latlng);
      else {
        shooterMarker = L.marker(e.latlng, { draggable: true }).addTo(map).bindTooltip("Shooter").openTooltip();
        shooterMarker.on('dragend', setCoords);
      }
      setCoords();
      updateSetMode(null);
    } else if (setMode === 'target') {
      if (targetMarker) targetMarker.setLatLng(e.latlng);
      else {
        targetMarker = L.marker(e.latlng, {
          draggable: true,
          icon: L.icon({ iconUrl: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png', iconSize: [32, 32] })
        }).addTo(map).bindTooltip("Target").openTooltip();
        targetMarker.on('dragend', setCoords);
      }
      setCoords();
      updateSetMode(null);
    }
  });

  const mapDiv = document.getElementById('map');
  const apiPanel = document.getElementById('api-panel');
  const modeToggleBtn = document.getElementById('modeToggleBtn');
  let showingAPI = false;

  modeToggleBtn.onclick = () => {
    showingAPI = !showingAPI;
    if (showingAPI) {
      mapDiv.style.display = 'none';
      apiPanel.style.display = 'block';
      modeToggleBtn.textContent = 'Map Mode';
    } else {
      apiPanel.style.display = 'none';
      mapDiv.style.display = 'block';
      modeToggleBtn.textContent = 'API Mode';

      map.invalidateSize();
    }
  };

function stopSolutionAgeTimer() {
  if (solutionAgeInterval) {
    clearInterval(solutionAgeInterval);
    solutionAgeInterval = null;
  }
  solutionTimestamp = null;
}

  let solutionAgeInterval = null;
  let solutionTimestamp = null;

  function startSolutionAgeTimer() {
  stopSolutionAgeTimer();
  solutionTimestamp = Date.now();
  solutionAgeInterval = setInterval(() => {
    if (!solutionTimestamp) return;
    let ageS = (Date.now() - solutionTimestamp) / 1000;
    const elm = document.getElementById('solutionAge');
    if (elm) {
      elm.textContent = `Solution Age: ${ageS.toFixed(1)} s`;
      if (ageS >= 30) {
        elm.classList.add('red-text');
      } else {
        elm.classList.remove('red-text');
      }
    }
  }, 100);
}

  let trajectoryChart = null;

  function drawTrajectory(rangeArray, dropArray) {
  const ctx = document.getElementById('trajectoryCanvas').getContext('2d');
  if (trajectoryChart) trajectoryChart.destroy();

  // For most shooters, negative is down; positiveDrops flips this
  const positiveDrops = dropArray.map(v => -v);

  trajectoryChart = new Chart(ctx, {
    type: 'line',
     data:{
      labels: rangeArray,
      datasets: [{
  label: 'Drop (MOA)',       // name shown in the chart legend
  data: positiveDrops,       // here you assign the array of values
  borderColor: '#d9ff62',
  backgroundColor: 'rgba(217,255,98,0.16)',
  pointRadius: 2,
  borderWidth: 2,
  tension: 0.16
      }]
    },
    options: {
      plugins: { legend: { labels: { color: '#fff', font: { weight: 'bold' } } } },
      scales: {
        x: {
          title: { display: true, text: 'Range (yds)', color: '#d9ff62' },
          ticks: { color: '#fff' }
        },
        y: {
          title: { display: true, text: 'Drop (MOA)', color: '#d9ff62' },
          ticks: { color: '#fff' }
        }
      }
    }
  });
}

  async function calculateBallistics() {
    const payload = {
      bc_g7: parseFloat(document.getElementById('bcG7').value) || 0,
      muzzle_velocity_fps: parseFloat(document.getElementById('velocity').value) || 0,
      pressure_inhg: parseFloat(document.getElementById('pressure').value) || 0,
      temp_f: parseFloat(document.getElementById('temperature').value) || 0,
      wind_speed_mph: parseFloat(document.getElementById('windSpeed').value) || 0,
      wind_direction_deg: parseFloat(document.getElementById('windDirection').value) || 0,
      range_yds: parseFloat(document.getElementById('rangeToTarget').value) || 0
    };

    try {
      const response = await fetch('/api/ballistics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();

      if (!response.ok) {
        displayError(data);
        return;
      }

      const resultsContainer = document.getElementById('apiResults');
      resultsContainer.innerHTML = `
        Drop: ${data.drop_moa} MOA<br>
        Windage: ${data.windage_moa} MOA<br>
        Time of Flight: ${data.time_of_flight_sec} s<br>
        Velocity at Target: ${data.velocity_at_target_fps} ft/s
        <br><span id="solutionAge"></span>
      `;
      if (data.range_yds && data.drop_array_moa) {
        drawTrajectory(data.range_yds, data.drop_array_moa);
      } else {
        if (trajectoryChart) trajectoryChart.destroy();
      }
      startSolutionAgeTimer();
    } catch (err) {
      displayError({ error: err.message });
    }
  }

  document.getElementById('calculateBtn').onclick = calculateBallistics;

  function displayError(apiResponse) {
    document.getElementById('apiResults').innerHTML =
      "<span style='color:#ff4646;font-weight:bold'>Error: </span>" +
      (apiResponse.error || "Unknown error") +
      (apiResponse.details ? "<br><small>" + apiResponse.details + "</small>" : "");
    if (trajectoryChart) trajectoryChart.destroy();
  }

  async function fetchWeatherFromExternal(lat, lon) {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&hourly=pressure_msl,temperature_2m,relativehumidity_2m,windspeed_10m,winddirection_10m,windgusts_10m,cloudcover&timezone=auto`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error('External API response not OK');
    return await resp.json();
  }

  async function fetchWeatherFromLocal(lat, lon) {
    const url = `http://raspberrypi.local:5000/api/local_wind?latitude=${lat}&longitude=${lon}`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error('Local API response not OK');
    return await resp.json();
  }

  async function updateWeatherFields(data, source) {
    let cw = data.current_weather || data;
    let idx = 0;
    let pressure = (data.hourly && data.hourly.pressure_msl) ? data.hourly.pressure_msl[idx] : 1013.25;
    let temp = cw.temperature || 20;
    let windSpd = cw.windspeed || 0;
    let windDir = cw.winddirection || 0;

    document.getElementById('pressure').value = (pressure * 0.02953).toFixed(2);
    document.getElementById('temperature').value = (temp * 9 / 5 + 32).toFixed(1);
    document.getElementById('windSpeed').value = (windSpd * 0.621371).toFixed(1);
    document.getElementById('windDirection').value = windDir;

    document.getElementById('weatherStatus').textContent = `Fields updated from ${source}.`;

    let hum = (data.hourly && data.hourly.relativehumidity_2m) ? data.hourly.relativehumidity_2m[idx] : '-';
    let gust = (data.hourly && data.hourly.windgusts_10m) ? data.hourly.windgusts_10m[idx] : (cw.windgust || '-');
    let cloud = (data.hourly && data.hourly.cloudcover) ? data.hourly.cloudcover[idx] : '-';
    document.getElementById('weatherPreview').textContent = `Humidity: ${hum}% • Gust: ${gust} km/h • Clouds: ${cloud}%`;
  }

  async function tryFetchWeather() {
    if (!shooterMarker) {
      document.getElementById('weatherStatus').textContent = "Set shooter marker first!";
      document.getElementById('weatherPreview').textContent = "";
      return;
    }
    const lat = shooterMarker.getLatLng().lat;
    const lon = shooterMarker.getLatLng().lng;
    document.getElementById('weatherStatus').textContent = "Loading...";
    document.getElementById('weatherPreview').textContent = "";
    const useExternal = document.getElementById('weatherExt').checked;
    if (useExternal){
      try {
        const data = await fetchWeatherFromExternal(lat, lon);
        await updateWeatherFields(data, 'External API');
      }
      catch(e){
        document.getElementById('weatherStatus').textContent = "External API failed, trying local API...";
        try {
          const data = await fetchWeatherFromLocal(lat, lon);
          await updateWeatherFields(data, 'Local API');
        }
        catch(e){
          document.getElementById('weatherStatus').textContent = "Both weather APIs unavailable.";
          document.getElementById('weatherPreview').textContent = "";
        }
      }
    }
    else {
      try {
        const data = await fetchWeatherFromLocal(lat, lon);
        await updateWeatherFields(data, 'Local API');
      }
      catch(e){
        document.getElementById('weatherStatus').textContent = "Local API failed; try external API.";
        document.getElementById('weatherPreview').textContent = "";
      }
    }
  }
  document.getElementById('fetchWeatherBtn').onclick = tryFetchWeather;

  const infoToggleBtn = document.getElementById('infoToggle');
  const instructionsDiv = document.getElementById('instructions');
  const rightPanelInfo = document.getElementById('right-panel-info');

  infoToggleBtn.onclick = () => {
    const visible = instructionsDiv.style.display === 'block';
    if (visible) {
      rightPanelInfo.style.display = '';
      instructionsDiv.style.display = 'none';
    } else {
      rightPanelInfo.style.display = 'none';
      instructionsDiv.style.display = 'block';
      instructionsDiv.focus();
    }
    infoToggleBtn.setAttribute('aria-pressed', !visible);
  };

  const multiplierSlider = document.getElementById('multiplier');
  const multiplierValDisplay = document.getElementById('multiplierVal');
  multiplierSlider.oninput = () => {
    multiplierValDisplay.textContent = multiplierSlider.value;
  };

  document.getElementById('downloadTilesBtn').onclick = () => {
    alert('Map tiles download feature not implemented.');
  };
</script>
</body>
</html>
