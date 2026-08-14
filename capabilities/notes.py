import re

from brain.capability import Capability
from brain.errors import InvalidNoteCommandError, NoteNotFoundError
from database.connection import Database
from database.repositories import NotesRepository


class NotesCapability(Capability):
    """Create and manage local notes through a small chat command grammar."""

    _CREATE = re.compile(
        r"^(?:create|save|add)\s+(?:a\s+)?note\s*:\s*(?P<content>.+)$",
        re.IGNORECASE,
    )
    _LIST = re.compile(r"^(?:list|show)\s+notes?$", re.IGNORECASE)
    _READ = re.compile(r"^(?:read|show)\s+note\s+(?P<id>\d+)$", re.IGNORECASE)
    _UPDATE = re.compile(
        r"^update\s+note\s+(?P<id>\d+)\s*:\s*(?P<content>.+)$",
        re.IGNORECASE,
    )
    _DELETE = re.compile(r"^delete\s+note\s+(?P<id>\d+)$", re.IGNORECASE)

    def __init__(self, database: Database | None = None):
        database = database or Database()
        database.initialize()
        self.notes = NotesRepository(database)

    def execute(self, request, context=None):
        request = request.strip()

        if match := self._CREATE.match(request):
            note_id = self.notes.create(match["content"].strip())
            return f"Note {note_id} saved."

        if self._LIST.match(request):
            notes = self.notes.list_all()
            if not notes:
                return "You do not have any notes yet."
            return "\n".join(
                f"{note['id']}. {note['content']}" for note in notes
            )

        if match := self._READ.match(request):
            note = self._get_note(int(match["id"]))
            return f"Note {note['id']}: {note['content']}"

        if match := self._UPDATE.match(request):
            note_id = int(match["id"])
            self._get_note(note_id)
            self.notes.update(note_id, match["content"].strip())
            return f"Note {note_id} updated."

        if match := self._DELETE.match(request):
            note_id = int(match["id"])
            self._get_note(note_id)
            self.notes.delete(note_id)
            return f"Note {note_id} deleted."

        raise InvalidNoteCommandError()

    def _get_note(self, note_id: int):
        note = self.notes.get(note_id)
        if note is None:
            raise NoteNotFoundError(note_id)
        return note
