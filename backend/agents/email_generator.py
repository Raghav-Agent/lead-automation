import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple
import os
from db import Session, Lead
from services.database import EmailCampaignService
from .ai_client import ai_client
import json
import re

class EmailGeneratorAgent:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')

    def generate_personalized_email(self, lead: Lead, website_url: str) -> Tuple[str, str]:
        """Generate email subject and body using AI."""
        business_name = lead.business_name or lead.name
        niche = lead.niche
        location = lead.location
        prompt = f"""Write a persuasive, personalized email to a {niche} business called "{business_name}" in {location}.
Include a link to their website prototype: {website_url}
Keep it concise, professional, and focused on benefits. End with a clear call-to-action.
Format:
SUBJECT: <subject line>
BODY: <email body>"""
        response = ai_client.generate(prompt, max_tokens=300)
        # Parse subject and body
        if "BODY:" in response:
            parts = response.split("BODY:")
            subject = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip()
        else:
            subject = f"Professional {niche} website for {business_name}"
            body = response
        return subject, body

    async def send_email(self, to_email: str, subject: str, body: str, lead_id: int, session: Session) -> bool:
        """Send email and record campaign."""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email

            html = f"""<html><body><p>{body.replace(chr(10), '<br>')}</p></body></html>"""
            part1 = MIMEText(body, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)

            # Send synchronously in a thread to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_smtp, message, to_email)

            # Record campaign
            campaign = EmailCampaign(
                lead_id=lead_id,
                subject=subject,
                body=body,
                status="sent",
                sent_at=datetime.utcnow()
            )
            EmailCampaignService.create_campaign(session, campaign)
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False

    def _send_smtp(self, message, to_email: str):
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.sender_email, self.sender_password)
        server.sendmail(self.sender_email, to_email, message.as_string())
        server.quit()

email_generator = EmailGeneratorAgent()
