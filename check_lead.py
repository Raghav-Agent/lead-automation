from db import Session, Lead
session = Session()
lead = session.query(Lead).get(1)
print(f"Lead {lead.id}: name={lead.name}, email={lead.email}, phone={lead.phone}, prototype_url={lead.prototype_url}, status={lead.status}")
session.close()