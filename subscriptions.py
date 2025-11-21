# subscriptions.py
from db import execute, fetchone, fetchall
from datetime import datetime, timedelta
import config
from utils import now_iso

def activate_subscription(user_id: int, plan_key: str, provider: str, provider_payment_id: str, amount: float):
    plan = config.PLANS.get(plan_key)
    if not plan:
        return False
    duration = int(plan["duration_days"])
    # check existing active subscription
    row = fetchone("SELECT * FROM subscriptions WHERE user_id=? AND status='active' ORDER BY expiry_ts DESC LIMIT 1", (user_id,))
    if row and row["expiry_ts"]:
        try:
            current_expiry = datetime.fromisoformat(row["expiry_ts"])
        except Exception:
            current_expiry = datetime.utcnow()
        start = current_expiry if current_expiry > datetime.utcnow() else datetime.utcnow()
    else:
        start = datetime.utcnow()
    expiry = (start + timedelta(days=duration)).isoformat()
    start_ts = datetime.utcnow().isoformat()
    execute("INSERT INTO subscriptions (user_id,plan_key,start_ts,expiry_ts,status,provider,provider_payment_id,amount) VALUES (?,?,?,?,?,?,?,?)",
            (user_id, plan_key, start_ts, expiry, "active", provider, provider_payment_id, amount))
    return True

def get_user_active_subscription(user_id: int):
    row = fetchone("SELECT * FROM subscriptions WHERE user_id=? AND status='active' ORDER BY expiry_ts DESC LIMIT 1", (user_id,))
    return dict(row) if row else None

def is_user_allowed(user_id: int):
    # config free mode
    if getattr(config, "FREE_MODE", False):
        return True
    user = fetchone("SELECT * FROM users WHERE user_id=?", (user_id,))
    if user and user["free_access"]:
        return True
    row = fetchone("SELECT * FROM subscriptions WHERE user_id=? AND status='active' ORDER BY expiry_ts DESC LIMIT 1", (user_id,))
    if row and row["expiry_ts"] and row["expiry_ts"] > datetime.utcnow().isoformat():
        return True
    return False

def manual_activate(user_id: int, plan_key: str, days: int = None):
    plan = config.PLANS.get(plan_key)
    if not plan and not days:
        return False
    from datetime import datetime
    if days is None:
        days = int(plan["duration_days"])
    start = datetime.utcnow()
    expiry = (start + timedelta(days=days)).isoformat()
    execute("INSERT INTO subscriptions (user_id,plan_key,start_ts,expiry_ts,status,provider,provider_payment_id,amount) VALUES (?,?,?,?,?,?,?,?)",
            (user_id, plan_key or "manual", start.isoformat(), expiry, "active", "manual", "manual", 0.0))
    return True