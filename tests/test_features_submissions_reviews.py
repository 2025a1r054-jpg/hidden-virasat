import os
import json
import unittest
from app import app, ADMIN_PASSWORD
from database.db import get_db_connection, init_db


class TestCommunitySubmissionsAndReviews(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

    def tearDown(self):
        # Clean up any test records created by this test class
        conn = get_db_connection()
        conn.execute("DELETE FROM places WHERE is_community = 1")
        conn.execute("DELETE FROM community_submissions WHERE submitter_name IN ('Raman Sharma', 'SpamBot', 'Vikram Dev', 'Harpreet Singh', 'Tester')")
        conn.execute("DELETE FROM reviews WHERE author_name IN ('Sunita Jamwal', 'Aarav Dogra', 'Questionable User')")
        conn.commit()
        conn.close()

    def test_suggest_page_loads(self):
        """Verifies that the /suggest community form loads with 200 OK."""
        res = self.client.get("/suggest")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Suggest a Forgotten Sanctuary", res.data)
        self.assertIn(b"name=\"website_url\"", res.data)  # Honeypot field exists

    def test_submit_place_form_valid(self):
        """Tests submitting a valid community place via the web form."""
        payload = {
            "name": "Basohli Citadel Ruins",
            "category": "Heritage & Forts",
            "location": "Basohli, Kathua",
            "address": "Overlooking Ranjit Sagar Lake, Basohli",
            "latitude": "32.4350",
            "longitude": "75.8150",
            "short_desc": "Ancient ruined citadel overlooking the sacred waters of Ranjit Sagar lake with historical Dogra wall fragments.",
            "history": "Belonged to the Pal and Dogra lineages of Basohli principality.",
            "cultural_significance": "Cradle of Basohli miniature painting tradition.",
            "things_to_see": "Scenic lake vistas and stone ramparts.",
            "best_time": "October to March",
            "submitter_name": "Raman Sharma",
            "submitter_email": "raman@basohli.org",
            "website_url": ""  # Honeypot left empty
        }
        res = self.client.post("/suggest", data=payload, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Thank You for Contributing to Duggar Virasat", res.data)

        # Verify it was saved as 'pending' in database
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM community_submissions WHERE name = ?", ("Basohli Citadel Ruins",)).fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["status"], "pending")
        self.assertEqual(row["location"], "Basohli, Kathua")

    def test_submit_place_honeypot_bot_rejected(self):
        """Tests that automated bot submissions with honeypot filled are discarded."""
        payload = {
            "name": "Spam Casino Place",
            "category": "Heritage & Forts",
            "location": "Spam Area",
            "short_desc": "Spam description that is sufficiently long for length checks.",
            "submitter_name": "SpamBot",
            "website_url": "http://spamsite.xyz"  # Honeypot filled!
        }
        res = self.client.post("/suggest", data=payload, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Ensure NOT added to database
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM community_submissions WHERE name = ?", ("Spam Casino Place",)).fetchone()
        conn.close()
        self.assertIsNone(row)

    def test_submit_place_validation_errors(self):
        """Tests validation failures (short desc too short, name missing)."""
        payload = {
            "name": "A",  # too short
            "category": "",  # missing
            "location": "",
            "short_desc": "Too short",  # less than 20 chars
            "submitter_name": "",
            "website_url": ""
        }
        res = self.client.post("/suggest", data=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn(b"Please rectify the following items", res.data)

    def test_api_community_submission_json(self):
        """Tests JSON REST endpoint for community submissions."""
        payload = {
            "name": "Jasrota Palace Sanctuary",
            "category": "Heritage & Forts",
            "location": "Jasrota, Kathua",
            "latitude": 32.4800,
            "longitude": 75.4200,
            "short_desc": "Magnificent sprawling palace ruins surrounded by the Jasrota Wildlife Sanctuary and ancient baolis.",
            "submitter_name": "Vikram Dev",
            "submitter_email": "vikram@dogra.in"
        }
        res = self.client.post("/api/community-submissions", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("status"), "pending")

    def test_admin_access_protection(self):
        """Ensures /admin and moderation routes redirect unauthorized users."""
        res = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/login", res.headers.get("Location", ""))

        res_sub = self.client.get("/admin/submissions", follow_redirects=False)
        self.assertEqual(res_sub.status_code, 302)

    def test_admin_login_and_approval_workflow(self):
        """Tests admin login, submission review, and approval into public places."""
        # 1. First insert a pending submission
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO community_submissions (
                name, category, location, short_desc, submitter_name, status
            ) VALUES (?, ?, ?, ?, ?, 'pending')
        """, (
            "Dhanidhar Fort Rajouri",
            "Heritage & Forts",
            "Rajouri",
            "Historic high elevation fortress commanding valley views of Rajouri town built during Dogra reign.",
            "Harpreet Singh"
        ))
        conn.commit()
        sub_id = cursor.lastrowid
        conn.close()

        # 2. Login as admin
        login_res = self.client.post("/admin/login", data={"password": ADMIN_PASSWORD}, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        # 3. View admin dashboard
        dash_res = self.client.get("/admin")
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b"Curation Administration", dash_res.data)

        # 4. Approve the pending submission
        approve_res = self.client.post(f"/admin/submissions/{sub_id}/approve", follow_redirects=True)
        self.assertEqual(approve_res.status_code, 200)

        # 5. Verify submission status updated to 'approved'
        conn = get_db_connection()
        sub_row = conn.execute("SELECT status FROM community_submissions WHERE id = ?", (sub_id,)).fetchone()
        self.assertEqual(sub_row["status"], "approved")

        # 6. Verify newly approved place exists in public 'places' table with is_community = 1
        place_row = conn.execute("SELECT * FROM places WHERE name = ?", ("Dhanidhar Fort Rajouri",)).fetchone()
        conn.close()
        self.assertIsNotNone(place_row)
        self.assertEqual(place_row["is_community"], 1)

        # 7. Verify it appears in /api/places search
        api_res = self.client.get(f"/api/places/{place_row['slug']}")
        self.assertEqual(api_res.status_code, 200)
        place_json = api_res.get_json()
        self.assertEqual(place_json["name"], "Dhanidhar Fort Rajouri")

    def test_admin_reject_submission(self):
        """Tests admin rejection of invalid or inappropriate submission."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO community_submissions (
                name, category, location, short_desc, submitter_name, status
            ) VALUES (?, ?, ?, ?, ?, 'pending')
        """, (
            "Irrelevant Commercial Mall",
            "Local Markets",
            "New City",
            "Modern shopping center with glass facade and international brands.",
            "Tester"
        ))
        conn.commit()
        sub_id = cursor.lastrowid
        conn.close()

        # Authenticate
        with self.client.session_transaction() as sess:
            sess["is_admin"] = True

        res = self.client.post(f"/admin/submissions/{sub_id}/reject", data={
            "admin_notes": "Not a traditional heritage or cultural landmark."
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        conn = get_db_connection()
        row = conn.execute("SELECT status, admin_notes FROM community_submissions WHERE id = ?", (sub_id,)).fetchone()
        conn.close()
        self.assertEqual(row["status"], "rejected")
        self.assertIn("Not a traditional heritage", row["admin_notes"])

    def test_place_reviews_api_and_form(self):
        """Tests submitting a review via web form and API, checking ratings calculation."""
        conn = get_db_connection()
        place = conn.execute("SELECT id, slug FROM places LIMIT 1").fetchone()
        place_id = place["id"]
        place_slug = place["slug"]
        conn.close()

        # 1. Submit review via JSON API
        api_rev = {
            "author_name": "Sunita Jamwal",
            "rating": 5,
            "review_text": "An unforgettable spiritual and historical experience walking through these ancient courtyards."
        }
        post_res = self.client.post(f"/api/places/{place_slug}/reviews", json=api_rev)
        self.assertEqual(post_res.status_code, 201)
        data = post_res.get_json()
        self.assertTrue(data.get("success"))

        # 2. Get reviews for this place
        get_res = self.client.get(f"/api/places/{place_slug}/reviews")
        self.assertEqual(get_res.status_code, 200)
        rev_data = get_res.get_json()
        self.assertGreaterEqual(rev_data["count"], 1)
        self.assertIsNotNone(rev_data["average_rating"])

        # 3. Submit review via Web Form
        form_payload = {
            "author_name": "Aarav Dogra",
            "rating": "4",
            "review_text": "Wonderful architecture and preservation work. Highly recommended for travelers.",
            "website_url": ""
        }
        form_res = self.client.post(f"/places/{place_slug}/review", data=form_payload, follow_redirects=True)
        self.assertEqual(form_res.status_code, 200)
        self.assertIn(b"Your reflection has been recorded", form_res.data)

    def test_review_validation_and_reporting(self):
        """Tests review validation, reporting inappropriate review, and auto-flagging."""
        conn = get_db_connection()
        place = conn.execute("SELECT id, slug FROM places LIMIT 1").fetchone()
        place_id = place["id"]
        place_slug = place["slug"]

        # Insert a test review to report
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reviews (place_id, place_slug, author_name, rating, review_text, status, reported_count)
            VALUES (?, ?, ?, ?, ?, 'approved', 0)
        """, (place_id, place_slug, "Questionable User", 1, "Testing report functionality for offensive text."))
        conn.commit()
        rev_id = cursor.lastrowid
        conn.close()

        # Report 1st time
        r1 = self.client.post(f"/api/reviews/{rev_id}/report")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.get_json()["reported_count"], 1)

        # Report 2nd time
        r2 = self.client.post(f"/api/reviews/{rev_id}/report")
        self.assertEqual(r2.get_json()["reported_count"], 2)
        self.assertFalse(r2.get_json()["flagged"])

        # Report 3rd time (threshold reached -> auto-flag)
        r3 = self.client.post(f"/api/reviews/{rev_id}/report")
        self.assertEqual(r3.get_json()["reported_count"], 3)
        self.assertTrue(r3.get_json()["flagged"])

        # Check DB status
        conn = get_db_connection()
        row = conn.execute("SELECT status, reported_count FROM reviews WHERE id = ?", (rev_id,)).fetchone()
        conn.close()
        self.assertEqual(row["status"], "flagged")
        self.assertEqual(row["reported_count"], 3)

        # Admin moderation: approve and clear flags
        with self.client.session_transaction() as sess:
            sess["is_admin"] = True
        app_res = self.client.post(f"/admin/reviews/{rev_id}/approve", follow_redirects=True)
        self.assertEqual(app_res.status_code, 200)

        conn = get_db_connection()
        row = conn.execute("SELECT status, reported_count FROM reviews WHERE id = ?", (rev_id,)).fetchone()
        conn.close()
        self.assertEqual(row["status"], "approved")
        self.assertEqual(row["reported_count"], 0)

        # Admin delete review
        del_res = self.client.post(f"/admin/reviews/{rev_id}/delete", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)

        conn = get_db_connection()
        deleted_row = conn.execute("SELECT * FROM reviews WHERE id = ?", (rev_id,)).fetchone()
        conn.close()
        self.assertIsNone(deleted_row)


if __name__ == "__main__":
    unittest.main()
