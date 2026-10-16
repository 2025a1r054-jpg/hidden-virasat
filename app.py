"""
HIDDEN VIRASAT — Discover the Soul of Jammu
Flask Web Application & REST API
"""

import os
import sys
import json
import math
import time
import html
import re
import uuid
import secrets
from functools import wraps
from pathlib import Path
from flask import Flask, render_template, request, jsonify, abort, session, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Ensure local imports work
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.db import get_db_connection, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "hidden-virasat-jammu-heritage-key-2026")

# Upload and Security Configurations
UPLOAD_FOLDER = BASE_DIR / "static" / "images" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "virasat-admin-2026")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


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
        "SELECT * FROM stories WHERE COALESCE(status, 'approved') = 'approved' ORDER BY id ASC LIMIT 3"
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

    # Fetch approved community reviews
    reviews_rows = conn.execute(
        "SELECT * FROM reviews WHERE place_id = ? AND status = 'approved' ORDER BY created_at DESC",
        (place["id"],)
    ).fetchall()
    reviews = [dict(r) for r in reviews_rows]
    if reviews:
        avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 1)
    else:
        avg_rating = None
        
    conn.close()
    return render_template(
        "place.html",
        place=place,
        nearby_places=nearby_places,
        tags=tags,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=len(reviews)
    )


@app.route("/places/<slug>/review", methods=["POST"])
def submit_place_review(slug):
    """Handles review and rating submission for a specific place."""
    conn = get_db_connection()
    place = conn.execute("SELECT id, name, slug FROM places WHERE slug = ?", (slug,)).fetchone()
    if not place:
        conn.close()
        flash("Heritage place not found.", "error")
        return redirect(url_for("explore"))

    # Anti-spam honeypot
    honeypot = request.form.get("website_url", "").strip()
    if honeypot:
        conn.close()
        flash("Thank you for your reflection.", "success")
        return redirect(url_for("place_detail", slug_or_id=slug))

    author_name = request.form.get("author_name", "").strip() or "Dogra Explorer"
    rating_str = request.form.get("rating", "5").strip()
    review_text = request.form.get("review_text", "").strip()

    errors = []
    try:
        rating = int(rating_str)
        if not (1 <= rating <= 5):
            errors.append("Rating must be between 1 and 5 stars.")
    except (ValueError, TypeError):
        errors.append("Invalid rating value.")
        rating = 5

    if len(review_text) < 10 or len(review_text) > 1000:
        errors.append("Your reflection should be between 10 and 1,000 characters.")

    if len(author_name) > 60:
        errors.append("Name cannot exceed 60 characters.")

    if errors:
        for err in errors:
            flash(err, "error")
        conn.close()
        return redirect(url_for("place_detail", slug_or_id=slug) + "#reflections")

    # Insert into reviews table (defaults to 'approved')
    conn.execute("""
        INSERT INTO reviews (place_id, place_slug, author_name, rating, review_text, status, reported_count)
        VALUES (?, ?, ?, ?, ?, 'approved', 0)
    """, (place["id"], place["slug"], author_name, rating, review_text))
    conn.commit()
    conn.close()

    flash("Your reflection has been recorded. Thank you for enriching Jammu's living archives!", "success")
    return redirect(url_for("place_detail", slug_or_id=slug) + "#reflections")


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
    stories_list = conn.execute(
        "SELECT * FROM stories WHERE COALESCE(status, 'approved') = 'approved' ORDER BY id ASC"
    ).fetchall()
    conn.close()
    return render_template("stories.html", stories=stories_list)


STORY_CATEGORIES = ["Folklore & Legends", "Oral History", "Local Traditions", "Folk Tales"]


