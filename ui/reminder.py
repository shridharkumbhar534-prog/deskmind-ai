from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.connection import Database
from database.repositories import RemindersRepository


class ReminderPage(QWidget):

    def __init__(self):
        super().__init__()

        self.database = Database()
        self.database.initialize()

        self.reminders = RemindersRepository(
            self.database
        )

        layout = QVBoxLayout(self)

        title = QLabel("⏰ Reminders")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
        """)

        layout.addWidget(title)

        self.reminder_list = QListWidget()
        layout.addWidget(self.reminder_list)

        self.refresh_button = QPushButton(
            "Refresh"
        )
        self.refresh_button.clicked.connect(
            self.load_reminders
        )

        layout.addWidget(self.refresh_button)

        self.load_reminders()

    def load_reminders(self):

        self.reminder_list.clear()

        reminders = self.reminders.list_active()

        if not reminders:
            item = QListWidgetItem(
                "No active reminders."
            )
            self.reminder_list.addItem(item)
            return

        for reminder in reminders:

            row = QWidget()
            row_layout = QHBoxLayout(row)

            info = QLabel(
                f"⏰ {reminder['title']}\n"
                f"Due: {reminder['due_at']}"
            )

            complete_button = QPushButton(
                "Complete"
            )

            delete_button = QPushButton(
                "Delete"
            )

            reminder_id = reminder["id"]

            complete_button.clicked.connect(
                lambda checked=False,
                rid=reminder_id:
                self.complete_reminder(rid)
            )

            delete_button.clicked.connect(
                lambda checked=False,
                rid=reminder_id:
                self.delete_reminder(rid)
            )

            row_layout.addWidget(info)
            row_layout.addStretch()
            row_layout.addWidget(
                complete_button
            )
            row_layout.addWidget(
                delete_button
            )

            item = QListWidgetItem()
            item.setSizeHint(row.sizeHint())

            self.reminder_list.addItem(item)
            self.reminder_list.setItemWidget(
                item,
                row
            )

    def complete_reminder(self, reminder_id):

        self.reminders.complete(
            reminder_id
        )

        self.load_reminders()

    def delete_reminder(self, reminder_id):

        answer = QMessageBox.question(
            self,
            "Delete Reminder",
            "Delete this reminder?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.reminders.delete(
            reminder_id
        )

        self.load_reminders()