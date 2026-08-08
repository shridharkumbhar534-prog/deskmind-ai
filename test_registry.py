from brain.registry import CapabilityRegistry
from capabilities.chat import ChatCapability


registry = CapabilityRegistry()

registry.register("chat", ChatCapability)

chat = registry.get("chat")

print(chat.execute(None, None))