import os
import yaml
import shutil
import subprocess
from db import Session, Lead
from datetime import datetime

with open('config.yaml') as f:
    config = yaml.safe_load(f)

TEMPLATE_DIST = 'templates/vite/dist'
DOCS_DIR = 'docs'

def build_react_app():
    """Build the Vite React app if not already built or if source changed."""
    if not os.path.exists(TEMPLATE_DIST):
        print("Building React app...")
        result = subprocess.run(['npm', '--prefix', 'templates/vite', 'run', 'build'], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Vite build failed: {result.stderr}")
        print("React app built.")
    else:
        print("React app already built.")

def generate_prototype(lead):
    """
    Generate a customized landing page from the Vite React template.
    Copies the built app and adds a config.json with lead-specific data.
    """
    # Ensure build exists
    build_react_app()

    # Create output directory
    output_dir = os.path.join(DOCS_DIR, f'lead_{lead.id}')
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Copy built assets
    for item in os.listdir(TEMPLATE_DIST):
        s = os.path.join(TEMPLATE_DIST, item)
        d = os.path.join(output_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    # Write config.json at the root of the site
    config_data = {
        "business_name": lead.name or "Your Business",
        "niche": config.get('niche', ''),
        "lead_id": lead.id,
        "phone": lead.phone
    }
    with open(os.path.join(output_dir, 'config.json'), 'w') as f:
        import json
        json.dump(config_data, f, indent=2)

    # Determine GitHub Pages URL from git remote
    try:
        remote_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], cwd=DOCS_DIR).decode().strip()
        # Example: https://github.com/Raghav-Agent/lead-automation.git
        # Extract owner and repo
        import re
        m = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', remote_url)
        if m:
            owner = m.group(1)
            repo = m.group(2)
            url = f"https://{owner}.github.io/{repo}/lead_{lead.id}/"
        else:
            url = f"https://raghav-agent.github.io/lead-automation/lead_{lead.id}/"
    except Exception:
        url = f"https://raghav-agent.github.io/lead-automation/lead_{lead.id}/"
    return url

def build_prototypes():
    session = Session()
    leads = session.query(Lead).filter_by(status='replied_yes').filter(Lead.prototype_url.is_(None)).all()
    if not leads:
        print("No leads need prototypes.")
        session.close()
        return

    # Ensure docs dir exists
    os.makedirs(DOCS_DIR, exist_ok=True)

    for lead in leads:
        try:
            url = generate_prototype(lead)
            lead.prototype_url = url
            lead.status = 'prototype_sent'
            session.commit()
            print(f"Prototype for lead {lead.id} ready: {url}")
        except Exception as e:
            print(f"Failed for lead {lead.id}: {e}")
            session.rollback()

    session.close()

    # Commit and push to GitHub
    try:
        # Ensure docs folder is tracked
        subprocess.run(['git', 'add', '-f', 'docs'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Update prototypes (React)'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("Prototypes committed and pushed. GitHub Pages will update shortly.")
    except subprocess.CalledProcessError as e:
        print("Git push failed:", e)

if __name__ == '__main__':
    build_prototypes()
