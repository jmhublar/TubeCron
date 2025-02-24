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
            posted_at TEXT,
            transcript_fetched INTEGER DEFAULT 0,
            transcript_path TEXT,
            summary_generated INTEGER DEFAULT 0,
            obsidian_path TEXT
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
        """INSERT OR IGNORE INTO posted_videos 
           (video_id, title, posted_at, transcript_fetched, summary_generated) 
           VALUES (?, ?, ?, 0, 0)""",
        (video_id, title, timestamp)
    )
    conn.commit()
    conn.close()

def update_transcript_status(video_id, transcript_path, db_path="state.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """UPDATE posted_videos 
           SET transcript_fetched = 1, transcript_path = ? 
           WHERE video_id = ?""",
        (transcript_path, video_id)
    )
    conn.commit()
    conn.close()

def update_obsidian_status(video_id, obsidian_path, db_path="state.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """UPDATE posted_videos 
           SET summary_generated = 1, obsidian_path = ? 
           WHERE video_id = ?""",
        (obsidian_path, video_id)
    )
    conn.commit()
    conn.close()

def get_pending_transcripts(db_path="state.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """SELECT video_id, title FROM posted_videos 
           WHERE transcript_fetched = 0"""
    )
    results = c.fetchall()
    conn.close()
    return results

def get_pending_summaries(db_path="state.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """SELECT video_id, title, transcript_path FROM posted_videos 
           WHERE transcript_fetched = 1 AND summary_generated = 0"""
    )
    results = c.fetchall()
    conn.close()
    return results
