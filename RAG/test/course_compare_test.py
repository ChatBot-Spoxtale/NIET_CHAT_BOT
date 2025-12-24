from RAG.scripts.Facilities.compare_course import handle_user_query

def test_why_choose():
    q = "Why choose Bachelor of Computer Applications?"
    ans = handle_user_query(q)
    assert ans is not None
    assert "Why choose" in ans

def test_compare():
    q = "Compare BCA vs BTech"
    ans = handle_user_query(q)
    assert ans is not None
    assert "Course Comparison" in ans
