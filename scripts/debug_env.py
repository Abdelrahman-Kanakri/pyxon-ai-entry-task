
import os
from dotenv import load_dotenv

load_dotenv()

print("Checking Environment Variables...")
keys_to_check = [
    "MISTRAL_API_KEY", "OPENAI_MISTRAL_API_KEY", "LLM_MISTRAL_API_KEY",
    "GOOGLE_GENAI_API_KEY", "GEMINI_API_KEY", "OPENAI_GOOGLE_GENAI_API_KEY"
]

found = False
for key in keys_to_check:
    val = os.getenv(key)
    if val:
        found = True
        masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "****"
        print(f"✅ Found {key}: {masked}")
    else:
        print(f"❌ Missing {key}")

from src.config.settings import Settings
try:
    s = Settings()
    print("\nSettings Loaded:")
    print(f"Mistral Key: {'SET' if s.llm.mistral_api_key else 'NOT SET'}")
    print(f"GenAI Key: {'SET' if s.llm.google_genai_api_key else 'NOT SET'}")
except Exception as e:
    print(f"\nError loading settings: {e}")
