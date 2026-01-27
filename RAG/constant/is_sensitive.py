SENSITIVE_KEYWORDS = [
    "close",
    "closed",
    "closure",
    "shut",
    "shutdown",
    "shutting",
    "college close",
    "institute close",
    "college shut",

    "ban",
    "banned",
    "blacklist",
    "blacklisted",
    "approval cancelled",
    "approval cancel",
    "recognition cancelled",
    "not approved",
    "approval issue",
    "government ban",
    "aicte ban",
    "aktu ban",
    "ugc ban",

    "arrest",
    "arrested",
    "jail",
    "police",
    "police case",
    "case",
    "court",
    "legal case",
    "raid",
    "fir",
    "complaint",
    "investigation",

    "fraud",
    "scam",
    "fake",
    "fake college",
    "fraud college",
    "scam college",
    "cheating",
    "cheat",
    "misleading",
    "illegal",
    "illegal college",

    "degree valid",
    "degree validity",
    "valid degree",
    "fake degree",
    "invalid degree",
    "degree value",
    "is degree valid",
    "is degree accepted",

    "fake placement",
    "placement fraud",
    "placement scam",
    "false placement",
    "fake package",
    "fees fraud",
    "extra fees",
    "hidden fees",
    "money issue",

    "is it safe",
    "safe to join",
    "future safe",
    "career risk",
    "risky college",
    "should i join",
    "should i take admission",
    "worth joining",
    "trustable",
    "trusted",
    "reliable or not",

    "bad review",
    "negative review",
    "bad college",
    "worst college",
    "poor reputation",
    "why bad",
    "why students complain",

    "news",
    "rumour",
    "rumor",
    "viral",
    "exposed",
    "truth",
    "reality",
]

SAFETY_POSITIVE_KEYWORDS = [
    "safe",
    "safety",
    "is it safe",
    "is safe",
    "safe or not",
    "safe to join",
    "safe for students",
    "safe college",
    "safe campus",

    "trusted",
    "trustable",
    "trustworthy",
    "reliable",
    "reliable or not",
    "genuine",
    "authentic",
    "legit",
    "legitimate",

    "should i join",
    "should i take admission",
    "worth joining",
    "worth it",
    "good college",
    "good institute",
    "right choice",

    "safe for girls",
    "safe for boys",
    "hostel safe",
    "hostel safety",
    "campus safety",
    "student safety",

    "degree valid",
    "degree value",
    "degree accepted",
    "future safe",
    "career safe"
]


def is_sensitive_query(text: str) -> bool:
    if not text:
        return False

    lower_text = text.lower()
    return any(keyword in lower_text for keyword in SENSITIVE_KEYWORDS)

def is_safety_confirmation_query(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in SAFETY_POSITIVE_KEYWORDS)
