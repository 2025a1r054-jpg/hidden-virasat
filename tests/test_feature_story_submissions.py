import os
import json
import unittest
from app import app, ADMIN_PASSWORD
from database.db import get_db_connection


class TestStorySubmissions(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

    def tearDown(self):
        # Clean up any test records created by this test class
        conn = get_db_connection()
        conn.execute("DELETE FROM stories WHERE is_community = 1")
        conn.execute("DELETE FROM story_submissions WHERE contributor_name IN ('Raman Dev', 'SpamBot', 'Pooja Jamwal', 'Balwant Dogra', 'Rejected Submitter')")
        conn.commit()
        conn.close()

    def test_add_your_story_button_present(self):
        """Verifies + Add Your Story button is present beside Local Stories title in stories.html and index.html."""
        # 1. Dedicated stories page
        res_stories = self.client.get("/stories")
        self.assertEqual(res_stories.status_code, 200)
        self.assertIn(b"+ Add Your Story", res_stories.data)
        self.assertIn(b"/stories/submit", res_stories.data)

        # 2. Homepage stories section
        res_index = self.client.get("/")
        self.assertEqual(res_index.status_code, 200)
        self.assertIn(b"+ Add Your Story", res_index.data)
        self.assertIn(b"/stories/submit", res_index.data)

    def test_story_submission_page_loads(self):
        """Verifies GET /stories/submit renders form with all required categories and fields."""
        res = self.client.get("/stories/submit")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Add Your Local Story", res.data)
        self.assertIn(b"Folklore &amp; Legends", res.data)
        self.assertIn(b"Oral History", res.data)
        self.assertIn(b"Local Traditions", res.data)
        self.assertIn(b"Folk Tales", res.data)
        self.assertIn(b"name=\"website_url\"", res.data)  # Honeypot

    def test_submit_story_valid_form(self):
        """Tests submitting a valid community story via web form and saving as pending."""
        payload = {
            "title": "The Golden Serpent of Devika Spring",
            "category": "Folklore & Legends",
            "related_place": "Purmandal (Chhota Kashi)",
            "contributor_name": "Raman Dev",
            "content": "In ancient times, pilgrims visiting the Devika river believed a golden serpent guarded the subterranean waters during the annual Chaitra Chaudash mela.",
            "website_url": ""  # Honeypot empty
        }
        res = self.client.post("/stories/submit", data=payload, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Your Chronicle Has Been Recorded", res.data)

        # Verify saved in SQLite with status 'pending'
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM story_submissions WHERE title = ?", ("The Golden Serpent of Devika Spring",)).fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["status"], "pending")
        self.assertEqual(row["category"], "Folklore & Legends")
        self.assertEqual(row["contributor_name"], "Raman Dev")

        # Verify it does NOT appear publicly on /stories yet
        public_res = self.client.get("/stories")
        self.assertNotIn(b"The Golden Serpent of Devika Spring", public_res.data)

    def test_submit_story_honeypot_bot_rejection(self):
        """Tests that automated bot story submissions with honeypot filled are ignored."""
        payload = {
            "title": "Spam Casino Promo Story",
            "category": "Oral History",
            "content": "Spam promotional text that meets the minimum length requirement easily.",
            "contributor_name": "SpamBot",
            "website_url": "http://spambot.xyz"  # Honeypot filled!
        }
        res = self.client.post("/stories/submit", data=payload, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Ensure NOT in database
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM story_submissions WHERE title = ?", ("Spam Casino Promo Story",)).fetchone()
        conn.close()
        self.assertIsNone(row)

    def test_submit_story_validation_errors(self):
        """Tests validation failures (short title, short narrative, invalid category)."""
        payload = {
            "title": "No",  # < 5 chars
            "category": "Invalid Category Name",
            "content": "Too short",  # < 30 chars
            "contributor_name": "X",
            "website_url": ""
        }
        res = self.client.post("/stories/submit", data=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b"Please rectify the following items", res.data)

    def test_api_story_submission_json(self):
        """Tests JSON REST endpoint for story submission."""
        payload = {
            "title": "Song of the Tawi River Rafters",
            "category": "Oral History",
            "related_place": "Mubarak Mandi Palace Complex",
            "contributor_name": "Pooja Jamwal",
            "content": "Generations of boatmen on the Tawi river sang heroic verses commemorating Raja Maldev and the defense of the Jammu cliffs."
        }
        res = self.client.post("/api/stories/submit", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("status"), "pending")

    def test_admin_stories_protected_access(self):
        """Ensures /admin/stories requires authentication."""
        res = self.client.get("/admin/stories", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/login", res.headers.get("Location", ""))

    def test_admin_approve_story_workflow(self):
        """Tests admin reviewing and approving a story into public stories journal."""
        # 1. Insert a pending story submission
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO story_submissions (title, content, category, related_place, contributor_name, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (
            "Legends of the Dogra Sentry",
            "On misty winter dawns atop Bahu Fort, traditional sentries spoke of footsteps echoing along the stone ramparts.",
            "Folk Tales",
            "Bahu Fort & Kali Temple",
            "Balwant Dogra"
        ))
        conn.commit()
        sub_id = cursor.lastrowid
        conn.close()

        # 2. Authenticate admin
        with self.client.session_transaction() as sess:
            sess["is_admin"] = True

        # 3. View admin stories desk
        desk_res = self.client.get("/admin/stories")
        self.assertEqual(desk_res.status_code, 200)
        self.assertIn(b"Legends of the Dogra Sentry", desk_res.data)

        # 4. Approve story
        approve_res = self.client.post(f"/admin/stories/{sub_id}/approve", follow_redirects=True)
        self.assertEqual(approve_res.status_code, 200)

        # 5. Verify status updated to approved in story_submissions
        conn = get_db_connection()
        sub_row = conn.execute("SELECT status FROM story_submissions WHERE id = ?", (sub_id,)).fetchone()
        self.assertEqual(sub_row["status"], "approved")

        # 6. Verify story inserted into public stories table
        story_row = conn.execute("SELECT * FROM stories WHERE title = ?", ("Legends of the Dogra Sentry",)).fetchone()
        conn.close()
        self.assertIsNotNone(story_row)
        self.assertEqual(story_row["is_community"], 1)

        # 7. Verify it now appears publicly on /stories
        pub_res = self.client.get("/stories")
        self.assertEqual(pub_res.status_code, 200)
        self.assertIn(b"Legends of the Dogra Sentry", pub_res.data)

    def test_admin_reject_story(self):
        """Tests admin rejecting an inappropriate story submission."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO story_submissions (title, content, category, related_place, contributor_name, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (
            "Unrelated Modern Gossip",
            "A story with no historical or cultural relevance to Jammu heritage or Dogra culture.",
            "Oral History",
            "",
            "Rejected Submitter"
        ))
        conn.commit()
        sub_id = cursor.lastrowid
        conn.close()

        with self.client.session_transaction() as sess:
            sess["is_admin"] = True

        reject_res = self.client.post(f"/admin/stories/{sub_id}/reject", data={
            "admin_notes": "Not relevant to Duggar folklore."
        }, follow_redirects=True)
        self.assertEqual(reject_res.status_code, 200)

        conn = get_db_connection()
        sub_row = conn.execute("SELECT status, admin_notes FROM story_submissions WHERE id = ?", (sub_id,)).fetchone()
        conn.close()
        self.assertEqual(sub_row["status"], "rejected")
        self.assertIn("Not relevant", sub_row["admin_notes"])


if __name__ == "__main__":
    unittest.main()
