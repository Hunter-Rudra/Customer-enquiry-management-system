import sqlite3
from datetime import datetime

DB_NAME = "leads.db"



def connect():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    with connect() as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS leads(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT NOT NULL,
                         phone TEXT NOT NULL,
                         course TEXT NOT NULL,
                         Source TEXT,
                         status TEXT DEFAULT 'New',
                         follow_up DATE,
                         notes TEXT,
                         created_at TEXT
                    )
                """)
        conn.commit()
        
def add_lead(name, phone, course, source, follow_up, notes):
    with connect() as conn:
        conn.execute("""
                     INSERT INTO leads
                     (name, phone, course, source, status,
                     follow_up, notes, created_at)
                     VALUES (?, ?, ?, ?, 'New', ?, ?, ?)
                     """, (
                         name,
                         phone,
                         course,
                         source,
                         follow_up,
                         notes,
                         datetime.now().isoformat()
                     ))
        conn.commit()
        
def get_leads():
    with connect() as conn:
        return conn.execute("""
                            SELECT * FROM leads
                            ORDER BY id DESC
                            """). fetchall()
        
        
def update_lead(lead_id, status, follow_up, notes):
    with connect() as conn:
        conn.execute("""
                     UPDATE leads
                     SET status = ?, follow_up = ?, notes = ?
                     WHERE id = ?
                     """, (status, follow_up, notes, lead_id)
                )
        conn.commit()
        
def delete_lead(lead_id):
    with connect() as conn:
        conn.execute(
            "DELETE FROM leads WHERE id = ?",
            (lead_id,)
        )
        conn.commit()
        
def update_lead_status(lead_id, new_status):
    
    valid_statuses = {
        "new": "New",
        "interested": "Interested",
        "follow-up": "Follow-up",
        "converted": "Converted",
        "lost": "Lost"
        }
    new_status = new_status.strip().lower()

    if new_status not in valid_statuses:
        print("Invalid status!")
        return
        
    new_status = valid_statuses[new_status]
    
    with connect() as conn:
        conn.execute(
            """
            UPDATE leads
            SET status = ? 
            WHERE id = ?
            """, (new_status, lead_id)
            
        )
        conn.commit()
        