@app.route("/stories/submit", methods=["GET", "POST"])
def submit_story():
    """Form and handler for community members to submit a local story or oral folklore."""
    conn = get_db_connection()
    places_rows = conn.execute("SELECT id, slug, name, location FROM places ORDER BY name ASC").fetchall()
    places = [dict(p) for p in places_rows]

    if request.method == "POST":
        # Anti-spam Honeypot check
        honeypot = request.form.get("website_url", "").strip()
        if honeypot:
            conn.close()
            return render_template(
                "submit_story.html",
                categories=STORY_CATEGORIES,
                places=places,
                success=True,
                submitted_title="Your Chronicle"
            )

        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        content = request.form.get("content", "").strip()
        related_place = request.form.get("related_place", "").strip()
        contributor_name = request.form.get("contributor_name", "").strip()

        errors = []
        if len(title) < 5 or len(title) > 120:
            errors.append("Story title must be between 5 and 120 characters.")
        if category not in STORY_CATEGORIES:
            errors.append("Please select a valid story category from the list.")
        if len(content) < 30 or len(content) > 5000:
            errors.append("Story narrative must be between 30 and 5,000 characters.")
        if len(contributor_name) > 60:
            errors.append("Contributor name cannot exceed 60 characters.")

        # Optional Photo Upload Validation & Storage
        image_url = None
        if "image_file" in request.files:
            file = request.files["image_file"]
            if file and file.filename and file.filename.strip():
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_name = f"story_{int(time.time())}_{uuid.uuid4().hex[:6]}_{filename}"
                    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
                    file.save(upload_path)
                    image_url = f"/static/images/uploads/{unique_name}"
                else:
                    errors.append("Story photograph must be a valid image (.jpg, .jpeg, .png, or .webp).")

        if errors:
            conn.close()
            return render_template(
                "submit_story.html",
                categories=STORY_CATEGORIES,
                places=places,
                errors=errors,
                form_data=request.form
            ), 400

        # Generate unique private edit passkey
        edit_token = secrets.token_hex(12)

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO story_submissions (
                title, content, category, related_place, contributor_name, image_url, edit_token, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (title, content, category, related_place, contributor_name, image_url, edit_token))
        conn.commit()
        story_id = cursor.lastrowid
        conn.close()

        return render_template(
            "submit_story.html",
            categories=STORY_CATEGORIES,
            places=places,
            success=True,
            submitted_title=title,
            submission_id=story_id,
            edit_token=edit_token
        )

    conn.close()
    return render_template("submit_story.html", categories=STORY_CATEGORIES, places=places)


@app.route("/stories/<int:story_id>/edit", methods=["GET", "POST"])
def edit_story(story_id):
    """
    Allows the original contributor (verified via private edit key) or admin
    to edit their submitted story text, category, and optional photograph.
    """
    conn = get_db_connection()
    story = conn.execute("SELECT * FROM story_submissions WHERE id = ?", (story_id,)).fetchone()
    if not story:
        conn.close()
        flash("Story submission not found.", "error")
        return redirect(url_for("stories"))

    # Verify ownership: check ?key= query parameter, form input, or admin session
    req_key = request.args.get("key", "").strip() or request.form.get("edit_key", "").strip()
    is_admin = session.get("is_admin", False)
    authorized = is_admin or (bool(story["edit_token"]) and req_key == story["edit_token"])

    if not authorized:
        conn.close()
        error = "Invalid or missing private story edit key." if req_key else None
        return render_template("edit_story.html", authorized=False, story_id=story_id, error=error), (403 if req_key else 200)

    places_rows = conn.execute("SELECT id, slug, name, location FROM places ORDER BY name ASC").fetchall()
    places = [dict(p) for p in places_rows]

    if request.method == "POST":
        # Anti-spam Honeypot check
        honeypot = request.form.get("website_url", "").strip()
        if honeypot:
            conn.close()
            return redirect(url_for("stories"))

        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        content = request.form.get("content", "").strip()
        related_place = request.form.get("related_place", "").strip()
        contributor_name = request.form.get("contributor_name", "").strip()

        errors = []
        if len(title) < 5 or len(title) > 120:
            errors.append("Story title must be between 5 and 120 characters.")
        if category not in STORY_CATEGORIES:
            errors.append("Please select a valid story category from the list.")
        if len(content) < 30 or len(content) > 5000:
            errors.append("Story narrative must be between 30 and 5,000 characters.")
        if len(contributor_name) > 60:
            errors.append("Contributor name cannot exceed 60 characters.")

        # Handle photo upload or retention
        image_url = story["image_url"]  # retain existing by default
        if "image_file" in request.files:
            file = request.files["image_file"]
            if file and file.filename and file.filename.strip():
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_name = f"story_{int(time.time())}_{uuid.uuid4().hex[:6]}_{filename}"
                    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
                    file.save(upload_path)
                    image_url = f"/static/images/uploads/{unique_name}"
                else:
                    errors.append("Story photograph must be a valid image (.jpg, .jpeg, .png, or .webp).")

        if errors:
            conn.close()
            return render_template(
                "edit_story.html",
                authorized=True,
                story=story,
                story_id=story_id,
                categories=STORY_CATEGORIES,
                places=places,
                key=req_key,
                errors=errors,
                form_data=request.form
            ), 400

        # Update story_submissions record in place (ID preserved)
        # Sets status back to 'pending'
        conn.execute("""
            UPDATE story_submissions
            SET title = ?, content = ?, category = ?, related_place = ?, contributor_name = ?,
                image_url = ?, status = 'pending', reviewed_at = NULL
            WHERE id = ?
        """, (title, content, category, related_place, contributor_name, image_url, story_id))

        # If story was already in public stories table, mark it pending so changes are not displayed until approved
        conn.execute("UPDATE stories SET status = 'pending' WHERE submission_id = ?", (story_id,))

        conn.commit()

        # Re-fetch updated story
        updated_story = conn.execute("SELECT * FROM story_submissions WHERE id = ?", (story_id,)).fetchone()
        conn.close()

        return render_template(
            "edit_story.html",
            authorized=True,
            story=updated_story,
            story_id=story_id,
            categories=STORY_CATEGORIES,
            places=places,
            key=req_key,
            success=True,
            updated_title=title
        )

    conn.close()
    return render_template(
        "edit_story.html",
        authorized=True,
        story=story,
        story_id=story_id,
        categories=STORY_CATEGORIES,
        places=places,
        key=req_key
    )


