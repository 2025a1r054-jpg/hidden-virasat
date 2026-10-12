# HIDDEN VIRASAT — Discover the Soul of Jammu

> **"Beyond the Famous. Into the Forgotten."**  
> *A College AI Capstone & Cultural Web Systems Project*

**Hidden Virasat** is a digital tourism platform and cultural archive dedicated to cataloging and celebrating the lesser-known Dogra heritage, ancient sandstone forts, living artisan guilds, sacred cave shrines, and traditional culinary ways of Jammu (Duggar Pradesh).

---

## 🏛️ Brand Identity & Aesthetics

- **Mauve:** `#8D718A` — Primary brand identity & accents
- **Dusty Pink:** `#D6A3B0` — Badges, warm highlights & micro-accents
- **Soft Grey:** `#E9E5E7` — Neutral borders & subtle dividers
- **Warm Ivory:** `#FAF7F5` — Page background & editorial canvas
- **Deep Plum Text:** `#382F39` — High-contrast typography

### Visual Style
Styled as a cultural travel journal with a modern editorial aesthetic. Features authentic Jammu heritage photography, serif typography (`Cormorant Garamond`), crisp modern body text (`Plus Jakarta Sans`), rounded cards with delicate shadows, and responsive layouts across desktop, tablet, and mobile.

---

## 🌟 Key Features

1. **Editorial Home Page (`/`)**:
   - Hero header with authentic Jammu heritage imagery and search bar.
   - Live meteorological conditions banner powered by the Open-Meteo satellite feed.
   - Quick statistics ribbon (3,000+ years of lore, 15 curated gems, 6 cultural dimensions).
   - "Featured Hidden Gems" directory cards with quick "Add to Trip" buttons.
   - "Stories Carved in Time" chronicle preview.
   - Cultural spotlights: Basohli Miniatures, Kalari Cheese, Dogra Calico Printing, and Chhota Kashi.
   - Interactive Leaflet mini-map preview.

2. **Explore Directory (`/explore`)**:
   - Filterable catalog of 15 curated Jammu landmarks across 6 distinct categories:
     1. *Heritage & Forts*
     2. *Temples & Spiritual Heritage*
     3. *Museums & Art*
     4. *Local Markets*
     5. *Traditional Crafts*
     6. *Nature & Cultural Experiences*
   - Real-time client search with debouncing.
   - Duration sorting (Shortest first, Longest first, Alphabetical).
   - Dynamic URL state synchronization (`?category=...&q=...`).

3. **Place Details Page (`/places/<slug>`)**:
   - Dynamic, data-driven route loaded from SQLite.
   - High-resolution cover photograph with source attribution and license details.
   - Detailed history, cultural significance, and lesser-known historical arcana.
   - Things to see, best visiting season, and visitor accessibility notes.
   - Live location-specific weather conditions for the exact coordinates.
   - Embedded Leaflet location map with one-click Google Maps / OpenStreetMap directions.
   - Nearby recommended heritage sites calculated using the Haversine formula.

4. **Interactive Map (`/map`)**:
   - Fullscreen Leaflet.js cartography with OpenStreetMap tiles.
   - Custom SVG map markers color-coded by cultural category.
   - Interactive popups featuring photos, category tags, snippets, detail links, and directions.
   - Floating category filter pills.
   - Synchronized sidebar list: clicking any place automatically pans the map and opens the popup.
   - "Fit All Markers" auto-boundary control.

5. **Personalized Trip Planner (`/planner`)**:
   - User customizable parameters: Duration (1, 2, or 3 days), Travel Pace (Relaxed, Balanced, Packed), Base Hub (Old City, Bahu Fort, Railway Station), and Cultural Interests (Heritage, Spirituality, Food, Shopping, Crafts, Nature).
   - **Transparent Recommendation Algorithm**: Groups places geographically to minimize crisscrossing travel, assigns realistic time slots (Morning, Midday, Afternoon, Evening), and calculates route distances.
   - Displays clear match reasons (*"Matched because: Renowned Dogra heritage landmark..."*).
   - Route map preview plotting stops with sequential day numbers.
   - Interactive controls: remove individual stops, recalculate distances, or regenerate plan.
   - **Persistent SQLite Trip Storage**: Save customized itineraries (`POST /api/trips`), view saved trips (`GET /api/trips`), reload past plans, and delete itineraries (`DELETE /api/trips/<id>`).

