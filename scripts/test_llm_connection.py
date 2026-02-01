
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import Settings

print("Load settings...")
settings = Settings()

print("\n--- Testing Mistral ---")
if settings.llm.mistral_api_key:
    try:
        from mistralai.client import MistralClient
        from mistralai.models.chat_completion import ChatMessage
        
        print(f"Key: {settings.llm.mistral_api_key[:4]}...")
        client = MistralClient(api_key=settings.llm.mistral_api_key)
        print("Client initialized. Sending request...")
        
        resp = client.chat(
            model=settings.llm.mistral_model,
            messages=[ChatMessage(role="user", content="Hello")]
        )
        print("✅ Success!")
        print(resp.choices[0].message.content)
    except Exception as e:
        print(f"❌ Mistral Failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Skipped (No Key)")

print("\n--- Testing Google GenAI ---")
if settings.llm.google_genai_api_key:
    try:
        import google.generativeai as genai
        
        print(f"Key: {settings.llm.google_genai_api_key[:4]}...")
        genai.configure(api_key=settings.llm.google_genai_api_key)
        
        model = genai.GenerativeModel(settings.llm.google_genai_model)
        print("Client initialized. Sending request...")
        
        resp = model.generate_content("Hello")
        print("✅ Success!")
        print(resp.text)
    except Exception as e:
        print(f"❌ Google Failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Skipped (No Key)")
