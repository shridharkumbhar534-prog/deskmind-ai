from brain.dispatcher import Dispatcher
from brain.registry import CapabilityRegistry
from capabilities.chat import ChatCapability


registry = CapabilityRegistry()

registry.register("chat", ChatCapability)

dispatcher = Dispatcher(registry)

result = dispatcher.dispatch(
    "chat",
    "Hello",
    {}
)

print(result)

first = registry.get("chat")
second = registry.get("chat")

print(first is second)