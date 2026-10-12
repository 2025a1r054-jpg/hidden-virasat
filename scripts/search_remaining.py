import urllib.request
import urllib.parse
import json

headers = {'User-Agent': 'HiddenVirasatApp/1.0 (academic-demo) Python/3.11'}

def search_files(q):
    url = f'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&srnamespace=6&srlimit=5&format=json'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            for item in data.get('query', {}).get('search', []):
                print(f"[{q}] -> {item['title']}")
    except Exception as e:
        print(f"Error {q}: {e}")

search_files('Ranbireshwar')
search_files('Peer Kho')
search_files('Tawi River Jammu')
search_files('Sialkot railway')
search_files('Suchetgarh')
