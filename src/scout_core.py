import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

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
        self.state_path = self.root_dir / "data" / "state.json"
        self.bak_path = self.root_dir / "data" / "state.json.bak"
        self.log_path = self.root_dir / "logs" / "system.log"
        
        (self.root_dir / "data").mkdir(exist_ok=True)
        (self.root_dir / "logs").mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=self.log_path, 
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        if not self.state_path.exists():
            self.state = {
                "state_metadata": {
                    "version": "1.0",
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "total_records": 0
                },
                "entities": {}
            }
            self._persist_state()
        else:
            with open(self.state_path, 'r') as f:
                self.state = json.load(f)

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

    def _persist_state(self):
        """
        Atomic Write Protocol: Protects the global state from corruption 
        by utilizing a backup-before-write routine.
        """
        try:
            if self.state_path.exists():
                os.replace(self.state_path, self.bak_path)
            
            with open(self.state_path, 'w') as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            logging.error(f"Persistence Failure: {str(e)}")

    def upsert_record(self, record_data: dict):
        """
        Ingest an entity record or update an existing entry.
        Tracks global hit counts and temporal metadata for the record.
        """
        v_id = record_data.get("vanguard_id")
        
        if v_id in self.state["entities"]:
            self.state["entities"][v_id]["metadata"]["last_seen"] = \
                datetime.utcnow().isoformat() + "Z"
            self.state["entities"][v_id]["metadata"]["hit_count"] += 1
        else:
            self.state["entities"][v_id] = record_data
            self.state["state_metadata"]["total_records"] += 1
            
        self._persist_state()

core_engine = ScoutCore()