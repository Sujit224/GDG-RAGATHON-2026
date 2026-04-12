def process_features(data):
    return [
        data["academic_score"],
        data["dsa"],
        data["projects"],
        data["experience"],
        data["opensource"],
        data["soft_skills"],
        data["tech_stack"]
    ]