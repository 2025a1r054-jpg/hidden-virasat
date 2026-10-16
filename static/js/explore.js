/**
 * HIDDEN VIRASAT — Explore Discovery Directory
 * Live category filtering, Explore Near Me with geolocation,
 * distance filtering, manual map picker, and instant search.
 */

let currentMode = 'category'; // 'category' or 'near'
let currentCategory = '';
let currentSearch = '';
let currentSort = 'name';
let searchDebounceTimer = null;

// Near Me state
let nearUserLat = null;
let nearUserLon = null;
let nearLocationLabel = '';
let nearRadius = '';
let nearPickerMap = null;
let nearPickerMarker = null;

document.addEventListener('DOMContentLoaded', () => {
  const filterTabs = document.querySelectorAll('#category-filter-section .filter-tab');
  const searchInput = document.getElementById('explore-search');
  const sortSelect = document.getElementById('explore-sort');

  // Mode Switch Buttons
  const modeCategoryBtn = document.getElementById('mode-category-btn');
  const modeNearBtn = document.getElementById('mode-near-btn');
  const categoryFilterSection = document.getElementById('category-filter-section');
  const nearMePanel = document.getElementById('near-me-panel');
  const sortControlsWrap = document.getElementById('sort-controls-wrap');

  // Read initial URL params
  const urlParams = new URLSearchParams(window.location.search);
  currentCategory = urlParams.get('category') || '';
  currentSearch = urlParams.get('q') || '';
  currentSort = urlParams.get('sort') || 'name';
  const shouldOpenNear = urlParams.get('near') === '1' || urlParams.has('lat');

  if (searchInput && currentSearch) {
    searchInput.value = currentSearch;
  }
  if (sortSelect && currentSort) {
    sortSelect.value = currentSort;
  }

  // 1. Bind Category Filter Tabs
  filterTabs.forEach(tab => {
    const tabCat = tab.dataset.category || '';
    if (tabCat === currentCategory) {
      tab.classList.add('active');
    } else {
      tab.classList.remove('active');
    }

    tab.addEventListener('click', () => {
      filterTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentCategory = tab.dataset.category || '';
      updateUrlAndFetch();
    });
  });

  // 2. Mode Switching Logic
  if (modeCategoryBtn && modeNearBtn) {
    modeCategoryBtn.addEventListener('click', () => {
      setDiscoveryMode('category');
    });

    modeNearBtn.addEventListener('click', () => {
      setDiscoveryMode('near');
    });
  }

  // 3. Near Me: GPS Detect Button
  const detectGpsBtn = document.getElementById('btn-detect-gps');
  if (detectGpsBtn) {
    detectGpsBtn.addEventListener('click', () => {
      requestUserLocation(true);
    });
  }

  // 4. Near Me: Landmark Presets
  const presetBtns = document.querySelectorAll('.near-preset-btn');
  presetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      presetBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      nearUserLat = parseFloat(btn.dataset.lat);
      nearUserLon = parseFloat(btn.dataset.lon);
      nearLocationLabel = btn.dataset.name || 'Selected Landmark';

      updateNearStatusUI(`📍 Reference: ${nearLocationLabel}`, `Coordinates: ${nearUserLat.toFixed(4)}° N, ${nearUserLon.toFixed(4)}° E`);
      updateNearPickerMarker(nearUserLat, nearUserLon);
      fetchAndRenderPlaces();
    });
  });

  // 5. Near Me: Radius Filter Pills
  const radiusBtns = document.querySelectorAll('.near-radius-btn');
  radiusBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      radiusBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      nearRadius = btn.dataset.radius || '';
      fetchAndRenderPlaces();
    });
  });

  // 6. Near Me: Map Picker Toggle
  const toggleMapPickerBtn = document.getElementById('btn-toggle-map-picker');
  const mapPickerContainer = document.getElementById('near-map-picker-container');
  if (toggleMapPickerBtn && mapPickerContainer) {
    toggleMapPickerBtn.addEventListener('click', () => {
      const isVisible = mapPickerContainer.style.display !== 'none';
      mapPickerContainer.style.display = isVisible ? 'none' : 'block';
      toggleMapPickerBtn.innerHTML = isVisible ? '<span>🗺️ Pick on Map</span>' : '<span>✕ Close Map Picker</span>';

      if (!isVisible) {
        initNearPickerMap();
      }
    });
  }

  // 7. Search Input with Debounce
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        currentSearch = e.target.value.trim();
        updateUrlAndFetch();
      }, 250);
    });
  }

  // 8. Sort Select
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      currentSort = e.target.value;
      updateUrlAndFetch();
    });
  }

  // Check if near mode requested initially
  if (shouldOpenNear) {
    if (urlParams.has('lat') && urlParams.has('lon')) {
      nearUserLat = parseFloat(urlParams.get('lat'));
      nearUserLon = parseFloat(urlParams.get('lon'));
      nearLocationLabel = urlParams.get('label') || 'Specified Coordinates';
      setDiscoveryMode('near', false);
      updateNearStatusUI(`📍 Reference: ${nearLocationLabel}`, `Coordinates: ${nearUserLat.toFixed(4)}° N, ${nearUserLon.toFixed(4)}° E`);
      fetchAndRenderPlaces();
    } else {
      setDiscoveryMode('near', true);
    }
  } else {
    // Initial fetch for standard category directory
    fetchAndRenderPlaces();
  }
});

