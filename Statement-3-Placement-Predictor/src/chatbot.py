from rag_engine import RAGEngine

def main():
    print("🎯 Placement Predictor Chatbot\n")

    # 🧑 User Input
    cgpa = float(input("Enter your CGPA: "))
    internships = int(input("Number of internships: "))
    projects = int(input("Number of projects: "))
    dsa = input("DSA level (Beginner/Intermediate/Advanced): ")
    communication = input("Communication (Poor/Average/Good/Excellent): ")

    skills_input = input("Enter your skills (comma separated): ")
    skills = [s.strip() for s in skills_input.split(",")]

    user_profile = {
        "cgpa": cgpa,
        "internships": internships,
        "projects": projects,
        "dsa": dsa,
        "communication": communication,
        "skills": skills
    }

    # 🤖 Engine
    engine = RAGEngine()

    result = engine.full_analysis(user_profile)

    # 🎯 Output
    print("\n==============================")
    print("📊 Readiness Score:", result["score"])
    print("📈 Level:", result["level"])

    print("\n💡 Suggestions:")
    for f in result["feedback"]:
        print("-", f)

    print("\n📚 Relevant Interview Experiences:")
    for exp in result["experiences"]:
        print("-", exp["experience"][:200])
        print()

if __name__ == "__main__":
    main()