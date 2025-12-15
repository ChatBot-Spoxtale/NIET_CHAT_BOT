import requests, time, hashlib, os

SITEMAP = "https://www.niet.co.in/sitemap.xml"
PARSE_ENDPOINT = "http://127.0.0.1:5001/parse"
STATE_FILE = "scraper/data/sitemap.hash"
CHECK_INTERVAL = 3600  # 1 hour


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


def trigger_scrape():
    try:
        requests.post(
            PARSE_ENDPOINT,
            json={"refresh": True},
            timeout=2   # VERY IMPORTANT (no blocking)
        )
        print("✅ Scrape trigger sent")
    except Exception as e:
        print("❌ Could not reach parse_service:", e)


def watch():
    print("👀 Watcher started (monitoring NIET sitemap)")

    while True:
        try:
            current = fetch_hash()
            last = load_last_hash()

            if current != last:
                print("🔄 Change detected in sitemap!")
                trigger_scrape()
                save_hash(current)
            else:
                print("✓ No change detected")

        except Exception as e:
            print("⚠️ Watcher error:", e)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    watch()
