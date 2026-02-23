from db import Session, Lead
session = Session()
lead = session.query(Lead).get(1)
lead.status = 'replied_yes'
lead.prototype_url = None
session.commit()
print(f"Reset lead {lead.id} status to replied_yes, cleared prototype_url")
session.close()