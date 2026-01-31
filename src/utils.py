import sqlite3
import pandas as pd
import os
from datetime import datetime
import pytz

# Database Path
DB_PATH = os.path.join("data", "attendance.db")

def init_db():
    """Initialize the SQLite Database."""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create Table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_action(name, action):
    """
    Logs the action (IN/OUT) to the database.
    Includes logic to prevent double-punching within 60 seconds.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get current time
    now = datetime.now()
    
    # 1. Check for spam (Logic: Did this user perform ANY action in the last minute?)
    c.execute('''
        SELECT timestamp, action FROM logs 
        WHERE name = ? 
        ORDER BY id DESC LIMIT 1
    ''', (name,))
    
    last_record = c.fetchone()
    
    if last_record:
        last_time_str = last_record[0]
        last_action = last_record[1]
        
        # Parse timestamp (SQLite stores as string)
        try:
            last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
            time_diff = (now - last_time).total_seconds()
            
            # Rule: Cooldown of 60 seconds
            if time_diff < 60:
                conn.close()
                return False, f"Wait! You just punched {last_action} {int(time_diff)}s ago."
            
            # Rule: Logic check (Optional - can be disabled for testing)
            # if action == "IN" and last_action == "IN":
            #     return False, "You are already Punched IN."
        except:
            pass # Ignore date parse errors, just proceed

    # 2. Insert new record
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO logs (name, action, timestamp) VALUES (?, ?, ?)', (name, action, timestamp_str))
    
    conn.commit()
    conn.close()
    return True, f"Success: {name} Marked {action} at {timestamp_str}"

def get_logs():
    """Fetch all logs for display."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    
    # Fetch data into a Pandas DataFrame for easy display
    df = pd.read_sql_query("SELECT * FROM logs ORDER BY id DESC", conn)
    conn.close()
    return df