@app.route("/about")
def about():
    """About Hidden Virasat: Mission, Dogra heritage, recommendation logic, disclaimer."""
    return render_template("about.html")


# ---------------------------------------------------------------------------
# Community Place Submissions & Protected Admin Moderation
# ---------------------------------------------------------------------------

@app.route("/suggest", methods=["GET", "POST"])
def suggest_place():
    """Form and handler for community members to suggest a heritage site or tradition."""
    conn = get_db_connection()
    categories_rows = conn.execute("SELECT DISTINCT category FROM places ORDER BY category ASC").fetchall()
    categories = [r["category"] for r in categories_rows]
    conn.close()

    if request.method == "POST":
        # Anti-spam Honeypot check
        honeypot = request.form.get("website_url", "").strip()
        if honeypot:
            return render_template("suggest.html", categories=categories, success=True, submitted_name="Submission")

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        address = request.form.get("address", "").strip()
        lat_str = request.form.get("latitude", "").strip()
        lon_str = request.form.get("longitude", "").strip()
        short_desc = request.form.get("short_desc", "").strip()
        history = request.form.get("history", "").strip()
        cultural_significance = request.form.get("cultural_significance", "").strip()
        things_to_see = request.form.get("things_to_see", "").strip()
        best_time = request.form.get("best_time", "").strip()
        submitter_name = request.form.get("submitter_name", "").strip()
        submitter_email = request.form.get("submitter_email", "").strip()

        errors = []
        if len(name) < 3 or len(name) > 100:
            errors.append("Place name must be between 3 and 100 characters.")
        if not category:
            errors.append("Please select a cultural category.")
        if len(location) < 2 or len(location) > 100:
            errors.append("Please specify a location or district in Jammu.")
        if len(short_desc) < 20 or len(short_desc) > 1200:
            errors.append("Short description must be between 20 and 1,200 characters.")
        if len(submitter_name) < 2 or len(submitter_name) > 60:
            errors.append("Please provide your name (2 to 60 characters).")

        latitude = None
        longitude = None
        if lat_str and lon_str:
            try:
                latitude = float(lat_str)
                longitude = float(lon_str)
                if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                    errors.append("Latitude must be between -90 and 90, and longitude between -180 and 180.")
            except (ValueError, TypeError):
                errors.append("Coordinates must be valid numerical values.")

        image_url = "/static/images/fallback-heritage.svg"
        if "image_file" in request.files:
            file = request.files["image_file"]
            if file and file.filename and file.filename.strip():
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_name = f"sub_{int(time.time())}_{uuid.uuid4().hex[:6]}_{filename}"
                    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
                    file.save(upload_path)
                    image_url = f"/static/images/uploads/{unique_name}"
                else:
                    errors.append("Uploaded file must be a valid image (.jpg, .jpeg, .png, or .webp).")
        elif request.form.get("image_url"):
            ext_url = request.form.get("image_url", "").strip()
            if ext_url.startswith(("http://", "https://", "/static/")):
                image_url = ext_url

        if errors:
            return render_template(
                "suggest.html",
                categories=categories,
                errors=errors,
                form_data=request.form
            ), 400

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO community_submissions (
                name, category, location, address, latitude, longitude,
                short_desc, history, cultural_significance, things_to_see, best_time,
                submitter_name, submitter_email, image_url, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (
            name, category, location, address, latitude, longitude,
            short_desc, history, cultural_significance, things_to_see, best_time,
            submitter_name, submitter_email, image_url
        ))
        conn.commit()
        conn.close()

        return render_template("suggest.html", categories=categories, success=True, submitted_name=name)

    return render_template("suggest.html", categories=categories)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Protected admin login view."""
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    error = None
    if request.method == "POST":
        entered_password = request.form.get("password", "").strip()
        if entered_password == ADMIN_PASSWORD:
            session["is_admin"] = True
            next_url = request.args.get("next") or url_for("admin_dashboard")
            return redirect(next_url)
        else:
            error = "Invalid archival authorization key. Please verify your credentials."

    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    """Logs out admin."""
    session.pop("is_admin", None)
    flash("You have been signed out of the curation panel.", "info")
    return redirect(url_for("home"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    """Admin overview dashboard."""
    conn = get_db_connection()
    pending_count = conn.execute("SELECT COUNT(*) FROM community_submissions WHERE status = 'pending'").fetchone()[0]
    approved_count = conn.execute("SELECT COUNT(*) FROM community_submissions WHERE status = 'approved'").fetchone()[0]
    rejected_count = conn.execute("SELECT COUNT(*) FROM community_submissions WHERE status = 'rejected'").fetchone()[0]
    pending_stories = conn.execute("SELECT COUNT(*) FROM story_submissions WHERE status = 'pending'").fetchone()[0]
    approved_stories = conn.execute("SELECT COUNT(*) FROM story_submissions WHERE status = 'approved'").fetchone()[0]
    total_places = conn.execute("SELECT COUNT(*) FROM places").fetchone()[0]
    total_reviews = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    reported_reviews = conn.execute("SELECT COUNT(*) FROM reviews WHERE reported_count > 0 OR status = 'flagged'").fetchone()[0]

    recent_submissions = conn.execute(
        "SELECT * FROM community_submissions ORDER BY created_at DESC LIMIT 5"
    ).fetchall()
    recent_reviews = conn.execute(
        "SELECT r.*, p.name as place_name FROM reviews r LEFT JOIN places p ON r.place_id = p.id ORDER BY r.created_at DESC LIMIT 5"
    ).fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        pending_stories=pending_stories,
        approved_stories=approved_stories,
        total_places=total_places,
        total_reviews=total_reviews,
        reported_reviews=reported_reviews,
        recent_submissions=recent_submissions,
        recent_reviews=recent_reviews
    )


@app.route("/admin/submissions")
@admin_required
def admin_submissions():
    """Lists community submissions filtered by status."""
    status_filter = request.args.get("status", "pending").lower()
    conn = get_db_connection()
    if status_filter in ("pending", "approved", "rejected"):
        submissions = conn.execute(
            "SELECT * FROM community_submissions WHERE status = ? ORDER BY created_at DESC",
            (status_filter,)
        ).fetchall()
    else:
        status_filter = "all"
        submissions = conn.execute("SELECT * FROM community_submissions ORDER BY created_at DESC").fetchall()
    conn.close()

    return render_template("admin_submissions.html", submissions=submissions, status_filter=status_filter)


@app.route("/admin/submissions/<int:sub_id>/approve", methods=["POST"])
@admin_required
def admin_approve_submission(sub_id):
    """Approves a community submission and adds it to the public places table."""
    conn = get_db_connection()
    sub = conn.execute("SELECT * FROM community_submissions WHERE id = ?", (sub_id,)).fetchone()
    if not sub:
        conn.close()
        flash("Submission not found.", "error")
        return redirect(url_for("admin_submissions"))

    if sub["status"] == "approved":
        conn.close()
        flash("This submission has already been approved.", "info")
        return redirect(url_for("admin_submissions"))

    # Generate unique slug
    base_slug = slugify(sub["name"]) or f"community-place-{sub['id']}"
    slug = base_slug
    suffix = 1
    while conn.execute("SELECT id FROM places WHERE slug = ?", (slug,)).fetchone():
        suffix += 1
        slug = f"{base_slug}-{suffix}"

    lat = sub["latitude"] if sub["latitude"] is not None else 32.7266
    lon = sub["longitude"] if sub["longitude"] is not None else 74.8570
    address = sub["address"] or f"{sub['location']}, Jammu"
    image_url = sub["image_url"] or "/static/images/fallback-heritage.svg"

    conn.execute("""
        INSERT INTO places (
            slug, name, category, location, address, latitude, longitude,
            short_desc, history, cultural_significance, lesser_known_facts,
            things_to_see, best_time, visit_duration_minutes, visit_duration_label,
            tips_accessibility, image_url, image_caption, image_credit, featured, tags, is_community
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        slug,
        sub["name"],
        sub["category"],
        sub["location"],
        address,
        lat,
        lon,
        sub["short_desc"],
        sub["history"] or sub["short_desc"],
        sub["cultural_significance"] or "Community submitted cultural heritage landmark.",
        "Contributed by local Jammu heritage enthusiast via Hidden Virasat community portal.",
        sub["things_to_see"] or "Explore the local architecture and cultural surroundings.",
        sub["best_time"] or "October to March",
        90,
        "1.5 hours",
        "Public visitor access. Please respect local traditions and heritage structures.",
        image_url,
        f"{sub['name']} — Community suggested heritage",
        f"Contributed by {sub['submitter_name']}",
        0,
        json.dumps(["community", sub["category"].lower(), slug])
    ))

    conn.execute(
        "UPDATE community_submissions SET status = 'approved', reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
        (sub_id,)
    )
    conn.commit()
    conn.close()

    flash(f"'{sub['name']}' was successfully approved and is now live in the heritage directory!", "success")
    return redirect(url_for("admin_submissions"))


