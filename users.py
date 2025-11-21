# users.py
from db import execute, fetchone, fetchall
from utils import now_iso

def ensure_user_exists(user_id: int):
    row = fetchone("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not row:
        execute(
            "INSERT INTO users (user_id, free_access, created_at, updated_at) VALUES (?,?,?,?)",
            (user_id, 0, now_iso(), now_iso())
        )

def get_user(user_id: int):
    row = fetchone("SELECT * FROM users WHERE user_id=?", (user_id,))
    return dict(row) if row else None

def set_free_access(user_id: int, value: int):
    ensure_user_exists(user_id)
    execute(
        "UPDATE users SET free_access=?, updated_at=? WHERE user_id=?",
        (value, now_iso(), user_id)
    )

def list_users():
    rows = fetchall("SELECT * FROM users")
    return [dict(r) for r in rows]