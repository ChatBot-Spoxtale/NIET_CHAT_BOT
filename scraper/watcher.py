import time
import hashlib
import os
import subprocess
import requests
import sqlite3

SITEMAP_URL = "https://www.niet.co.in/sitemap.xml"
CHECK_INTERVAL = 3600  # 1 hour

DATA_DIR = "data"
STATE_DIR = "state"

SITEMAP_STATE = os.path.join(STATE_DIR, "sitemap.hash")
DB_STATE = os.path.join(STATE_DIR, "db.timestamp")

DB_PATH = os.path.join(DATA_DIR, "data.db")
BUILD_SCRIPT = "build_base_knowledge.py"

def ensure_dirs():
    os.makedirs(STATE_DIR, exist_ok=True)

def fetch_db_last_updated():
    if not os.path.exists(DB_PATH):
        return None

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT MAX(last_updated) FROM data")
        return cur.fetchone()[0]
    finally:
        conn.close()

def load_last_db_timestamp():
    return open(DB_STATE).read().strip() if os.path.exists(DB_STATE) else None

def save_db_timestamp(ts):
    with open(DB_STATE, "w") as f:
        f.write(str(ts))

def fetch_sitemap_hash():
    r = requests.get(SITEMAP_URL, timeout=20)
    r.raise_for_status()
    return hashlib.md5(r.text.encode()).hexdigest()

def load_last_sitemap_hash():
    return open(SITEMAP_STATE).read().strip() if os.path.exists(SITEMAP_STATE) else None

def save_sitemap_hash(h):
    with open(SITEMAP_STATE, "w") as f:
        f.write(h)


def trigger_build(reason):
    print(f"\n🚀 Triggered rebuild due to {reason}\n")
    subprocess.run(["python", BUILD_SCRIPT], check=True)


def watch():
    ensure_dirs()
    print("👀 Watcher started (DB → Sitemap priority)")

    while True:
        try:
            current_db_ts = fetch_db_last_updated()
            last_db_ts = load_last_db_timestamp()

            if current_db_ts and str(current_db_ts) != str(last_db_ts):
                save_db_timestamp(current_db_ts)
                trigger_build("DATABASE CHANGE")
                time.sleep(CHECK_INTERVAL)
                continue  
            current_hash = fetch_sitemap_hash()
            last_hash = load_last_sitemap_hash()

            if current_hash != last_hash:
                save_sitemap_hash(current_hash)
                trigger_build("SITEMAP CHANGE")
            else:
                print("✓ No change detected")

        except Exception as e:
            print("⚠️ Watcher error:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    watch()
