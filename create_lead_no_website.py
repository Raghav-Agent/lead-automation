from db import Session, Lead
from datetime import datetime

session = Session()
lead = Lead(
    name='Justdal Dental',
    email=None,  # no email yet
    phone=None,
    source_url='',  # no website
    niche='small businesses needing website',
    status='replied_yes',
    created_at=datetime.utcnow()
)
session.add(lead)
session.commit()
print(f"Created lead id {lead.id}")
session.close()
