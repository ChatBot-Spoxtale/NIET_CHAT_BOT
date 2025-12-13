#!/usr/bin/env python3

import os, json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUT = DATA_DIR / "merged.toon"

def extract_strings(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values(): extract_strings(v, out)
    elif isinstance(obj, list):
        for i in obj: extract_strings(i, out)

def merge():
    parts = []
    for p in sorted(DATA_DIR.iterdir()):
        if p.name == "merged.toon": continue
        if p.suffix.lower() in [".json"]:
            try:
                js = json.load(open(p, "r", encoding="utf-8"))
                temp=[]
                extract_strings(js, temp)
                for t in temp:
                    clean = t.strip()
                    if clean:
                        parts.append(clean)
            except Exception as e:
                print("Skipping json parse error", p, e)
        elif p.suffix.lower() in [".txt", ".toon"]:
            txt = p.read_text(encoding="utf-8").strip()
            if txt:
                parts.append(txt)
    # join with double newlines for chunker clarity
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n\n".join(parts), encoding="utf-8")
    print(f"merged {len(parts)} text blocks -> {OUT}")

if __name__ == "__main__":
    merge()
