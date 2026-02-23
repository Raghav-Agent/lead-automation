from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime

class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # contact name or business name
    email: Optional[str] = None
    phone: Optional[str] = None
    business_type: str  # e.g., "dental clinic", "restaurant"
    business_name: str  # official business name
    location: str  # city, region
    address: Optional[str] = None
    niche: str  # campaign niche
    website_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    email_sent: bool = False
    email_sent_date: Optional[datetime] = None
    prototype_created: bool = False
    prototype_url: Optional[str] = None
    status: str = "new"  # new, contacted, qualified, website_created
    notes: Optional[str] = None

class LeadSearchQuery(SQLModel):
    niche: str
    location: str
    business_type: Optional[str] = None
    radius_km: int = 50

class EmailCampaign(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id")
    subject: str
    body: str
    status: str  # pending, sent, opened, clicked
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None

class WebsitePrototype(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id")
    template_type: str
    website_url: str
    website_content: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    customizations: Optional[str] = None
