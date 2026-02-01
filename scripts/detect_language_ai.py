
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import Settings
from src.ingestion.loader import DocumentLoader
from src.parsing.llm_interpreter import LLMInterpreter
from src.config.settings import Settings

def detect_language_with_ai(file_path: str):
    print(f"\n🔍 Processing file: {file_path}")
    
    # 1. Load Document (Extract Text)
    print("   Extracting text...")
    try:
        content = DocumentLoader.load_document(file_path)
        text = content.cleaned_text
        print(f"   ✅ Text extracted ({len(text)} chars)")
        if len(text) < 50:
            print("   ⚠️ WARNING: Extracted text is very short! LLM might struggle.")
            print(f"   Sample: {repr(text)}")
    except Exception as e:
        print(f"   ❌ Extraction failed: {e}")
        return

    # 2. Initialize LLM
    print("   Initializing LLM...")
    interpreter = LLMInterpreter()
    
    # Check for keys
    settings = Settings()
    if not settings.llm.mistral_api_key and not settings.llm.google_genai_api_key:
        print("\n❌ Error: No LLM API keys configured!")
        print("   Please set MISTRAL_API_KEY or GOOGLE_GENAI_API_KEY in your .env file.")
        print("   Without an API key, we cannot use AI for detection.")
        return

    # 3. Ask LLM
    print("   Asking AI to identify language...")
    
    try:
        language_code = interpreter.detect_language(text)
        print(f"\n✅ AI Detected Language: {language_code.upper()}")
        print("-" * 40)
        return language_code
    except Exception as e:
        print(f"   ❌ AI Request failed: {e}")

if __name__ == "__main__":
    # Find uploaded PDF
    uploads_dir = project_root / "data" / "uploads"
    if not uploads_dir.exists():
        print("No uploads directory found.")
        sys.exit(1)
        
    pdf_files = list(uploads_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in data/uploads")
        sys.exit(1)
        
    print(f"Found {len(pdf_files)} PDFs. Testing the most recent one...")
    
    # Get most recent file
    latest_file = max(pdf_files, key=os.path.getctime)
    detect_language_with_ai(str(latest_file))
