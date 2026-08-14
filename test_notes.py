from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from brain.brain import Brain
from brain.errors import InvalidNoteCommandError, NoteNotFoundError
from capabilities.notes import NotesCapability
from database.connection import Database


def main():
    with TemporaryDirectory() as directory:
        database = Database(Path(directory) / "notes-test.db")
        notes = NotesCapability(database)

        assert notes.execute("create note: First note") == "Note 1 saved."
        assert notes.execute("list notes") == "1. First note"
        assert notes.execute("read note 1") == "Note 1: First note"
        assert notes.execute("update note 1: Revised note") == "Note 1 updated."
        assert notes.execute("read note 1") == "Note 1: Revised note"

        try:
            notes.execute("read note 99")
        except NoteNotFoundError:
            pass
        else:
            raise AssertionError("Expected a missing-note error")

        try:
            notes.execute("note please")
        except InvalidNoteCommandError:
            pass
        else:
            raise AssertionError("Expected an invalid-note-command error")

        assert notes.execute("delete note 1") == "Note 1 deleted."
        assert notes.execute("list notes") == "You do not have any notes yet."

    with TemporaryDirectory() as directory:
        database = Database(Path(directory) / "brain-notes-test.db")
        with patch("capabilities.notes.Database", return_value=database):
            brain = Brain()
            assert brain.process("create note: Through the Brain") == "Note 1 saved."
            assert brain.process("read note 1") == "Note 1: Through the Brain"

    print("Notes capability checks passed.")


if __name__ == "__main__":
    main()