@app.route("/admin/submissions/<int:sub_id>/reject", methods=["POST"])
@admin_required
def admin_reject_submission(sub_id):
    """Rejects a community submission."""
    admin_notes = request.form.get("admin_notes", "Does not meet heritage criteria.").strip()
    conn = get_db_connection()
    conn.execute(
        "UPDATE community_submissions SET status = 'rejected', admin_notes = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
        (admin_notes, sub_id)
    )
    conn.commit()
    conn.close()

    flash("Submission has been marked as rejected.", "info")
    return redirect(url_for("admin_submissions"))


@app.route("/admin/stories")
@admin_required
def admin_stories():
    """Lists community story submissions filtered by status."""
    status_filter = request.args.get("status", "pending").lower()
    conn = get_db_connection()
    if status_filter in ("pending", "approved", "rejected"):
        stories_rows = conn.execute(
            "SELECT * FROM story_submissions WHERE status = ? ORDER BY created_at DESC",
            (status_filter,)
        ).fetchall()
    else:
        status_filter = "all"
        stories_rows = conn.execute("SELECT * FROM story_submissions ORDER BY created_at DESC").fetchall()
    conn.close()

    return render_template("admin_stories.html", stories=stories_rows, status_filter=status_filter)


@app.route("/admin/stories/<int:story_id>/approve", methods=["POST"])
@admin_required
def admin_approve_story(story_id):
    """Approves a community story and adds or updates it in the public stories journal."""
    conn = get_db_connection()
    sub = conn.execute("SELECT * FROM story_submissions WHERE id = ?", (story_id,)).fetchone()
    if not sub:
        conn.close()
        flash("Story submission not found.", "error")
        return redirect(url_for("admin_stories"))

    word_count = len(sub["content"].split())
    read_time = f"{max(1, word_count // 130)} min read"
    contributor = sub["contributor_name"] or "Community Chronicler"
    summary = sub["content"][:180].strip() + ("..." if len(sub["content"]) > 180 else "")
    story_image = sub["image_url"] if (sub["image_url"] and sub["image_url"].strip()) else "/static/images/fallback-heritage.svg"

    # Check if a story linked to this submission already exists (e.g. re-approving an edited story)
    existing_story = conn.execute("SELECT id, slug FROM stories WHERE submission_id = ?", (story_id,)).fetchone()

    if existing_story:
        conn.execute("""
            UPDATE stories SET
                title = ?,
                subtitle = ?,
                category = ?,
                read_time = ?,
                image_url = ?,
                image_credit = ?,
                summary = ?,
                content = ?,
                related_place_slugs = ?,
                contributor_name = ?,
                status = 'approved'
            WHERE id = ?
        """, (
            sub["title"],
            f"A {sub['category']} chronicle from Jammu's living heritage",
            sub["category"],
            read_time,
            story_image,
            f"Contributed by {contributor}",
            summary,
            sub["content"],
            json.dumps([sub["related_place"]] if sub["related_place"] else []),
            contributor,
            existing_story["id"]
        ))
    else:
        # Generate unique slug
        base_slug = slugify(sub["title"]) or f"community-story-{sub['id']}"
        slug = base_slug
        suffix = 1
        while conn.execute("SELECT id FROM stories WHERE slug = ?", (slug,)).fetchone():
            suffix += 1
            slug = f"{base_slug}-{suffix}"

        conn.execute("""
            INSERT INTO stories (
                slug, title, subtitle, category, read_time,
                image_url, image_credit, summary, content,
                related_place_slugs, sources, is_community, contributor_name,
                submission_id, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, 'approved')
        """, (
            slug,
            sub["title"],
            f"A {sub['category']} chronicle from Jammu's living heritage",
            sub["category"],
            read_time,
            story_image,
            f"Contributed by {contributor}",
            summary,
            sub["content"],
            json.dumps([sub["related_place"]] if sub["related_place"] else []),
            f"Community oral chronicle contributed by {contributor}",
            contributor,
            story_id
        ))

    conn.execute(
        "UPDATE story_submissions SET status = 'approved', reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
        (story_id,)
    )
    conn.commit()
    conn.close()

    flash(f"'{sub['title']}' was successfully approved and is now live in the Stories Journal!", "success")
    return redirect(url_for("admin_stories"))


