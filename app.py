"""
HIDDEN VIRASAT — Discover the Soul of Jammu
Flask Web Application & REST API
"""

import os
import sys
import json
import math
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, abort

# Ensure local imports work
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.db import get_db_connection, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "hidden-virasat-jammu-heritage-key-2026")

# Ensure database exists on boot
init_db(seed=True)

# ---------------------------------------------------------------------------
# Weather cache & WMO Weather Code Mapper
# ---------------------------------------------------------------------------
WEATHER_CACHE = {}  # key: (lat_round, lon_round), value: (timestamp, data)
WEATHER_CACHE_TTL = 600  # 10 minutes

WMO_WEATHER_CODES = {
    0: ("Clear Sky", "sunny", "Clear sunny skies across Jammu"),
    1: ("Mainly Clear", "partly-cloudy", "Pleasant, mostly clear skies"),
    2: ("Partly Cloudy", "cloudy", "Scattered clouds over the Tawi valley"),
    3: ("Overcast", "cloudy", "Overcast skies across the foothills"),
    45: ("Foggy", "fog", "Misty fog along the river basin"),
    48: ("Depositing Rime Fog", "fog", "Chilly morning frost/fog"),
    51: ("Light Drizzle", "drizzle", "Gentle passing drizzle"),
    53: ("Moderate Drizzle", "drizzle", "Consistent light drizzle"),
    55: ("Dense Drizzle", "rain", "Misty hill drizzle"),
    61: ("Slight Rain", "rain", "Light rain showers"),
    63: ("Moderate Rain", "rain", "Moderate rainfall"),
    65: ("Heavy Rain", "heavy-rain", "Heavy rain showers"),
    71: ("Slight Snow", "snow", "Flurries in surrounding heights"),
    73: ("Moderate Snow", "snow", "Snowfall on nearby peaks"),
    75: ("Heavy Snow", "snow", "Heavy snow on higher Pir Panjal"),
    80: ("Brief Showers", "rain", "Passing rain showers"),
    81: ("Moderate Showers", "rain", "Moderate showers"),
    82: ("Violent Showers", "heavy-rain", "Sudden heavy showers"),
    95: ("Thunderstorm", "thunderstorm", "Thunderstorms over the Shivalik hills"),
    96: ("Thunderstorm with Hail", "thunderstorm", "Thunderstorm and hail"),
}


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between two GPS coordinates in kilometers."""
    r = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 2)


# ---------------------------------------------------------------------------
# Template Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    """Homepage: Hero, search, featured gems, stories preview, culture highlights."""
    conn = get_db_connection()
    featured_places = conn.execute(
        "SELECT * FROM places WHERE featured = 1 ORDER BY id ASC LIMIT 6"
    ).fetchall()
    
    stories = conn.execute(
        "SELECT * FROM stories ORDER BY id ASC LIMIT 3"
    ).fetchall()
    
    conn.close()
    return render_template(
        "index.html",
        featured_places=featured_places,
        stories=stories
    )


@app.route("/explore")
def explore():
    """Explore Discovery Directory: search, category filters, sorting."""
    category_filter = request.args.get("category", "").strip()
    search_query = request.args.get("q", "").strip()
    
    conn = get_db_connection()
    categories_rows = conn.execute(
        "SELECT DISTINCT category FROM places ORDER BY category ASC"
    ).fetchall()
    categories = [r["category"] for r in categories_rows]
    conn.close()
    
    return render_template(
        "explore.html",
        categories=categories,
        initial_category=category_filter,
        initial_search=search_query
    )


@app.route("/places/<slug_or_id>")
def place_detail(slug_or_id):
    """Dynamic place details page."""
    conn = get_db_connection()
    if slug_or_id.isdigit():
        place = conn.execute("SELECT * FROM places WHERE id = ?", (int(slug_or_id),)).fetchone()
    else:
        place = conn.execute("SELECT * FROM places WHERE slug = ?", (slug_or_id,)).fetchone()
        
    if not place:
        conn.close()
        abort(404)
        
    # Find nearby places (within same category or nearest coordinates)
    all_others = conn.execute(
        "SELECT id, slug, name, category, location, latitude, longitude, image_url, short_desc, visit_duration_label "
        "FROM places WHERE id != ? ORDER BY id ASC",
        (place["id"],)
    ).fetchall()
    
    nearby_with_dist = []
    for other in all_others:
        dist = haversine_distance_km(place["latitude"], place["longitude"], other["latitude"], other["longitude"])
        item = dict(other)
        item["distance_km"] = dist
        nearby_with_dist.append(item)
        
    # Sort by geographic distance, take top 3
    nearby_with_dist.sort(key=lambda x: x["distance_km"])
    nearby_places = nearby_with_dist[:3]
    
    # Parse tags
    tags = []
    try:
        tags = json.loads(place["tags"])
    except Exception:
        tags = []
        
    conn.close()
    return render_template(
        "place.html",
        place=place,
        nearby_places=nearby_places,
        tags=tags
    )


@app.route("/map")
def interactive_map():
    """Full-featured interactive Leaflet map."""
    conn = get_db_connection()
    places = conn.execute(
        "SELECT id, slug, name, category, location, latitude, longitude, image_url, short_desc, visit_duration_label "
        "FROM places ORDER BY name ASC"
    ).fetchall()
    categories_rows = conn.execute("SELECT DISTINCT category FROM places ORDER BY category ASC").fetchall()
    categories = [r["category"] for r in categories_rows]
    conn.close()
    
    return render_template(
        "map.html",
        places=places,
        categories=categories
    )


@app.route("/planner")
def planner():
    """Personalized Trip Planner."""
    return render_template("planner.html")


@app.route("/stories")
def stories():
    """Editorial Local Stories journal."""
    conn = get_db_connection()
    stories_list = conn.execute("SELECT * FROM stories ORDER BY id ASC").fetchall()
    conn.close()
    return render_template("stories.html", stories=stories_list)


@app.route("/about")
def about():
    """About Hidden Virasat: Mission, Dogra heritage, recommendation logic, disclaimer."""
    return render_template("about.html")


# ---------------------------------------------------------------------------
# REST API Endpoints
# ---------------------------------------------------------------------------

@app.route("/api/places", methods=["GET"])
def api_get_places():
    """Returns list of curated places with optional filtering and search."""
    q = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip()
    sort_by = request.args.get("sort", "name")
    featured_only = request.args.get("featured", "").lower() in ("1", "true", "yes")

    conn = get_db_connection()
    query = "SELECT * FROM places WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if featured_only:
        query += " AND featured = 1"

    if q:
        query += " AND (LOWER(name) LIKE ? OR LOWER(short_desc) LIKE ? OR LOWER(location) LIKE ? OR LOWER(tags) LIKE ?)"
        wildcard = f"%{q}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])

    if sort_by == "duration_asc":
        query += " ORDER BY visit_duration_minutes ASC"
    elif sort_by == "duration_desc":
        query += " ORDER BY visit_duration_minutes DESC"
    else:
        query += " ORDER BY name ASC"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    places = []
    for r in rows:
        item = dict(r)
        try:
            item["tags"] = json.loads(item["tags"])
        except Exception:
            item["tags"] = []
        places.append(item)

    return jsonify({"count": len(places), "places": places})


@app.route("/api/places/<slug_or_id>", methods=["GET"])
def api_get_place(slug_or_id):
    """Returns detailed information for a single place."""
    conn = get_db_connection()
    if slug_or_id.isdigit():
        row = conn.execute("SELECT * FROM places WHERE id = ?", (int(slug_or_id),)).fetchone()
    else:
        row = conn.execute("SELECT * FROM places WHERE slug = ?", (slug_or_id,)).fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Place not found"}), 404

    place = dict(row)
    try:
        place["tags"] = json.loads(place["tags"])
    except Exception:
        place["tags"] = []

    conn.close()
    return jsonify(place)


@app.route("/api/stories", methods=["GET"])
def api_get_stories():
    """Returns all curated local stories."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM stories ORDER BY id ASC").fetchall()
    conn.close()

    stories_data = []
    for r in rows:
        item = dict(r)
        try:
            item["related_place_slugs"] = json.loads(item["related_place_slugs"])
        except Exception:
            item["related_place_slugs"] = []
        stories_data.append(item)

    return jsonify({"count": len(stories_data), "stories": stories_data})


