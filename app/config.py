import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    POLICY_PATH: Path = BASE_DIR / "policy.json"

    @classmethod
    def load_policy(cls) -> str:
        """Loads policy.json and converts it to a string for model prompt injection."""
        if not cls.POLICY_PATH.exists():
            raise FileNotFoundError(f"Policy file missing at {cls.POLICY_PATH}")
        
        with open(cls.POLICY_PATH, "r", encoding="utf-8") as f:
            policy_data = json.load(f)
        
        return json.dumps(policy_data, indent=2)

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is missing. Check your .env file.")