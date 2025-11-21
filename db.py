# db.py
import sqlite3
import threading
from config import DB_PATH
from datetime import datetime

_lock = threading.Lock()
_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.row_factory = sqlite3.Row
_cur = _conn.cursor()

def init_db():
    with _lock:
        _cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            free_access INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
        """)
        _cur.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions(
            sub_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_key TEXT,
            start_ts TEXT,
            expiry_ts TEXT,
            status TEXT,
            provider TEXT,
            provider_payment_id TEXT,
            amount REAL
        )
        """)
        _cur.execute("""
        CREATE TABLE IF NOT EXISTS payments(
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            provider TEXT,
            payload TEXT,
            status TEXT,
            ts TEXT
        )
        """)
        _cur.execute("""
        CREATE TABLE IF NOT EXISTS mappings(
            mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            source_channel TEXT,
            target_channel TEXT,
            filters TEXT,
            watermark INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT
        )
        """)
        _conn.commit()

def execute(query, params=()):
    with _lock:
        _cur.execute(query, params)
        _conn.commit()
        return _cur

def fetchone(query, params=()):
    with _lock:
        _cur.execute(query, params)
        return _cur.fetchone()

def fetchall(query, params=()):
    with _lock:
        _cur.execute(query, params)
        return _cur.fetchall()

# initialize on import
init_db()