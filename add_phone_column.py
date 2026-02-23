"""
Add phone column to leads table.
"""
from db import engine, Base
from sqlalchemy import text

with engine.connect() as conn:
    # Check if column exists
    try:
        conn.execute(text("ALTER TABLE leads ADD COLUMN phone VARCHAR"))
        conn.commit()
        print("Added phone column.")
    except Exception as e:
        print("Column may already exist or error:", e)
