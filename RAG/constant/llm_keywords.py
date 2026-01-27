LLM_KEYWORDS = [
    # 🔹 Comparison & choice
    "compare",
    "comparison",
    "vs",
    "versus",
    "difference",
    "difference between",
    "which is better",
    "better than",
    "instead of",
    "or should i choose",
    "is should"

    # 🔹 Opinion & suggestion
    "should i",
    "should we",
    "is it good to",
    "worth it",
    "opinion",
    "suggest",
    "recommend",
    "recommendation",
    "advice",

    # 🔹 Reasoning & explanation
    "why",
    "explain",
    "reason",
    "benefits of",
    "advantages of",
    "disadvantages of",
    "pros",
    "cons",
    "impact of",

    # 🔹 Career & future
    "scope",
    "future",
    "career",
    "jobs",
    "job opportunities",
    "salary",
    "growth",
    "placement comparison"
]

def should_go_to_llm(question: str) -> bool:
    q = question.lower()
    return any(keyword in q for keyword in LLM_KEYWORDS)
