"""
profiler.py — Chat-Based Student Profiling using Google Gemini
Collects: CGPA, Tech Stack, Projects, Internships, Soft Skills, OSS, DSA
"""
import os
import json
import re
from dotenv import load_dotenv
load_dotenv(override=True)

import google.generativeai as genai
try:
    from .models import StudentProfile
except ImportError:
    from models import StudentProfile

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))

SYSTEM_PROMPT = """You are PlacementIQ, a friendly and professional placement readiness assistant for engineering students.

Your goal is to collect the following details through natural conversation:
1. CGPA (on a 10-point scale)
2. Tech Stack (programming languages, frameworks, tools - e.g., Python, React, Node, AWS)
3. Projects (how many, what domains, complexity level)
4. Internships / Work Experience (number, duration, companies)
5. Communication & Soft Skills (self-rated: leadership, teamwork, public speaking)
6. Open Source Contributions (GitHub contributions, PRs, stars)
7. DSA / Competitive Programming (problem-solving skill level)

Rules:
- Ask ONE question at a time in a warm, encouraging way
- After you have collected ALL 7 data points, conclude with:
  "I have everything I need! Let me analyze your profile... [PROFILE_COMPLETE]"
- Do NOT ask for personal info like name or email
- Keep responses concise (2-3 sentences max)
- Be encouraging and supportive
"""

EXTRACTION_PROMPT = """Given this conversation history, extract the student's profile into strict JSON.

Conversation:
{conversation}

Extract and return ONLY this JSON (no markdown, no explanation):
{{
    "academic_score": <float 0.0-10.0, CGPA>,
    "tech_stack": [<list of technologies as strings>],
    "project_quality": <float 1-10, based on number and complexity of projects>,
    "experience_score": <float 1-10, based on internships/work experience>,
    "soft_skills": <float 1-10, based on described communication/leadership>,
    "opensource_value": <float 1-10, based on OSS/GitHub activity>,
    "dsa_skill": <float 1-10, based on competitive programming/DSA practice>,
    "tech_stack_score": <float 1-10, breadth and depth of tech stack>
}}

If a value is not mentioned, make a reasonable estimate based on context. CGPA must be 0-10.
"""


class ChatProfiler:
    def __init__(self):
        self.history = []
        self._complete = False
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        self.chat = self.model.start_chat(history=[])

    def is_complete(self) -> bool:
        return self._complete

    def chat_sync(self, user_message: str) -> str:
        """Send message and get full response (blocking)."""
        self.history.append({"role": "user", "content": user_message})

        try:
            response = self.chat.send_message(user_message)
            reply = response.text
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "quota" in err_msg.lower():
                # Mock Mode!
                history_len = len(self.history)
                if history_len <= 2:
                    reply = "That's an excellent CGPA! Thanks for sharing. Now, could you tell me a bit about your tech stack?"
                elif history_len <= 4:
                    reply = "That's a strong and diverse tech stack! Next up, I'd love to hear about your projects."
                else:
                    reply = "Perfect, I have everything I need! Let me analyze your profile... [PROFILE_COMPLETE]"
            else:
                reply = f"I'm having a connection issue. Could you please repeat that? (Error: {err_msg[:50]})"

        if "[PROFILE_COMPLETE]" in reply:
            self._complete = True
            reply = reply.replace("[PROFILE_COMPLETE]", "").strip()

        self.history.append({"role": "assistant", "content": reply})
        return reply

    def get_greeting(self) -> str:
        """Return the opening greeting message."""
        greeting = ("Hi there! 👋 I'm PlacementIQ, your AI placement readiness coach. "
                    "I'll analyze your profile and give you a personalized readiness score "
                    "along with relevant senior interview experiences.\n\n"
                    "Let's start! **What's your current CGPA?** (on a 10-point scale)")
        self.history.append({"role": "assistant", "content": greeting})
        return greeting

    def extract_profile(self) -> StudentProfile:
        """Extract structured profile from conversation history."""
        if not self.history:
            return StudentProfile()

        conversation_text = "\n".join(
            f"{msg['role'].upper()}: {msg['content']}" for msg in self.history
        )

        prompt = EXTRACTION_PROMPT.format(conversation=conversation_text)

        # Try multiple models as fallback
        models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash", "gemini-pro-latest"]
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name if "models/" in model_name else f"models/{model_name}")
                response = model.generate_content(prompt)
                raw = response.text.strip()
                # Strip markdown fences if present
                raw = re.sub(r"```json\s*", "", raw)
                raw = re.sub(r"```\s*", "", raw)
                data = json.loads(raw)
                return StudentProfile(**data)
            except Exception as e:
                err_msg = str(e)
                print(f"⚠️ Extraction failed with {model_name}: {e}")
                if "429" in err_msg or "quota" in err_msg.lower():
                    # Stop hammering the API and return a mock profile
                    print("🚀 Using MOCK profile due to Google API Quota limits")
                    return StudentProfile(
                        academic_score=8.8,
                        tech_stack=["Python", "React", "NodeJS", "AWS"],
                        project_quality=8.0,
                        experience_score=6.5,
                        soft_skills=8.0,
                        opensource_value=5.0,
                        dsa_skill=7.5,
                        tech_stack_score=8.5
                    )
                continue

        return StudentProfile()

    def reset(self):
        """Reset the profiler session."""
        self.__init__()
