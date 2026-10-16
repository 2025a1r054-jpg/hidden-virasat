"""
Hidden Virasat - Database Module
SQLite connection management and schema migration.
"""

import os
import sys
import sqlite3
import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
DB_PATH = INSTANCE_DIR / "hidden_virasat.db"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def get_db_connection():
    """Returns a SQLite connection with row factory enabled."""
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(seed=True):
    """Initializes the database schema and seeds initial data idempotently."""
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Places table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        location TEXT NOT NULL,
        address TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        short_desc TEXT NOT NULL,
        history TEXT NOT NULL,
        cultural_significance TEXT NOT NULL,
        lesser_known_facts TEXT NOT NULL,
        things_to_see TEXT NOT NULL,
        best_time TEXT NOT NULL,
        visit_duration_minutes INTEGER NOT NULL,
        visit_duration_label TEXT NOT NULL,
        tips_accessibility TEXT NOT NULL,
        image_url TEXT NOT NULL,
        image_caption TEXT NOT NULL,
        image_credit TEXT NOT NULL,
        featured INTEGER NOT NULL DEFAULT 0,
        tags TEXT NOT NULL
    )
    """)

    # Stories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        subtitle TEXT NOT NULL,
        category TEXT NOT NULL,
        read_time TEXT NOT NULL,
        image_url TEXT NOT NULL,
        image_credit TEXT NOT NULL,
        summary TEXT NOT NULL,
        content TEXT NOT NULL,
        related_place_slugs TEXT NOT NULL,
        sources TEXT NOT NULL
    )
    """)

    # Saved Trips table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        traveler_name TEXT NOT NULL,
        duration_days INTEGER NOT NULL,
        pace TEXT NOT NULL,
        interests TEXT NOT NULL,
        start_area TEXT NOT NULL,
        itinerary_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Community Submissions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS community_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        location TEXT NOT NULL,
        address TEXT,
        latitude REAL,
        longitude REAL,
        short_desc TEXT NOT NULL,
        history TEXT,
        cultural_significance TEXT,
        things_to_see TEXT,
        best_time TEXT,
        submitter_name TEXT NOT NULL,
        submitter_email TEXT,
        image_url TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        admin_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP
    )
    """)

    # Reviews and Ratings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        place_id INTEGER NOT NULL,
        place_slug TEXT NOT NULL,
        author_name TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        review_text TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'approved',
        reported_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
    )
    """)

    # Safe migration: ensure is_community column in places
    cursor.execute("PRAGMA table_info(places)")
    existing_place_cols = [row[1] for row in cursor.fetchall()]
    if "is_community" not in existing_place_cols:
        cursor.execute("ALTER TABLE places ADD COLUMN is_community INTEGER NOT NULL DEFAULT 0")

    # Story Submissions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS story_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT NOT NULL,
        related_place TEXT,
        contributor_name TEXT,
        image_url TEXT,
        edit_token TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        admin_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP
    )
    """)

    # Safe migration: ensure image_url and edit_token columns in story_submissions
    cursor.execute("PRAGMA table_info(story_submissions)")
    existing_sub_cols = [row[1] for row in cursor.fetchall()]
    if "image_url" not in existing_sub_cols:
        cursor.execute("ALTER TABLE story_submissions ADD COLUMN image_url TEXT")
    if "edit_token" not in existing_sub_cols:
        cursor.execute("ALTER TABLE story_submissions ADD COLUMN edit_token TEXT")

    # Safe migration: ensure is_community, contributor_name, submission_id, status columns in stories
    cursor.execute("PRAGMA table_info(stories)")
    existing_story_cols = [row[1] for row in cursor.fetchall()]
    if "is_community" not in existing_story_cols:
        cursor.execute("ALTER TABLE stories ADD COLUMN is_community INTEGER NOT NULL DEFAULT 0")
    if "contributor_name" not in existing_story_cols:
        cursor.execute("ALTER TABLE stories ADD COLUMN contributor_name TEXT")
    if "submission_id" not in existing_story_cols:
        cursor.execute("ALTER TABLE stories ADD COLUMN submission_id INTEGER")
    if "status" not in existing_story_cols:
        cursor.execute("ALTER TABLE stories ADD COLUMN status TEXT NOT NULL DEFAULT 'approved'")

    conn.commit()

    if seed:
        from database.seed_data import seed_places, seed_stories, seed_reviews
        seed_places(conn)
        seed_stories(conn)
        seed_reviews(conn)

    conn.close()


if __name__ == "__main__":
    print(f"Initializing database at {DB_PATH}...")
    init_db(seed=True)
    print("Database initialized successfully.")
