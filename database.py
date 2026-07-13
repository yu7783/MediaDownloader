import sqlite3
import os
from datetime import datetime

DB_PATH = 'history.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_download(title, url, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO downloads (title, url, status, timestamp) VALUES (?, ?, ?, ?)', 
              (title, url, status, datetime.now()))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT title, url, status, timestamp FROM downloads ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    return rows