function setDiscoveryMode(mode, triggerGeo = true) {
  currentMode = mode;
  const modeCategoryBtn = document.getElementById('mode-category-btn');
  const modeNearBtn = document.getElementById('mode-near-btn');
  const categoryFilterSection = document.getElementById('category-filter-section');
  const nearMePanel = document.getElementById('near-me-panel');
  const sortControlsWrap = document.getElementById('sort-controls-wrap');

  if (mode === 'near') {
    modeNearBtn.classList.add('active');
    modeCategoryBtn.classList.remove('active');
    categoryFilterSection.style.display = 'none';
    nearMePanel.style.display = 'block';
    if (sortControlsWrap) sortControlsWrap.style.display = 'none'; // Sorted by distance in near mode

    if (triggerGeo && (!nearUserLat || !nearUserLon)) {
      requestUserLocation(false);
    } else {
      fetchAndRenderPlaces();
    }
  } else {
    modeCategoryBtn.classList.add('active');
    modeNearBtn.classList.remove('active');
    categoryFilterSection.style.display = 'block';
    nearMePanel.style.display = 'none';
    if (sortControlsWrap) sortControlsWrap.style.display = 'flex';
    fetchAndRenderPlaces();
  }
}

function requestUserLocation(forcePrompt = false) {
  const statusText = document.getElementById('near-status-text');
  const coordsSubtext = document.getElementById('near-coords-subtext');

  if (!navigator.geolocation) {
    useDefaultLandmarkFallback('Geolocation is not supported by your browser. Defaulting to Old City, Jammu.');
    return;
  }

  updateNearStatusUI('📡 Contacting device GPS...', 'Requesting location permission to find nearest heritage sites...');

  navigator.geolocation.getCurrentPosition(
    (position) => {
      nearUserLat = position.coords.latitude;
      nearUserLon = position.coords.longitude;
      nearLocationLabel = 'Your Current Location';

      updateNearStatusUI(
        '📍 Near Your Current Location',
        `Live GPS: ${nearUserLat.toFixed(4)}° N, ${nearUserLon.toFixed(4)}° E (Sorted by proximity)`
      );
      updateNearPickerMarker(nearUserLat, nearUserLon);
      fetchAndRenderPlaces();
    },
    (err) => {
      console.warn('Geolocation error:', err);
      let reason = 'Location permission was denied or unavailable.';
      if (err.code === 1) reason = 'Location permission was denied by user.';
      else if (err.code === 2) reason = 'GPS position could not be acquired.';
      else if (err.code === 3) reason = 'Location request timed out.';

      useDefaultLandmarkFallback(`${reason} Selected Mubarak Mandi, Old City as starting reference point.`);
    },
    { timeout: 8000, enableHighAccuracy: true, maximumAge: 60000 }
  );
}

function useDefaultLandmarkFallback(message) {
  nearUserLat = 32.7308;
  nearUserLon = 74.8692;
  nearLocationLabel = 'Mubarak Mandi (Old City)';

  // Activate corresponding preset button
  const presetBtns = document.querySelectorAll('.near-preset-btn');
  presetBtns.forEach(b => {
    if (b.dataset.name && b.dataset.name.includes('Mubarak Mandi')) {
      b.classList.add('active');
    } else {
      b.classList.remove('active');
    }
  });

  updateNearStatusUI(`📍 Landmark: ${nearLocationLabel}`, message);
  updateNearPickerMarker(nearUserLat, nearUserLon);
  fetchAndRenderPlaces();
}

