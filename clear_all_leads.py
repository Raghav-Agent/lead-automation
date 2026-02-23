from db import Session, Lead
session = Session()
session.query(Lead).delete()
session.commit()
print("All leads deleted")
session.close()
