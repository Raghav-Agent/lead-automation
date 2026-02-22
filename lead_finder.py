import requests
from bs4 import BeautifulSoup
import yaml
import os
from db import Session, Lead
from datetime import datetime
import time

with open('config.yaml') as f:
    config = yaml.safe_load(f)

BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')

def search_brave_api(query, count=10):
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {
        "q": query,
        "count": count
    }
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for web in data.get('web', {}).get('results', []):
        results.append({"title": web.get('title'), "url": web.get('url'), "description": web.get('description')})
    return results

def search_brave_scrape(query, count=10):
    url = "https://search.brave.com/search"
    params = {"q": query, "count": count}
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(resp.text, 'lxml')
    results = []
    for result in soup.select('.snippet'):
        title = result.select_one('.title')
        link = result.select_one('a')
        if title and link:
            results.append({"title": title.text.strip(), "url": link['href']})
    return results

def find_leads():
    session = Session()
    queries = config['search']['queries']
    for q in queries:
        print(f"Searching: {q}")
        try:
            if BRAVE_API_KEY:
                results = search_brave_api(q, config['search']['results_per_query'])
            else:
                results = search_brave_scrape(q, config['search']['results_per_query'])
        except Exception as e:
            print(f"Search error for '{q}': {e}")
            results = []
        for r in results:
            name = r['title'].split()[0] if r['title'] else "Business"
            email = None  # Could use hunter.io or similar
            existing = session.query(Lead).filter_by(source_url=r['url']).first()
            if not existing:
                lead = Lead(
                    name=name,
                    email=email,
                    source_url=r['url'],
                    niche=config['niche'],
                    status='new',
                    created_at=datetime.utcnow()
                )
                session.add(lead)
        session.commit()
        time.sleep(1)
    session.close()
    print("Lead finding complete.")

if __name__ == '__main__':
    find_leads()
