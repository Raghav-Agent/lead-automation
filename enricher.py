import os
import yaml
import requests
from db import Session, Lead
from datetime import datetime
import time
import re
from urllib.parse import urlparse

with open('config.yaml') as f:
    config = yaml.safe_load(f)

ENRICH_METHOD = config['enrich']['method']
PATTERNS = config['enrich']['patterns']

def guess_email_from_name(name, domain):
    """
    Generate possible emails from name and domain using patterns.
    """
    if not name or not domain:
        return None
    parts = name.lower().replace('.', '').split()
    if len(parts) == 0:
        return None
    first = parts[0]
    last = parts[-1] if len(parts) > 1 else ''
    for pattern in PATTERNS:
        email = pattern.format(first=first, last=last, domain=domain)
        yield email

def scrape_website_for_email(website_url):
    """
    Scrape a website homepage for email addresses.
    """
    if not website_url:
        return None
    try:
        resp = requests.get(website_url, timeout=config['enrich']['scrape_timeout'])
        resp.raise_for_status()
        html = resp.text
        # Find email-like strings
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
        if emails:
            # Return first found that looks like contact email
            for email in emails:
                if 'contact' in email or 'info' in email or 'hello' in email:
                    return email
            return emails[0]
    except Exception as e:
        print(f"Scrape error {website_url}: {e}")
    return None

def find_email(lead):
    """
    Enrich a lead with an email address using configured method.
    """
    source = lead.source_url or ''
    domain = None

    # If source is a website URL, use it directly
    if source and source.startswith('http'):
        domain = urlparse(source).netloc
    else:
        # If it's a place_id or we don't have a website, try to guess domain from business name and location
        # Heuristic: lower case, remove spaces, add .in or .com
        if lead.name:
            guess = lead.name.lower().replace(' ', '').replace("'", '').replace('"', '')
            # Try common TLDs
            for tld in ['.in', '.com', '.co.in', '.net']:
                candidate = guess + tld
                # Simple DNS check could be done, but we'll just use it
                domain = candidate
                break  # use first guess
        else:
            return None

    if ENRICH_METHOD == 'hunter':
        api_key = os.getenv('HUNTER_API_KEY')
        if not api_key or not domain:
            return None
        url = "https://api.hunter.io/v2/domain-search"
        params = {"domain": domain, "api_key": api_key, "limit": 1}
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

    elif ENRICH_METHOD == 'pattern':
        if not domain:
            return None
        for email in guess_email_from_name(lead.name, domain):
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return email
        return None

    elif ENRICH_METHOD == 'scrape':
        if source and source.startswith('http'):
            return scrape_website_for_email(source)
        return None
    else:
        return None

def enrich_leads():
    session = Session()
    leads = session.query(Lead).filter_by(email=None).all()
    for lead in leads:
        email = find_email(lead)
        if email:
            lead.email = email
            print(f"Enriched lead {lead.id} with email {email}")
        time.sleep(1)  # be polite
    session.commit()
    session.close()

if __name__ == '__main__':
    enrich_leads()