6. **Local Stories Journal (`/stories`)**:
   - Editorial articles detailing Dogra history and living traditions:
     - *The Legend of Jamboo Lochan (Peace on the Tawi)*
     - *The Forgotten Splendor of Mubarak Mandi (150 Years of Royal Architecture)*
     - *The Secret World of Basohli Miniatures (Beetle-Wing Emeralds)*
     - *From Kalari to Rajma (The Soulful Food Traditions of Duggar)*
     - *Purmandal: The Sacred Chhota Kashi & The Underground Devika*
     - *Carving the Paisley (Revival of Dogra Calico Printing)*
   - Formal bibliographical sources and citations (*Gulabnama*, Archaeological Survey of India, *Jammu Gazetteer*).

7. **Live Weather (`/api/weather`)**:
   - Real-time integration with Open-Meteo Public API (free, no paid key required).
   - Server-side in-memory caching (10-minute TTL) to optimize external network requests.
   - Reports temperature (°C), apparent temperature, humidity, wind velocity, and local weather condition descriptions.
   - Graceful offline/error state handling with manual retry.

8. **About Page (`/about`)**:
   - Educational mission: Promoting Jammu beyond its transit hub perception.
   - Transparent walkthrough of the multi-factor recommendation algorithm.
   - Project scope, limitations, and future roadmap.
   - Full citation table for open data sources.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.11+ / Flask 3.1+
- **Database:** SQLite 3 (stored locally in `instance/hidden_virasat.db`)
- **Photographic Assets:** 15 verified, high-resolution Jammu heritage photographs stored locally in `static/images/` for 100% reliable, zero-latency local presentations without Wikimedia rate-limiting or CORS issues.
- **Frontend:** Semantic HTML5, CSS3 Custom Properties (Design System), Vanilla JavaScript (ES6+)
- **Mapping:** Leaflet.js 1.9.4 with OpenStreetMap Tiles
- **Weather:** Open-Meteo High-Resolution Forecast API
- **External Dependencies:** Only `Flask` and `requests` (no Node.js backend, no Docker, no heavy frameworks)

---

## 🚀 Windows Setup & Run Guide

### 1. Prerequisites
- Windows 10 or 11
- Python 3.10+ installed and available in PATH (verify with `python --version`)

### 2. Open PowerShell or Command Prompt in the Project Folder
```powershell
cd "c:\Users\mahan\OneDrive\Desktop\Hidden Virasat"
```

### 3. Install Minimal Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Initialize Database (Optional, app does this automatically on boot)
```powershell
python database/db.py
```

### 5. Run the Automated Test Suite
```powershell
python -m unittest tests/test_app.py
```
*All 9 test cases should pass with `OK`.*

### 6. Start the Flask Web Application
```powershell
python app.py
```

### 7. Access in Your Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🌐 Deploying to Render (Public Cloud Deployment)

### 1. Build & Start Commands
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

### 2. Deployment Steps via GitHub
1. **Push to GitHub**:
   - Initialize git (or use GitHub Desktop) in `c:\Users\mahan\OneDrive\Desktop\Hidden Virasat`.
   - Commit all project files (`.gitignore` protects virtualenvs and cache).
   - Push to a new GitHub repository (e.g., `hidden-virasat`).

2. **Create Web Service on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com).
   - Click **New +** > **Web Service**.
   - Connect your GitHub repository `hidden-virasat`.

3. **Configure Settings**:
   - **Name:** `hidden-virasat`
   - **Region:** Any (e.g., Singapore or Oregon)
   - **Branch:** `main` (or `master`)
   - **Root Directory:** *(leave blank for repository root)*
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`

4. **Environment Variables**:
   Add the following in the **Environment** tab:
   - `PYTHON_VERSION`: `3.11.7`
   - `SECRET_KEY`: *(click Generate or enter a secret phrase)*
   - `FLASK_DEBUG`: `0`

5. **Deploy**:
   - Click **Deploy Web Service**.
   - Render will run `pip install -r requirements.txt`, start Gunicorn, and allocate a live URL like `https://hidden-virasat.onrender.com`.

---

## 📋 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/places` | List places with optional `?category=`, `?q=`, and `?sort=` parameters |
| `GET` | `/api/places/<slug_or_id>` | Detailed record for a single landmark |
| `GET` | `/api/stories` | List all curated editorial stories |
| `GET` | `/api/weather?lat=...&lon=...` | Live weather with caching and fallbacks |
| `POST` | `/api/recommend-itinerary` | Generates a day-wise itinerary matching user interests and pace |
| `POST` | `/api/trips` | Saves a customized itinerary into SQLite |
| `GET` | `/api/trips` | Retrieves all saved itineraries |
| `GET` | `/api/trips/<id>` | Retrieves a specific saved itinerary |
| `DELETE` | `/api/trips/<id>` | Deletes a saved itinerary from SQLite |

---

## 🎓 Academic Notice
This project is developed as an educational capstone prototype demonstrating intelligent travel recommendation systems and cultural GIS mapping. It is not an official government tourism portal.
