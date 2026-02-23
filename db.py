from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
import yaml

load_dotenv()

with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Ensure data directory exists for SQLite
import os
db_url = config['database']['url']
if db_url.startswith('sqlite:///'):
    db_path = db_url.replace('sqlite:///', '')
    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    address = Column(String)
    source_url = Column(String)
    niche = Column(String)
    business_type = Column(String)
    business_name = Column(String)
    location = Column(String)
    website_url = Column(String)
    email_sent = Column(Boolean, default=False)
    email_sent_date = Column(DateTime)
    prototype_created = Column(Boolean, default=False)
    prototype_url = Column(String)
    status = Column(String, default='new')  # new, contacted, qualified, website_created
    notes = Column(String)
    last_contacted = Column(DateTime)
    reply_count = Column(Integer, default=0)
    conversation_history = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()
    print("Database initialized at:", config['database']['url'])
