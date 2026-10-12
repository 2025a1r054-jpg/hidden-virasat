"""
Comprehensive Test Suite for Hidden Virasat Web Application
Tests database integrity, web views, REST APIs, recommendation logic,
and persistent SQLite trip saving.
"""

import unittest
import json
import os
import sys
from pathlib import Path

# Ensure application imports work
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import app
from database.db import get_db_connection, init_db


class HiddenVirasatTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db(seed=True)
        cls.client = app.test_client()
        cls.client.testing = True

    def test_database_counts_and_categories(self):
        """Verifies database contains required curated records and categories."""
        conn = get_db_connection()
        places_count = conn.execute("SELECT COUNT(*) FROM places").fetchone()[0]
        stories_count = conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
        categories = conn.execute("SELECT DISTINCT category FROM places").fetchall()
        category_names = [c[0] for c in categories]
        conn.close()

        self.assertGreaterEqual(places_count, 15, "Should have at least 15 curated places")
        self.assertGreaterEqual(stories_count, 6, "Should have at least 6 curated stories")
        
        expected_categories = [
            "Heritage & Forts",
            "Temples & Spiritual Heritage",
            "Museums & Art",
            "Local Markets",
            "Traditional Crafts",
            "Nature & Cultural Experiences"
        ]
        for ec in expected_categories:
            self.assertIn(ec, category_names, f"Category {ec} must be present in database")

    def test_web_routes(self):
        """Verifies all main HTML pages render with status 200."""
        routes = [
            ("/", b"HIDDEN VIRASAT"),
            ("/explore", b"Explore Jammu"),
            ("/places/mubarak-mandi-palace", b"Mubarak Mandi"),
            ("/places/bahu-fort", b"Bahu Fort"),
            ("/places/amar-mahal-palace-museum", b"Amar Mahal"),
            ("/map", b"Jammu Heritage Map"),
            ("/planner", b"Craft Your Jammu Virasat Trail"),
            ("/stories", b"Stories Carved in Time"),
            ("/about", b"About Hidden Virasat"),
        ]
        for route, keyword in routes:
            with self.subTest(route=route):
                res = self.client.get(route)
                self.assertEqual(res.status_code, 200, f"Route {route} failed with {res.status_code}")
                self.assertIn(keyword, res.data, f"Keyword missing in route {route}")

    def test_place_detail_not_found(self):
        """Verifies 404 error page for non-existent place."""
        res = self.client.get("/places/non-existent-ruin-1234")
        self.assertEqual(res.status_code, 404)
        self.assertIn(b"Sanctuary Not Found", res.data)

    def test_api_places(self):
        """Tests /api/places listing, category filter, and search query."""
        # 1. All places
        res = self.client.get("/api/places")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data["count"], 15)

        # 2. Filter by category
        res = self.client.get("/api/places?category=Heritage%20%26%20Forts")
        data = res.get_json()
        self.assertGreaterEqual(data["count"], 1)
        for p in data["places"]:
            self.assertEqual(p["category"], "Heritage & Forts")

        # 3. Search query
        res = self.client.get("/api/places?q=kalari")
        data = res.get_json()
        self.assertGreaterEqual(data["count"], 1)

    def test_api_single_place(self):
        """Tests /api/places/<slug>."""
        res = self.client.get("/api/places/mubarak-mandi-palace")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["slug"], "mubarak-mandi-palace")
        self.assertIn("latitude", data)
        self.assertIn("longitude", data)

    def test_api_stories(self):
        """Tests /api/stories listing."""
        res = self.client.get("/api/stories")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["count"], 6)

    def test_api_weather(self):
        """Tests /api/weather endpoint (cached or live response)."""
        res = self.client.get("/api/weather?lat=32.7266&lon=74.8570")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("status", data)
        self.assertIn(data["status"], ["success", "unavailable"])

    def test_api_recommend_itinerary(self):
        """Tests recommendation engine returns day-wise stops with travel distances."""
        payload = {
            "duration_days": 2,
            "interests": ["heritage", "spirituality", "food"],
            "pace": "balanced",
            "start_area": "old-city"
        }
        res = self.client.post("/api/recommend-itinerary",
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["days"]), 2)
        for day in data["days"]:
            self.assertGreaterEqual(len(day["stops"]), 1)
            self.assertIn("approx_travel_distance_km", day)
            for stop in day["stops"]:
                self.assertIn("match_reason", stop)
                self.assertIn("latitude", stop)
                self.assertIn("longitude", stop)

    def test_trip_save_retrieve_delete_lifecycle(self):
        """Tests saving, retrieving, and deleting trips from SQLite database."""
        trip_payload = {
            "title": "Faculty Demonstration Dogra Heritage Trail",
            "traveler_name": "AI Evaluation Team",
            "duration_days": 2,
            "pace": "balanced",
            "interests": ["heritage", "food"],
            "start_area": "old-city",
            "itinerary": [
                {
                    "day_number": 1,
                    "title": "Day 1: Dogra Heritage & Old City",
                    "approx_travel_distance_km": 4.2,
                    "stops": [
                        {
                            "time_slot": "09:30 AM",
                            "place_id": 1,
                            "name": "Mubarak Mandi Heritage Complex",
                            "location": "Old Heritage Zone, Panjtirthi, Jammu"
                        }
                    ]
                }
            ]
        }

        # 1. Save trip
        post_res = self.client.post("/api/trips",
                                    data=json.dumps(trip_payload),
                                    content_type="application/json")
        self.assertEqual(post_res.status_code, 201)
        post_data = post_res.get_json()
        self.assertTrue(post_data["success"])
        trip_id = post_data["trip_id"]

        # 2. Retrieve all trips
        get_res = self.client.get("/api/trips")
        self.assertEqual(get_res.status_code, 200)
        trips = get_res.get_json()["trips"]
        found = any(t["id"] == trip_id for t in trips)
        self.assertTrue(found, "Saved trip should appear in /api/trips list")

        # 3. Retrieve single trip
        single_res = self.client.get(f"/api/trips/{trip_id}")
        self.assertEqual(single_res.status_code, 200)
        single_data = single_res.get_json()
        self.assertEqual(single_data["title"], "Faculty Demonstration Dogra Heritage Trail")
        self.assertEqual(len(single_data["itinerary"]), 1)

        # 4. Delete trip
        del_res = self.client.delete(f"/api/trips/{trip_id}")
        self.assertEqual(del_res.status_code, 200)
        self.assertTrue(del_res.get_json()["success"])

        # 5. Verify deletion
        verify_res = self.client.get(f"/api/trips/{trip_id}")
        self.assertEqual(verify_res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
