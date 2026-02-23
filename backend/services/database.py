from sqlmodel import Session, create_engine, SQLModel, select
from typing import List, Optional
from datetime import datetime
from config import settings
from models.lead import Lead, LeadSearchQuery, EmailCampaign, WebsitePrototype

engine = create_engine(settings.DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    return Session(engine)

class LeadService:
    @staticmethod
    def create_lead(session: Session, lead: Lead) -> Lead:
        session.add(lead)
        session.commit()
        session.refresh(lead)
        return lead

    @staticmethod
    def get_lead(session: Session, lead_id: int) -> Optional[Lead]:
        return session.get(Lead, lead_id)

    @staticmethod
    def get_all_leads(session: Session, skip: int = 0, limit: int = 100) -> List[Lead]:
        statement = select(Lead).offset(skip).limit(limit)
        return session.exec(statement).all()

    @staticmethod
    def search_leads(
        session: Session,
        niche: Optional[str] = None,
        location: Optional[str] = None,
        business_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Lead]:
        statement = select(Lead)
        if niche:
            statement = statement.where(Lead.niche == niche)
        if location:
            statement = statement.where(Lead.location.contains(location))
        if business_type:
            statement = statement.where(Lead.business_type == business_type)
        if status:
            statement = statement.where(Lead.status == status)
        return session.exec(statement).all()

    @staticmethod
    def update_lead(session: Session, lead_id: int, **kwargs) -> Optional[Lead]:
        lead = session.get(Lead, lead_id)
        if lead:
            for key, value in kwargs.items():
                if hasattr(lead, key):
                    setattr(lead, key, value)
            lead.updated_at = datetime.utcnow()
            session.add(lead)
            session.commit()
            session.refresh(lead)
        return lead

    @staticmethod
    def delete_lead(session: Session, lead_id: int) -> bool:
        lead = session.get(Lead, lead_id)
        if lead:
            session.delete(lead)
            session.commit()
            return True
        return False

class EmailCampaignService:
    @staticmethod
    def create_campaign(session: Session, campaign: EmailCampaign) -> EmailCampaign:
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        return campaign

    @staticmethod
    def get_pending_campaigns(session: Session) -> List[EmailCampaign]:
        statement = select(EmailCampaign).where(EmailCampaign.status == "pending")
        return session.exec(statement).all()

    @staticmethod
    def update_campaign_status(session: Session, campaign_id: int, status: str):
        campaign = session.get(EmailCampaign, campaign_id)
        if campaign:
            campaign.status = status
            campaign.sent_at = datetime.utcnow()
            session.add(campaign)
            session.commit()

class WebsitePrototypeService:
    @staticmethod
    def create_prototype(session: Session, prototype: WebsitePrototype) -> WebsitePrototype:
        session.add(prototype)
        session.commit()
        session.refresh(prototype)
        return prototype

    @staticmethod
    def get_lead_prototypes(session: Session, lead_id: int) -> List[WebsitePrototype]:
        statement = select(WebsitePrototype).where(WebsitePrototype.lead_id == lead_id)
        return session.exec(statement).all()
