import asyncio
from typing import List
import os
import yaml
import requests
from datetime import datetime
from db import Session, Lead
from services.database import LeadService

with open('../config.yaml') as f:
    config = yaml.safe_load(f)

BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')

class LeadSearcherAgent:
    def __init__(self):
        pass

    def search_osm(self, query: str) -> List[dict]:
        """Search OpenStreetMap Nominatim for businesses."""
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "limit": config['places']['osm']['max_results'],
            "addressdetails": 1,
            "extratags": 1
        }
        headers = {"User-Agent": config['places']['osm']['user_agent']}
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"OSM error: {e}")
            return []
        results = []
        for place in data:
            name = place.get('name')
            if not name:
                display = place.get('display_name', '')
                name = display.split(',')[0] if display else 'Unknown'
            address = place.get('display_name')
            website = None
            if isinstance(place.get('extratags'), dict):
                website = place['extratags'].get('website')
            results.append({
                "name": name,
                "address": address,
                "website": website
            })
        return results

    async def search_brave(self, query: str, count=10) -> List[dict]:
        """Search Brave for business listings."""
        if not BRAVE_API_KEY:
            return []
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": BRAVE_API_KEY
        }
        params = {"q": query, "count": count}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for web in data.get('web', {}).get('results', []):
                results.append({
                    "title": web.get('title'),
                    "url": web.get('url'),
                    "description": web.get('description')
                })
            return results
        except Exception as e:
            print(f"Brave search error: {e}")
            return []

    async def generate_leads(self, niche: str, location: str, business_type: str = None) -> List[Lead]:
        """Generate leads from OSM and Brave search."""
        all_leads = []
        # OSM query
        osm_query = f"{niche} in {location}"
        osm_results = self.search_osm(osm_query)
        for r in osm_results:
            lead = Lead(
                name=r['name'],
                email=None,
                phone=None,
                business_type=business_type or niche,
                business_name=r['name'],
                location=location,
                address=r.get('address'),
                niche=niche,
                website_url=r.get('website') or '',
                status='new'
            )
            all_leads.append(lead)

        # Brave search for additional contacts
        brave_query = f"{niche} businesses {location} contact email phone"
        brave_results = await self.search_brave(brave_query, count=10)
        # We'll store these as raw leads without full structure; enrichment will fill details
        for r in brave_results:
            lead = Lead(
                name=r.get('title', 'Unknown'),
                email=None,
                phone=None,
                business_type=business_type or niche,
                business_name=r.get('title', 'Unknown'),
                location=location,
                address=None,
                niche=niche,
                website_url=r.get('url', ''),
                status='new'
            )
            all_leads.append(lead)

        return all_leads

lead_searcher = LeadSearcherAgent()
