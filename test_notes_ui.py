import os
from pathlib import Path
from tempfile import TemporaryDirectory

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from database.connection import Database
from ui.notes import NotesPage


def main():
    application = QApplication.instance() or QApplication([])

    with TemporaryDirectory() as directory:
        page = NotesPage(Database(Path(directory) / "notes-ui-test.db"))
        page.title_input.setText("UI note")
        page.content_input.setPlainText("Created from the notes screen")
        page.save_note()

        assert page.notes_list.count() == 1
        assert page.current_note_id == 1

        page.content_input.setPlainText("Updated from the notes screen")
        page.save_note()
        assert page.notes.get(1)["content"] == "Updated from the notes screen"

    application.quit()
    print("Notes UI checks passed.")


if __name__ == "__main__":
    main()