@app.route("/api/weather", methods=["GET"])
def api_get_weather():
    """
    Fetches real-time weather from Open-Meteo with caching and error fallbacks.
    Default coords: Jammu (32.7266, 74.8570)
    """
    try:
        lat = float(request.args.get("lat", 32.7266))
        lon = float(request.args.get("lon", 74.8570))
    except (ValueError, TypeError):
        lat = 32.7266
        lon = 74.8570

    # Round for cache key
    cache_key = (round(lat, 3), round(lon, 3))
    now = time.time()

    if cache_key in WEATHER_CACHE:
        cached_time, cached_data = WEATHER_CACHE[cache_key]
        if now - cached_time < WEATHER_CACHE_TTL:
            cached_data["cached"] = True
            return jsonify(cached_data)

    # Fetch live weather from Open-Meteo (No API key needed)
    import requests
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,weather_code,wind_speed_10m",
        "timezone": "Asia/Kolkata"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        code = current.get("weather_code", 0)
        desc, icon, local_note = WMO_WEATHER_CODES.get(
            code, ("Pleasant", "partly-cloudy", "Fair weather in Jammu region")
        )

        weather_result = {
            "status": "success",
            "location_name": "Jammu & Surrounds",
            "latitude": lat,
            "longitude": lon,
            "temperature": current.get("temperature_2m"),
            "apparent_temperature": current.get("apparent_temperature"),
            "relative_humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": code,
            "condition": desc,
            "condition_note": local_note,
            "icon": icon,
            "is_day": current.get("is_day", 1),
            "units": {
                "temperature": "°C",
                "relative_humidity": "%",
                "wind_speed": "km/h"
            },
            "timestamp": current.get("time", time.strftime("%Y-%m-%d %H:%M")),
            "cached": False,
            "source": "Open-Meteo Public API"
        }

        WEATHER_CACHE[cache_key] = (now, weather_result)
        return jsonify(weather_result)

    except Exception as e:
        # Graceful fallback error state
        return jsonify({
            "status": "unavailable",
            "error": "Live weather service temporarily unreachable",
            "message": "Unable to connect to Open-Meteo satellite feed. Please check your internet connection.",
            "latitude": lat,
            "longitude": lon,
            "fallback_info": {
                "climate_note": "Jammu experiences warm pleasant autumns (Oct-Nov), crisp winters (Dec-Feb), and sunny springs (Mar-Apr)."
            }
        }), 200  # Return 200 with status=unavailable for graceful frontend rendering


