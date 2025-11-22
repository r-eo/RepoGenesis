import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server', 'database.db')

def migrate_sessions():
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating 'active_sessions' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_sessions (
            user_id INTEGER PRIMARY KEY,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Migration complete: active_sessions table created.")

if __name__ == '__main__':
    migrate_sessions()
