from pathlib import Path
from tempfile import TemporaryDirectory

from database.connection import Database
from database.repositories import (
    NotesRepository,
    RemindersRepository,
    SettingsRepository,
)


def main():
    with TemporaryDirectory() as directory:
        database = Database(Path(directory) / "deskmind-test.db")
        database.initialize()

        notes = NotesRepository(database)
        note_id = notes.create("Initial content", "Project plan")
        assert notes.get(note_id)["title"] == "Project plan"
        assert notes.update(note_id, "Updated content", "Revised plan")
        assert notes.get(note_id)["content"] == "Updated content"
        assert notes.delete(note_id)
        assert notes.get(note_id) is None

        reminders = RemindersRepository(database)
        reminder_id = reminders.create("Submit prototype", "2026-09-01T09:00:00")
        assert len(reminders.list_active()) == 1
        assert reminders.complete(reminder_id)
        assert reminders.list_active() == []

        settings = SettingsRepository(database)
        assert settings.get("theme", "dark") == "dark"
        settings.set("theme", "light")
        assert settings.get("theme") == "light"

    print("SQLite storage checks passed.")


if __name__ == "__main__":
    main()
