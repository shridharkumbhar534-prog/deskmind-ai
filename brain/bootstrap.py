"""Application capability registrations.

Keep this module as the single place to wire intent names to capability
classes. CapabilityRegistry still creates each class only when it is used.
"""

from capabilities.pdf import PDFCapability
from brain.registry import CapabilityRegistry
from capabilities.chat import ChatCapability
from capabilities.notes import NotesCapability
from capabilities.file_search import FileSearchCapability
from capabilities.reminder import ReminderCapability


def register_capabilities(registry: CapabilityRegistry) -> None:
    """Register the capabilities enabled for this application."""
    registry.register("chat", ChatCapability)
    registry.register("notes", NotesCapability)
    registry.register("pdf", PDFCapability)
    registry.register("file_search", FileSearchCapability)
    registry.register("create_reminder", ReminderCapability)