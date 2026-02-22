import imaplib
import email
from email.header import decode_header
import os
import yaml
from db import Session, Lead
from datetime import datetime
import re

with open('config.yaml') as f:
    config = yaml.safe_load(f)

def connect_imap():
    imap_server = os.getenv('IMAP_SERVER', config['email'].get('imap_server', 'imap.gmail.com'))
    imap_user = os.getenv('IMAP_USER', config['email']['from_address'])
    imap_pass = os.getenv('IMAP_PASSWORD')
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(imap_user, imap_pass)
    return mail

def check_replies():
    session = Session()
    mail = connect_imap()
    mail.select('inbox')
    # Search for unseen emails
    status, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()
    for eid in email_ids:
        _, msg_data = mail.fetch(eid, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject, encoding = decode_header(msg['Subject'])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8')
        from_header = msg['From']
        # Extract email address
        match = re.search(r'<(.+?)>', from_header)
        email_addr = match.group(1) if match else from_header
        # Get body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
        # Check if this email is from a lead we contacted
        lead = session.query(Lead).filter_by(email=email_addr).first()
        if lead:
            # Simple intent detection
            if re.search(r'\byes\b', body, re.IGNORECASE):
                lead.status = 'replied_yes'
            else:
                lead.status = 'replied_no'
            lead.reply_count += 1
            session.commit()
            print(f"Updated lead {lead.id} status to {lead.status}")
        # Mark as seen (already UNSEEN, but we could flag)
    mail.close()
    mail.logout()
    session.close()

if __name__ == '__main__':
    check_replies()
