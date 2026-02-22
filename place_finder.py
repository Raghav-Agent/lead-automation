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
    return places

def find_places_osm(niche, location, radius=None, max_results=None):
    """
    Find businesses using OpenStreetMap Nominatim + Overpass API (free, rate-limited).
    No API key required but please be respectful (1 req/s).
    """
    if max_results is None:
        max_results = config['places']['osm']['max_results']
    # First, geocode location to lat,lon
    nominatim_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": config['places']['osm']['user_agent']}
    resp = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return []
    lat = results[0]['lat']
    lon = results[0]['lon']
    # Use Overpass to find businesses by name/tags within radius
    overpass_url = "https://overpass-api.de/api/interpreter"
    # Search for nodes/ways with name containing niche and within radius
    query = f"""
    [out:json][timeout:{config['places']['osm']['timeout']}];
    (
      node["name"~"{niche}", i](around:{radius or 10000},{lat},{lon});
      way["name"~"{niche}", i](around:{radius or 10000},{lat},{lon});
    );
    out body {max_results} ;
    """
    resp = requests.post(overpass_url, data=query, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    places = []
    for el in data.get('elements', []):
        tags = el.get('tags', {})
        name = tags.get('name', 'Unknown')
        # Try to get website
        website = tags.get('website') or tags.get('url')
        place_id = str(el.get('id'))
        address = tags.get('addr:full') or f"{tags.get('addr:street','')} {tags.get('addr:city','')}"
        location = {'lat': el.get('lat') or el.get('center', {}).get('lat'), 'lon': el.get('lon') or el.get('center', {}).get('lon')}
        places.append({
            'name': name,
            'address': address,
            'website': website,
            'place_id': place_id,
            'location': location
        })
        if len(places) >= max_results:
            break
    return places

def find_places(niche, location, radius=None, max_results=None):
    if PROVIDER == 'yelp':
        return find_places_yelp(niche, location, radius, max_results)
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
