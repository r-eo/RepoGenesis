import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server', 'database.db')

def migrate():
    if not os.path.exists(db_path):
        print("Database not found, nothing to migrate.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check if 'password' column exists in 'users'
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'password' not in columns:
        print("Adding 'password' column to users table...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN password TEXT")
        except Exception as e:
            print(f"Error adding column: {e}")
    else:
        print("'password' column already exists.")

    # 2. Ensure 'friends' table exists
    print("Ensuring 'friends' table exists...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, friend_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (friend_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
