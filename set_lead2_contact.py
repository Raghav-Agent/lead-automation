from db import Session, Lead
session = Session()
lead = session.query(Lead).get(2)
if lead:
    lead.phone = '+919876543210'  # example phone
    session.commit()
    print(f"Lead {lead.id} phone set.")
else:
    print("Lead not found.")
session.close()