@app.route("/api/recommend-itinerary", methods=["POST"])
def api_recommend_itinerary():
    """
    Transparent, heuristic itinerary recommendation engine.
    Filters places by user interests, duration (1, 2, or 3 days),
    pacing (relaxed, balanced, packed), and starting area.
    Calculates geographic clustering and realistic travel routes.
    """
    data = request.get_json() or {}
    days = int(data.get("duration_days", 2))
    days = max(1, min(3, days))  # Bound between 1 and 3

    user_interests = [i.lower() for i in data.get("interests", ["heritage", "spirituality", "food"])]
    pace = data.get("pace", "balanced").lower()
    start_area = data.get("start_area", "old-city")

    # Places per day based on pace
    places_per_day = {
        "relaxed": 2,
        "balanced": 3,
        "packed": 4
    }.get(pace, 3)

    target_total_places = days * places_per_day

    conn = get_db_connection()
    all_places_rows = conn.execute("SELECT * FROM places").fetchall()
    conn.close()

    places = []
    for r in all_places_rows:
        item = dict(r)
        try:
            item["tags"] = json.loads(item["tags"])
        except Exception:
            item["tags"] = []
        places.append(item)

    # Reference coordinates for start areas
    area_coords = {
        "old-city": (32.7272, 74.8617),   # Raghunath Chowk / Old Jammu
        "bahu-fort": (32.7297, 74.8839),  # Bahu Plateau
        "railway": (32.7050, 74.8700),    # Jammu Tawi Station
        "any": (32.7266, 74.8570)
    }
    origin_lat, origin_lon = area_coords.get(start_area, area_coords["old-city"])

    # Score each place based on:
    # 1. Interest relevance
    # 2. Category mapping
    # 3. Proximity to start origin
    scored_places = []
    for p in places:
        score = 0
        reasons = []
        p_cat = p["category"].lower()
        p_tags = [t.lower() for t in p["tags"]]

        # Interest matching
        if "heritage" in user_interests and "heritage" in p_cat:
            score += 4
            reasons.append("Renowned Dogra heritage landmark")
        if "spirituality" in user_interests and ("temple" in p_cat or "spiritual" in p_cat or "spiritual" in p_tags):
            score += 4
            reasons.append("Sacred spiritual sanctuary")
        if "shopping" in user_interests and "market" in p_cat:
            score += 4
            reasons.append("Authentic local trade and shopping")
        if "crafts" in user_interests and ("craft" in p_cat or "crafts" in p_tags or "textiles" in p_tags):
            score += 4
            reasons.append("Living artisan and craft heritage")
        if "food" in user_interests and ("food" in p_tags or "culinary" in p_tags or "kalari" in p_tags):
            score += 4
            reasons.append("Traditional Duggar culinary experience")
        if "nature" in user_interests and ("nature" in p_cat or "gardens" in p_tags or "sunset" in p_tags):
            score += 4
            reasons.append("Scenic natural landscape and riverfront")

        # Proximity score (closer = higher score, max distance bonus 3)
        dist_from_origin = haversine_distance_km(origin_lat, origin_lon, p["latitude"], p["longitude"])
        if dist_from_origin < 5.0:
            score += 3
            reasons.append("Conveniently close to your starting point")
        elif dist_from_origin < 15.0:
            score += 2
        else:
            score += 1
            if dist_from_origin > 30.0:
                reasons.append("Scenic excursion into Jammu provincial landscapes")

        if p["featured"] == 1:
            score += 1

        if not reasons:
            reasons.append(f"Essential {p['category']} highlight of Jammu")

        scored_places.append({
            "place": p,
            "score": score,
            "match_reason": " • ".join(reasons[:2]),
            "dist_origin": dist_from_origin
        })

    # Sort candidates by score descending, then proximity
    scored_places.sort(key=lambda x: (-x["score"], x["dist_origin"]))

    # Select top candidates, ensuring category diversity
    selected_candidates = []
    seen_categories = {}
    
    # First pass: pick best from diverse categories
    for sp in scored_places:
        cat = sp["place"]["category"]
        if seen_categories.get(cat, 0) < 2 and len(selected_candidates) < target_total_places:
            selected_candidates.append(sp)
            seen_categories[cat] = seen_categories.get(cat, 0) + 1

    # Second pass: fill remaining slots
    for sp in scored_places:
        if len(selected_candidates) >= target_total_places:
            break
        if sp not in selected_candidates:
            selected_candidates.append(sp)

    # Distribute selected places across days using geographic clustering
    # Day 1: Closer / Old City / Heritage
    # Day 2: Bahu / Riverfront / Cultural
    # Day 3: Outskirts / Excursions (Purmandal, Akhnoor, or Krimchi)
    selected_candidates.sort(key=lambda x: x["dist_origin"])

    day_slots = [
        {"time": "09:30 AM", "label": "Morning Exploration"},
        {"time": "12:30 PM", "label": "Midday Heritage & Lunch"},
        {"time": "03:30 PM", "label": "Afternoon Walk"},
        {"time": "06:00 PM", "label": "Evening Golden Hour"}
    ]

    itinerary_days = []
    chunk_size = math.ceil(len(selected_candidates) / days)

    for d in range(days):
        day_items = selected_candidates[d * chunk_size : (d + 1) * chunk_size]
        day_stops = []
        prev_lat, prev_lon = origin_lat, origin_lon
        total_day_dist = 0.0

        for idx, item in enumerate(day_items):
            p = item["place"]
            step_dist = haversine_distance_km(prev_lat, prev_lon, p["latitude"], p["longitude"])
            total_day_dist += step_dist
            slot_info = day_slots[min(idx, len(day_slots) - 1)]

            day_stops.append({
                "time_slot": slot_info["time"],
                "slot_label": slot_info["label"],
                "place_id": p["id"],
                "slug": p["slug"],
                "name": p["name"],
                "category": p["category"],
                "location": p["location"],
                "latitude": p["latitude"],
                "longitude": p["longitude"],
                "image_url": p["image_url"],
                "visit_duration_label": p["visit_duration_label"],
                "match_reason": item["match_reason"],
                "travel_from_prev_km": step_dist
            })
            prev_lat, prev_lon = p["latitude"], p["longitude"]

        itinerary_days.append({
            "day_number": d + 1,
            "title": f"Day {d + 1}: " + ("Dogra Heritage & Old City" if d == 0 else "Riverfront & Living Culture" if d == 1 else "Provincial Vistas & Sacred Sites"),
            "approx_travel_distance_km": round(total_day_dist, 1),
            "stops": day_stops
        })

    return jsonify({
        "success": True,
        "parameters": {
            "duration_days": days,
            "pace": pace,
            "interests": user_interests,
            "start_area": start_area
        },
        "days": itinerary_days
    })