@app.route("/admin/stories/<int:story_id>/reject", methods=["POST"])
@admin_required
def admin_reject_story(story_id):
    """Rejects a community story submission."""
    admin_notes = request.form.get("admin_notes", "Does not meet regional folklore criteria.").strip()
    conn = get_db_connection()
    conn.execute(
        "UPDATE story_submissions SET status = 'rejected', admin_notes = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?",
        (admin_notes, story_id)
    )
    conn.execute(
        "UPDATE stories SET status = 'rejected' WHERE submission_id = ?",
        (story_id,)
    )
    conn.commit()
    conn.close()

    flash("Story submission has been marked as rejected.", "info")
    return redirect(url_for("admin_stories"))


@app.route("/admin/reviews")
@admin_required
def admin_reviews():
    """Lists community reviews with moderation controls."""
    filter_type = request.args.get("filter", "all")
    conn = get_db_connection()
    if filter_type == "reported":
        reviews = conn.execute(
            "SELECT r.*, p.name as place_name FROM reviews r JOIN places p ON r.place_id = p.id WHERE r.reported_count > 0 OR r.status = 'flagged' ORDER BY r.reported_count DESC, r.created_at DESC"
        ).fetchall()
    else:
        reviews = conn.execute(
            "SELECT r.*, p.name as place_name FROM reviews r JOIN places p ON r.place_id = p.id ORDER BY r.created_at DESC"
        ).fetchall()
    conn.close()

    return render_template("admin_reviews.html", reviews=reviews, filter_type=filter_type)


