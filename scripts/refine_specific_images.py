import urllib.request
import urllib.parse
import json
import time
import os

HEADERS = {
    'User-Agent': 'HiddenVirasatApp/1.0 (academic-college-demo; student@demo.edu) Python/3.11'
}

DEST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')

SPECIFIC_REPLACEMENTS = [
    {
        "title": "File:Another view of Bahu Fort from the garden.jpg",
        "file": "bagh-e-bahu.jpg"
    },
    {
        "title": "File:Amar Mahal Museum, Jammu.jpg",
        "file": "amar-mahal.jpg"
    },
    {
        "title": "File:River Tawi and Bridge, Jammu, India, ca.1875-ca.1940 (imp-cswc-GB-237-CSWC47-LS10-004).jpg",
        "file": "peer-kho.jpg"
    },
    {
        "title": "File:Sialkot Junction railway station 3.jpg",
        "file": "suchetgarh-border.jpg"
    },
    {
        "title": "File:The Temples of Raghunath, Jammu, India, ca.1875-ca.1940 (imp-cswc-GB-237-CSWC47-LS10-011).jpg",
        "file": "raghunath-bazaar.jpg"
    }
]

for item in SPECIFIC_REPLACEMENTS:
    title = item["title"]
    filename = item["file"]
    target = os.path.join(DEST_DIR, filename)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as res:
            data = json.loads(res.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, p in pages.items():
                if 'imageinfo' in p and len(p['imageinfo']) > 0:
                    raw_url = p['imageinfo'][0]['url']
                    parsed = urllib.parse.urlparse(raw_url)
                    direct_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    print(f"Downloading {title} -> {filename}...")
                    img_req = urllib.request.Request(direct_url, headers=HEADERS)
                    with urllib.request.urlopen(img_req, timeout=25) as img_res:
                        content = img_res.read()
                        with open(target, 'wb') as f:
                            f.write(content)
                        print(f"  Successfully wrote {len(content)} bytes to {filename}")
    except Exception as e:
        print(f"Error {title}: {e}")
    time.sleep(1)

print("Specific replacements complete.")
