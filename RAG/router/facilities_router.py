import json, os

FACILITY_PATH = os.path.join(
    os.path.dirname(__file__),
    "../Json_Format_Data/facilities.json"
)

with open(FACILITY_PATH, "r", encoding="utf-8") as f:
    FACILITIES = json.load(f)


def to_bullets(items):
    bullets = []
    link = None

    for item in items:
        desc = item.get("description", "")
        if not desc:
            continue

        # capture first available url
        if not link:
            link = item.get("url")

        sentences = desc.replace("\n", " ").split(".")
        for s in sentences:
            s = s.strip()
            if len(s) > 8:
                bullets.append(f"• {s}.")

    output = "\n".join(bullets)

    if link:
        output += f"\n\n🔗 Visit Official Link: {link}"

    return output




def facilities_router(query: str):
    q = query.lower()
    # -------- ACADEMIC FACILITIES --------
    if (
    "academic facility" in q
    or "academic facilities" in q
    or "classroom" in q
    or "classrooms" in q
    or "laboratory" in q
    or "laboratories" in q
    or "lab" in q
    or "labs" in q
):
        academic_items = FACILITIES.get("academic_facilities", [])
        return to_bullets(academic_items)

    # -------- HOSTEL --------
    if "hostel" in q or "hostel facilites" in q:
        return to_bullets(
            FACILITIES.get("hostel_facilities", [])
        )

    # -------- AUDITORIUM / SEMINAR --------
    if "auditorium" in q or "seminar hall" in q or "seminar" in q:
        auditorium_items = [
            f for f in FACILITIES.get("other_facilities", [])
            if "auditorium" in (f.get("title") or "").lower()
        ]
        return to_bullets(auditorium_items)

    # -------- MEDICAL --------
    if "medical" in q or "health" in q:
        return to_bullets(
            FACILITIES.get("medical_facilities", [])
        )

    # -------- SPORTS --------
    if "sports" in q or "playground" in q or "gym" in q:
        return to_bullets(
            FACILITIES.get("sports_facilities", [])
        )

    # -------- GENERIC --------
    if "facility" in q or "facilities" in q:
        return (
            "• Hostel facilities\n"
            "• Auditorium & seminar halls\n"
            "• Sports facilities\n"
            "• Medical facilities\n\n"
            "Please tell me which one you want details about."
        )

    return None
