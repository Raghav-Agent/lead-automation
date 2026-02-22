import yaml
import os
from db import Session, Lead
from datetime import datetime
from place_finder import find_leads_by_location
from enricher import enrich_leads
from emailer import send_initial_email
import openai

with open('config.yaml') as f:
    config = yaml.safe_load(f)

openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_sales_email(lead, niche):
    """
    Generate a personalized sales email using OpenAI.
    """
    system = f"You are a sales consultant for a web design agency targeting {niche}. Write a concise, friendly email (4-5 sentences) with three package options (Starter, Professional, Premium) and a clear CTA to reply YES for a free audit."
    user = f"Business name: {lead.name}\nNiche: {niche}"
    try:
        response = openai.chat.completions.create(
            model=config['ai']['model'],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=300,
            temperature=0.7
        )
        body = response.choices[0].message.content.strip()
        subject = f"Boost your {niche} business with a modern website"
        return subject, body
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None, None

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
        # Generate personalized email
        subject, body = generate_sales_email(lead, niche)
        if not subject:
            # Fallback to template
            from emailer import template_env
            template = template_env.get_template('sales_email.txt')
            body = template.render(name=lead.name, niche=niche)
            subject = f"Boost your {niche} business with a modern website"
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
