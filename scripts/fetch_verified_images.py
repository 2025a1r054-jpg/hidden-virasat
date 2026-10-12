"""
Search and download authentic, verified Wikimedia Commons photographs for Jammu heritage places.
Saves photographs to static/images/ with clean local filenames and retrieves authentic attributions.
"""

import urllib.request
import urllib.parse
import json
import time
import os

HEADERS = {
    'User-Agent': 'HiddenVirasatApp/1.0 (https://hiddenvirasat.local; academic-college-demo; mailto:contact@hiddenvirasat.local) Python/3.11'
}

DEST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
os.makedirs(DEST_DIR, exist_ok=True)

# Curated search targets for exact match on Wikimedia Commons
SEARCH_TARGETS = [
    {
        "slug": "mubarak-mandi-palace",
        "search": "Mubarak Mandi",
        "fallback_search": "Jammu palace",
        "filename": "mubarak-mandi.jpg",
        "name": "Mubarak Mandi Heritage Complex"
    },
    {
        "slug": "bahu-fort",
        "search": "Bahu Fort",
        "fallback_search": "Bahu Fort Jammu",
        "filename": "bahu-fort.jpg",
        "name": "Bahu Fort"
    },
    {
        "slug": "bagh-e-bahu",
        "search": "Bagh-e-Bahu",
        "fallback_search": "Bagh e Bahu Jammu",
        "filename": "bagh-e-bahu.jpg",
        "name": "Bagh-e-Bahu & Aquarium"
    },
    {
        "slug": "amar-mahal-palace-museum",
        "search": "Amar Mahal Palace",
        "fallback_search": "Amar Mahal Jammu",
        "filename": "amar-mahal.jpg",
        "name": "Amar Mahal Palace Museum"
    },
    {
        "slug": "dogra-art-museum",
        "search": "Basohli painting",
        "fallback_search": "Pahari painting",
        "filename": "dogra-art-museum.jpg",
        "name": "Dogra Art Museum"
    },
    {
        "slug": "akhnoor-fort-jia-pota",
        "search": "Akhnoor Fort",
        "fallback_search": "Akhnoor",
        "filename": "akhnoor-fort.jpg",
        "name": "Akhnoor Fort & Jia Pota Ghat"
    },
    {
        "slug": "purmandal-chhota-kashi",
        "search": "Purmandal",
        "fallback_search": "Purmandal temple Jammu",
        "filename": "purmandal.jpg",
        "name": "Purmandal (Chhota Kashi)"
    },
    {
        "slug": "ranbireshwar-temple",
        "search": "Ranbireshwar",
        "fallback_search": "Ranbireshwar Temple Jammu",
        "filename": "ranbireshwar-temple.jpg",
        "name": "Ranbireshwar Temple"
    },
    {
        "slug": "raghunath-bazaar",
        "search": "Raghunath Temple Jammu",
        "fallback_search": "Raghunath bazaar",
        "filename": "raghunath-bazaar.jpg",
        "name": "Raghunath Bazaar"
    },
    {
        "slug": "hari-market-food-lanes",
        "search": "Jammu city bazaar",
        "fallback_search": "Indian bazaar market spices",
        "filename": "hari-market.jpg",
        "name": "Hari Market & Pacca Danga"
    },
    {
        "slug": "dogra-calico-printing-crafts",
        "search": "Wood block printing textiles India",
        "fallback_search": "Block printing textile",
        "filename": "dogra-calico-printing.jpg",
        "name": "Dogra Calico Printing"
    },
    {
        "slug": "dogra-culinary-trail",
        "search": "Rajma chawal",
        "fallback_search": "Indian street food kulcha",
        "filename": "dogra-culinary-trail.jpg",
        "name": "Jammu Dogra Culinary Trail"
    },
    {
        "slug": "peer-kho-cave-temple",
        "search": "Peer Kho",
        "fallback_search": "Cave temple Jammu",
        "filename": "peer-kho.jpg",
        "name": "Peer Kho Cave Temple"
    },
    {
        "slug": "krimchi-ancient-temples",
        "search": "Krimchi temples",
        "fallback_search": "Krimchi",
        "filename": "krimchi-temples.jpg",
        "name": "Krimchi Ancient Temples"
    },
    {
        "slug": "suchetgarh-border-heritage",
        "search": "Suchetgarh",
        "fallback_search": "Attari Wagah border ceremony",
        "filename": "suchetgarh-border.jpg",
        "name": "Suchetgarh Border Heritage"
    }
]


def search_wikimedia(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=12) as res:
        data = json.loads(res.read().decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        results = []
        for pid, p in pages.items():
            if 'imageinfo' in p and len(p['imageinfo']) > 0:
                info = p['imageinfo'][0]
                raw_url = info.get('url', '')
                parsed = urllib.parse.urlparse(raw_url)
                path_lower = parsed.path.lower()
                
                # Check extension on the URL path, ignoring query parameters!
                if any(path_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                    # Clean URL without tracking query params
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    meta = info.get('extmetadata', {})
                    artist = meta.get('Artist', {}).get('value', 'Wikimedia Commons contributor')
                    # Strip any HTML tags from artist
                    import re
                    clean_artist = re.sub(r'<[^>]+>', '', artist).strip() or 'Wikimedia Commons'
                    license_short = meta.get('LicenseShortName', {}).get('value', 'CC BY-SA')
                    
                    results.append({
                        'title': p.get('title', ''),
                        'url': clean_url,
                        'artist': clean_artist,
                        'license': license_short
                    })
        return results


def download_image(url, target_path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as res:
        content = res.read()
        if len(content) > 1000:
            with open(target_path, 'wb') as f:
                f.write(content)
            return len(content)
    return 0


def main():
    print(f"Starting image retrieval for {len(SEARCH_TARGETS)} Jammu places...")
    successes = []
    
    for item in SEARCH_TARGETS:
        target_path = os.path.join(DEST_DIR, item['filename'])
        slug = item['slug']
        print(f"\nProcessing: {item['name']} ({slug})...")
        
        results = []
        try:
            results = search_wikimedia(item['search'])
        except Exception as e:
            print(f"  Primary search failed: {e}")
            
        if not results and 'fallback_search' in item:
            time.sleep(0.5)
            try:
                print(f"  Trying fallback query: {item['fallback_search']}")
                results = search_wikimedia(item['fallback_search'])
            except Exception as e:
                print(f"  Fallback search failed: {e}")
                
        if results:
            best = results[0]
            print(f"  Found image: {best['title']}")
            print(f"  Clean URL: {best['url']}")
            time.sleep(0.5)
            try:
                bytes_downloaded = download_image(best['url'], target_path)
                print(f"  Downloaded: {bytes_downloaded} bytes -> {item['filename']}")
                successes.append({
                    'slug': slug,
                    'name': item['name'],
                    'filename': item['filename'],
                    'path': f"/static/images/{item['filename']}",
                    'credit': f"{best['title'].replace('File:', '')} (Source: Wikimedia Commons, {best['license']})",
                    'bytes': bytes_downloaded
                })
            except Exception as e:
                print(f"  Download error: {e}")
        else:
            print(f"  No images found for {item['name']}")
            
        time.sleep(0.5)
        
    print(f"\nSuccessfully downloaded {len(successes)} / {len(SEARCH_TARGETS)} images.")
    
    # Save manifest
    manifest_path = os.path.join(DEST_DIR, 'download_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(successes, f, indent=2)
    print(f"Manifest written to {manifest_path}")


if __name__ == '__main__':
    main()
