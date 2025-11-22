import sqlite3
import os
import time

db_path = os.path.join(os.path.dirname(__file__), 'server', 'database.db')

print(f"Connecting to {db_path}")

# Try multiple times with delays
for attempt in range(5):
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        cursor = conn.cursor()
        
        print("Clearing active_sessions...")
        cursor.execute('DELETE FROM active_sessions')
        
        print("Clearing sleep_logs...")
        cursor.execute('DELETE FROM sleep_logs')
        
        print("Clearing sleep_events...")
        cursor.execute('DELETE FROM sleep_events')
        
        print("Clearing user_reliability...")
        cursor.execute('DELETE FROM user_reliability')
        
        print("Clearing friends...")
        cursor.execute('DELETE FROM friends')
        
        print("Clearing users...")
        cursor.execute('DELETE FROM users')
        
        conn.commit()
        conn.close()
        
        print("✅ Database cleared successfully!")
        print("All user data has been removed.")
        break
        
    except sqlite3.OperationalError as e:
        if "locked" in str(e):
            print(f"Attempt {attempt + 1}: Database is locked, retrying in 2 seconds...")
            time.sleep(2)
        else:
            print(f"Error resetting database: {e}")
            break
    except Exception as e:
        print(f"Error resetting database: {e}")
        break
else:
    print("❌ Failed to clear database after 5 attempts. Please close all applications using the database.")
