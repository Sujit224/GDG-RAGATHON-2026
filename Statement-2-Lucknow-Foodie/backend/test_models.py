import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

available = []
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        # short test
        try:
            model = genai.GenerativeModel(m.name)
            res = model.generate_content('hi')
            print(f"Success: {m.name}")
            available.append(m.name)
            break # Just need one working model
        except Exception as e:
            msg = getattr(e, "message", str(e))
            if "exhausted" not in msg and "Quota" not in msg and "exceeded" not in msg:
                print(f"Failed with other error: {m.name} - {msg}")
            else:
                pass # print(f"Quota error: {m.name}")

if available:
    print("Found working models:", available)
else:
    print("No working models found due to quota or other errors.")
