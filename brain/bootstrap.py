"""Application capability registrations.

Keep this module as the single place to wire intent names to capability
classes. CapabilityRegistry still creates each class only when it is used.
"""

from brain.registry import CapabilityRegistry
from capabilities.chat import ChatCapability


def register_capabilities(registry: CapabilityRegistry) -> None:
    """Register the capabilities enabled for this application."""
    registry.register("chat", ChatCapability)
