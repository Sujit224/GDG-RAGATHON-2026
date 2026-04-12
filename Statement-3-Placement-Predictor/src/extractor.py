import re

def extract_from_text(text):
    text = text.lower()

    data = {
        "cgpa": 0,
        "projects": 0,
        "internships": 0,
        "skills": 0,
        "dsa": 5
    }

    # -------------------------
    # CGPA
    # -------------------------
    cgpa_match = re.search(r'cgpa[:\s]*([0-9]\.?[0-9]*)', text)
    if cgpa_match:
        data["cgpa"] = float(cgpa_match.group(1))

    # -------------------------
    # Projects
    # -------------------------
    data["projects"] = len(re.findall(r'project', text))

    # -------------------------
    # Internships
    # -------------------------
    data["internships"] = len(re.findall(r'intern', text))

    # -------------------------
    # Skills (basic count)
    # -------------------------
    skills_list = [
        "python", "java", "c++", "sql", "ml", "ai",
        "react", "node", "django", "flask"
    ]

    skill_count = sum(1 for skill in skills_list if skill in text)
    data["skills"] = skill_count

    # -------------------------
    # DSA estimation
    # -------------------------
    if "leetcode" in text or "codeforces" in text:
        data["dsa"] = 8
    elif "data structures" in text:
        data["dsa"] = 6

    return data