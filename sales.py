import yaml
import os
from db import Session, Lead
from datetime import datetime
from place_finder import find_leads_by_location
from enricher import enrich_leads
from emailer import send_initial_email
import time

with open('config.yaml') as f:
    config = yaml.safe_load(f)

def run_sales_campaign(niche, location):
    """
    Full workflow: find leads by location, enrich emails, send personalized sales emails.
    """
    print(f"Starting sales campaign for {niche} near {location}")
    # 1. Find leads
    count = find_leads_by_location(niche, location)
    print(f"Found {count} leads")
    # 2. Enrich emails
    enrich_leads()
    # 3. Send emails to new leads with email
    session = Session()
    leads = session.query(Lead).filter(
        Lead.niche == niche,
        Lead.email.isnot(None),
        Lead.status == 'new'
    ).all()
    print(f"Sending emails to {len(leads)} leads")
    for lead in leads:
        # Use emailer's AI to generate personalized sales email
        from emailer import generate_personalized_email
        subject, body = generate_personalized_email(lead, niche)
        # Send
        from emailer import send_email
        success = send_email(lead.email, subject, body)
        if success:
            lead.status = 'emailed'
            lead.last_contacted = datetime.utcnow()
            session.commit()
            print(f"Sent to {lead.email}")
        time.sleep(1)
    session.close()
    print("Campaign complete")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python sales.py <niche> <location>")
        sys.exit(1)
    niche = sys.argv[1]
    location = sys.argv[2]
    run_sales_campaign(niche, location)
