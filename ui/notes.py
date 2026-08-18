from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from database.connection import Database
from database.repositories import NotesRepository


class NotesPage(QWidget):
    def __init__(self, database: Database | None = None, context=None):
        super().__init__()

        database = database or Database()
        database.initialize()

        self.notes = NotesRepository(database)
        self.current_note_id = None
        self.context = context if context is not None else {}

        # Notes list
        self.notes_list = QListWidget()
        self.notes_list.itemSelectionChanged.connect(
            self.load_selected_note
        )

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(
            "Note title (optional)"
        )

        # Content
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText(
            "Write your note..."
        )

        # Buttons
        new_button = QPushButton("New note")
        new_button.clicked.connect(self.new_note)

        save_button = QPushButton("Save note")
        save_button.clicked.connect(self.save_note)

        delete_button = QPushButton("Delete note")
        delete_button.clicked.connect(self.delete_note)

        # Editor layout
        editor_layout = QVBoxLayout()

        editor_layout.addWidget(QLabel("Title"))
        editor_layout.addWidget(self.title_input)

        editor_layout.addWidget(QLabel("Content"))
        editor_layout.addWidget(self.content_input)

        actions = QHBoxLayout()
        actions.addWidget(new_button)
        actions.addStretch()
        actions.addWidget(delete_button)
        actions.addWidget(save_button)

        editor_layout.addLayout(actions)

        # Main layout
        layout = QHBoxLayout(self)

        layout.addWidget(self.notes_list, 1)

        editor = QWidget()
        editor.setLayout(editor_layout)

        layout.addWidget(editor, 2)

        self.load_notes()

    def load_notes(self):
        """Reload notes from the database."""

        selected_id = self.current_note_id

        # Prevent selection signals while rebuilding the list.
        self.notes_list.blockSignals(True)
        self.notes_list.clear()

        found_selected = False

        for note in self.notes.list_all():

            label = (
                note["title"]
                or note["content"].splitlines()[0][:50]
            )

            item = QListWidgetItem(label)

            item.setData(
                Qt.ItemDataRole.UserRole,
                note["id"]
            )

            self.notes_list.addItem(item)

            if note["id"] == selected_id:
                self.notes_list.setCurrentItem(item)
                found_selected = True

        self.notes_list.blockSignals(False)

        # The previously selected note no longer exists.
        if not found_selected:
            self.current_note_id = None

    def load_selected_note(self):
        """Load the selected note into the editor."""

        selected = self.notes_list.currentItem()

        if selected is None:
            return

        note_id = selected.data(
            Qt.ItemDataRole.UserRole
        )

        note = self.notes.get(note_id)

        if note is None:
            self.current_note_id = None
            self.title_input.clear()
            self.content_input.clear()
            self.load_notes()
            return

        self.current_note_id = note_id
        self.context["active_note"] = {
            "id": note["id"],
            "title": note["title"],
            "content": note["content"],
        }

        self.title_input.setText(
            note["title"]
        )

        self.content_input.setPlainText(
            note["content"]
        )

    def new_note(self):
        """Clear the editor and prepare for a new note."""

        self.current_note_id = None
        self.context.pop("active_note", None)

        # Prevent selection signals from loading
        # the previous note again.
        self.notes_list.blockSignals(True)

        self.notes_list.clearSelection()
        self.notes_list.setCurrentItem(None)

        self.notes_list.blockSignals(False)

        self.title_input.clear()
        self.content_input.clear()

        self.content_input.setFocus()

    def save_note(self):
        """Create a new note or update the selected note."""

        content = self.content_input.toPlainText().strip()
        title = self.title_input.text().strip()

        if not content:
            QMessageBox.warning(
                self,
                "Note is empty",
                "Write something before saving."
            )
            return

        if self.current_note_id is None:

            # CREATE
            self.current_note_id = self.notes.create(
                content,
                title
            )

        else:

            # UPDATE
            self.notes.update(
                self.current_note_id,
                content,
                title
            )

        self.load_notes()
        note = self.notes.get(self.current_note_id)

        if note:
            self.context["active_note"] = {
                "id": note["id"],
                "title": note["title"],
                "content": note["content"],
            }

    def delete_note(self):
        """Delete the currently selected note."""

        if self.current_note_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete note",
            "Delete this note permanently?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.notes.delete(
            self.current_note_id
        )

        self.new_note()
        self.load_notes()

    def showEvent(self, event):
        """Refresh notes whenever the page becomes visible."""

        super().showEvent(event)
        self.load_notes()