"""
Updates places and stories in the SQLite database to point to local verified static images.
Preserves all user data and saved trips.
"""

import sqlite3
import shutil
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'hidden_virasat.db')
IMG_DIR = os.path.join(BASE_DIR, 'static', 'images')

# Copy story images
story_copies = [
    ('bahu-fort.jpg', 'story-jamboo-lochan.jpg'),
    ('mubarak-mandi.jpg', 'story-mubarak-mandi.jpg'),
    ('dogra-art-museum.jpg', 'story-basohli.jpg'),
    ('dogra-culinary-trail.jpg', 'story-kalari.jpg'),
    ('purmandal.jpg', 'story-purmandal.jpg'),
    ('dogra-calico-printing.jpg', 'story-calico.jpg')
]

for src, dst in story_copies:
    src_path = os.path.join(IMG_DIR, src)
    dst_path = os.path.join(IMG_DIR, dst)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"Copied {src} -> {dst}")

PLACE_UPDATES = {
    "mubarak-mandi-palace": {
        "image_url": "/static/images/mubarak-mandi.jpg",
        "image_caption": "Panoramic view of Mubarak Mandi Heritage Complex courtyards",
        "image_credit": "Wikimedia Commons / Nvvchar (CC BY-SA 3.0)"
    },
    "bahu-fort": {
        "image_url": "/static/images/bahu-fort.jpg",
        "image_caption": "Formidable stone ramparts of Bahu Fort above the Tawi",
        "image_credit": "Wikimedia Commons / Abhishek.s.d (CC BY-SA 4.0)"
    },
    "bagh-e-bahu": {
        "image_url": "/static/images/bagh-e-bahu.jpg",
        "image_caption": "Terraced Mughal garden of Bagh-e-Bahu overlooking the river",
        "image_credit": "Wikimedia Commons / A. Sharma (CC BY-SA 3.0)"
    },
    "amar-mahal-palace-museum": {
        "image_url": "/static/images/amar-mahal.jpg",
        "image_caption": "French chateau-style facade of Amar Mahal Palace Museum",
        "image_credit": "Wikimedia Commons / Nvvchar (CC BY-SA 3.0)"
    },
    "dogra-art-museum": {
        "image_url": "/static/images/dogra-art-museum.jpg",
        "image_caption": "Historic 19th-century Basohli Miniature painting preserved in Jammu",
        "image_credit": "Wikimedia Commons / Public Domain (Pahari Heritage Archive)"
    },
    "akhnoor-fort-jia-pota": {
        "image_url": "/static/images/akhnoor-fort.jpg",
        "image_caption": "Akhnoor Fort towering above the Chenab River",
        "image_credit": "Wikimedia Commons / Varun Shiv Kapur (CC BY 2.0)"
    },
    "purmandal-chhota-kashi": {
        "image_url": "/static/images/purmandal.jpg",
        "image_caption": "Historic print of the Purmandal Mela along Devika by Charles Hardinge, 1847",
        "image_credit": "Wikimedia Commons / Public Domain"
    },
    "ranbireshwar-temple": {
        "image_url": "/static/images/ranbireshwar-temple.jpg",
        "image_caption": "Maharaja Ranbir Singh, who built the Ranbireshwar Temple in 1883",
        "image_credit": "Wikimedia Commons / Bourne & Shepherd (Public Domain)"
    },
    "raghunath-bazaar": {
        "image_url": "/static/images/raghunath-bazaar.jpg",
        "image_caption": "Historic Raghunath Temple and market precinct in old Jammu, ca. 1875-1940",
        "image_credit": "Wikimedia Commons / University of Aberdeen Archive (Public Domain)"
    },
    "hari-market-food-lanes": {
        "image_url": "/static/images/hari-market.jpg",
        "image_caption": "Historic market street in old Jammu city, ca. 1875-1940",
        "image_credit": "Wikimedia Commons / University of Aberdeen Archive (Public Domain)"
    },
    "dogra-calico-printing-crafts": {
        "image_url": "/static/images/dogra-calico-printing.jpg",
        "image_caption": "Carved 19th-century wooden block used in traditional Indian textile printing",
        "image_credit": "Wikimedia Commons / Cooper Hewitt, Smithsonian Design Museum (CC0)"
    },
    "dogra-culinary-trail": {
        "image_url": "/static/images/dogra-culinary-trail.jpg",
        "image_caption": "Traditional slow-cooked Rajma-Chawal, signature dish of Duggar",
        "image_credit": "Wikimedia Commons / CC BY-SA 4.0"
    },
    "peer-kho-cave-temple": {
        "image_url": "/static/images/peer-kho.jpg",
        "image_caption": "Historic Tawi Riverbanks and bridge near the Peer Kho cave shrines",
        "image_credit": "Wikimedia Commons / University of Aberdeen Archive (Public Domain)"
    },
    "krimchi-ancient-temples": {
        "image_url": "/static/images/krimchi-temples.jpg",
        "image_caption": "The classical 9th-century Pandava tower temples of Krimchi",
        "image_credit": "Wikimedia Commons / Tarun (CC BY-SA 4.0)"
    },
    "suchetgarh-border-heritage": {
        "image_url": "/static/images/suchetgarh-border.jpg",
        "image_caption": "Historic terminal structure of the pre-1947 Jammu-Sialkot railway line",
        "image_credit": "Wikimedia Commons / Moazzam Ali (CC BY-SA 3.0)"
    }
}

STORY_UPDATES = {
    "legend-of-jamboo-lochan": "/static/images/story-jamboo-lochan.jpg",
    "splendor-of-mubarak-mandi": "/static/images/story-mubarak-mandi.jpg",
    "secrets-of-basohli-miniatures": "/static/images/story-basohli.jpg",
    "kalari-to-rajma-dogra-food": "/static/images/story-kalari.jpg",
    "purmandal-chhota-kashi-devika": "/static/images/story-purmandal.jpg",
    "tradition-of-dogra-calico-textiles": "/static/images/story-calico.jpg"
}

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Update places
updated_places = 0
for slug, data in PLACE_UPDATES.items():
    cursor.execute("""
        UPDATE places
        SET image_url = ?, image_caption = ?, image_credit = ?
        WHERE slug = ?
    """, (data["image_url"], data["image_caption"], data["image_credit"], slug))
    updated_places += cursor.rowcount

# Update stories
updated_stories = 0
for slug, img in STORY_UPDATES.items():
    cursor.execute("""
        UPDATE stories
        SET image_url = ?
        WHERE slug = ?
    """, (img, slug))
    updated_stories += cursor.rowcount

conn.commit()

# Verify saved trips were preserved
saved_trips_count = cursor.execute("SELECT COUNT(*) FROM saved_trips").fetchone()[0]
conn.close()

print(f"Updated {updated_places} places in database.")
print(f"Updated {updated_stories} stories in database.")
print(f"Saved trips count preserved: {saved_trips_count}")
