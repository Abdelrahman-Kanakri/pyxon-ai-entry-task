
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import Settings

print("Loading Settings...")
try:
    s = Settings()
    print(f"Mistral Key Present: {bool(s.llm.mistral_api_key)}")
    if s.llm.mistral_api_key:
        print(f"Mistral Key Value: {s.llm.mistral_api_key[:4]}...{s.llm.mistral_api_key[-4:]}")

    print(f"GenAI Key Present: {bool(s.llm.google_genai_api_key)}")
    if s.llm.google_genai_api_key:
        print(f"GenAI Key Value: {s.llm.google_genai_api_key[:4]}...{s.llm.google_genai_api_key[-4:]}")

    print(f"OpenAI Key Present: {bool(s.llm.openai_api_key)}")
except Exception as e:
    print(f"Error: {e}")
