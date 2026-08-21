from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal

from database.connection import Database
from database.repositories import RemindersRepository


class ReminderScheduler(QObject):
    reminder_due = Signal(str, str)

    def __init__(self, interval_ms=30_000):
        super().__init__()

        self.database = Database()
        self.database.initialize()

        self.reminders = RemindersRepository(
            self.database
        )

        self.timer = QTimer(self)
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(
            self.check_reminders
        )

        # Prevent the same reminder from being
        # notified repeatedly while the app is running.
        self.notified_ids = set()

    def start(self):
        self.check_reminders()
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def check_reminders(self):

        now = datetime.now()

        try:
            reminders = self.reminders.list_active()
        except Exception as error:
            print("Reminder scheduler error:", error)
            return

        for reminder in reminders:

            reminder_id = reminder["id"]

            if reminder_id in self.notified_ids:
                continue

            due_at = self.parse_datetime(
                reminder["due_at"]
            )

            if due_at is None:
                print(
                    f"Invalid reminder date/time "
                    f"for reminder {reminder_id}: "
                    f"{reminder['due_at']}"
                )
                continue

            if due_at <= now:

                self.notified_ids.add(
                    reminder_id
                )

                self.reminder_due.emit(
                    reminder["title"],
                    reminder["due_at"]
                )

    @staticmethod
    def parse_datetime(value):

        formats = (
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
        )

        for date_format in formats:

            try:
                return datetime.strptime(
                    value,
                    date_format
                )
            except ValueError:
                continue

        return None