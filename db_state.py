# db_state.py
import sqlite3
from datetime import datetime

def init_db(db_path="state.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posted_videos (
            video_id TEXT PRIMARY KEY,
            title TEXT,
            posted_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def is_posted(video_id, db_path="state.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT 1 FROM posted_videos WHERE video_id = ?", (video_id,))
    row = c.fetchone()
    conn.close()
    return row is not None

def mark_posted(video_id, title, db_path="state.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    c.execute(
        "INSERT OR IGNORE INTO posted_videos (video_id, title, posted_at) VALUES (?, ?, ?)",
        (video_id, title, timestamp)
    )
    conn.commit()
    conn.close()
