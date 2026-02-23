"""
Update existing leads to populate new fields.
"""
import os
import sys
# Add parent directory to path to import db from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import Session, Lead
from datetime import datetime

session = Session()
leads = session.query(Lead).all()
updated_count = 0
for lead in leads:
    changed = False
    # Set business_name to existing name if not already set
    if not lead.business_name and lead.name:
        lead.business_name = lead.name
        changed = True
    # Set business_type to niche if not set
    if not lead.business_type and lead.niche:
        lead.business_type = lead.niche
        changed = True
    # Set website_url from source_url if not set
    if not lead.website_url and lead.source_url:
        lead.website_url = lead.source_url
        changed = True
    # Set location to empty string if null
    if lead.location is None:
        lead.location = ''
        changed = True
    # Set boolean flags
    if lead.email_sent is None:
        lead.email_sent = False
        changed = True
    if lead.prototype_created is None:
        lead.prototype_created = bool(lead.prototype_url)
        changed = True
    if changed:
        updated_count += 1
        session.add(lead)

session.commit()
session.close()
print(f"Updated {updated_count} leads.")
