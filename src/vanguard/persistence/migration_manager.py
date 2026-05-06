import logging
from pathlib import Path
from .engine import SQLiteEngine

logger = logging.getLogger("vanguard.persistence.migrations")

class MigrationManager:
    """
    Manages database schema transitions using SQL migration scripts.
    """

    def __init__(self, engine: SQLiteEngine, migrations_dir: Path) -> None:
        self.engine = engine
        self.migrations_dir = migrations_dir
        self._ensure_migration_table()

    def _ensure_migration_table(self) -> None:
        """Creates the internal table to track applied migrations."""
        with self.engine.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    migration_name TEXT PRIMARY KEY,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)

    def apply_all(self) -> None:
        """Executes all pending migration scripts in alphabetical order."""
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        
        with self.engine.get_connection() as conn:
            applied = [row[0] for row in conn.execute("SELECT migration_name FROM _migrations").fetchall()]
            
            for m_file in migration_files:
                if m_file.name not in applied:
                    logger.info(f"Applying migration: {m_file.name}")
                    try:
                        with open(m_file, 'r') as f:
                            sql = f.read()
                            conn.executescript(sql)
                            conn.execute("INSERT INTO _migrations (migration_name) VALUES (?)", (m_file.name,))
                            logger.info(f"Successfully applied {m_file.name}")
                    except Exception as e:
                        logger.error(f"Failed to apply migration {m_file.name}: {str(e)}")
                        raise
            conn.commit()
