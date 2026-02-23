from db import Session, Lead

session = Session()
lead = session.query(Lead).get(1)
if lead:
    lead.email = 'contact@manishdental.com'
    lead.phone = '+919876543210'
    lead.source_url = 'https://manishdental.com'  # example; replace with real if known
    session.commit()
    print(f"Lead {lead.id} updated with contact info.")
else:
    print("Lead not found.")
session.close()
