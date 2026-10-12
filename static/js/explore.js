/**
 * HIDDEN VIRASAT — Explore Discovery Directory
 * Live category filtering, instant search, and duration sorting.
 */

let currentCategory = '';
let currentSearch = '';
let currentSort = 'name';
let searchDebounceTimer = null;

document.addEventListener('DOMContentLoaded', () => {
  const filterTabs = document.querySelectorAll('.filter-tab');
  const searchInput = document.getElementById('explore-search');
  const sortSelect = document.getElementById('explore-sort');

  // Read initial URL params
  const urlParams = new URLSearchParams(window.location.search);
  currentCategory = urlParams.get('category') || '';
  currentSearch = urlParams.get('q') || '';
  currentSort = urlParams.get('sort') || 'name';

  if (searchInput && currentSearch) {
    searchInput.value = currentSearch;
  }
  if (sortSelect && currentSort) {
    sortSelect.value = currentSort;
  }

  // Bind category tabs
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

  // Bind search input with debounce
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        currentSearch = e.target.value.trim();
        updateUrlAndFetch();
      }, 250);
    });
  }

  // Bind sort select
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      currentSort = e.target.value;
      updateUrlAndFetch();
    });
  }

  // Initial fetch
  fetchAndRenderPlaces();
});

function updateUrlAndFetch() {
  const params = new URLSearchParams();
  if (currentCategory) params.set('category', currentCategory);
  if (currentSearch) params.set('q', currentSearch);
  if (currentSort && currentSort !== 'name') params.set('sort', currentSort);

  const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
  window.history.replaceState({}, '', newUrl);

  fetchAndRenderPlaces();
}

async function fetchAndRenderPlaces() {
  const container = document.getElementById('explore-cards-grid');
  const countSpan = document.getElementById('results-count');
  if (!container) return;

  container.innerHTML = `
    <div style="grid-column: 1 / -1; padding: 4rem 1rem; text-align: center; color: var(--mauve);">
      <div style="font-size: 2rem; margin-bottom: 0.5rem; animation: pulse 1.5s infinite;">🏛️</div>
      <p style="font-family: var(--font-serif); font-size: 1.25rem;">Curating Jammu's hidden heritage...</p>
    </div>
  `;

  try {
    const params = new URLSearchParams();
    if (currentCategory) params.set('category', currentCategory);
    if (currentSearch) params.set('q', currentSearch);
    if (currentSort) params.set('sort', currentSort);

    const res = await fetch(`/api/places?${params.toString()}`);
    const data = await res.json();
    const places = data.places || [];

    if (countSpan) {
      countSpan.textContent = `Showing ${places.length} cultural ${places.length === 1 ? 'gem' : 'gems'}`;
    }

    if (places.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 4rem 2rem; text-align: center; background: var(--white); border-radius: var(--radius-md); border: var(--border-subtle);">
          <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔍</div>
          <h3 style="margin-bottom: 0.5rem;">No Forgotten Sanctuaries Found</h3>
          <p style="max-width: 440px; margin: 0 auto 1.5rem; color: #6F6270;">We could not find places matching "${currentSearch}". Try searching for forts, kalari, bazaar, or temples.</p>
          <button class="btn btn-secondary btn-sm" onclick="resetExploreFilters()">Reset All Filters</button>
        </div>
      `;
      return;
    }

    container.innerHTML = places.map(p => `
      <article class="place-card">
        <div class="card-media">
          <img src="${p.image_url}" alt="${p.name}" class="card-img" loading="lazy" onerror="this.onerror=null;this.src='/static/images/fallback-heritage.svg';">
          <span class="badge badge-mauve card-badge-top">${p.category}</span>
          <span class="card-duration-badge">⏱️ ${p.visit_duration_label}</span>
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
  currentCategory = '';
  currentSearch = '';
  currentSort = 'name';

  const searchInput = document.getElementById('explore-search');
  if (searchInput) searchInput.value = '';

  const filterTabs = document.querySelectorAll('.filter-tab');
  filterTabs.forEach(t => {
    if (!t.dataset.category) t.classList.add('active');
    else t.classList.remove('active');
  });

  updateUrlAndFetch();
}