@app.route("/api/trips", methods=["POST"])
def api_save_trip():
    """Saves a customized user trip itinerary into SQLite."""
    data = request.get_json() or {}
    title = data.get("title", "").strip() or "My Jammu Virasat Journey"
    traveler_name = data.get("traveler_name", "").strip() or "Dogra Explorer"
    duration_days = int(data.get("duration_days", 1))
    pace = data.get("pace", "balanced")
    interests = json.dumps(data.get("interests", []))
    start_area = data.get("start_area", "old-city")
    itinerary = data.get("itinerary", [])

    if not itinerary:
        return jsonify({"error": "Itinerary cannot be empty"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO saved_trips (
            title, traveler_name, duration_days, pace, interests, start_area, itinerary_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        traveler_name,
        duration_days,
        pace,
        interests,
        start_area,
        json.dumps(itinerary)
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "success": True,
        "message": "Trip successfully saved to your cultural journal",
        "trip_id": new_id
    }), 201


@app.route("/api/trips", methods=["GET"])
def api_get_saved_trips():
    """Retrieves all saved trips from SQLite."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM saved_trips ORDER BY created_at DESC").fetchall()
    conn.close()

    trips = []
    for r in rows:
        item = dict(r)
        try:
            item["interests"] = json.loads(item["interests"])
        except Exception:
            item["interests"] = []
        try:
            item["itinerary"] = json.loads(item["itinerary_json"])
        except Exception:
            item["itinerary"] = []
        del item["itinerary_json"]
        trips.append(item)

    return jsonify({"count": len(trips), "trips": trips})


@app.route("/api/trips/<int:trip_id>", methods=["GET"])
def api_get_single_trip(trip_id):
    """Retrieves a single saved trip by ID."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM saved_trips WHERE id = ?", (trip_id,)).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Trip not found"}), 404

    item = dict(row)
    try:
        item["interests"] = json.loads(item["interests"])
    except Exception:
        item["interests"] = []
    try:
        item["itinerary"] = json.loads(item["itinerary_json"])
    except Exception:
        item["itinerary"] = []
    del item["itinerary_json"]

    return jsonify(item)


@app.route("/api/trips/<int:trip_id>", methods=["DELETE"])
def api_delete_trip(trip_id):
    """Deletes a saved trip from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_trips WHERE id = ?", (trip_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Trip not found"}), 404

    return jsonify({"success": True, "message": "Trip deleted successfully"})


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", error_title="404 - Sanctuary Not Found",
                           error_message="The heritage corridor you are looking for does not exist in our archives. Perhaps it remains waiting to be rediscovered."), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", error_title="500 - Archival Interruption",
                           error_message="A quiet disturbance in the archives. Please try refreshing."), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "0") in ("1", "true", "True")
    print(f"Starting Hidden Virasat Flask server on http://{host}:{port} ...")
    app.run(host=host, port=port, debug=debug)