@app.route("/admin/reviews/<int:rev_id>/delete", methods=["POST"])
@admin_required
def admin_delete_review(rev_id):
    """Deletes an inappropriate review."""
    conn = get_db_connection()
    conn.execute("DELETE FROM reviews WHERE id = ?", (rev_id,))
    conn.commit()
    conn.close()
    flash("Review has been permanently removed.", "info")
    return redirect(url_for("admin_reviews"))


@app.route("/admin/reviews/<int:rev_id>/approve", methods=["POST"])
@admin_required
def admin_approve_review(rev_id):
    """Approves a flagged review and resets report count."""
    conn = get_db_connection()
    conn.execute("UPDATE reviews SET status = 'approved', reported_count = 0 WHERE id = ?", (rev_id,))
    conn.commit()
    conn.close()
    flash("Review has been approved and restored to public view.", "success")
    return redirect(url_for("admin_reviews"))


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


@app.route("/api/places/near", methods=["GET"])
def api_get_places_near():
    """
    Returns places sorted by distance from user-provided GPS coordinates (lat, lon).
    Supports optional ?radius= (in km, e.g. 5, 10, 25), ?category=, and ?q= search.
    Gracefully handles missing or invalid coordinates.
    """
    lat_str = request.args.get("lat", "").strip()
    lon_str = request.args.get("lon", "").strip()
    radius_str = request.args.get("radius", "").strip()
    category = request.args.get("category", "").strip()
    q = request.args.get("q", "").strip().lower()

    if not lat_str or not lon_str:
        return jsonify({
            "error": "Missing coordinates",
            "message": "Both 'lat' and 'lon' query parameters are required for proximity discovery."
        }), 400

    try:
        user_lat = float(lat_str)
        user_lon = float(lon_str)
    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid coordinates",
            "message": "'lat' and 'lon' must be valid numerical values."
        }), 400

    radius_km = None
    if radius_str:
        try:
            r_val = float(radius_str)
            if r_val > 0:
                radius_km = r_val
        except (ValueError, TypeError):
            radius_km = None

    conn = get_db_connection()
    query = "SELECT * FROM places WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if q:
        query += " AND (LOWER(name) LIKE ? OR LOWER(short_desc) LIKE ? OR LOWER(location) LIKE ? OR LOWER(tags) LIKE ?)"
        wildcard = f"%{q}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])

    rows = conn.execute(query, params).fetchall()
    conn.close()

    places_with_distance = []
    for r in rows:
        item = dict(r)
        try:
            item["tags"] = json.loads(item["tags"])
        except Exception:
            item["tags"] = []

        p_lat = item.get("latitude")
        p_lon = item.get("longitude")

        if (p_lat is not None and p_lon is not None and 
            isinstance(p_lat, (int, float)) and isinstance(p_lon, (int, float)) and 
            not (p_lat == 0 and p_lon == 0)):
            dist = haversine_distance_km(user_lat, user_lon, p_lat, p_lon)
            item["distance_km"] = dist
            item["distance_formatted"] = f"{dist:.1f} km" if dist >= 1.0 else f"{int(dist * 1000)} m"
        else:
            item["distance_km"] = None
            item["distance_formatted"] = "Distance unknown"

        if radius_km is not None:
            if item["distance_km"] is not None and item["distance_km"] <= radius_km:
                places_with_distance.append(item)
        else:
            places_with_distance.append(item)

    places_with_distance.sort(
        key=lambda x: (x["distance_km"] is None, x["distance_km"] if x["distance_km"] is not None else float("inf"))
    )

    return jsonify({
        "success": True,
        "user_coords": {"latitude": user_lat, "longitude": user_lon},
        "radius_km": radius_km,
        "count": len(places_with_distance),
        "places": places_with_distance
    })


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


