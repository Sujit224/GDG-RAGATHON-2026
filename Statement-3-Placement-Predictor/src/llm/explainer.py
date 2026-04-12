def _top_strengths(profile):
    strengths = []

    if profile.get("academic_score", 0) >= 8.0:
        strengths.append("Strong academics foundation")
    if len(profile.get("skills", [])) >= 6:
        strengths.append("Wide and relevant tech stack")
    if profile.get("projects", 0) >= 3:
        strengths.append("Good project depth")
    if profile.get("experience", 0) >= 1:
        strengths.append("Has internship/industry exposure")
    if profile.get("dsa", 0) >= 7:
        strengths.append("Solid DSA readiness")

    if not strengths:
        strengths.append("Early stage profile with clear growth potential")
    return strengths[:3]


def _priority_gaps(profile, role):
    gaps = []
    dsa = profile.get("dsa", 0)
    projects = profile.get("projects", 0)
    experience = profile.get("experience", 0)
    skills = set(profile.get("skills", []))

    if dsa < 7:
        gaps.append("DSA consistency and speed under timed conditions")
    if projects < 3:
        gaps.append("Project depth (problem statement, scale, measurable impact)")
    if experience < 1:
        gaps.append("Internship or open-source proof of execution")
    if role == "ML" and "ML" not in skills and "AI" not in skills:
        gaps.append("ML-focused portfolio alignment for target role")
    if "SQL" not in skills:
        gaps.append("SQL fundamentals for screening rounds")

    return gaps[:4]


def _next_7_days_plan(profile, role):
    plan = []

    if profile.get("dsa", 0) < 7:
        plan.append("Solve 15-20 DSA problems (arrays, graphs, DP) and revise patterns.")
    if profile.get("projects", 0) < 3:
        plan.append("Ship one portfolio-grade project update with README, architecture, and demo.")
    if profile.get("experience", 0) < 1:
        plan.append("Apply to 20 internships/open-source tasks with tailored resume bullets.")
    if role == "ML":
        plan.append("Train and deploy one ML mini-project with metrics and error analysis.")
    else:
        plan.append("Practice one system-design topic and one behavioral mock interview.")

    return plan[:4]


def _trim_chunk(text, max_len=260):
    cleaned = " ".join(str(text).strip().split())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3] + "..."


def generate_explanation(profile, score, interviews, role="SDE"):
    score = round(float(score), 2)
    role = role or "SDE"

    if score >= 75:
        verdict = "You are in a strong zone for shortlist conversion."
    elif score >= 50:
        verdict = "You are in a moderate zone; focused improvements can move you up quickly."
    else:
        verdict = "You are in a building phase; fundamentals first will create the biggest jump."

    strengths = _top_strengths(profile)
    gaps = _priority_gaps(profile, role)
    plan = _next_7_days_plan(profile, role)

    lines = [
        f"Placement Readiness Score: {score}/100",
        f"Target Role: {role}",
        f"Verdict: {verdict}",
        "",
        "Top Strengths:",
    ]
    lines.extend([f"- {item}" for item in strengths])

    lines.append("")
    lines.append("Priority Gaps:")
    lines.extend([f"- {item}" for item in gaps] if gaps else ["- Keep consistency and interview rhythm high."])

    lines.append("")
    lines.append("Action Plan (Next 7 Days):")
    lines.extend([f"- {item}" for item in plan])

    lines.append("")
    lines.append("Interview Prep Anchors (Top Matches):")
    if interviews:
        for idx, interview in enumerate(interviews[:3], start=1):
            lines.append(f"- Match {idx}: {_trim_chunk(interview)}")
    else:
        lines.append("- No interview records matched right now. Add/populate vector DB for stronger personalization.")

    lines.append("")
    lines.append("Mentor Note:")
    lines.append("Focus on one measurable upgrade per week and track mock performance + resume quality together.")

    return "\n".join(lines)