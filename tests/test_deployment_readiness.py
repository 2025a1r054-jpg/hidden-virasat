"""
Deployment Readiness & Production Smoke Test for Hidden Virasat
Verifies that the application is fully configured for public deployment on Render.
"""

import unittest
import os
import sys
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import app
from database.db import get_db_connection, DB_PATH


class DeploymentReadinessTestCase(unittest.TestCase):
    def test_requirements_file(self):
        """Checks requirements.txt contains essential production dependencies."""
        req_path = BASE_DIR / "requirements.txt"
        self.assertTrue(req_path.exists(), "requirements.txt must exist")
        content = req_path.read_text(encoding="utf-8")
        self.assertIn("gunicorn", content.lower(), "requirements.txt must include gunicorn")
        self.assertIn("flask", content.lower(), "requirements.txt must include Flask")
        self.assertIn("requests", content.lower(), "requirements.txt must include requests")

    def test_procfile_and_render_yaml(self):
        """Checks Procfile and render.yaml for correct start commands."""
        proc_path = BASE_DIR / "Procfile"
        self.assertTrue(proc_path.exists(), "Procfile must exist")
        proc_content = proc_path.read_text(encoding="utf-8").strip()
        self.assertEqual(proc_content, "web: gunicorn app:app", "Procfile must use gunicorn app:app")

        yaml_path = BASE_DIR / "render.yaml"
        self.assertTrue(yaml_path.exists(), "render.yaml must exist")
        yaml_content = yaml_path.read_text(encoding="utf-8")
        self.assertIn("startCommand: gunicorn app:app", yaml_content)
        self.assertIn("buildCommand: pip install -r requirements.txt", yaml_content)

    def test_gitignore_protects_secrets(self):
        """Verifies .gitignore excludes environment variables and cache."""
        gi_path = BASE_DIR / ".gitignore"
        self.assertTrue(gi_path.exists(), ".gitignore must exist")
        content = gi_path.read_text(encoding="utf-8")
        self.assertIn(".env", content)
        self.assertIn("__pycache__", content)

    def test_wsgi_app_callable(self):
        """Verifies app object is imported cleanly and named 'app'."""
        self.assertIsNotNone(app)
        self.assertEqual(app.name, "app")

    def test_static_photographs_exist(self):
        """Verifies all 15 place photographs exist and are non-empty in static/images/."""
        img_dir = BASE_DIR / "static" / "images"
        self.assertTrue(img_dir.exists())

        conn = get_db_connection()
        places = conn.execute("SELECT slug, image_url FROM places").fetchall()
        stories = conn.execute("SELECT slug, image_url FROM stories").fetchall()
        conn.close()

        self.assertEqual(len(places), 15)
        for p in places:
            rel_path = p["image_url"].lstrip("/")
            file_path = BASE_DIR / rel_path
            self.assertTrue(file_path.exists(), f"Image file missing: {file_path}")
            self.assertGreater(file_path.stat().st_size, 5000, f"Image file empty: {file_path}")

        self.assertEqual(len(stories), 6)
        for s in stories:
            rel_path = s["image_url"].lstrip("/")
            file_path = BASE_DIR / rel_path
            self.assertTrue(file_path.exists(), f"Story image file missing: {file_path}")
            self.assertGreater(file_path.stat().st_size, 5000, f"Story image file empty: {file_path}")

    def test_database_schema_and_persistence(self):
        """Verifies database tables exist and saved_trips table is ready."""
        conn = get_db_connection()
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        conn.close()

        self.assertIn("places", tables)
        self.assertIn("stories", tables)
        self.assertIn("saved_trips", tables)

    def test_production_http_routes(self):
        """Smoke tests core pages via WSGI test client."""
        client = app.test_client()
        routes = ["/", "/explore", "/places/mubarak-mandi-palace", "/map", "/planner", "/stories", "/about"]
        for r in routes:
            res = client.get(r)
            self.assertEqual(res.status_code, 200, f"Failed GET {r}")

        # Test static image delivery
        img_res = client.get("/static/images/mubarak-mandi.jpg")
        self.assertEqual(img_res.status_code, 200)
        self.assertGreater(len(img_res.data), 100000)

        # Test weather endpoint handles gracefully
        weather_res = client.get("/api/weather?lat=32.7266&lon=74.8570")
        self.assertEqual(weather_res.status_code, 200)

        # Test planner recommendation
        plan_res = client.post("/api/recommend-itinerary",
                               data=json.dumps({"duration_days": 2, "interests": ["heritage"], "pace": "balanced"}),
                               content_type="application/json")
        self.assertEqual(plan_res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
