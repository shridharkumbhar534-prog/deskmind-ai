"""AI-dependent dispatcher integration check.

Run this test only when a Gemini API key is configured.
"""

from brain.dispatcher import Dispatcher
from brain.registry import CapabilityRegistry
from capabilities.chat import ChatCapability
from config.settings import GEMINI_API_KEY


if not GEMINI_API_KEY:
    print("SKIPPED: test_dispatcher.py requires a configured Gemini API key.")
else:
    registry = CapabilityRegistry()
    registry.register("chat", ChatCapability)
    dispatcher = Dispatcher(registry)

    result = dispatcher.dispatch("chat", "Hello", {})
    print(result)

    first = registry.get("chat")
    second = registry.get("chat")
    assert first is second
    print("Dispatcher checks passed.")
