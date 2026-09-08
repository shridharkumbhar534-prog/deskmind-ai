"""AI-dependent Brain chat integration check.

Run this test only when a Gemini API key is configured.
"""

from brain.brain import Brain
from config.settings import GEMINI_API_KEY


if not GEMINI_API_KEY:
    print("SKIPPED: test_brain.py requires a configured Gemini API key.")
else:
    result = Brain().process("Hello")
    print(result)
