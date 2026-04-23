import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from persistence_interface import SQLitePersistence, JSONPersistence

class ScoutCore:
    """
    The central orchestration engine for the Vanguard platform.
    
    A domain-agnostic singleton that manages state persistence, 
    entity deduplication, and data integrity for all specialized scouts.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScoutCore, cls).__new__(cls)
            cls._instance._initialize_core()
        return cls._instance

    def _initialize_core(self):
        """
        Initialize the system environment and load the persistent state.
        Ensures the local infrastructure exists for agnostic data storage.
        """
        self.root_dir = Path(__file__).parent.parent
        self.data_dir = self.root_dir / "data"
        self.state_path = self.data_dir / "state.json"
        self.db_path = self.data_dir / "vanguard.db"
        self.log_path = self.root_dir / "logs" / "system.log"
        
        self.data_dir.mkdir(exist_ok=True)
        (self.root_dir / "logs").mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=self.log_path, 
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize persistence layer (Beta: SQLite)
        self.persistence = SQLitePersistence(self.db_path)
        
        # Check for legacy data and migrate if necessary
        if self.state_path.exists():
            self._migrate_from_json()

    def _migrate_from_json(self):
        """Migrates legacy JSON state to SQLite."""
        logging.info("Legacy state.json found. Initiating migration to SQLite...")
        json_prov = JSONPersistence(self.state_path)
        legacy_state = json_prov.load_state()
        
        if legacy_state and "entities" in legacy_state:
            for v_id, entry in legacy_state["entities"].items():
                self.persistence.upsert_entry(entry)
            
            # Backup the legacy file after successful migration
            bak_path = self.state_path.with_suffix(".json.migrated")
            os.rename(self.state_path, bak_path)
            logging.info(f"Migration complete. Legacy state moved to {bak_path}")

    @property
    def state(self):
        """Legacy compatibility property for state access."""
        return self.persistence.load_state()

    def _sanitize_url(self, raw_url: str) -> str:
        """
        Strip tracking tokens and fragments from a source URL.
        Ensures the base source remains the unique identifier key.
        """
        parsed = urlparse(raw_url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    def generate_vanguard_id(self, source_url: str, entity_label: str) -> str:
        """
        Generate a unique SHA-256 fingerprint for a record.
        Combines the sanitized source and a primary label (e.g., title/name).
        """
        sanitized_url = self._sanitize_url(source_url)
        input_string = f"{sanitized_url}{entity_label}".strip().lower()
        return hashlib.sha256(input_string.encode()).hexdigest()

    def upsert_record(self, record_data: dict):
        """
        Ingest an entity record or update an existing entry.
        Tracks global hit counts and temporal metadata for the record.
        """
        self.persistence.upsert_entry(record_data)

core_engine = ScoutCore()
