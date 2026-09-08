"""AI-dependent Gemini service integration check.

Run this test only when a Gemini API key is configured.
"""

from config.settings import GEMINI_API_KEY
from services.gemini_service import ask_gemini


if not GEMINI_API_KEY:
    print("SKIPPED: test_gemini.py requires a configured Gemini API key.")
else:
    reply = ask_gemini("Introduce yourself in one sentence.")
    print(reply)
