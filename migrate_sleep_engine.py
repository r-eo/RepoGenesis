import sqlite3
import os
from datetime import datetime

def migrate_database():
    """
    Migration script to add sleep_events and user_reliability tables.
    This enables the enhanced sleep tracking engine with validation and reliability scoring.
    """
    db_path = os.path.join(os.path.dirname(__file__), 'server', 'database.db')
    
    print(f"Migrating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create sleep_events table
    print("Creating sleep_events table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sleep_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            duration_seconds INTEGER,
            metadata TEXT,
            reliability_impact REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create user_reliability table
    print("Creating user_reliability table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_reliability (
            user_id INTEGER PRIMARY KEY,
            score REAL DEFAULT 0.75,
            total_events INTEGER DEFAULT 0,
            auto_closed_events INTEGER DEFAULT 0,
            manual_corrections INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create index for faster queries
    print("Creating indexes...")
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sleep_events_user_timestamp 
        ON sleep_events(user_id, timestamp)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sleep_events_type 
        ON sleep_events(event_type)
    ''')
    
    conn.commit()
    
    # Initialize reliability scores for existing users
    print("Initializing reliability scores for existing users...")
    cursor.execute('''
        INSERT OR IGNORE INTO user_reliability (user_id, score, total_events)
        SELECT id, 0.75, 0 FROM users
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Migration completed successfully!")
    print("New tables created:")
    print("  - sleep_events")
    print("  - user_reliability")

if __name__ == '__main__':
    migrate_database()
