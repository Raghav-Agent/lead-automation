from db import Session, Lead
from datetime import datetime

session = Session()
lead = Lead(
    name='Manish Dental Clinic',
    email='fake@example.com',  # placeholder, will be enriched
    phone=None,
    source_url='https://manishdental.com',  # placeholder; will be guessed
    niche='small businesses needing website',
    status='replied_yes',
    created_at=datetime.utcnow()
)
session.add(lead)
session.commit()
print(f"Created test lead id {lead.id}")
session.close()
