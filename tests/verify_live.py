import urllib.request
import json
import sys

def check(url, method='GET', data=None):
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8')
    else:
        body = None
    with urllib.request.urlopen(req, data=body) as res:
        return res.status, res.read().decode('utf-8')

pages = [
    '/',
    '/explore',
    '/places/mubarak-mandi-palace',
    '/places/bahu-fort',
    '/places/amar-mahal-palace-museum',
    '/map',
    '/planner',
    '/stories',
    '/about'
]

print("--- TESTING WEB PAGES ---")
for p in pages:
    st, html = check('http://127.0.0.1:5000' + p)
    print(f"[PAGE] {p:<35} -> {st} ({len(html)} bytes)")

print("\n--- TESTING APIS ---")
st, res = check('http://127.0.0.1:5000/api/places?category=Heritage%20%26%20Forts')
d = json.loads(res)
print(f"[API]  /api/places (category)             -> {st}, count: {d['count']}")

st, res = check('http://127.0.0.1:5000/api/weather?lat=32.7266&lon=74.8570')
d = json.loads(res)
print(f"[API]  /api/weather                        -> {st}, status: {d.get('status')}, temp: {d.get('temperature')} C")

plan_payload = {
    'duration_days': 2,
    'pace': 'balanced',
    'interests': ['heritage', 'food'],
    'start_area': 'old-city'
}
st, res = check('http://127.0.0.1:5000/api/recommend-itinerary', method='POST', data=plan_payload)
d = json.loads(res)
print(f"[API]  /api/recommend-itinerary (POST)     -> {st}, days: {len(d['days'])}")

trip_payload = {
    'title': 'Faculty Live Verification Journey',
    'traveler_name': 'Evaluation Team',
    'duration_days': 2,
    'pace': 'balanced',
    'interests': ['heritage', 'food'],
    'start_area': 'old-city',
    'itinerary': d['days']
}
st, res = check('http://127.0.0.1:5000/api/trips', method='POST', data=trip_payload)
d_trip = json.loads(res)
trip_id = d_trip['trip_id']
print(f"[API]  /api/trips (POST)                   -> {st}, new trip id: {trip_id}")

st, res = check('http://127.0.0.1:5000/api/trips')
d_trips = json.loads(res)
print(f"[API]  /api/trips (GET)                    -> {st}, total saved trips: {d_trips['count']}")

st, res = check(f'http://127.0.0.1:5000/api/trips/{trip_id}', method='DELETE')
d_del = json.loads(res)
print(f"[API]  /api/trips/{trip_id} (DELETE)        -> {st}, success: {d_del.get('success')}")

print("\n--- ALL VERIFICATIONS PASSED ---")
