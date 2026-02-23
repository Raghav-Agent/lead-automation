import requests
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

OSM_USER_AGENT = config['places']['osm']['user_agent']
query = "dental clinics in Mumbai, India"
url = "https://nominatim.openstreetmap.org/search"
params = {
    "q": query,
    "format": "json",
    "limit": 10,
    "addressdetails": 1,
    "extratags": 1
}
headers = {"User-Agent": OSM_USER_AGENT}
resp = requests.get(url, params=params, headers=headers, timeout=10)
print("Status:", resp.status_code)
if resp.status_code == 200:
    data = resp.json()
    print("Results count:", len(data))
    for r in data[:3]:
        print("Name:", r.get('name'))
        print("Display:", r.get('display_name')[:100])
        print("---")
else:
    print("Error:", resp.text)
