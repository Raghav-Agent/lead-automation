import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple
import os
from db import Session, Lead
from services.database import EmailCampaignService

class EmailGeneratorAgent:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')

    def generate_personalized_email(self, lead: Lead, website_url: str) -> Tuple[str, str]:
        """Generate email subject and body using simple templates (no LLM required)."""
        business_name = lead.business_name or lead.name
        niche = lead.niche
        subject = f"Professional {niche} website for {business_name}"
        body = f"""Hi {business_name} team,

I noticed {business_name} is a trusted {niche} in {lead.location}. I specialize in building modern, conversion-focused websites for {niche} businesses like yours.

I've put together a quick prototype that could work for you: {website_url}

Having a professional website helps you:
- Attract more customers online
- Build credibility and trust
- Showcase your services 24/7

Would you be interested in seeing a custom design for your business? I can have a draft ready within 48 hours.

Best regards,
[Your Name]
Freelance Web Developer
"""
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
