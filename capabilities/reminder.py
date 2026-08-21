from datetime import datetime

from brain.capability import Capability
from database.connection import Database
from database.repositories import RemindersRepository


class ReminderCapability(Capability):

    def execute(self, request, context=None):
        request = request.strip()

        if not request:
            return "Please tell me what you want to be reminded about."

        database = Database()
        database.initialize()

        reminders = RemindersRepository(database)

        # Temporary simple format:
        # remind me: Submit assignment | 2026-08-21 18:00
        if ":" not in request:
            return (
                "Use this format:\n"
                "remind me: <task> | YYYY-MM-DD HH:MM"
            )

        command = request.split(":", 1)[1].strip()

        if "|" not in command:
            return (
                "Use this format:\n"
                "remind me: <task> | YYYY-MM-DD HH:MM"
            )

        title, due_at = command.split("|", 1)

        title = title.strip()
        due_at = due_at.strip()

        if not title:
            return "Please provide a reminder title."

        try:
            datetime.strptime(due_at, "%Y-%m-%d %H:%M")
        except ValueError:
            return (
                "Invalid date/time.\n"
                "Use: YYYY-MM-DD HH:MM"
            )

        reminder_id = reminders.create(
            title,
            due_at
        )

        return (
            f"Reminder {reminder_id} created.\n"
            f"Task: {title}\n"
            f"Due: {due_at}"
        )