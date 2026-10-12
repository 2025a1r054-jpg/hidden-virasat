/**
 * HIDDEN VIRASAT — Personalized Trip Planner
 * Interactive itinerary generator, transparent recommendation engine,
 * interactive itinerary map, and persistent SQLite trip storage.
 */

let currentItineraryData = null;
let plannerMap = null;
let plannerMapLayer = null;

document.addEventListener('DOMContentLoaded', () => {
  const plannerForm = document.getElementById('planner-form');
  const saveTripModal = document.getElementById('save-trip-modal');
  const savedTripsModal = document.getElementById('saved-trips-modal');

  if (plannerForm) {
    plannerForm.addEventListener('submit', (e) => {
      e.preventDefault();
      generateItinerary();
    });

    // Auto-generate on load with default settings
    generateItinerary();
  }

  // Bind Saved Trips modal open/close
  const viewSavedBtn = document.getElementById('view-saved-trips-btn');
  if (viewSavedBtn) {
    viewSavedBtn.addEventListener('click', openSavedTripsModal);
  }

  // Modal backdrop click to close
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('active');
      }
    });
  });

  const closeBtns = document.querySelectorAll('.modal-close-btn');
  closeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.modal-backdrop').forEach(m => m.classList.remove('active'));
    });
  });

  // Save trip form submit
  const saveForm = document.getElementById('save-trip-form');
  if (saveForm) {
    saveForm.addEventListener('submit', handleSaveTripSubmit);
  }
});

async function generateItinerary() {
  const resultsContainer = document.getElementById('planner-results');
  if (!resultsContainer) return;

  // Gather form values
  const durationDays = parseInt(document.querySelector('input[name="duration"]:checked')?.value || '2');
  const pace = document.querySelector('input[name="pace"]:checked')?.value || 'balanced';
  const startArea = document.querySelector('input[name="start_area"]:checked')?.value || 'old-city';

  const interestCheckboxes = document.querySelectorAll('input[name="interests"]:checked');
  const interests = Array.from(interestCheckboxes).map(cb => cb.value);

  resultsContainer.innerHTML = `
    <div style="padding: 4rem; text-align: center; background: var(--white); border-radius: var(--radius-md); border: var(--border-subtle);">
      <div style="font-size: 2.2rem; margin-bottom: 1rem; animation: spin 2s infinite linear;">🧭</div>
      <h3 style="font-family: var(--font-serif); font-size: 1.5rem; margin-bottom: 0.5rem;">Weaving Your Dogra Itinerary...</h3>
      <p style="color: #6C5F6D; font-size: 0.95rem;">Balancing geographic routes, opening hours, and your cultural interests.</p>
    </div>
  `;

  try {
    const res = await fetch('/api/recommend-itinerary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        duration_days: durationDays,
        pace: pace,
        interests: interests.length > 0 ? interests : ['heritage', 'food', 'spirituality'],
        start_area: startArea
      })
    });

    const data = await res.json();
    if (data.success) {
      currentItineraryData = data;
      renderItinerary(data);
    } else {
      resultsContainer.innerHTML = `<p style="padding: 2rem; color: red;">Failed to generate plan. Please try again.</p>`;
    }
  } catch (err) {
    console.error('Error generating plan:', err);
    resultsContainer.innerHTML = `<p style="padding: 2rem; color: red;">Network error. Please try again.</p>`;
  }
}

