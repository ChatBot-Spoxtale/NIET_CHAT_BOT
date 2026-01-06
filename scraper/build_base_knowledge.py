import subprocess
import sys

SCRIPTS = [
    "discover_urls.py",
    "about_courses.py",
    "courses.py",
    "placements.py",
    "facilities.py",
    "institute.py",
    "research.py",
    "placement_records.py"
]

def run(script):
    print(f"\n▶ Running {script}")
    subprocess.run([sys.executable, script], check=True)

def build():
    print("\n🔁 FULL RE-SCRAPE STARTED\n")

    for script in SCRIPTS:
        run(script)

    print("\n✅ Base knowledge rebuild completed successfully\n")

if __name__ == "__main__":
    build()
