# utils.py
from datetime import datetime, timedelta
import csv
import io
import os
from config import FORWARD_LOG_FILE

def now_iso():
    return datetime.utcnow().isoformat()

def add_days_iso(days):
    return (datetime.utcnow() + timedelta(days=days)).isoformat()

def export_logs_csv(rows):
    output = io.StringIO()
    writer = csv.writer(output)
    # accept sqlite3.Row or dict-like rows
    writer.writerow(["log_id","mapping_id","user_id","message_id","source_channel","target_channel","status","error_text","ts"])
    for r in rows:
        writer.writerow([r.get("log_id") if isinstance(r, dict) else (r["log_id"] if "log_id" in r.keys() else ""),
                         r.get("mapping_id") if isinstance(r, dict) else (r["mapping_id"] if "mapping_id" in r.keys() else ""),
                         r.get("user_id") if isinstance(r, dict) else (r["user_id"] if "user_id" in r.keys() else ""),
                         r.get("message_id") if isinstance(r, dict) else (r["message_id"] if "message_id" in r.keys() else ""),
                         r.get("source_channel") if isinstance(r, dict) else (r["source_channel"] if "source_channel" in r.keys() else ""),
                         r.get("target_channel") if isinstance(r, dict) else (r["target_channel"] if "target_channel" in r.keys() else ""),
                         r.get("status") if isinstance(r, dict) else (r["status"] if "status" in r.keys() else ""),
                         r.get("error_text") if isinstance(r, dict) else (r["error_text"] if "error_text" in r.keys() else ""),
                         r.get("ts") if isinstance(r, dict) else (r["ts"] if "ts" in r.keys() else "")])
    output.seek(0)
    return output

def ensure_logs_folder():
    logfile = FORWARD_LOG_FILE
    folder = os.path.dirname(logfile)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)