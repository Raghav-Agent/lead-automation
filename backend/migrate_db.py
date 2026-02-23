"""
Migrate existing leads.db to new schema with additional fields.
"""
import os
from sqlalchemy import create_engine, text, inspect

# Use the same DB as config: sqlite:///leads.db in workspace root
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leads.db'))
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL)

def add_column_if_not_exists(conn, column_name, column_type="VARCHAR"):
    try:
        conn.execute(text(f"ALTER TABLE leads ADD COLUMN {column_name} {column_type}"))
        conn.commit()
        print(f"Added column {column_name}")
    except Exception as e:
        print(f"Column {column_name} may already exist or error: {e}")

with engine.connect() as conn:
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns('leads')]
    print("Existing columns:", existing_columns)

    new_columns = {
        'business_type': 'VARCHAR',
        'business_name': 'VARCHAR',
        'location': 'VARCHAR',
        'website_url': 'VARCHAR',
        'email_sent': 'BOOLEAN',
        'email_sent_date': 'DATETIME',
        'prototype_created': 'BOOLEAN',
        'notes': 'VARCHAR',
        'updated_at': 'DATETIME'
    }
    for col, col_type in new_columns.items():
        if col not in existing_columns:
            add_column_if_not_exists(conn, col, col_type)
        else:
            print(f"Column {col} already exists")

print("Migration complete.")
