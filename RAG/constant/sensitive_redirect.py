SENSITIVE_REDIRECT_RESPONSE = {
    "type": "sensitive_redirect",
    "text": (
        "For sensitive or official matters, we do not provide information via chat. "
        "Please contact NIET directly for verified details."
    ),
    "actions": [
        {
            "type": "callback",
            "label": "Request Callback"
        },
        {
            "type": "link",
            "label": "Visit Official Website",
            "url": "https://www.niet.co.in/"
        }
    ]
}


POSITIVE_SENSITIVE_RESPONSE = {
    "type": "positive_sensitive",
    "text": (
        "Yes, NIET is safe. The institute provides a secure and supportive "
        "environment for students."
    ),
    "details": [
        "24×7 campus security with trained guards",
        "CCTV surveillance across the campus",
        "Separate and secure hostels for boys and girls",
        "On-campus medical and first-aid facilities",
        "Well-maintained academic and residential infrastructure"
    ],
    "actions": [
        {
            "type": "callback",
            "label": "Request Callback"
        },
        {
            "type": "link",
            "label": "Visit Official Website",
            "url": "https://www.niet.co.in/"
        }
    ]
}
