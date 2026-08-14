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
    def __init__(self, database: Database | None = None):
        super().__init__()

        database = database or Database()
        database.initialize()
        self.notes = NotesRepository(database)
        self.current_note_id = None

        self.notes_list = QListWidget()
        self.notes_list.itemSelectionChanged.connect(self.load_selected_note)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Note title (optional)")

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Write your note...")

        new_button = QPushButton("New note")
        new_button.clicked.connect(self.new_note)
        save_button = QPushButton("Save note")
        save_button.clicked.connect(self.save_note)
        delete_button = QPushButton("Delete note")
        delete_button.clicked.connect(self.delete_note)

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

        layout = QHBoxLayout(self)
        layout.addWidget(self.notes_list, 1)

        editor = QWidget()
        editor.setLayout(editor_layout)
        layout.addWidget(editor, 2)

        self.load_notes()

    def load_notes(self):
        selected_id = self.current_note_id
        self.notes_list.clear()

        for note in self.notes.list_all():
            label = note["title"] or note["content"].splitlines()[0][:50]
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, note["id"])
            self.notes_list.addItem(item)

            if note["id"] == selected_id:
                self.notes_list.setCurrentItem(item)

    def load_selected_note(self):
        selected = self.notes_list.currentItem()
        if selected is None:
            return

        note_id = selected.data(Qt.ItemDataRole.UserRole)
        note = self.notes.get(note_id)
        if note is None:
            self.new_note()
            return

        self.current_note_id = note_id
        self.title_input.setText(note["title"])
        self.content_input.setPlainText(note["content"])

    def new_note(self):
        self.current_note_id = None
        self.notes_list.clearSelection()
        self.title_input.clear()
        self.content_input.clear()
        self.content_input.setFocus()

    def save_note(self):
        content = self.content_input.toPlainText().strip()
        title = self.title_input.text().strip()

        if not content:
            QMessageBox.warning(self, "Note is empty", "Write something before saving.")
            return

        if self.current_note_id is None:
            self.current_note_id = self.notes.create(content, title)
        else:
            self.notes.update(self.current_note_id, content, title)

        self.load_notes()

    def delete_note(self):
        if self.current_note_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete note",
            "Delete this note permanently?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.notes.delete(self.current_note_id)
        self.new_note()
        self.load_notes()
