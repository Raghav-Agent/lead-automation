import requests
import yaml
import time
from db import Session, Lead
from datetime import datetime

with open('config.yaml') as f:
    config = yaml.safe_load(f)

PLACES_PROVIDER = config['places']['provider']
OSM_USER_AGENT = config['places']['osm']['user_agent']
OSM_MAX_RESULTS = config['places']['osm']['max_results']

def search_osm(query, lat=None, lon=None, radius=10000):
    """
    Use OpenStreetMap Nominatim to find businesses.
    For free-form queries, use 'q' parameter. For bounded search, use viewbox.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": OSM_MAX_RESULTS,
        "addressdetails": 1,
        "extratags": 1
    }
    if lat and lon:
        params["viewbox"] = f"{lon-0.1},{lat-0.1},{lon+0.1},{lat+0.1}"
        params["bounded"] = 1
    headers = {"User-Agent": OSM_USER_AGENT}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"OSM request failed: {e}")
        return []
    results = []
    for place in data:
        name = place.get('name')
        if not name:
            # Fallback: use first part of display_name
            display = place.get('display_name', '')
            name = display.split(',')[0] if display else 'Unknown'
        address = place.get('display_name')
        website = None
        if isinstance(place.get('extratags'), dict):
            website = place['extratags'].get('website')
        results.append({
            "name": name,
            "address": address,
            "website": website,
            "osm_id": place.get('osm_id')
        })
    return results

def find_leads():
    session = Session()
    # Build queries: if search.queries is empty, generate from niche + location
    base_queries = config['search'].get('queries', [])
    location = config.get('location')
    niche = config['niche']
    if not base_queries:
        if location:
            base_queries = [f"{niche} in {location}"]
        else:
            base_queries = [niche]
    queries = base_queries
    for q in queries:
        print(f"Finding leads for: {q}")
        try:
            results = search_osm(q)
        except Exception as e:
            import traceback
            traceback.print_exc()
            results = []
        print(f"Found {len(results)} results")
        for r in results:
            # Avoid duplicates by name+address or source_url
            existing = session.query(Lead).filter_by(name=r['name'], address=r['address']).first()
            if not existing:
                lead = Lead(
                    name=r['name'],
                    email=None,
                    phone=None,
                    address=r['address'],
                    source_url=r.get('website') or '',
                    niche=niche,
                    status='new',
                    created_at=datetime.utcnow()
                )
                session.add(lead)
        session.commit()
        time.sleep(1)  # be polite to OSM
    session.close()
    print("Lead finding complete.")

if __name__ == '__main__':
    find_leads()
