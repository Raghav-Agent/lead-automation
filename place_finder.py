import os
import googlemaps
import yaml
from db import Session, Lead
from datetime import datetime
import time

with open('config.yaml') as f:
    config = yaml.safe_load(f)

GOOGLE_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

def find_places(niche, location, radius=None, max_results=None):
    """
    Find businesses by niche and location using Google Places API.
    niche: e.g., "dentist", "restaurant"
    location: "lat,lng" or address string
    Returns list of dicts with name, address, website, place_id.
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_PLACES_API_KEY not set")
    client = googlemaps.Client(key=GOOGLE_API_KEY)
    if radius is None:
        radius = config['google_places']['radius']
    if max_results is None:
        max_results = config['google_places']['max_results']
    # Use textsearch to find by niche
    response = client.places(query=f"{niche} near {location}", radius=radius)
    places = []
    while response.get('results'):
        for place in response['results']:
            places.append({
                'name': place.get('name'),
                'address': place.get('formatted_address'),
                'website': place.get('website'),
                'place_id': place.get('place_id'),
                'location': place.get('geometry', {}).get('location')
            })
            if len(places) >= max_results:
                break
        if len(places) >= max_results:
            break
        # pagination
        if 'next_page_token' in response:
            time.sleep(2)  # Google requires delay before next_page_token
            response = client.places(page_token=response['next_page_token'])
        else:
            break
    return places

def find_leads_by_location(niche, location):
    session = Session()
    places = find_places(niche, location)
    for p in places:
        # Avoid duplicates by place_id or website
        existing = session.query(Lead).filter(
            (Lead.source_url == p['website']) |
            (Lead.source_url == p['place_id'])
        ).first()
        if not existing:
            lead = Lead(
                name=p['name'],
                email=None,  # will enrich later
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
    # Example usage
    find_leads_by_location("dentist", "New York, NY")
