
import sys
from pathlib import Path
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.parsing.llm_interpreter import LLMInterpreter

print("Initializing Interpreter...")
try:
    interpreter = LLMInterpreter()
except Exception as e:
    print(f"Init failed: {e}")
    sys.exit(1)

print("Calling _raw_llm_call directly...")
prompt = "Identify the language: Hello world"

try:
    response = interpreter._raw_llm_call(prompt)
    print(f"Success: {response}")
except Exception as e:
    print("Caught Exception in Raw Call:")
    traceback.print_exc()
