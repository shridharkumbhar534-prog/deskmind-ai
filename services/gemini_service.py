from google import genai
from config.settings import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def ask_gemini(prompt):
    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt,
    )

    return response.text