function updateNearStatusUI(title, subtitle) {
  const statusText = document.getElementById('near-status-text');
  const coordsSubtext = document.getElementById('near-coords-subtext');
  if (statusText) statusText.textContent = title;
  if (coordsSubtext) coordsSubtext.textContent = subtitle;
}

function initNearPickerMap() {
  const mapContainer = document.getElementById('near-picker-map');
  if (!mapContainer) return;

  const initialLat = nearUserLat || 32.7308;
  const initialLon = nearUserLon || 74.8692;

  if (!nearPickerMap) {
    nearPickerMap = L.map('near-picker-map', {
      center: [initialLat, initialLon],
      zoom: 12
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap',
      maxZoom: 18
    }).addTo(nearPickerMap);

    nearPickerMarker = L.marker([initialLat, initialLon], {
      draggable: true
    }).addTo(nearPickerMap);

    nearPickerMarker.bindPopup(`<strong>Reference Point</strong><br>${initialLat.toFixed(4)}, ${initialLon.toFixed(4)}`).openPopup();

    nearPickerMap.on('click', (e) => {
      const clickedLat = e.latlng.lat;
      const clickedLon = e.latlng.lng;
      setManualCoordinates(clickedLat, clickedLon, 'Pinned Point on Map');
    });

    nearPickerMarker.on('dragend', (e) => {
      const pos = e.target.getLatLng();
      setManualCoordinates(pos.lat, pos.lng, 'Pinned Point on Map');
    });
  } else {
    nearPickerMap.invalidateSize();
    nearPickerMap.setView([initialLat, initialLon], 12);
  }
}

function setManualCoordinates(lat, lon, label) {
  nearUserLat = lat;
  nearUserLon = lon;
  nearLocationLabel = label;

  // Clear active preset buttons
  document.querySelectorAll('.near-preset-btn').forEach(b => b.classList.remove('active'));

  updateNearStatusUI(`📍 Custom: ${label}`, `Point: ${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E`);
  updateNearPickerMarker(lat, lon);
  fetchAndRenderPlaces();
}

function updateNearPickerMarker(lat, lon) {
  if (nearPickerMap && nearPickerMarker) {
    nearPickerMarker.setLatLng([lat, lon]);
    nearPickerMarker.setPopupContent(`<strong>Reference Point</strong><br>${lat.toFixed(4)}, ${lon.toFixed(4)}`);
    nearPickerMap.panTo([lat, lon]);
  }
}

function updateUrlAndFetch() {
  const params = new URLSearchParams();
  if (currentMode === 'near') {
    params.set('near', '1');
    if (nearUserLat && nearUserLon) {
      params.set('lat', nearUserLat.toFixed(4));
      params.set('lon', nearUserLon.toFixed(4));
    }
    if (nearRadius) params.set('radius', nearRadius);
  } else {
    if (currentCategory) params.set('category', currentCategory);
    if (currentSort && currentSort !== 'name') params.set('sort', currentSort);
  }

  if (currentSearch) params.set('q', currentSearch);

  const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
  window.history.replaceState({}, '', newUrl);

  fetchAndRenderPlaces();
}

