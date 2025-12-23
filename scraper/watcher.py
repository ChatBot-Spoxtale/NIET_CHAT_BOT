import requests, time, hashlib, os, subprocess

SITEMAP = "https://www.niet.co.in/sitemap.xml"
CHECK_INTERVAL = 3600  # 1 hour

STATE_FILE = "data/sitemap.hash"

SCRIPTS = [
    "discover_urls.py",
    "courses.py",
    "placements.py",
    "facilities.py",
    "about_courses.py"
]

def fetch_hash():
    r = requests.get(SITEMAP, timeout=20)
    return hashlib.md5(r.text.encode()).hexdigest()

def load_last_hash():
    if os.path.exists(STATE_FILE):
        return open(STATE_FILE).read().strip()
    return None

def save_hash(h):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        f.write(h)

def trigger_scrapers():
    print("🚀 Triggering independent scrapers (sequential)")

    for script in SCRIPTS:
        print(f"▶ Running {script}")
        try:
            subprocess.run(
                ["python", script],
                check=True
            )
            print(f"✓ Finished {script}")
        except subprocess.CalledProcessError as e:
            print(f"❌ {script} failed:", e)
            break   # stop if URLs are missing

def watch():
    print("👀 Watcher started (monitoring NIET sitemap)")

    while True:
        try:
            current = fetch_hash()
            last = load_last_hash()

            if current != last:
                print("🔄 Sitemap changed → running scrapers")
                trigger_scrapers()
                save_hash(current)
            else:
                print("✓ No change detected")

        except Exception as e:
            print("⚠️ Watcher error:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    watch()
