from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Base directory (points to src/)
BASE_DIR = Path(__file__).resolve().parent

# OpenAI key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Absolute path to model file
MODEL_PATH = BASE_DIR / "models" / "regression.pkl"