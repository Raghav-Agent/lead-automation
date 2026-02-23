"""
Sub-agent for lead enrichment.
Finds correct email, phone, and verifies address using web search and website scraping.
"""
import os
import yaml
import re
import requests
from db import Session, Lead
from datetime import datetime
from urllib.parse import urlparse
import time

with open('config.yaml') as f:
    config = yaml.safe_load(f)

BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')
PATTERNS = config['enrich']['patterns']

def guess_email_from_name(name, domain):
    if not name or not domain:
        return None
    parts = name.lower().replace('.', '').split()
    if not parts:
        return None
    first = parts[0]
    last = parts[-1] if len(parts) > 1 else ''
    for pattern in PATTERNS:
        email = pattern.format(first=first, last=last, domain=domain)
        yield email

def extract_phone_from_text(text):
    phones = re.findall(r'(?:\+?91)?[6-9]\d{9}', text)
    if phones:
        seen = set()
        for p in phones:
            p_clean = re.sub(r'[^\d+]', '', p)
            if p_clean not in seen:
                seen.add(p_clean)
                return p_clean
    return None

def search_brave_for_contact(business_name, location_hint=None):
    """
    Use Brave Search API to find contact info snippets.
    Returns (email, phone, address) from top results.
    """
    if not BRAVE_API_KEY:
        return None, None, None
    query = f"{business_name} contact email phone address"
    if location_hint:
        query += f" {location_hint}"
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {"q": query, "count": 10}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        email = None
        phone = None
        address = None
        for result in data.get('web', {}).get('results', []):
            snippet = result.get('description', '')
            # Extract email
            if not email:
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', snippet)
                if emails:
                    for e in emails:
                        if 'contact' in e or 'info' in e or 'hello' in e:
                            email = e
                            break
                    if not email:
                        email = emails[0]
            # Extract phone
            if not phone:
                phone = extract_phone_from_text(snippet)
            # Extract address (simple heuristic: lines with digits and city/state keywords)
            if not address:
                # Look for a line that looks like an address
                lines = snippet.split(',')
                for line in lines:
                    if re.search(r'\d{1,5} [\w\s]+ (street|st|road|rd|avenue|ave|lane|ln|block|sector|phase)', line, re.IGNORECASE):
                        address = line.strip()
                        break
            if email and phone and address:
                break
        return email, phone, address
    except Exception as e:
        print(f"Brave search error: {e}")
        return None, None, None

def scrape_website(url):
    """
    Scrape a website for email and phone.
    """
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            html = resp.text
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
            email = None
            if emails:
                for e in emails:
                    if 'contact' in e or 'info' in e or 'hello' in e:
                        email = e
                        break
                if not email:
                    email = emails[0]
            phone = extract_phone_from_text(html)
            return email, phone
    except Exception:
        pass
    return None, None

def enrich_lead(lead):
    updated = False
    # If we have a website, scrape it first
    if lead.source_url and lead.source_url.startswith('http'):
        email, phone = scrape_website(lead.source_url)
        if email and not lead.email:
            lead.email = email
            updated = True
        if phone and not lead.phone:
            lead.phone = phone
            updated = True

    # If still missing info, use Brave Search with business name and address/location hint
    if not lead.email or not lead.phone:
        location_hint = None
        if lead.address:
            # Extract city/region from address (simple: take last 2 comma parts)
            parts = lead.address.split(',')
            if len(parts) >= 2:
                location_hint = parts[-2].strip() + ' ' + parts[-1].strip()
        email, phone, addr = search_brave_for_contact(lead.name, location_hint)
        if email and not lead.email:
            lead.email = email
            updated = True
        if phone and not lead.phone:
            lead.phone = phone
            updated = True
        if addr and not lead.address:
            lead.address = addr
            updated = True

    # If still no email, try domain guessing from business name
    if not lead.email:
        domain = None
        if lead.source_url and lead.source_url.startswith('http'):
            domain = urlparse(lead.source_url).netloc
        else:
            guess = lead.name.lower().replace(' ', '').replace("'", '').replace('"', '')
            domain = guess + '.in'  # default to .in for India
        for email in guess_email_from_name(lead.name, domain):
            lead.email = email
            updated = True
            break

    return updated

def enrich_pending_leads():
    session = Session()
    leads = session.query(Lead).filter(
        (Lead.email.is_(None)) | (Lead.phone.is_(None))
    ).filter(
        Lead.status.in_(['new', 'emailed', 'replied_yes', 'in_conversation', 'prototype_sent'])
    ).all()
    for lead in leads:
        try:
            updated = enrich_lead(lead)
            if updated:
                print(f"Enriched lead {lead.id}: email={lead.email}, phone={lead.phone}, address={lead.address}")
            else:
                print(f"No enrichment found for lead {lead.id}")
        except Exception as e:
            print(f"Error enriching lead {lead.id}: {e}")
        time.sleep(2)  # be polite
    session.commit()
    session.close()
    return len(leads)

def run():
    count = enrich_pending_leads()
    return {"status": "ok", "processed": count}

if __name__ == '__main__':
    print(run())
