import os
import json
import logging
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime

class PersistenceInterface(ABC):
    """
    Abstract interface for state persistence to allow alpha-to-beta migration.
    All I/O must pass through this interface.
    """
    
    @abstractmethod
    def load_state(self) -> dict:
        """Loads the current global state from storage. (Legacy/Migration)"""
        pass

    @abstractmethod
    def save_state(self, state: dict):
        """Saves the global state using an atomic write routine. (Legacy/Migration)"""
        pass

    @abstractmethod
    def get_entry(self, vanguard_id: str) -> dict:
        """Retrieves a single entry for analysis or status updates."""
        pass

    @abstractmethod
    def upsert_entry(self, entry_object: dict) -> bool:
        """Handles new discovery ingestion and updating existing records."""
        pass

    @abstractmethod
    def query_entries(self, filter_criteria: dict = None) -> list:
        """Retrieves entries based on status or other criteria."""
        pass

    @abstractmethod
    def archive_expired(self, ttl_days: int = 30) -> int:
        """Executes the State Decay logic to transition stale entries to 'expired'."""
        pass

class JSONPersistence(PersistenceInterface):
    """
    JSON implementation of the persistence interface.
    Follows the Atomic Write Protocol as defined in the SDD.
    """
    
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.bak_path = state_path.with_suffix(state_path.suffix + ".bak")
        self.tmp_path = state_path.with_suffix(state_path.suffix + ".tmp")

    def load_state(self) -> dict:
        if not self.state_path.exists():
            return None
        
        try:
            with open(self.state_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load state: {str(e)}")
            return None

    def save_state(self, state: dict):
        try:
            if self.state_path.exists():
                if self.bak_path.exists():
                    self.bak_path.unlink()
                os.rename(self.state_path, self.bak_path)
            
            with open(self.tmp_path, 'w') as f:
                json.dump(state, f, indent=4)
            
            os.rename(self.tmp_path, self.state_path)
        except Exception as e:
            logging.error(f"Persistence Failure (Atomic Write Protocol): {str(e)}")
            if self.tmp_path.exists() and not self.state_path.exists():
                os.rename(self.tmp_path, self.state_path)

    def get_entry(self, vanguard_id: str) -> dict:
        state = self.load_state()
        if state and "entities" in state:
            return state["entities"].get(vanguard_id)
        return None

    def upsert_entry(self, entry_object: dict) -> bool:
        v_id = entry_object.get("vanguard_id")
        state = self.load_state() or {"state_metadata": {"version": "1.0", "total_records": 0}, "entities": {}}
        
        if v_id in state["entities"]:
            # Update existing
            existing = state["entities"][v_id]
            existing["metadata"]["last_seen"] = datetime.utcnow().isoformat() + "Z"
            existing["metadata"]["hit_count"] += 1
            existing["status"] = "active"
        else:
            # New entry
            state["entities"][v_id] = entry_object
            state["state_metadata"]["total_records"] += 1
            
        self.save_state(state)
        return True

    def query_entries(self, filter_criteria: dict = None) -> list:
        state = self.load_state()
        if not state or "entities" not in state:
            return []
        
        entities = list(state["entities"].values())
        if not filter_criteria:
            return entities
            
        filtered = []
        for e in entities:
            match = True
            for k, v in filter_criteria.items():
                if e.get(k) != v:
                    match = False
                    break
            if match:
                filtered.append(e)
        return filtered

    def archive_expired(self, ttl_days: int = 30) -> int:
        # Simplified implementation for JSON
        return 0

class SQLitePersistence(PersistenceInterface):
    """
    SQLite implementation of the persistence interface (Phase 2 / Beta).
    Uses WAL mode and adheres to VAN_SCHEMA_PERSISTENCE.
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self):
        with self._get_connection() as conn:
            conn.execute("PRAGMA journal_mode = WAL;")
            # Table: entries
            # Adding hit_count to the standard as it's required for lifecycle management
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    vanguard_id TEXT PRIMARY KEY,
                    provider_id TEXT NOT NULL,
                    identity_manifest TEXT NOT NULL,
                    entry_data TEXT NOT NULL,
                    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    hit_count INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'active'
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS enrichment (
                    vanguard_id TEXT PRIMARY KEY,
                    integrity_score REAL CHECK (integrity_score >= 0.0 AND integrity_score <= 1.0),
                    alignment_score REAL CHECK (alignment_score >= 0.0 AND alignment_score <= 1.0),
                    analysis_payload TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vanguard_id) REFERENCES entries (vanguard_id) ON DELETE CASCADE
                );
            """)
            # Indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_provider ON entries(provider_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_last_seen ON entries(last_seen);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status);")

    def _map_row_to_discovery(self, row) -> dict:
        """Maps a DB row back to the Vanguard Discovery Contract structure."""
        if not row:
            return None
        res = dict(row)
        entry_data = json.loads(res["entry_data"])
        
        # Reconstruct the structured dictionary
        # Ensure source_url and scout are correctly mapped
        source_url = entry_data.get("source_url") or entry_data.get("source") or "unknown"
        scout_name = res["provider_id"]
        
        # Ensure title/label is available in content
        if "title" not in entry_data and "label" not in entry_data:
            # Try to find it if it was at the top level during migration
            pass

        return {
            "vanguard_id": res["vanguard_id"],
            "source_info": {
                "scout": scout_name,
                "source_url": source_url
            },
            "content": entry_data,
            "metadata": {
                "first_seen": res["first_seen"],
                "last_seen": res["last_seen"],
                "hit_count": res["hit_count"]
            },
            "status": res["status"]
        }

    def load_state(self) -> dict:
        """Legacy compatibility: returns full state as dict."""
        entries_list = self.query_entries()
        return {
            "state_metadata": {
                "version": "1.0-beta",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "total_records": len(entries_list)
            },
            "entities": {e["vanguard_id"]: e for e in entries_list}
        }

    def save_state(self, state: dict):
        """Legacy compatibility: upserts all entries from dict."""
        for v_id, entry in state.get("entities", {}).items():
            self.upsert_entry(entry)

    def get_entry(self, vanguard_id: str) -> dict:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM entries WHERE vanguard_id = ?", (vanguard_id,)).fetchone()
            return self._map_row_to_discovery(row)

    def upsert_entry(self, entry_object: dict) -> bool:
        v_id = entry_object.get("vanguard_id")
        
        # Better provider_id extraction
        provider_id = entry_object.get("source_info", {}).get("scout") or \
                      entry_object.get("scout") or \
                      "unknown"
        
        # Entry Data normalization
        # If it has 'content', that's our data. If not, maybe it's legacy 'data' or the object itself.
        entry_data_dict = entry_object.get("content") or \
                          entry_object.get("data") or \
                          entry_object
        
        # Preserve source/label/title in the data blob if they were at the top level
        if "source_url" not in entry_data_dict:
            source = entry_object.get("source_info", {}).get("source_url") or \
                     entry_object.get("source")
            if source:
                entry_data_dict["source_url"] = source
        
        if "title" not in entry_data_dict:
            title = entry_object.get("label") or entry_object.get("title")
            if title:
                entry_data_dict["title"] = title

        entry_data = json.dumps(entry_data_dict)
        identity_manifest = json.dumps(["source_url", "entity_label"])
        
        incoming_hit_count = entry_object.get("metadata", {}).get("hit_count", 1)
        incoming_first_seen = entry_object.get("metadata", {}).get("first_seen")
        incoming_last_seen = entry_object.get("metadata", {}).get("last_seen")

        with self._get_connection() as conn:
            row = conn.execute("SELECT hit_count FROM entries WHERE vanguard_id = ?", (v_id,)).fetchone()
            if row:
                conn.execute("""
                    UPDATE entries SET
                        last_seen = CURRENT_TIMESTAMP,
                        hit_count = hit_count + 1,
                        status = 'active',
                        entry_data = ?
                    WHERE vanguard_id = ?
                """, (entry_data, v_id))
            else:
                first_seen = incoming_first_seen if incoming_first_seen else datetime.utcnow().isoformat() + "Z"
                last_seen = incoming_last_seen if incoming_last_seen else datetime.utcnow().isoformat() + "Z"
                
                conn.execute("""
                    INSERT INTO entries (vanguard_id, provider_id, identity_manifest, entry_data, first_seen, last_seen, hit_count, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
                """, (v_id, provider_id, identity_manifest, entry_data, first_seen, last_seen, incoming_hit_count))
            return True

    def query_entries(self, filter_criteria: dict = None) -> list:
        query = "SELECT * FROM entries"
        params = []
        if filter_criteria:
            clauses = [f"{k} = ?" for k in filter_criteria.keys()]
            query += " WHERE " + " AND ".join(clauses)
            params = list(filter_criteria.values())
        
        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._map_row_to_discovery(row) for row in rows]

    def archive_expired(self, ttl_days: int = 30) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE entries 
                SET status = 'expired' 
                WHERE last_seen < datetime('now', ?) AND status = 'active'
            """, (f'-{ttl_days} days',))
            return cursor.rowcount
