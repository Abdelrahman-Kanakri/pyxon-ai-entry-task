    
try:
    from mistralai.client import MistralClient
    print("Old style import SUCCESS")
except ImportError as e:
    print(f"Old style import FAILED: {e}")

try:
    from mistralai import Mistral
    print("New style import SUCCESS")
except ImportError as e:
    print(f"New style import FAILED: {e}")
