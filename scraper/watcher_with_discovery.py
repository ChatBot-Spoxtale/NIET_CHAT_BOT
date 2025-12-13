import requests, hashlib, json, time
from pathlib import Path

BASE = Path(__file__).resolve().parent / "data"
URLS = BASE / "urls_meta.json"
META = BASE / "watcher_meta.json"
WEBHOOK = "http://localhost:5001/parse"

def h(t): return hashlib.sha256(t.encode()).hexdigest()
meta = json.load(open(META)) if META.exists() else {}

while True:
    urls = json.load(open(URLS))["urls"]
    for u in urls:
        try:
            r = requests.get(u, timeout=15)
            if meta.get(u) != h(r.text):
                requests.post(WEBHOOK, json={"url": u})
                meta[u] = h(r.text)
                json.dump(meta, open(META, "w"), indent=2)
        except:
            pass
    time.sleep(60)