@app.route("/api/places/<slug_or_id>/reviews", methods=["GET"])
def api_get_place_reviews(slug_or_id):
    """Returns all approved reviews for a given place."""
    conn = get_db_connection()
    if slug_or_id.isdigit():
        place = conn.execute("SELECT id, name, slug FROM places WHERE id = ?", (int(slug_or_id),)).fetchone()
    else:
        place = conn.execute("SELECT id, name, slug FROM places WHERE slug = ?", (slug_or_id,)).fetchone()
    if not place:
        conn.close()
        return jsonify({"error": "Place not found"}), 404

    rows = conn.execute(
        "SELECT id, place_id, place_slug, author_name, rating, review_text, created_at, reported_count "
        "FROM reviews WHERE place_id = ? AND status = 'approved' ORDER BY created_at DESC",
        (place["id"],)
    ).fetchall()
    conn.close()

    reviews = [dict(r) for r in rows]
    avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else None

    return jsonify({
        "place_id": place["id"],
        "place_name": place["name"],
        "place_slug": place["slug"],
        "count": len(reviews),
        "average_rating": avg_rating,
        "reviews": reviews
    })


@app.route("/api/places/<slug_or_id>/reviews", methods=["POST"])
def api_submit_place_review(slug_or_id):
    """JSON API endpoint to submit a review and rating."""
    conn = get_db_connection()
    if slug_or_id.isdigit():
        place = conn.execute("SELECT id, name, slug FROM places WHERE id = ?", (int(slug_or_id),)).fetchone()
    else:
        place = conn.execute("SELECT id, name, slug FROM places WHERE slug = ?", (slug_or_id,)).fetchone()
    if not place:
        conn.close()
        return jsonify({"error": "Place not found"}), 404

    data = request.get_json() or {}
    # Anti-spam honeypot
    if data.get("website_url"):
        conn.close()
        return jsonify({"success": True, "message": "Reflection recorded."}), 201

    author_name = str(data.get("author_name", "")).strip() or "Dogra Explorer"
    rating = data.get("rating")
    review_text = str(data.get("review_text", "")).strip()

    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            conn.close()
            return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
    except (ValueError, TypeError):
        conn.close()
        return jsonify({"error": "Invalid rating format"}), 400

    if len(review_text) < 10 or len(review_text) > 1000:
        conn.close()
        return jsonify({"error": "Review text must be between 10 and 1,000 characters"}), 400

    if len(author_name) > 60:
        conn.close()
        return jsonify({"error": "Author name cannot exceed 60 characters"}), 400

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reviews (place_id, place_slug, author_name, rating, review_text, status, reported_count)
        VALUES (?, ?, ?, ?, ?, 'approved', 0)
    """, (place["id"], place["slug"], author_name, rating, review_text))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "success": True,
        "message": "Your cultural reflection has been recorded.",
        "review_id": new_id,
        "rating": rating,
        "author_name": author_name
    }), 201


@app.route("/api/reviews/<int:review_id>/report", methods=["POST"])
def api_report_review(review_id):
    """Reports a review for moderation. Auto-flags if report threshold (3) is reached."""
    conn = get_db_connection()
    review = conn.execute("SELECT id, reported_count, status FROM reviews WHERE id = ?", (review_id,)).fetchone()
    if not review:
        conn.close()
        return jsonify({"error": "Review not found"}), 404

    new_count = (review["reported_count"] or 0) + 1
    new_status = review["status"]
    if new_count >= 3:
        new_status = "flagged"

    conn.execute(
        "UPDATE reviews SET reported_count = ?, status = ? WHERE id = ?",
        (new_count, new_status, review_id)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Thank you. This reflection has been submitted for editorial review.",
        "reported_count": new_count,
        "flagged": (new_status == "flagged")
    })


@app.route("/api/community-submissions", methods=["POST"])
def api_community_submission():
    """JSON API endpoint to submit a community heritage place."""
    data = request.get_json() or {}
    if data.get("website_url"):
        return jsonify({"success": True, "message": "Submission received."}), 201

    name = str(data.get("name", "")).strip()
    category = str(data.get("category", "")).strip()
    location = str(data.get("location", "")).strip()
    address = str(data.get("address", "")).strip()
    short_desc = str(data.get("short_desc", "")).strip()
    submitter_name = str(data.get("submitter_name", "")).strip()
    submitter_email = str(data.get("submitter_email", "")).strip()
    history = str(data.get("history", "")).strip()
    cultural_significance = str(data.get("cultural_significance", "")).strip()
    things_to_see = str(data.get("things_to_see", "")).strip()
    best_time = str(data.get("best_time", "")).strip()
    image_url = str(data.get("image_url", "/static/images/fallback-heritage.svg")).strip()

    if len(name) < 3 or len(name) > 100:
        return jsonify({"error": "Place name must be between 3 and 100 characters"}), 400
    if not category:
        return jsonify({"error": "Category is required"}), 400
    if len(location) < 2 or len(location) > 100:
        return jsonify({"error": "Location must be between 2 and 100 characters"}), 400
    if len(short_desc) < 20 or len(short_desc) > 1200:
        return jsonify({"error": "Short description must be between 20 and 1200 characters"}), 400
    if len(submitter_name) < 2 or len(submitter_name) > 60:
        return jsonify({"error": "Submitter name must be between 2 and 60 characters"}), 400

    lat = None
    lon = None
    if "latitude" in data and "longitude" in data:
        try:
            lat = float(data["latitude"])
            lon = float(data["longitude"])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return jsonify({"error": "Coordinates out of bounds"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Coordinates must be numbers"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO community_submissions (
            name, category, location, address, latitude, longitude,
            short_desc, history, cultural_significance, things_to_see, best_time,
            submitter_name, submitter_email, image_url, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (
        name, category, location, address, lat, lon,
        short_desc, history, cultural_significance, things_to_see, best_time,
        submitter_name, submitter_email, image_url
    ))
    conn.commit()
    sub_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "success": True,
        "message": "Submission received and queued for admin curation.",
        "submission_id": sub_id,
        "status": "pending"
    }), 201


@app.route("/api/stories", methods=["GET"])
def api_get_stories():
    """Returns all curated local stories."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM stories WHERE COALESCE(status, 'approved') = 'approved' ORDER BY id ASC").fetchall()
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


