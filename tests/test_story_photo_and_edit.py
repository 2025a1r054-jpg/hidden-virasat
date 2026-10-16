"""
Unit & Integration Tests for Local Stories: Photo Upload and Contributor Edit Workflow
Tests image validation, secure upload handling, passkey ownership verification,
story ID preservation, status lifecycle reversion to pending upon edit,
and admin re-approval without duplicate records.
"""

import io
import os
import json
import unittest
from pathlib import Path

from app import app, ADMIN_PASSWORD
from database.db import get_db_connection


class TestStoryPhotoAndEdit(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self.created_upload_files = []

    def tearDown(self):
        # Clean up database records
        conn = get_db_connection()
        conn.execute("DELETE FROM stories WHERE is_community = 1")
        conn.execute("DELETE FROM story_submissions WHERE contributor_name LIKE 'TestContributor%'")
        conn.commit()
        conn.close()

        # Clean up any test files written to static/images/uploads/
        for filepath in self.created_upload_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except OSError:
                pass

    def _track_and_get_path(self, image_url):
        if image_url and image_url.startswith("/static/images/uploads/"):
            filename = image_url.replace("/static/images/uploads/", "")
            full_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            self.created_upload_files.append(full_path)
            return full_path
        return None

    def test_submit_story_with_valid_photo(self):
        """Tests submitting a story with an optional JPEG photo upload."""
        fake_image = (io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"A" * 100), "bahu_gateway.jpg")
        data = {
            "title": "The Whispering Stone of Bahu Gateway",
            "category": "Folklore & Legends",
            "related_place": "Bahu Fort & Kali Temple",
            "contributor_name": "TestContributor One",
            "content": "Legend recounts an ancient carved sentry stone at the lower gate that hummed when mountain winds passed through the gorge.",
            "image_file": fake_image,
            "website_url": ""
        }
        res = self.client.post("/stories/submit", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Your Chronicle Has Been Recorded", res.data)
        self.assertIn(b"Private Story Revision Link", res.data)
        self.assertIn(b"Access Key:", res.data)

        # Check database
        conn = get_db_connection()
        sub = conn.execute("SELECT * FROM story_submissions WHERE contributor_name = 'TestContributor One'").fetchone()
        conn.close()

        self.assertIsNotNone(sub)
        self.assertEqual(sub["title"], "The Whispering Stone of Bahu Gateway")
        self.assertIsNotNone(sub["image_url"])
        self.assertTrue(sub["image_url"].startswith("/static/images/uploads/story_"))
        self.assertTrue(sub["image_url"].endswith("bahu_gateway.jpg"))
        self.assertIsNotNone(sub["edit_token"])
        self.assertGreaterEqual(len(sub["edit_token"]), 16)

        upload_path = self._track_and_get_path(sub["image_url"])
        self.assertTrue(os.path.exists(upload_path))

    def test_submit_story_invalid_photo_extension_rejected(self):
        """Tests that non-image file uploads are safely rejected."""
        fake_bad_file = (io.BytesIO(b"malicious executable or text"), "script.sh")
        data = {
            "title": "Invalid Extension Chronicle",
            "category": "Oral History",
            "related_place": "Mubarak Mandi Palace Complex",
            "contributor_name": "TestContributor BadExt",
            "content": "A story submitted with an invalid script attachment to test upload sanitation.",
            "image_file": fake_bad_file,
            "website_url": ""
        }
        res = self.client.post("/stories/submit", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 400)
        self.assertIn(b"Story photograph must be a valid image", res.data)

    def test_edit_authorization_challenge_and_unauthorized_key(self):
        """Tests passkey ownership challenge and rejection of invalid keys."""
        # Insert test submission
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO story_submissions (title, content, category, related_place, contributor_name, edit_token, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """, ("Secret Shrine Tale", "A secret shrine oral tale with sufficient narrative length for validation.",
              "Folk Tales", "Bahu Fort & Kali Temple", "TestContributor Auth", "secret-test-key-12345"))
        conn.commit()
        sub_id = cur.lastrowid
        conn.close()

        # 1. Access without key -> should show passkey entry challenge prompt
        res_no_key = self.client.get(f"/stories/{sub_id}/edit")
        self.assertEqual(res_no_key.status_code, 200)
        self.assertIn(b"Contributor Verification", res_no_key.data)
        self.assertIn(b"Story Edit Access", res_no_key.data)
        self.assertIn(b"Private Edit Key", res_no_key.data)

        # 2. Access with wrong key -> returns 403 Forbidden
        res_wrong_key = self.client.get(f"/stories/{sub_id}/edit?key=wrong-invalid-key")
        self.assertEqual(res_wrong_key.status_code, 403)
        self.assertIn(b"Invalid or missing private story edit key", res_wrong_key.data)

    def test_contributor_can_edit_story_content(self):
        """Tests authorized contributor editing title, narrative, and category with preserved ID."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO story_submissions (title, content, category, related_place, contributor_name, edit_token, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """, ("Original Title Here", "Original long narrative describing Dogra traditions and folklore in Jammu hills.",
              "Local Traditions", "Mubarak Mandi Palace Complex", "TestContributor Edit1", "editkey-token-abcd-1234"))
        conn.commit()
        sub_id = cur.lastrowid
        conn.close()

        # Authorized GET loads pre-filled form
        res_get = self.client.get(f"/stories/{sub_id}/edit?key=editkey-token-abcd-1234")
        self.assertEqual(res_get.status_code, 200)
        self.assertIn(b"Original Title Here", res_get.data)

        # POST updated content
        update_data = {
            "edit_key": "editkey-token-abcd-1234",
            "title": "Revised Title by Author",
            "category": "Oral History",
            "related_place": "Akhnoor Fort & Jia Pota Ghat",
            "contributor_name": "TestContributor Edit1",
            "content": "Updated oral history narrative containing far more historical context and regional depth.",
            "website_url": ""
        }
        res_post = self.client.post(f"/stories/{sub_id}/edit", data=update_data)
        self.assertEqual(res_post.status_code, 200)
        self.assertIn(b"Changes Successfully Saved!", res_post.data)

        # Verify database record updated in place with same ID
        conn = get_db_connection()
        sub = conn.execute("SELECT * FROM story_submissions WHERE id = ?", (sub_id,)).fetchone()
        conn.close()

        self.assertEqual(sub["title"], "Revised Title by Author")
        self.assertEqual(sub["category"], "Oral History")
        self.assertIn("Updated oral history", sub["content"])

    def test_add_photo_later_to_existing_story(self):
        """Tests that a story submitted without a photo can have an image added later during edit."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO story_submissions (title, content, category, related_place, contributor_name, image_url, edit_token, status)
            VALUES (?, ?, ?, ?, ?, NULL, ?, 'pending')
        """, ("Story Without Initial Photo", "Narrative created without an image originally to verify later photo addition.",
              "Oral History", "Peer Kho Cave Temple", "TestContributor PhotoAdd", "token-photo-add-999"))
        conn.commit()
        sub_id = cur.lastrowid
        conn.close()

        # Contributor uploads a WebP photo
        fake_webp = (io.BytesIO(b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"X" * 60), "peer_kho_night.webp")
        update_data = {
            "edit_key": "token-photo-add-999",
            "title": "Story Without Initial Photo",
            "category": "Oral History",
            "related_place": "Peer Kho Cave Temple",
            "contributor_name": "TestContributor PhotoAdd",
            "content": "Narrative created without an image originally to verify later photo addition.",
            "image_file": fake_webp,
            "website_url": ""
        }
        res = self.client.post(f"/stories/{sub_id}/edit", data=update_data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)

        # Verify photo was added
        conn = get_db_connection()
        sub = conn.execute("SELECT * FROM story_submissions WHERE id = ?", (sub_id,)).fetchone()
        conn.close()

        self.assertIsNotNone(sub["image_url"])
        self.assertTrue(sub["image_url"].endswith("peer_kho_night.webp"))
        upload_path = self._track_and_get_path(sub["image_url"])
        self.assertTrue(os.path.exists(upload_path))

    def test_approved_story_edit_reverts_to_pending_and_hides_from_public(self):
        """
        Tests that editing an already-approved story sends it back to Pending Review,
        hiding it from the public stories page until re-approved.
        """
        # 1. Contributor submits story
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO story_submissions (title, content, category, related_place, contributor_name, edit_token, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """, ("The Royal Falconer", "An archival chronicle detailing the royal hunting falconers of Dogra kings.",
              "Folklore & Legends", "Mubarak Mandi Palace Complex", "TestContributor Lifecycle", "falcon-key-777"))
        conn.commit()
        sub_id = cur.lastrowid
        conn.close()

        # 2. Admin approves story
        with self.client.session_transaction() as sess:
            sess["is_admin"] = True
        approve_res = self.client.post(f"/admin/stories/{sub_id}/approve", follow_redirects=True)
        self.assertEqual(approve_res.status_code, 200)

        # Verify it appears publicly
        pub_res = self.client.get("/stories")
        self.assertIn(b"The Royal Falconer", pub_res.data)

        # 3. Contributor edits the story
        with self.client.session_transaction() as sess:
            sess["is_admin"] = False  # regular visitor mode

        edit_data = {
            "edit_key": "falcon-key-777",
            "title": "The Royal Falconer (Revised Edition)",
            "category": "Folklore & Legends",
            "related_place": "Mubarak Mandi Palace Complex",
            "contributor_name": "TestContributor Lifecycle",
            "content": "An expanded archival chronicle detailing the royal hunting falconers of Dogra kings with newly discovered oral verses.",
            "website_url": ""
        }
        edit_res = self.client.post(f"/stories/{sub_id}/edit", data=edit_data)
        self.assertEqual(edit_res.status_code, 200)

        # 4. Verify status reverted to pending in both tables
        conn = get_db_connection()
        sub_row = conn.execute("SELECT status FROM story_submissions WHERE id = ?", (sub_id,)).fetchone()
        story_row = conn.execute("SELECT status FROM stories WHERE submission_id = ?", (sub_id,)).fetchone()
        conn.close()

        self.assertEqual(sub_row["status"], "pending")
        self.assertEqual(story_row["status"], "pending")

        # 5. Verify it is now HIDDEN from public /stories and /api/stories
        pub_res2 = self.client.get("/stories")
        self.assertNotIn(b"The Royal Falconer (Revised Edition)", pub_res2.data)
        self.assertNotIn(b"The Royal Falconer", pub_res2.data)

        api_res = self.client.get("/api/stories")
        self.assertNotIn("The Royal Falconer", api_res.get_data(as_text=True))

        # 6. Admin re-approves the edited story
        with self.client.session_transaction() as sess:
            sess["is_admin"] = True
        reapprove_res = self.client.post(f"/admin/stories/{sub_id}/approve", follow_redirects=True)
        self.assertEqual(reapprove_res.status_code, 200)

        # 7. Verify updated story is now live and NO duplicate rows were created
        conn = get_db_connection()
        all_falcon_stories = conn.execute("SELECT * FROM stories WHERE submission_id = ?", (sub_id,)).fetchall()
        conn.close()

        self.assertEqual(len(all_falcon_stories), 1, "Should NOT duplicate stories row upon re-approval")
        self.assertEqual(all_falcon_stories[0]["title"], "The Royal Falconer (Revised Edition)")
        self.assertEqual(all_falcon_stories[0]["status"], "approved")

        # 8. Verify it now displays on public /stories
        pub_res3 = self.client.get("/stories")
        self.assertIn(b"The Royal Falconer (Revised Edition)", pub_res3.data)

    def test_admin_direct_edit_access(self):
        """Tests that an authenticated admin can access edit form directly without a contributor key."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO story_submissions (title, content, category, related_place, contributor_name, edit_token, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """, ("Admin Direct Edit Tale", "Narrative created to verify admin bypasses the passkey gate.",
              "Folk Tales", "Bahu Fort & Kali Temple", "TestContributor AdminAccess", "admin-unneeded-key-555"))
        conn.commit()
        sub_id = cur.lastrowid
        conn.close()

        with self.client.session_transaction() as sess:
            sess["is_admin"] = True

        res = self.client.get(f"/stories/{sub_id}/edit")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Revise Your Story", res.data)
        self.assertIn(b"Story Revision Portal", res.data)


if __name__ == "__main__":
    unittest.main()
