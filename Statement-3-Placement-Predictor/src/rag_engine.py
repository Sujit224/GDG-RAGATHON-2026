def calculate_readiness_score(data):
    score = 0

    # CGPA (20)
    if data["cgpa"] >= 9:
        score += 20
    elif data["cgpa"] >= 8:
        score += 15
    elif data["cgpa"] >= 7:
        score += 10

    # Projects (20)
    score += min(data["projects"] * 5, 20)

    # Internships (20)
    score += min(data["internships"] * 10, 20)

    # Skills (20)
    score += min(data["skills"] * 3, 20)

    # DSA (20)
    score += data["dsa"] * 2

    return min(score, 100)