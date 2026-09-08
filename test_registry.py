"""AI-dependent registry integration check.

Run this test only when a Gemini API key is configured.
"""

from brain.registry import CapabilityRegistry
from capabilities.chat import ChatCapability
from config.settings import GEMINI_API_KEY


if not GEMINI_API_KEY:
    print("SKIPPED: test_registry.py requires a configured Gemini API key.")
else:
    registry = CapabilityRegistry()
    registry.register("chat", ChatCapability)

    chat = registry.get("chat")
    print(chat.execute(None, None))
    print("Registry checks passed.")