async function fetchAndRenderPlaces() {
  const container = document.getElementById('explore-cards-grid');
  const countSpan = document.getElementById('results-count');
  const subtextSpan = document.getElementById('results-subtext');
  if (!container) return;

  container.innerHTML = `
    <div style="grid-column: 1 / -1; padding: 4rem 1rem; text-align: center; color: var(--mauve);">
      <div style="font-size: 2rem; margin-bottom: 0.5rem; animation: pulse 1.5s infinite;">🏛️</div>
      <p style="font-family: var(--font-serif); font-size: 1.25rem;">
        ${currentMode === 'near' ? 'Calculating distances to nearby heritage sanctuaries...' : "Curating Jammu's hidden heritage..."}
      </p>
    </div>
  `;

  try {
    let url = '';
    const params = new URLSearchParams();

    if (currentMode === 'near') {
      const lat = nearUserLat || 32.7308;
      const lon = nearUserLon || 74.8692;
      params.set('lat', lat);
      params.set('lon', lon);
      if (nearRadius) params.set('radius', nearRadius);
      if (currentSearch) params.set('q', currentSearch);
      url = `/api/places/near?${params.toString()}`;
    } else {
      if (currentCategory) params.set('category', currentCategory);
      if (currentSearch) params.set('q', currentSearch);
      if (currentSort) params.set('sort', currentSort);
      url = `/api/places?${params.toString()}`;
    }

    const res = await fetch(url);
    const data = await res.json();
    const places = data.places || [];

    if (countSpan) {
      if (currentMode === 'near') {
        const radiusLabel = nearRadius ? `within ${nearRadius} km` : 'sorted by proximity';
        countSpan.textContent = `Found ${places.length} cultural ${places.length === 1 ? 'gem' : 'gems'} ${radiusLabel}`;
        if (subtextSpan) {
          subtextSpan.textContent = `📍 Measured from ${nearLocationLabel || 'your location'}`;
        }
      } else {
        countSpan.textContent = `Showing ${places.length} cultural ${places.length === 1 ? 'gem' : 'gems'}`;
        if (subtextSpan) {
          subtextSpan.textContent = '⚡ All entries verified with satellite coordinates & historical references';
        }
      }
    }

    if (places.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 4rem 2rem; text-align: center; background: var(--white); border-radius: var(--radius-md); border: var(--border-subtle);">
          <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔍</div>
          <h3 style="margin-bottom: 0.5rem;">No Forgotten Sanctuaries Found</h3>
          <p style="max-width: 440px; margin: 0 auto 1.5rem; color: #6F6270;">
            ${currentMode === 'near' && nearRadius
              ? `No heritage sites found within ${nearRadius} km of your location. Try expanding the radius to 10 km or 25 km.`
              : `We could not find places matching "${currentSearch}". Try searching for forts, kalari, bazaar, or temples.`}
          </p>
          <button class="btn btn-secondary btn-sm" onclick="resetExploreFilters()">
            ${currentMode === 'near' ? 'Show All Distances' : 'Reset All Filters'}
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = places.map(p => `
      <article class="place-card">
        <div class="card-media">
          <img src="${p.image_url}" alt="${p.name}" class="card-img" loading="lazy" onerror="this.onerror=null;this.src='/static/images/fallback-heritage.svg';">
          <span class="badge badge-mauve card-badge-top">${p.category}</span>
          ${currentMode === 'near' && p.distance_formatted ? `
            <span class="badge badge-pink" style="position: absolute; bottom: 0.8rem; left: 0.8rem; z-index: 2; font-weight: 700; box-shadow: 0 2px 6px rgba(0,0,0,0.25);">
              📍 ${p.distance_formatted} away
            </span>
          ` : `
            <span class="card-duration-badge">⏱️ ${p.visit_duration_label || '1.5 hours'}</span>
          `}
          ${currentMode === 'near' ? `
            <span class="card-duration-badge">⏱️ ${p.visit_duration_label || '1.5 hrs'}</span>
          ` : ''}
        </div>
        <div class="card-body">
          <div class="card-location">
            <span>📍</span>
            <span>${p.location}</span>
          </div>
          <h3 class="card-title">${p.name}</h3>
          <p class="card-desc">${p.short_desc}</p>
          <div class="card-footer">
            <a href="/places/${p.slug}" class="btn btn-primary btn-sm">View Details</a>
            <button class="card-add-btn" data-place-id="${p.id}" data-place-name="${p.name}">
              + Add to Trip
            </button>
          </div>
        </div>
      </article>
    `).join('');

  } catch (err) {
    console.error('Failed to load places:', err);
    container.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 3rem; text-align: center; color: var(--deep-plum);">
        <p>Could not retrieve place records from database. Please reload the page.</p>
      </div>
    `;
  }
}

function resetExploreFilters() {
  if (currentMode === 'near') {
    nearRadius = '';
    const radiusBtns = document.querySelectorAll('.near-radius-btn');
    radiusBtns.forEach(b => {
      if (!b.dataset.radius) b.classList.add('active');
      else b.classList.remove('active');
    });
  } else {
    currentCategory = '';
    currentSearch = '';
    currentSort = 'name';

    const searchInput = document.getElementById('explore-search');
    if (searchInput) searchInput.value = '';

    const filterTabs = document.querySelectorAll('#category-filter-section .filter-tab');
    filterTabs.forEach(t => {
      if (!t.dataset.category) t.classList.add('active');
      else t.classList.remove('active');
    });
  }

  updateUrlAndFetch();
}
