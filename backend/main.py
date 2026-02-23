from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from typing import List
import asyncio
from pathlib import Path
import os

from config import settings
from services.database import create_tables, get_session, LeadService, EmailCampaignService, WebsitePrototypeService
from agents.lead_searcher import lead_searcher
from agents.email_generator import email_generator
from agents.website_builder import website_builder
from models.lead import Lead, LeadSearchQuery, EmailCampaign, WebsitePrototype

app = FastAPI(title="Autonomous Lead Generator", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()
    # Ensure generated_sites directory exists
    Path(settings.WEBSITE_OUTPUT_PATH).mkdir(exist_ok=True)
    print("✅ Database initialized")

# Health check
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# ============= LEAD ENDPOINTS =============

@app.post("/api/leads/search")
async def search_leads(
    query: LeadSearchQuery,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Search for leads in a specific niche and location (async generation)."""
    try:
        # Start background task for lead generation
        background_tasks.add_task(
            _generate_and_save_leads,
            query.niche,
            query.location,
            query.business_type or query.niche,
            session
        )
        return {
            "status": "searching",
            "message": f"Searching for {query.niche} businesses in {query.location}...",
            "query": query.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_and_save_leads(niche: str, location: str, business_type: str, session: Session):
    """Background task to generate and save leads."""
    try:
        leads = await lead_searcher.generate_leads(niche, location, business_type)
        for lead in leads:
            # Avoid duplicates by name+location
            existing = session.query(Lead).filter_by(name=lead.name, location=lead.location).first()
            if not existing:
                LeadService.create_lead(session, lead)
        print(f"✅ Generated {len(leads)} leads")
    except Exception as e:
        print(f"❌ Error generating leads: {e}")

@app.get("/api/leads")
def get_leads(
    skip: int = 0,
    limit: int = 100,
    niche: str = None,
    location: str = None,
    business_type: str = None,
    status: str = None,
    session: Session = Depends(get_session)
):
    """Get all leads with optional filters."""
    leads = LeadService.search_leads(session, niche, location, business_type, status)
    return {
        "count": len(leads),
        "leads": leads
    }

@app.get("/api/leads/{lead_id}")
def get_lead(lead_id: int, session: Session = Depends(get_session)):
    """Get specific lead."""
    lead = LeadService.get_lead(session, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.put("/api/leads/{lead_id}")
def update_lead(
    lead_id: int,
    lead_data: dict,
    session: Session = Depends(get_session)
):
    """Update lead information."""
    lead = LeadService.update_lead(session, lead_id, **lead_data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.delete("/api/leads/{lead_id}")
def delete_lead(lead_id: int, session: Session = Depends(get_session)):
    """Delete a lead."""
    success = LeadService.delete_lead(session, lead_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "deleted"}

# ============= WEBSITE BUILDER ENDPOINTS =============

@app.post("/api/websites/create/{lead_id}")
async def create_website(
    lead_id: int,
    template_type: str = "modern",
    background_tasks: BackgroundTasks = None,
    session: Session = Depends(get_session)
):
    """Create a prototype website for a lead."""
    lead = LeadService.get_lead(session, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    # Build immediately (synchronous for simplicity)
    try:
        website_url = await website_builder.build_website(lead, template_type)
        # Save website prototype info
        prototype = WebsitePrototype(
            lead_id=lead.id,
            template_type=template_type,
            website_url=website_url,
            website_content=None
        )
        WebsitePrototypeService.create_prototype(session, prototype)
        # Update lead
        LeadService.update_lead(
            session,
            lead.id,
            prototype_created=True,
            prototype_url=website_url,
            status="website_created"
        )
        return {
            "status": "created",
            "website_url": website_url,
            "message": f"Website created for {lead.business_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/websites/{lead_id}")
def get_lead_websites(lead_id: int, session: Session = Depends(get_session)):
    """Get all websites for a lead."""
    prototypes = WebsitePrototypeService.get_lead_prototypes(session, lead_id)
    return {
        "count": len(prototypes),
        "websites": prototypes
    }

# ============= EMAIL ENDPOINTS =============

@app.post("/api/emails/send/{lead_id}")
async def send_email_to_lead(
    lead_id: int,
    include_website: bool = True,
    session: Session = Depends(get_session)
):
    """Send persuasion email to lead."""
    lead = LeadService.get_lead(session, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if not lead.email:
        raise HTTPException(status_code=400, detail="Lead has no email address")
    try:
        website_url = lead.prototype_url or "https://preview.example.com"
        subject, body = email_generator.generate_personalized_email(lead, website_url)
        success = await email_generator.send_email(lead.email, subject, body, lead.id, session)
        if success:
            LeadService.update_lead(
                session,
                lead.id,
                email_sent=True,
                email_sent_date=datetime.utcnow(),
                status="contacted"
            )
            return {"status": "sent", "message": f"Email sent to {lead.email}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/emails/{lead_id}")
def get_lead_emails(lead_id: int, session: Session = Depends(get_session)):
    """Get email campaigns for a lead."""
    from sqlmodel import select
    statement = select(EmailCampaign).where(EmailCampaign.lead_id == lead_id)
    campaigns = session.exec(statement).all()
    return {
        "count": len(campaigns),
        "campaigns": campaigns
    }

# ============= DASHBOARD ENDPOINTS =============

@app.get("/api/dashboard/stats")
def get_dashboard_stats(session: Session = Depends(get_session)):
    """Get dashboard statistics."""
    all_leads = LeadService.get_all_leads(session, 0, 10000)
    status_counts = {}
    for lead in all_leads:
        status_counts[lead.status] = status_counts.get(lead.status, 0) + 1
    emails_sent = sum(1 for lead in all_leads if lead.email_sent)
    websites_created = sum(1 for lead in all_leads if lead.prototype_created)
    total = len(all_leads)
    conversion_rate = (websites_created / total * 100) if total > 0 else 0
    return {
        "total_leads": total,
        "emails_sent": emails_sent,
        "websites_created": websites_created,
        "status_breakdown": status_counts,
        "conversion_rate": round(conversion_rate, 1)
    }

# ============= STATIC FILES =============

# Mount generated sites
generated_sites_path = Path(settings.WEBSITE_OUTPUT_PATH)
if not generated_sites_path.exists():
    generated_sites_path.mkdir(parents=True, exist_ok=True)
app.mount("/sites", StaticFiles(directory=str(generated_sites_path)), name="sites")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT)
