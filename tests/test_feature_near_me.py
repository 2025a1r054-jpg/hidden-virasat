"""
Unit tests for Feature 1: Explore Near Me
"""

import unittest
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import app


class ExploreNearMeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_near_missing_coordinates(self):
        """Verifies error response when lat or lon is missing."""
        res = self.client.get('/api/places/near')
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)

        res2 = self.client.get('/api/places/near?lat=32.73')
        self.assertEqual(res2.status_code, 400)

    def test_near_invalid_coordinates(self):
        """Verifies error response when lat or lon is invalid string."""
        res = self.client.get('/api/places/near?lat=abc&lon=def')
        self.assertEqual(res.status_code, 400)

    def test_near_mubarak_mandi_proximity(self):
        """Tests proximity calculation from Mubarak Mandi coordinates."""
        res = self.client.get('/api/places/near?lat=32.7308&lon=74.8692')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["count"], 15)

        # First place should be Mubarak Mandi (~0 km)
        first = data["places"][0]
        self.assertIn("distance_km", first)
        self.assertIn("distance_formatted", first)
        self.assertLess(first["distance_km"], 0.2)
        self.assertEqual(first["slug"], "mubarak-mandi-palace")

        # Verify sorted ascending
        prev_dist = -1
        for p in data["places"]:
            if p["distance_km"] is not None:
                self.assertGreaterEqual(p["distance_km"], prev_dist)
                prev_dist = p["distance_km"]

    def test_near_radius_filtering(self):
        """Tests radius filtering (e.g. within 5 km)."""
        res = self.client.get('/api/places/near?lat=32.7308&lon=74.8692&radius=5')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["count"], 0)
        for p in data["places"]:
            self.assertLessEqual(p["distance_km"], 5.0)

    def test_near_category_filtering(self):
        """Tests combining proximity with category filtering."""
        res = self.client.get('/api/places/near?lat=32.7308&lon=74.8692&category=Heritage%20%26%20Forts')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        for p in data["places"]:
            self.assertEqual(p["category"], "Heritage & Forts")

    def test_explore_page_serves_near_me_controls(self):
        """Tests that /explore serves Near Me HTML elements."""
        res = self.client.get('/explore?near=1')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        self.assertIn('mode-near-btn', html)
        self.assertIn('near-me-panel', html)
        self.assertIn('near-radius-btn', html)
        self.assertIn('near-preset-btn', html)


if __name__ == '__main__':
    unittest.main()
