import os
import yaml
import requests
from db import Session, Lead
from datetime import datetime
import time
from urllib.parse import quote_plus

with open('config.yaml') as f:
    config = yaml.safe_load(f)

PROVIDER = config['places']['provider']

def find_places_yelp(niche, location, radius=None, max_results=None):
    """
    Find businesses using Yelp Fusion API (free tier 5000/day).
    Requires YELP_API_KEY env var.
    """
    api_key = os.getenv('YELP_API_KEY')
    if not api_key:
        raise ValueError("YELP_API_KEY not set")
    if radius is None:
        radius = config['places']['yelp']['radius']
    if max_results is None:
        max_results = config['places']['yelp']['max_results']
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "term": niche,
        "location": location,
        "radius": radius,
        "limit": min(max_results, 50)  # Yelp max per page
    }
    places = []
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for biz in data.get('businesses', []):
            places.append({
                'name': biz.get('name'),
                'address': ' '.join(biz.get('location', {}).get('display_address', [])),
                'website': biz.get('url'),  # Yelp provides a Yelp URL, not business website
                'place_id': biz.get('id'),
                'location': biz.get('coordinates')
            })
            if len(places) >= max_results:
                break
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise ValueError(f"Invalid location or parameters: {e.response.text}")
        else:
            raise
    return places

def find_places_osm(niche, location, radius=None, max_results=None):
    """
    Find businesses using OpenStreetMap Nominatim (free, no API key).
    Uses Nominatim's search to find places by niche and location.
    """
    if max_results is None:
        max_results = config['places']['osm']['max_results']
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    query = f"{niche} in {location}"
    params = {
        "q": query,
        "format": "json",
        "limit": max_results,
        "addressdetails": 1
    }
    headers = {"User-Agent": config['places']['osm']['user_agent']}
    resp = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    results = resp.json()
    places = []
    for r in results:
        # Extract name, address, website, and coordinates
        name = r.get('name') or r.get('display_name', '').split(',')[0]
        address = r.get('display_name', '')
        website = None  # Nominatim doesn't provide website; we could enrich later
        place_id = r.get('osm_id')
        lat = r.get('lat')
        lon = r.get('lon')
        places.append({
            'name': name,
            'address': address,
            'website': website,
            'place_id': str(place_id),
            'location': {'lat': float(lat) if lat else None, 'lon': float(lon) if lon else None}
        })
        if len(places) >= max_results:
            break
    return places

def find_places(niche, location, radius=None, max_results=None):
    if PROVIDER == 'yelp':
        try:
            return find_places_yelp(niche, location, radius, max_results)
        except ValueError as e:
            # If Yelp returns a pattern error, try OSM as fallback if configured? For now, re-raise.
            raise
    elif PROVIDER == 'osm':
        return find_places_osm(niche, location, radius, max_results)
    else:
        raise ValueError(f"Unknown places provider: {PROVIDER}")

def find_leads_by_location(niche, location):
    session = Session()
    places = find_places(niche, location)
    for p in places:
        existing = session.query(Lead).filter(
            (Lead.source_url == p['website']) |
            (Lead.source_url == p['place_id'])
        ).first()
        if not existing:
            lead = Lead(
                name=p['name'],
                email=None,
                source_url=p['website'] or p['place_id'],
                niche=niche,
                status='new',
                created_at=datetime.utcnow()
            )
            session.add(lead)
    session.commit()
    session.close()
    print(f"Added {len(places)} leads for {niche} near {location}")
    return len(places)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python place_finder.py <niche> <location>")
        sys.exit(1)
    niche = sys.argv[1]
    location = sys.argv[2]
    find_leads_by_location(niche, location)
