import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
import os
from db import Session, Lead
from datetime import datetime
import openai
import re

with open('config.yaml') as f:
    config = yaml.safe_load(f)

openai.api_key = os.getenv('OPENAI_API_KEY')

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

def generate_personalized_email(lead):
    # Use OpenAI to generate a short, personalized email based on lead's name and source
    system = f"You are an outreach writer for a {config['niche']} service. Write a concise, friendly email (3-4 sentences) to a business. Mention something about their website or niche. End with a clear call-to-action to reply YES for a prototype."
    user = f"Lead name: {lead.name or 'Business'}\nSource: {lead.source_url or 'Unknown'}\nNiche: {config['niche']}"
    try:
        response = openai.chat.completions.create(
            model=config['ai']['model'],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=200,
            temperature=0.7
        )
        body = response.choices[0].message.content.strip()
        # Ensure body doesn't have placeholders
        body = re.sub(r'\[.*?\]', '', body)
        subject = f"Quick question about {lead.name or 'your business'}"
        return subject, body
    except Exception as e:
        print(f"OpenAI email generation failed: {e}")
        # Fallback to template
        subject = f"Quick question about your {config['niche']}"
        body = f"Hi {lead.name or 'there'},\n\nI noticed your business in the {config['niche']} space and was impressed.\n\nI'm building a new solution that could help you. Would you be interested in a quick prototype to see how it works?\n\nReply \"YES\" and I'll send over a link to a working demo.\n\nBest,\nYour AI Assistant"
        return subject, body

def send_initial_email(lead):
    subject, body = generate_personalized_email(lead)
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
