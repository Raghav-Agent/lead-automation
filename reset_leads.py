from db import Session, Lead
session = Session()
for lead in session.query(Lead).all():
    lead.prototype_url = None
    lead.status = 'replied_yes'
session.commit()
print("Reset all leads")
session.close()
