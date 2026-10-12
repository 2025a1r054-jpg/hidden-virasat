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

    conn.commit()

    if seed:
        from database.seed_data import seed_places, seed_stories
        seed_places(conn)
        seed_stories(conn)

    conn.close()


if __name__ == "__main__":
    print(f"Initializing database at {DB_PATH}...")
    init_db(seed=True)
    print("Database initialized successfully.")
