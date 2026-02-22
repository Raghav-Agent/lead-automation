import os
import yaml
from db import Session, Lead
from datetime import datetime
import json

with open('config.yaml') as f:
    config = yaml.safe_load(f)

def generate_simple_landing(lead):
    # Very simple prototype: a one-page HTML with lead's name and niche
    title = f"Solution for {lead.name or 'your business'}"
    html = f"""<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{ font-family: sans-serif; margin: 40px; }}
    .hero {{ background: #f0f0f0; padding: 20px; border-radius: 8px; }}
    .cta {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }}
  </style>
</head>
<body>
  <div class="hero">
    <h1>Hi {lead.name},</h1>
    <p>We built a quick prototype tailored to your needs in the {config['niche']} space.</p>
    <p>This is a simple demo to show the concept. We can iterate based on your feedback.</p>
    <a href="#" class="cta">Get Started</a>
  </div>
</body>
</html>"""
    # Save to a file under static/lead_{id}.html
    os.makedirs('static', exist_ok=True)
    filename = f"static/lead_{lead.id}.html"
    with open(filename, 'w') as f:
        f.write(html)
    # Return a URL (assuming we'll serve these statically)
    return f"http://localhost:8000/{filename}"

def build_prototypes():
    session = Session()
    leads = session.query(Lead).filter_by(status='replied_yes').filter(Lead.prototype_url.is_(None)).all()
    for lead in leads:
        url = generate_simple_landing(lead)
        lead.prototype_url = url
        lead.status = 'prototype_sent'
        session.commit()
        print(f"Prototype for lead {lead.id} ready: {url}")
    session.close()

if __name__ == '__main__':
    build_prototypes()
