"""
Migrate to a new database file owned by ubuntu and add phone column.
"""
import yaml
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# Load config
with open('config.yaml') as f:
    config = yaml.safe_load(f)

OLD_DB_URL = config['database']['url']
NEW_DB_URL = 'sqlite:///leads.db'

# Create new engine
new_engine = create_engine(NEW_DB_URL)
Base = declarative_base()

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    source_url = Column(String)
    niche = Column(String)
    status = Column(String, default='new')
    last_contacted = Column(DateTime)
    reply_count = Column(Integer, default=0)
    conversation_history = Column(JSON, default=list)
    prototype_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(new_engine)

# If old DB exists and has data, copy it over
if OLD_DB_URL.startswith('sqlite:///') and os.path.exists(OLD_DB_URL.replace('sqlite:///', '')):
    old_engine = create_engine(OLD_DB_URL)
    old_meta = MetaData()
    old_leads = Table('leads', old_meta, autoload_with=old_engine)
    old_session = sessionmaker(bind=old_engine)()
    new_session = sessionmaker(bind=new_engine)()
    try:
        for old_lead in old_session.query(old_leads).all():
            # Map columns manually
            new_lead = Lead(
                id=old_lead.id,
                name=old_lead.name,
                email=old_lead.email,
                phone=None,
                source_url=old_lead.source_url,
                niche=old_lead.niche,
                status=old_lead.status,
                last_contacted=old_lead.last_contacted,
                reply_count=old_lead.reply_count,
                conversation_history=old_lead.conversation_history,
                prototype_url=old_lead.prototype_url,
                created_at=old_lead.created_at
            )
            new_session.add(new_lead)
        new_session.commit()
        print("Migrated existing leads to new database.")
    except Exception as e:
        print("Migration error:", e)
    finally:
        old_session.close()
        new_session.close()
else:
    print("No old database found or using different backend; starting fresh.")

# Update config.yaml to use new DB
config['database']['url'] = NEW_DB_URL
with open('config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
print("Updated config.yaml to use new database:", NEW_DB_URL)