@app.route("/api/stories/submit", methods=["POST"])
def api_submit_story():
    """JSON API endpoint to submit a community story."""
    data = request.get_json() or {}
    if data.get("website_url"):
        return jsonify({"success": True, "message": "Story received."}), 201

    title = str(data.get("title", "")).strip()
    category = str(data.get("category", "")).strip()
    content = str(data.get("content", "")).strip()
    related_place = str(data.get("related_place", "")).strip()
    contributor_name = str(data.get("contributor_name", "")).strip()
    image_url = str(data.get("image_url", "")).strip() or None

    if len(title) < 5 or len(title) > 120:
        return jsonify({"error": "Story title must be between 5 and 120 characters"}), 400
    if category not in STORY_CATEGORIES:
        return jsonify({"error": f"Category must be one of: {', '.join(STORY_CATEGORIES)}"}), 400
    if len(content) < 30 or len(content) > 5000:
        return jsonify({"error": "Story content must be between 30 and 5,000 characters"}), 400
    if len(contributor_name) > 60:
        return jsonify({"error": "Contributor name cannot exceed 60 characters"}), 400

    edit_token = secrets.token_hex(12)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO story_submissions (
            title, content, category, related_place, contributor_name, image_url, edit_token, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (title, content, category, related_place, contributor_name, image_url, edit_token))
    conn.commit()
    story_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "success": True,
        "message": "Story submission received and queued for admin curation.",
        "story_id": story_id,
        "edit_token": edit_token,
        "edit_url": f"/stories/{story_id}/edit?key={edit_token}",
        "status": "pending"
    }), 201


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
