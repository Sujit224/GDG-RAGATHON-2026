import json
import re

from openai import OpenAI

from src.config import OPENAI_API_KEY


def _base_profile():
    return {
        "academic_score": 7,
        "dsa": 5,
        "projects": 1,
        "experience": 0,
        "opensource": 0,
        "soft_skills": 5,
        "tech_stack": 0,
        "skills": [],
    }


def _normalize_profile(profile):
    out = _base_profile()
    out.update(profile or {})

    out["academic_score"] = max(0, min(10, float(out.get("academic_score", 7))))
    out["dsa"] = max(0, min(10, int(out.get("dsa", 5))))
    out["projects"] = max(1, min(5, int(out.get("projects", 1))))
    out["experience"] = max(0, min(3, int(out.get("experience", 0))))
    out["opensource"] = max(0, min(1, int(out.get("opensource", 0))))
    out["soft_skills"] = max(0, min(10, int(out.get("soft_skills", 5))))
    out["tech_stack"] = max(0, min(10, int(out.get("tech_stack", 0))))

    skills = out.get("skills", [])
    if not isinstance(skills, list):
        skills = []
    skills = [str(s).strip() for s in skills if str(s).strip()]
    out["skills"] = skills if skills else ["General Programming"]
    return out


def _extract_profile_rules(text):
    text_lower = text.lower()
    profile = _base_profile()

    cgpa = re.findall(r"(\d\.\d{1,2})\s*(cgpa|gpa)", text_lower)
    percent = re.findall(r"(\d{2,3})\s*%", text_lower)
    percentile = re.findall(r"(\d{2,3})\s*percentile", text_lower)

    if cgpa:
        profile["academic_score"] = float(cgpa[0][0])
    elif percentile:
        profile["academic_score"] = min(10, int(percentile[0]) / 10)
    elif percent:
        profile["academic_score"] = min(10, int(percent[0]) / 10)

    if any(x in text_lower for x in ["iit", "nit", "iiit"]):
        profile["academic_score"] = max(profile["academic_score"], 8.5)

    skills_db = {
        "languages": ["python", "java", "c++", "c", "go", "javascript", "typescript"],
        "frontend": ["react", "next", "html", "css"],
        "backend": ["node", "express", "django", "flask"],
        "database": ["sql", "mysql", "mongodb"],
        "cloud": ["aws", "azure", "gcp"],
        "ml": ["ml", "ai", "nlp", "tensorflow", "pytorch"],
        "tools": ["docker", "kubernetes", "linux", "git"],
    }

    found_skills = set()
    domain_score = 0
    for _, skills in skills_db.items():
        for skill in skills:
            if re.search(rf"\b{skill}\b", text_lower):
                domain_score += 1
                if skill in ["ml", "ai", "nlp", "sql"]:
                    found_skills.add(skill.upper())
                elif skill == "c++":
                    found_skills.add("C++")
                elif skill == "go":
                    found_skills.add("Go")
                else:
                    found_skills.add(skill.capitalize())

    profile["skills"] = list(found_skills) if found_skills else ["General Programming"]
    profile["tech_stack"] = min(10, domain_score)

    if re.search(r"(dsa|data structures|algorithms)", text_lower):
        profile["dsa"] = 7
    if re.search(r"(competitive programming|codeforces|leetcode)", text_lower):
        profile["dsa"] = 9

    proj_num = re.search(r"projects?\s*[:\-]?\s*(\d+)", text_lower)
    if proj_num:
        profile["projects"] = min(5, int(proj_num.group(1)))
    else:
        verbs = len(re.findall(r"(built|developed|created|designed)", text_lower))
        profile["projects"] = min(5, max(1, verbs))

    if re.search(r"(scalable|architecture|system design)", text_lower):
        profile["projects"] = min(5, profile["projects"] + 1)

    exp_num = re.search(r"(internships?|experience)\s*[:\-]?\s*(\d+)", text_lower)
    if exp_num:
        profile["experience"] = min(3, int(exp_num.group(2)))
    else:
        exp_hits = len(re.findall(r"(intern|worked|engineer)", text_lower))
        profile["experience"] = min(3, exp_hits)

    if re.search(r"(open source|github|contribution)", text_lower):
        profile["opensource"] = 1

    soft_hits = len(re.findall(r"(leadership|communication|teamwork|management)", text_lower))
    profile["soft_skills"] = min(10, 5 + soft_hits)
    return _normalize_profile(profile)


def _extract_profile_llm(text):
    if not OPENAI_API_KEY:
        return None

    client = OpenAI(api_key=OPENAI_API_KEY)
    system_prompt = (
        "You are an extraction engine. Extract a placement profile as strict JSON only. "
        "Return keys: academic_score (0-10), dsa (0-10), projects (0-5), "
        "experience (0-3), opensource (0 or 1), soft_skills (0-10), tech_stack (0-10), "
        "skills (array of strings). No markdown. No extra keys."
    )

    user_prompt = (
        "Extract the profile from the following resume/profile text.\n\n"
        f"{text}\n\n"
        "Return JSON object only."
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = resp.choices[0].message.content or "{}"
        parsed = json.loads(content)
        return _normalize_profile(parsed)
    except Exception:
        return None


def extract_profile(text):
    llm_profile = _extract_profile_llm(text)
    if llm_profile:
        return llm_profile
    return _extract_profile_rules(text)