#!/usr/bin/env python3
from db import init_db, Session, Lead
from prototype import generate_simple_landing
from datetime import datetime

# Initialize DB
init_db()

# Create a dummy lead for testing
session = Session()
lead = Lead(
    name="Test Business",
    email="test@example.com",
    source_url="https://example.com",
    niche="small businesses needing website",
    status='replied_yes',
    created_at=datetime.utcnow()
)
session.add(lead)
session.commit()
print(f"Created test lead with id {lead.id}")

# Generate prototype
url = generate_simple_landing(lead)
print(f"Prototype generated: {url}")

# Update lead with URL
lead.prototype_url = url
lead.status = 'prototype_sent'
session.commit()
session.close()

print("Test complete. Open the generated HTML file in a browser.")
