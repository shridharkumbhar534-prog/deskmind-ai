import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


def default_database_path() -> Path:
    """Return a per-user location for DeskMind's local data."""
    data_dir = Path(
        os.getenv("LOCALAPPDATA", Path.home() / ".deskmind_ai")
    ) / "DeskMindAI"
    return data_dir / "deskmind.db"


class Database:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else default_database_path()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def session(self):
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.session() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    due_at TEXT NOT NULL,
                    is_complete INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
