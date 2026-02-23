import json
import uuid
from pathlib import Path
from datetime import datetime
from db import Lead
from services.database import WebsitePrototypeService
import os

class WebsiteBuilderAgent:
    def __init__(self):
        self.output_path = Path(os.getenv('WEBSITE_OUTPUT_PATH', './generated_sites'))
        self.output_path.mkdir(exist_ok=True)

    async def generate_website_content(self, lead: Lead) -> dict:
        """Generate website content using simple templates (no LLM required)."""
        business_name = lead.business_name or lead.name
        niche = lead.niche
        location = lead.location
        phone = lead.phone or ""
        email = lead.email or ""
        address = lead.address or location

        content = {
            "title": f"{business_name} - Professional {niche} in {location}",
            "headline": f"Welcome to {business_name}",
            "tagline": f"Your trusted {niche} in {location}",
            "about": f"{business_name} is a reputable {niche} serving {location} with quality and reliability.",
            "services": [f"{niche.title()} Services", "Consultation", "Support", "Custom Solutions"],
            "features": ["Experienced Team", "Customer Focused", "Quality Guaranteed", "Affordable Pricing"],
            "cta": "Contact us today to get started!",
            "phone": phone,
            "email": email,
            "location": address,
            "business_name": business_name,
            "niche": niche,
            "location_name": location
        }
        return content

    async def build_website(self, lead: Lead, template_type: str = "modern") -> str:
        """Build a static HTML website for the lead."""
        content = await self.generate_website_content(lead)
        site_id = str(uuid.uuid4())
        output_file = self.output_path / f"{site_id}.html"
        html = self._render_template(template_type, content)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        # Return a URL path (to be served by FastAPI)
        return f"/sites/{site_id}.html"

    def _render_template(self, template_type: str, content: dict) -> str:
        """Render HTML template with content."""
        business_name = content['business_name']
        location = content['location_name']
        phone = content.get('phone', '')
        email = content.get('email', '')
        services = content.get('services', [])
        features = content.get('features', [])
        about = content.get('about', '')
        cta = content.get('cta', 'Contact us')
        headline = content.get('headline', f'Welcome to {business_name}')
        tagline = content.get('tagline', f'Your trusted partner in {location}')

        # Simple responsive template
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{content['title']}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height:1.6; color:#333; }}
header {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 1rem 0; position: sticky; top:0; z-index:1000; box-shadow:0 2px 10px rgba(0,0,0,0.1); }}
nav {{ max-width:1200px; margin:0 auto; display:flex; justify-content:space-between; align-items:center; padding:0 20px; }}
nav a {{ color:white; text-decoration:none; margin:0 15px; font-weight:500; }}
.hero {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color:white; padding:100px 20px; text-align:center; min-height:60vh; display:flex; flex-direction:column; justify-content:center; align-items:center; }}
.hero h1 {{ font-size:3rem; margin-bottom:20px; }}
.hero p {{ font-size:1.2rem; margin-bottom:30px; opacity:0.9; }}
.cta-button {{ background:white; color:#2563eb; padding:15px 40px; border:none; border-radius:50px; font-size:1.1rem; font-weight:bold; cursor:pointer; text-decoration:none; display:inline-block; }}
.container {{ max-width:1200px; margin:0 auto; padding:0 20px; }}
section {{ padding:60px 20px; }}
section h2 {{ font-size:2rem; margin-bottom:30px; text-align:center; }}
.services {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(250px,1fr)); gap:20px; margin-top:30px; }}
.service-card {{ background:#f8f9fa; padding:20px; border-radius:8px; text-align:center; }}
.service-card h3 {{ color:#2563eb; margin-bottom:10px; }}
.about {{ background:#f8f9fa; }}
.about-content {{ display:grid; grid-template-columns:1fr 1fr; gap:40px; align-items:center; }}
.contact-section {{ text-align:center; background:#f8f9fa; padding:60px 20px; }}
.contact-info {{ display:flex; justify-content:center; gap:40px; flex-wrap:wrap; margin-top:20px; }}
footer {{ background:#333; color:white; text-align:center; padding:20px; font-size:0.9rem; }}
@media (max-width:768px) {{ .hero h1 {{ font-size:2rem; }} .about-content {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<header>
<nav>
<div style="font-weight:bold; font-size:1.2rem;">{business_name}</div>
<div><a href="#services">Services</a><a href="#about">About</a><a href="#contact">Contact</a></div>
</nav>
</header>
<section class="hero">
<h1>{headline}</h1>
<p>{tagline}</p>
<a href="#contact" class="cta-button">Get Started Today</a>
</section>
<section id="services" class="container">
<h2>Our Services</h2>
<div class="services">
{% for service in services %}
<div class="service-card"><h3>{service}</h3><p>Professional {service} tailored to your needs</p></div>
{% endfor %}
</div>
</section>
<section id="about" class="about">
<div class="container">
<h2>About Us</h2>
<div class="about-content">
<div><h3>Why Choose {business_name}?</h3><p>{about}</p><ul style="margin-top:15px;">{% for f in features %}<li style="margin:8px 0;">✓ {f}</li>{% endfor %}</ul></div>
<div style="background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%); border-radius:8px; height:250px; display:flex; align-items:center; justify-content:center; color:white;"><p>Your Business Image Here</p></div>
</div>
</div>
</section>
<section id="contact" class="contact-section">
<div class="container">
<h2>Get In Touch</h2>
<p>{cta}</p>
<div class="contact-info">
{% if phone %}<div><p>📞 Phone</p><a href="tel:{phone}">{phone}</a></div>{% endif %}
{% if email %}<div><p>📧 Email</p><a href="mailto:{email}">{email}</a></div>{% endif %}
<div><p>📍 Location</p><p>{location}</p></div>
</div>
</div>
</section>
<footer><p>&copy; {datetime.now().year} {business_name}. All rights reserved.</p></footer>
</body>
</html>"""

website_builder = WebsiteBuilderAgent()
