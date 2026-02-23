from db import Session, Lead
session = Session()
lead = session.query(Lead).get(2)
if lead:
    session.delete(lead)
    session.commit()
    print("Deleted lead 2")
session.close()
