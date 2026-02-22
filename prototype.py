import os
import yaml
from db import Session, Lead
from datetime import datetime
import subprocess

with open('config.yaml') as f:
    config = yaml.safe_load(f)

TEMPLATE_DIR = 'templates/smilecare'

def generate_prototype(lead):
    """
    Generate a customized landing page from the SmileCare template.
    Replaces placeholders with lead's business name and niche.
    """
    template_path = os.path.join(TEMPLATE_DIR, 'index.html')
    if not os.path.exists(template_path):
        # Fallback to simple if template missing
        return generate_simple_landing(lead)

    with open(template_path, 'r') as f:
        html = f.read()

    business_name = lead.name or 'Your Business'
    niche = config['niche']

    # Simple replacements: look for placeholders in template
    html = html.replace('{{business_name}}', business_name)
    html = html.replace('{{niche}}', niche)

    # Save to docs/lead_{id}/index.html for GitHub Pages
    output_dir = os.path.join('docs', f'lead_{lead.id}')
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, 'index.html')
    with open(filename, 'w') as f:
        f.write(html)

    # GitHub Pages URL
    url = f"https://raghav-prof.github.io/lead-automation/lead_{lead.id}/"
    return url

def generate_simple_landing(lead):
    """Fallback simple prototype."""
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
    output_dir = os.path.join('docs', f'lead_{lead.id}')
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, 'index.html')
    with open(filename, 'w') as f:
        f.write(html)
    return f"https://raghav-prof.github.io/lead-automation/lead_{lead.id}/"

def build_prototypes():
    session = Session()
    leads = session.query(Lead).filter_by(status='replied_yes').filter(Lead.prototype_url.is_(None)).all()
    for lead in leads:
        url = generate_prototype(lead)
        lead.prototype_url = url
        lead.status = 'prototype_sent'
        session.commit()
        print(f"Prototype for lead {lead.id} ready: {url}")
    session.close()
    # Commit and push to GitHub
    try:
        subprocess.run(['git', 'add', 'docs'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Update prototypes'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("Prototypes committed and pushed to GitHub Pages.")
    except subprocess.CalledProcessError as e:
        print("Git push failed:", e)

if __name__ == '__main__':
    build_prototypes()
