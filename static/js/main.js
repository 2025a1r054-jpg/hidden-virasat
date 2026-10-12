/**
 * HIDDEN VIRASAT — Discover the Soul of Jammu
 * Main JavaScript: Mobile navigation, image fallback handling, notifications, and quick trip helpers.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const mobileBtn = document.querySelector('.mobile-menu-btn');
  const navLinks = document.querySelector('.nav-links');

  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener('click', () => {
      navLinks.classList.toggle('mobile-open');
      const isOpen = navLinks.classList.contains('mobile-open');
      mobileBtn.setAttribute('aria-expanded', isOpen);
    });
  }

  // 2. Global Image Fallback Handler
  document.querySelectorAll('img').forEach(img => {
    img.addEventListener('error', function () {
      if (!this.getAttribute('data-fallback-tried')) {
        this.setAttribute('data-fallback-tried', 'true');
        this.src = '/static/images/fallback-heritage.svg';
      }
    });
  });

  // 3. Quick Add to Trip Handler across cards
  document.addEventListener('click', (e) => {
    const addBtn = e.target.closest('.card-add-btn');
    if (addBtn) {
      e.preventDefault();
      const placeId = addBtn.dataset.placeId;
      const placeName = addBtn.dataset.placeName || 'Heritage Site';
      addPlaceToTripBasket(placeId, placeName);
    }
  });
});

/**
 * Toast Notification System
 */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(12px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/**
 * Quick Add Place to local storage trip basket
 */
function addPlaceToTripBasket(placeId, placeName) {
  try {
    let basket = JSON.parse(localStorage.getItem('hv_trip_basket') || '[]');
    if (!basket.includes(placeId)) {
      basket.push(placeId);
      localStorage.setItem('hv_trip_basket', JSON.stringify(basket));
      showToast(`Added "${placeName}" to your journey planner!`, 'success');
    } else {
      showToast(`"${placeName}" is already in your journey basket.`, 'info');
    }
  } catch (err) {
    console.error('Storage error:', err);
    showToast(`Added "${placeName}" to plan!`, 'success');
  }
}
