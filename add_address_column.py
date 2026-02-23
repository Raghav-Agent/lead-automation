from db import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE leads ADD COLUMN address VARCHAR"))
        conn.commit()
        print("Added address column.")
    except Exception as e:
        print("Column may already exist or error:", e)
