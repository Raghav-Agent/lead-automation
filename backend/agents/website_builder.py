import os
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from db import Lead
from services.database import WebsitePrototypeService
from .ai_client import ai_client

class WebsiteBuilderAgent:
    def __init__(self):
        self.output_path = Path(os.getenv('WEBSITE_OUTPUT_PATH', './generated_sites'))
        self.vite_dist = Path(os.getenv('VITE_DIST_PATH', '../templates/vite/dist'))
        self.output_path.mkdir(exist_ok=True)

    async def generate_website_content(self, lead: Lead) -> dict:
        """Generate website content using AI."""
        business_name = lead.business_name or lead.name
        niche = lead.niche
        location = lead.location
        phone = lead.phone or ""
        email = lead.email or ""
        address = lead.address or lead.location or ""

        prompt = f"""Generate website content for a {niche} business called "{business_name}" located in {location}.
Contact: Phone {phone}, Email {email}, Address {address}.
Return JSON with:
{{
  "title": "...",
  "headline": "...",
  "tagline": "...",
  "about": "...",
  "services": ["...", "..."],
  "features": ["...", "..."],
  "cta": "..."
}}
Make it professional and conversion-focused."""
        response = ai_client.generate(prompt, max_tokens=500)
        try:
            # Extract JSON from response
            import re, json
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                content = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found")
        except Exception:
            # Fallback simple content
            content = {
                "title": f"{business_name} - Professional {niche} in {location}",
                "headline": f"Welcome to {business_name}",
                "tagline": f"Your trusted {niche} in {location}",
                "about": f"{business_name} is a reputable {niche} serving {location} with quality and reliability.",
                "services": [f"{niche.title()} Services", "Consultation", "Support", "Custom Solutions"],
                "features": ["Experienced Team", "Customer Focused", "Quality Guaranteed", "Affordable Pricing"],
                "cta": "Contact us today to get started!"
            }
        # Add contact fields
        content.update({
            "phone": phone,
            "email": email,
            "location": address,
            "business_name": business_name,
            "niche": niche,
            "location_name": location
        })
        return content

    async def build_website(self, lead: Lead, template_type: str = "modern") -> str:
        """Build a website by copying the Vite template and injecting config.json."""
        site_id = str(uuid.uuid4())
        output_dir = self.output_path / site_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Copy Vite built assets
        if self.vite_dist.exists():
            for item in self.vite_dist.iterdir():
                if item.is_dir():
                    shutil.copytree(item, output_dir / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, output_dir / item.name)
        else:
            raise FileNotFoundError(f"Vite dist not found at {self.vite_dist}. Build the template first.")

        # Generate content and write config.json
        content = await self.generate_website_content(lead)
        config_path = output_dir / "config.json"
        with open(config_path, 'w') as f:
            import json
            json.dump(content, f, indent=2)

        # Return URL path (served under /sites/{site_id}/)
        return f"/sites/{site_id}/"

website_builder = WebsiteBuilderAgent()
