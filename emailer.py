import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
import os
from db import Session, Lead
from datetime import datetime
import re
import requests

with open('config.yaml') as f:
    config = yaml.safe_load(f)

AI_PROVIDER = config['ai']['provider']
AI_MODEL = config['ai']['model']
AI_BASE_URL = config['ai'].get('base_url')
OPENAI_API_KEY = os.getenv(config['ai']['api_key_env'])

def send_email(to_address, subject, body, from_address=None, smtp_server=None, smtp_port=None, password=None):
    if not from_address:
        from_address = config['email']['from_address']
    if not smtp_server:
        smtp_server = config['email']['smtp_server']
    if not smtp_port:
        smtp_port = config['email']['smtp_port']
    if not password:
        password = os.getenv('SMTP_PASSWORD')
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_address, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email to {to_address}: {e}")
        return False

def generate_personalized_email(lead, niche):
    """
    Generate a personalized email using configured AI provider.
    """
    system = f"You are an outreach writer for a {niche} service. Write a concise, friendly email (3-4 sentences) to a business. Mention something about their business. End with a clear call-to-action to reply YES for a free audit."
    user = f"Business name: {lead.name or 'Business'}\nNiche: {niche}"
    try:
        if AI_PROVIDER == 'openai':
            import openai
            openai.api_key = OPENAI_API_KEY
            response = openai.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                max_tokens=200,
                temperature=0.7
            )
            body = response.choices[0].message.content.strip()
        elif AI_PROVIDER == 'groq':
            # Use Groq API (compatible with OpenAI client)
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.groq.com/openai/v1")
            response = client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                max_tokens=200,
                temperature=0.7
            )
            body = response.choices[0].message.content.strip()
        elif AI_PROVIDER == 'ollama':
            # Use local Ollama
            ollama_url = AI_BASE_URL.rstrip('/') + '/api/generate'
            payload = {
                "model": AI_MODEL,
                "prompt": f"{system}\n\n{user}",
                "stream": False,
                "options": {"num_predict": 200}
            }
            resp = requests.post(ollama_url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            body = data.get('response', '').strip()
        else:
            raise ValueError(f"Unknown AI provider: {AI_PROVIDER}")
        body = re.sub(r'\[.*?\]', '', body)
        subject = f"Quick question about {lead.name or 'your business'}"
        return subject, body
    except Exception as e:
        print(f"AI email generation failed ({AI_PROVIDER}): {e}")
        # Fallback template
        subject = f"Boost your {niche} business with a modern website"
        body = f"Hi {lead.name or 'there'},\n\nI noticed your business in the {niche} space. I specialize in building high-converting websites for {niche} like yours.\n\nI'd be happy to discuss how a new website can attract more customers. Would you be open to a quick chat this week?\n\nReply \"YES\" for a free site audit.\n\nBest,\nYour AI Assistant"
        return subject, body

def send_initial_email(lead, niche=None):
    if not niche:
        niche = config['niche']
    subject, body = generate_personalized_email(lead, niche)
    success = send_email(lead.email, subject, body)
    session = Session()
    if success:
        lead_obj = session.query(Lead).filter_by(id=lead.id).first()
        if lead_obj:
            lead_obj.status = 'emailed'
            lead_obj.last_contacted = datetime.utcnow()
            session.commit()
    session.close()
    return success

def email_leads():
    session = Session()
    leads = session.query(Lead).filter_by(status='new').all()
    for lead in leads:
        if lead.email:
            send_initial_email(lead)
        else:
            print(f"Skipping lead {lead.id} (no email)")
    session.close()

if __name__ == '__main__':
    email_leads()
