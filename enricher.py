import os
import requests
import yaml
from db import Session, Lead
from datetime import datetime
import time

with open('config.yaml') as f:
    config = yaml.safe_load(f)

HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')

def find_email(domain):
    """
    Use Hunter.io API to find email for a domain.
    Returns email or None.
    """
    if not HUNTER_API_KEY:
        return None
    url = "https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY,
        "limit": 1
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        emails = data.get('data', {}).get('emails', [])
        if emails:
            return emails[0].get('value')
    except Exception as e:
        print(f"Hunter error for {domain}: {e}")
    return None

def enrich_leads():
    """
    For leads without email and with a website/place_id, try to find email.
    """
    session = Session()
    leads = session.query(Lead).filter_by(email=None).all()
    for lead in leads:
        # Try to extract domain from source_url
        source = lead.source_url or ''
        if source.startswith('http'):
            # Extract domain
            from urllib.parse import urlparse
            parsed = urlparse(source)
            domain = parsed.netloc
        else:
            # Assume it's a place_id; we can't enrich without a website
            domain = None
        if domain:
            email = find_email(domain)
            if email:
                lead.email = email
                print(f"Enriched lead {lead.id} with email {email}")
            time.sleep(1.2)  # respect rate limit
    session.commit()
    session.close()

if __name__ == '__main__':
    enrich_leads()
