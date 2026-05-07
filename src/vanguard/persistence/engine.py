import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger("vanguard.persistence.engine")

class SQLiteEngine:
    """
    Manages the SQLite database connection and configuration.
    Enables WAL mode and handles row mapping.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Configure the database with recommended defaults."""
        with self.get_connection() as conn:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA foreign_keys = ON;")

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with dict-like row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
