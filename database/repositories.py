from database.connection import Database


class NotesRepository:
    def __init__(self, database: Database):
        self.database = database

    def create(self, content: str, title: str = "") -> int:
        with self.database.session() as connection:
            cursor = connection.execute(
                "INSERT INTO notes (title, content) VALUES (?, ?)",
                (title, content),
            )
            return cursor.lastrowid

    def get(self, note_id: int):
        with self.database.session() as connection:
            return connection.execute(
                "SELECT * FROM notes WHERE id = ?", (note_id,)
            ).fetchone()

    def list_all(self):
        with self.database.session() as connection:
            return connection.execute(
                "SELECT * FROM notes ORDER BY updated_at DESC, id DESC"
            ).fetchall()

    def update(self, note_id: int, content: str, title: str = "") -> bool:
        with self.database.session() as connection:
            cursor = connection.execute(
                """
                UPDATE notes
                SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (title, content, note_id),
            )
            return cursor.rowcount == 1

    def delete(self, note_id: int) -> bool:
        with self.database.session() as connection:
            cursor = connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            return cursor.rowcount == 1


class RemindersRepository:
    def __init__(self, database: Database):
        self.database = database

    def create(self, title: str, due_at: str) -> int:
        with self.database.session() as connection:
            cursor = connection.execute(
                "INSERT INTO reminders (title, due_at) VALUES (?, ?)",
                (title, due_at),
            )
            return cursor.lastrowid

    def list_active(self):
        with self.database.session() as connection:
            return connection.execute(
                """
                SELECT * FROM reminders
                WHERE is_complete = 0
                ORDER BY due_at, id
                """
            ).fetchall()

    def complete(self, reminder_id: int) -> bool:
        with self.database.session() as connection:
            cursor = connection.execute(
                "UPDATE reminders SET is_complete = 1 WHERE id = ?", (reminder_id,)
            )
            return cursor.rowcount == 1

    def delete(self, reminder_id: int) -> bool:
        with self.database.session() as connection:
            cursor = connection.execute(
                "DELETE FROM reminders WHERE id = ?", (reminder_id,)
            )
            return cursor.rowcount == 1


class SettingsRepository:
    def __init__(self, database: Database):
        self.database = database

    def get(self, key: str, default: str | None = None) -> str | None:
        with self.database.session() as connection:
            row = connection.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
            return row["value"] if row else default

    def set(self, key: str, value: str) -> None:
        with self.database.session() as connection:
            connection.execute(
                """
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
