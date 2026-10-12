/**
 * HIDDEN VIRASAT — Interactive Heritage Map
 * Leaflet.js with category-coded SVG markers, popups, and sidebar synchronization.
 */

let mapInstance = null;
let markersGroup = null;
let allPlacesData = [];
let activeCategoryFilter = 'all';

const CATEGORY_COLORS = {
  'Heritage & Forts': '#8D718A',            // Mauve
  'Temples & Spiritual Heritage': '#B2627E', // Rose Plum
  'Museums & Art': '#B88458',                // Bronze Gold
  'Local Markets': '#382F39',                // Deep Plum
  'Traditional Crafts': '#985268',           // Terracotta Rose
  'Nature & Cultural Experiences': '#4C7063' // Sage Forest
};

const CATEGORY_EMOJIS = {
  'Heritage & Forts': '🏰',
  'Temples & Spiritual Heritage': '🛕',
  'Museums & Art': '🎨',
  'Local Markets': '🛍️',
  'Traditional Crafts': '🧵',
  'Nature & Cultural Experiences': '🌿'
};

document.addEventListener('DOMContentLoaded', () => {
  const mapElement = document.getElementById('leaflet-full-map');
  if (!mapElement) return;

  initLeafletMap();
});

function initLeafletMap() {
  // Center on Jammu City
  mapInstance = L.map('leaflet-full-map', {
    center: [32.7300, 74.8700],
    zoom: 12,
    scrollWheelZoom: true
  });

  // OpenStreetMap Tile Layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(mapInstance);

  markersGroup = L.featureGroup().addTo(mapInstance);

  // Fetch places data
  fetch('/api/places')
    .then(res => res.json())
    .then(data => {
      allPlacesData = data.places || [];
      renderMarkersAndSidebar();
      setupMapFilterEvents();
    })
    .catch(err => {
      console.error('Failed to load map places:', err);
      showToast('Could not load map coordinates. Please refresh.', 'error');
    });
}

function createCategoryIcon(category) {
  const color = CATEGORY_COLORS[category] || '#8D718A';
  const emoji = CATEGORY_EMOJIS[category] || '📍';

  const svgHtml = `
    <div style="
      background-color: ${color};
      width: 38px;
      height: 38px;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(56, 47, 57, 0.35);
      border: 2px solid #FAF7F5;
      cursor: pointer;
    ">
      <span style="
        transform: rotate(45deg);
        font-size: 1.1rem;
        line-height: 1;
      ">${emoji}</span>
    </div>
  `;

  return L.divIcon({
    html: svgHtml,
    className: 'custom-map-pin',
    iconSize: [38, 38],
    iconAnchor: [19, 38],
    popupAnchor: [0, -38]
  });
}

function renderMarkersAndSidebar() {
  if (!mapInstance || !markersGroup) return;

  markersGroup.clearLayers();
  const sidebarList = document.getElementById('map-sidebar-places');
  if (sidebarList) sidebarList.innerHTML = '';

  const filteredPlaces = activeCategoryFilter === 'all'
    ? allPlacesData
    : allPlacesData.filter(p => p.category === activeCategoryFilter);

  const markerMap = {};

  filteredPlaces.forEach(place => {
    const icon = createCategoryIcon(place.category);
    const marker = L.marker([place.latitude, place.longitude], { icon: icon });

    const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${place.latitude},${place.longitude}`;

    const popupContent = `
      <div style="font-family: 'Plus Jakarta Sans', sans-serif; max-width: 260px; padding: 2px;">
        <img src="${place.image_url}" alt="${place.name}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 8px; margin-bottom: 8px;" onerror="this.onerror=null;this.src='/static/images/fallback-heritage.svg';">
        <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: ${CATEGORY_COLORS[place.category] || '#8D718A'}; margin-bottom: 3px;">
          ${place.category}
        </div>
        <h4 style="font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.25rem; font-weight: 700; margin-bottom: 6px; line-height: 1.2;">
          ${place.name}
        </h4>
        <p style="font-size: 0.82rem; color: #554856; margin-bottom: 10px; line-height: 1.4;">
          ${place.short_desc.slice(0, 110)}...
        </p>
        <div style="display: flex; gap: 6px; justify-content: space-between;">
          <a href="/places/${place.slug}" style="background: #8D718A; color: #FAF7F5; padding: 5px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; text-decoration: none;">
            View Details
          </a>
          <a href="${directionsUrl}" target="_blank" rel="noopener noreferrer" style="background: #FAF7F5; color: #382F39; border: 1px solid #D6A3B0; padding: 5px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; text-decoration: none;">
            🧭 Directions
          </a>
        </div>
      </div>
    `;

    marker.bindPopup(popupContent, { maxWidth: 280 });
    markersGroup.addLayer(marker);
    markerMap[place.id] = marker;

    // Append to sidebar
    if (sidebarList) {
      const itemEl = document.createElement('div');
      itemEl.className = 'map-place-item';
      itemEl.dataset.placeId = place.id;
      itemEl.innerHTML = `
        <img src="${place.image_url}" alt="${place.name}" class="map-place-thumb" onerror="this.onerror=null;this.src='/static/images/fallback-heritage.svg';">
        <div style="flex: 1; min-width: 0;">
          <div style="font-size: 0.72rem; color: var(--mauve); font-weight: 700; text-transform: uppercase;">
            ${place.category}
          </div>
          <h4 style="font-size: 1.05rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 2px;">
            ${place.name}
          </h4>
          <div style="font-size: 0.78rem; color: #726573;">⏱️ ${place.visit_duration_label}</div>
        </div>
      `;

      itemEl.addEventListener('click', () => {
        document.querySelectorAll('.map-place-item').forEach(el => el.classList.remove('active'));
        itemEl.classList.add('active');
        mapInstance.flyTo([place.latitude, place.longitude], 14, { duration: 1 });
        marker.openPopup();
      });

      sidebarList.appendChild(itemEl);
    }
  });

  // Auto-fit bounds if we have markers
  if (filteredPlaces.length > 0) {
    mapInstance.fitBounds(markersGroup.getBounds(), { padding: [50, 50] });
  }

  // Update counter
  const mapCounter = document.getElementById('map-places-count');
  if (mapCounter) {
    mapCounter.textContent = `${filteredPlaces.length} Landmarks Displayed`;
  }
}

function setupMapFilterEvents() {
  const filterBtns = document.querySelectorAll('.map-filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCategoryFilter = btn.dataset.category || 'all';
      renderMarkersAndSidebar();
    });
  });

  const fitBtn = document.getElementById('map-fit-bounds-btn');
  if (fitBtn) {
    fitBtn.addEventListener('click', () => {
      if (markersGroup.getLayers().length > 0) {
        mapInstance.fitBounds(markersGroup.getBounds(), { padding: [50, 50] });
      }
    });
  }
}
