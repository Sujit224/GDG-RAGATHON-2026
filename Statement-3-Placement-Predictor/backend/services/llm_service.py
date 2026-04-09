import anthropic, json, re, os

SYSTEM_PROMPT_CHAT = """
You are PlaceIQ, a friendly and encouraging placement mentor for engineering students.
Your job is to gather the following information through natural, conversational dialogue:

1. CGPA (0–10 scale)
2. Tech Stack (programming languages, frameworks, tools they know)
3. Number of Projects (with brief descriptions if possible)
4. Number of Internships (company names, duration optional)
5. Communication Skills (self-rated 1–10)
6. Open Source contributions (yes/no, how many PRs/repos)

Rules:
- Ask ONE question at a time, naturally
- Be encouraging and empathetic
- If the student seems uncertain, reassure them
- Once you have ALL 6 data points, say exactly: "PROFILE_COMPLETE"
- Keep responses under 100 words
- Start by greeting the student and asking for their CGPA
"""

SYSTEM_PROMPT_EXTRACT = """
Extract a structured JSON profile from the conversation below.
Return ONLY valid JSON, no markdown, no explanation.

Schema:
{
  "cgpa": <float 0-10>,
  "tech_stack": [<list of strings>],
  "num_projects": <int>,
  "num_internships": <int>,
  "communication": <float 1-10>,
  "opensource": <int, number of contributions or 0>,
  "tech_stack_score": <float, len(tech_stack) / 2 capped at 5>
}

If any value is missing, use a reasonable default (cgpa: 7.0, communication: 5.0, etc.)
"""

def chat_with_student(conversation_history: list[dict]) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Mock dialogue flow based on conversation turns
        turns = len([m for m in conversation_history if m["role"] == "user"])
        if turns == 1:
            return "That's a solid CGPA! What is your current tech stack?"
        elif turns == 2:
            return "Great technologies to know. How many projects have you built using them?"
        elif turns == 3:
            return "Nice! How many internships have you completed so far?"
        elif turns == 4:
            return "Got it. How would you rate your communication skills out of 10?"
        elif turns == 5:
            return "Awesome. Lastly, have you contributed to any open source projects or repos? How many?"
        else:
            return "PROFILE_COMPLETE Thanks for the info, evaluating your readiness now!"

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=256,
        system=SYSTEM_PROMPT_CHAT,
        messages=conversation_history
    )
    return response.content[0].text

def extract_profile(conversation_history: list[dict]) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        user_msgs = [m["content"] for m in conversation_history if m["role"] == "user"]
        
        def extract_num(text, default=0.0):
            nums = re.findall(r'\d+\.?\d*', text)
            return float(nums[0]) if nums else default
            
        cgpa = extract_num(user_msgs[0], 7.0) if len(user_msgs) > 0 else 7.0
        
        tech_stack = []
        if len(user_msgs) > 1:
            tech_text = re.sub(r'[^a-zA-Z0-9\s,]', '', user_msgs[1])
            tech_text = tech_text.replace(',', ' ').split()
            # Exclude very short words like 'and', 'I', etc.
            tech_stack = [t.strip() for t in tech_text if len(t) > 2 and t.lower() not in ('and','the','use','know','with')]
            
        num_projects = int(extract_num(user_msgs[2], 0)) if len(user_msgs) > 2 else 0
        num_internships = int(extract_num(user_msgs[3], 0)) if len(user_msgs) > 3 else 0
        communication = extract_num(user_msgs[4], 5.0) if len(user_msgs) > 4 else 5.0
        
        opensource = 0
        if len(user_msgs) > 5:
            txt = user_msgs[5].lower()
            if 'no' in txt or 'none' in txt:
                opensource = 0
            else:
                opensource = int(extract_num(txt, 0))
                
        tech_score = min(len(tech_stack) / 2.0, 5.0)
        
        return {
            "cgpa": cgpa,
            "tech_stack": tech_stack or ["python", "javascript"],
            "num_projects": num_projects,
            "num_internships": num_internships,
            "communication": communication,
            "opensource": opensource,
            "tech_stack_score": tech_score
        }

    client = anthropic.Anthropic(api_key=api_key)
    convo_text = "\\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in conversation_history
    )
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        system=SYSTEM_PROMPT_EXTRACT,
        messages=[{"role": "user", "content": f"Conversation:\\n{convo_text}"}]
    )
    raw = response.content[0].text
    # Strip markdown code fences if present
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)