function renderItinerary(data) {
  const container = document.getElementById('planner-results');
  if (!container) return;

  let totalStopsCount = 0;
  let totalKm = 0;
  data.days.forEach(d => {
    totalStopsCount += d.stops.length;
    totalKm += d.approx_travel_distance_km;
  });

  let daysHtml = data.days.map((day, dIdx) => `
    <div class="day-timeline-card" data-day-index="${dIdx}">
      <div class="day-timeline-header">
        <div>
          <span class="eyebrow" style="color: var(--mauve-dark);">Day ${day.day_number} Schedule</span>
          <h3 style="font-size: 1.4rem; margin-bottom: 2px;">${day.title}</h3>
          <span style="font-size: 0.82rem; color: #625564;">
            Approx. route distance: <strong>~${day.approx_travel_distance_km} km</strong> • ${day.stops.length} cultural stops
          </span>
        </div>
      </div>
      <div class="timeline-stops-list">
        ${day.stops.length === 0 ? '<p style="padding: 1.5rem; color: #887;">No stops assigned for this day.</p>' : ''}
        ${day.stops.map((stop, sIdx) => `
          <div class="timeline-stop-item" data-stop-index="${sIdx}">
            <div class="stop-time-col">
              <div>${stop.time_slot}</div>
              <div style="font-size: 0.72rem; color: #786C7A; font-weight: 500;">${stop.slot_label}</div>
            </div>
            <div class="stop-content-col">
              <div style="display: flex; gap: 1rem; align-items: flex-start;">
                <img src="${stop.image_url}" alt="${stop.name}" style="width: 80px; height: 80px; border-radius: 8px; object-fit: cover; flex-shrink: 0;" onerror="this.onerror=null;this.src='/static/images/fallback-heritage.svg';">
                <div style="flex: 1;">
                  <div style="display: flex; align-items: baseline; justify-content: space-between; gap: 0.5rem;">
                    <h4 style="font-size: 1.15rem; margin-bottom: 2px;">
                      <a href="/places/${stop.slug}" target="_blank" style="color: var(--deep-plum); text-decoration: underline; text-decoration-color: var(--dusty-pink);">
                        ${stop.name}
                      </a>
                    </h4>
                    <button type="button" onclick="removeStopFromDay(${dIdx}, ${sIdx})" style="background: none; border: none; color: #A08C9E; cursor: pointer; font-size: 1.1rem; padding: 2px 6px;" title="Remove stop">
                      ✕
                    </button>
                  </div>
                  <div style="font-size: 0.8rem; color: var(--mauve); font-weight: 600; margin-bottom: 4px;">
                    📍 ${stop.location} • ⏱️ ${stop.visit_duration_label}
                  </div>
                  <div class="stop-match-reason">
                    💡 <em>${stop.match_reason}</em>
                  </div>
                  ${stop.travel_from_prev_km > 0 ? `
                    <div style="margin-top: 6px; font-size: 0.75rem; color: #6D5F6F;">
                      🚗 ~${stop.travel_from_prev_km} km travel from preceding location
                    </div>
                  ` : ''}
                </div>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');

  container.innerHTML = `
    <div style="background: var(--white); border-radius: var(--radius-md); padding: 1.75rem; border: var(--border-subtle); margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1.25rem; box-shadow: var(--shadow-xs);">
      <div>
        <span class="badge badge-mauve" style="margin-bottom: 0.4rem;">Curated Itinerary</span>
        <h3 style="font-size: 1.55rem; margin-bottom: 2px;">Your Personalized Virasat Trail</h3>
        <p style="margin: 0; font-size: 0.88rem; color: #5C4F5E;">
          ${data.days.length} Days • ${totalStopsCount} Curated Stops • ~${Math.round(totalKm)} km total travel
        </p>
      </div>
      <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <button type="button" class="btn btn-secondary btn-sm" onclick="generateItinerary()">
          🔄 Regenerate
        </button>
        <button type="button" class="btn btn-primary btn-sm" onclick="openSaveTripModal()">
          💾 Save Itinerary to Journal
        </button>
      </div>
    </div>

    <!-- Interactive Planner Route Map -->
    <div style="background: var(--white); border-radius: var(--radius-md); border: var(--border-subtle); overflow: hidden; margin-bottom: 2.5rem; box-shadow: var(--shadow-sm);">
      <div style="padding: 1rem 1.5rem; background: var(--warm-ivory); border-bottom: var(--border-subtle); display: flex; align-items: center; justify-content: space-between;">
        <span style="font-weight: 600; font-size: 0.92rem; color: var(--deep-plum);">🗺️ Geographic Route Preview</span>
        <span style="font-size: 0.8rem; color: #7B6E7D;">Interactive stops plotted across Jammu</span>
      </div>
      <div id="planner-route-map" style="height: 350px; width: 100%;"></div>
    </div>

    <div class="itinerary-days-container">
      ${daysHtml}
    </div>
  `;

  initPlannerRouteMap(data);
}

function initPlannerRouteMap(data) {
  const mapEl = document.getElementById('planner-route-map');
  if (!mapEl) return;

  if (plannerMap) {
    plannerMap.remove();
  }

  plannerMap = L.map('planner-route-map', {
    center: [32.7300, 74.8700],
    zoom: 12
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18
  }).addTo(plannerMap);

  plannerMapLayer = L.featureGroup().addTo(plannerMap);

  let stopNumber = 1;
  const dayColors = ['#8D718A', '#B2627E', '#B88458'];

  data.days.forEach((day, dIdx) => {
    const dayColor = dayColors[dIdx % dayColors.length];
    const latlngs = [];

    day.stops.forEach(stop => {
      latlngs.push([stop.latitude, stop.longitude]);

      const pinIcon = L.divIcon({
        html: `
          <div style="
            background: ${dayColor};
            color: #FAF7F5;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.78rem;
            font-weight: bold;
            box-shadow: 0 3px 8px rgba(0,0,0,0.3);
            border: 2px solid #FFFFFF;
          ">${stopNumber}</div>
        `,
        className: 'route-step-pin',
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });

      const marker = L.marker([stop.latitude, stop.longitude], { icon: pinIcon });
      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 0.85rem;">
          <strong>Stop ${stopNumber}: ${stop.name}</strong><br>
          <span style="color: ${dayColor}; font-weight: 600;">Day ${day.day_number} (${stop.time_slot})</span><br>
          <span style="font-size: 0.78rem; color: #555;">${stop.location}</span>
        </div>
      `);
      plannerMapLayer.addLayer(marker);
      stopNumber++;
    });

    if (latlngs.length > 1) {
      const polyline = L.polyline(latlngs, {
        color: dayColor,
        weight: 3,
        opacity: 0.75,
        dashArray: '6, 8'
      });
      plannerMapLayer.addLayer(polyline);
    }
  });

  if (plannerMapLayer.getLayers().length > 0) {
    plannerMap.fitBounds(plannerMapLayer.getBounds(), { padding: [40, 40] });
  }
}

function removeStopFromDay(dayIdx, stopIdx) {
  if (!currentItineraryData || !currentItineraryData.days[dayIdx]) return;

  const day = currentItineraryData.days[dayIdx];
  const removed = day.stops.splice(stopIdx, 1)[0];

  // Recalculate distance for remaining stops
  let totalKm = 0;
  for (let i = 0; i < day.stops.length; i++) {
    if (i === 0) {
      day.stops[i].travel_from_prev_km = 0;
    } else {
      const prev = day.stops[i - 1];
      const curr = day.stops[i];
      const dist = haversineDistance(prev.latitude, prev.longitude, curr.latitude, curr.longitude);
      curr.travel_from_prev_km = dist;
      totalKm += dist;
    }
  }
  day.approx_travel_distance_km = Math.round(totalKm * 10) / 10;

  showToast(`Removed "${removed.name}" from Day ${day.day_number}`, 'info');
  renderItinerary(currentItineraryData);
}

function haversineDistance(lat1, lon1, lat2, lon2) {
  const r = 6371;
  const dlat = (lat2 - lat1) * Math.PI / 180;
  const dlon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dlat / 2) * Math.sin(dlat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dlon / 2) * Math.sin(dlon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(r * c * 10) / 10;
}

function openSaveTripModal() {
  const modal = document.getElementById('save-trip-modal');
  if (modal) modal.classList.add('active');
}

async function handleSaveTripSubmit(e) {
  e.preventDefault();
  if (!currentItineraryData) return;

  const titleInput = document.getElementById('save-trip-title');
  const nameInput = document.getElementById('save-traveler-name');

  const title = titleInput ? titleInput.value.trim() : 'My Jammu Heritage Journey';
  const travelerName = nameInput ? nameInput.value.trim() : 'Dogra Explorer';

  const payload = {
    title: title || 'My Jammu Heritage Journey',
    traveler_name: travelerName || 'Dogra Explorer',
    duration_days: currentItineraryData.parameters.duration_days,
    pace: currentItineraryData.parameters.pace,
    interests: currentItineraryData.parameters.interests,
    start_area: currentItineraryData.parameters.start_area,
    itinerary: currentItineraryData.days
  };

  try {
    const res = await fetch('/api/trips', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.success) {
      document.getElementById('save-trip-modal').classList.remove('active');
      showToast('🎉 Itinerary saved successfully to your SQLite journal!', 'success');
    } else {
      showToast(data.error || 'Failed to save trip', 'error');
    }
  } catch (err) {
    console.error('Error saving trip:', err);
    showToast('Network error while saving trip', 'error');
  }
}

async function openSavedTripsModal() {
  const modal = document.getElementById('saved-trips-modal');
  const listContainer = document.getElementById('saved-trips-list');
  if (!modal || !listContainer) return;

  modal.classList.add('active');
  listContainer.innerHTML = `
    <div style="padding: 2rem; text-align: center; color: var(--mauve);">
      Loading your saved cultural journeys...
    </div>
  `;

  try {
    const res = await fetch('/api/trips');
    const data = await res.json();
    const trips = data.trips || [];

    if (trips.length === 0) {
      listContainer.innerHTML = `
        <div style="padding: 3rem; text-align: center;">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">📜</div>
          <h4>No Saved Journeys Yet</h4>
          <p style="font-size: 0.88rem; color: #726373;">Generate a custom itinerary and click "Save Itinerary" to store it in your database.</p>
        </div>
      `;
      return;
    }

    listContainer.innerHTML = trips.map(t => `
      <div style="background: var(--warm-ivory); border-radius: var(--radius-sm); border: var(--border-subtle); padding: 1.25rem; margin-bottom: 1rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;">
        <div>
          <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--mauve); font-weight: 700;">
            ${t.duration_days} Day Trail • Pace: ${t.pace}
          </div>
          <h4 style="font-size: 1.2rem; margin-bottom: 2px;">${t.title}</h4>
          <div style="font-size: 0.8rem; color: #6D5F6F;">
            Traveler: <strong>${t.traveler_name}</strong> • Created: ${t.created_at ? t.created_at.slice(0, 10) : 'Recent'}
          </div>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <button class="btn btn-secondary btn-sm" onclick="loadSavedTripToView(${t.id})">
            Load Plan
          </button>
          <button class="btn btn-outline btn-sm" onclick="deleteSavedTrip(${t.id})" style="color: #A23B52; border-color: #E0BAC3;">
            Delete
          </button>
        </div>
      </div>
    `).join('');

  } catch (err) {
    console.error('Error fetching trips:', err);
    listContainer.innerHTML = `<p style="padding: 1.5rem; color: red;">Could not fetch saved trips.</p>`;
  }
}

async function loadSavedTripToView(tripId) {
  try {
    const res = await fetch(`/api/trips/${tripId}`);
    const trip = await res.json();

    if (trip && trip.itinerary) {
      currentItineraryData = {
        parameters: {
          duration_days: trip.duration_days,
          pace: trip.pace,
          interests: trip.interests,
          start_area: trip.start_area
        },
        days: trip.itinerary
      };

      document.getElementById('saved-trips-modal').classList.remove('active');
      renderItinerary(currentItineraryData);
      showToast(`Loaded "${trip.title}" into view!`, 'success');
      window.scrollTo({ top: document.getElementById('planner-results').offsetTop - 90, behavior: 'smooth' });
    }
  } catch (err) {
    console.error('Error loading trip:', err);
    showToast('Failed to load trip', 'error');
  }
}

async function deleteSavedTrip(tripId) {
  if (!confirm('Are you sure you want to remove this saved journey from your archives?')) return;

  try {
    const res = await fetch(`/api/trips/${tripId}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast('Trip deleted from journal', 'info');
      openSavedTripsModal(); // Refresh list
    }
  } catch (err) {
    console.error('Error deleting trip:', err);
    showToast('Failed to delete trip', 'error');
  }
}
