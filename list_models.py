from google import genai
from config.settings import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

for model in client.models.list():
    print("=" * 60)
    print("Name:", model.name)

    if hasattr(model, "supported_actions"):
        print("Supported Actions:", model.supported_actions)