import json
import os

DATA_DIR = "data"

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_context():
    admission = load_json("admission_data.json")
    courses = load_json("course_data.json")
    facilities = load_json("facility_data.json")
    clubs = load_json("club_data.json")
    overview_research = load_json("overview_research_data.json")

    context = []

    # --- ABOUT NIET ---
    context.append("ABOUT NIET:")
    if isinstance(overview_research, dict):
        for k, v in overview_research.items():
            context.append(f"{k.replace('_', ' ').title()}: {v}")

    # --- ADMISSION ---
    context.append("\nADMISSION INFORMATION:")
    if isinstance(admission, dict):
        for k, v in admission.items():
            context.append(f"- {k.replace('_', ' ').title()}: {v}")

    # --- COURSES ---
    context.append("\nCOURSES OFFERED:")
    if isinstance(courses, dict):
        for value in courses.values():
            if isinstance(value, list):
                for course in value:
                    if isinstance(course, dict):
                        context.append(
                            f"- {course.get('course_name', '')}: {course.get('overview', '')}"
                        )
            elif isinstance(value, dict):
                context.append(
                    f"- {value.get('course_name', '')}: {value.get('overview', '')}"
                )

    # --- FACILITIES ---
    context.append("\nFACILITIES:")
    if isinstance(facilities, dict):
        for value in facilities.values():
            if isinstance(value, list):
                for f in value:
                    if isinstance(f, dict):
                        context.append(f"- {f.get('name', '')}")
            elif isinstance(value, dict):
                context.append(f"- {value.get('name', '')}")

    # --- CLUBS ---
    context.append("\nSTUDENT CLUBS:")
    if isinstance(clubs, dict):
        for value in clubs.values():
            if isinstance(value, list):
                for c in value:
                    if isinstance(c, dict):
                        context.append(f"- {c.get('name', '')}")
            elif isinstance(value, dict):
                context.append(f"- {value.get('name', '')}")

    return "\n".join(context)
