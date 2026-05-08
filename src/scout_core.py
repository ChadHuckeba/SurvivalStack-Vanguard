from typing import Any, Dict, Union
import hashlib
import logging
import sys
from pathlib import Path
from urllib.parse import urlparse
from vanguard.models.lead import Lead
from vanguard.persistence.engine import SQLiteEngine
from vanguard.persistence.leads_dao import LeadsDAO
from vanguard.persistence.companies_dao import CompaniesDAO
from vanguard.persistence.migration_manager import MigrationManager


class ScoutCore:
    """
    The central orchestration engine for the Vanguard platform.

    A domain-agnostic singleton that manages state persistence,
    entity deduplication, and data integrity for all specialized scouts.
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args: Any, **kwargs: Any) -> "ScoutCore":
        if cls._instance is None:
            cls._instance = super(ScoutCore, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._initialize_core()
            self.__class__._initialized = True

    def _initialize_core(self) -> None:
        """
        Initialize the system environment and load the persistent state.
        Ensures the local infrastructure exists for agnostic data storage.
        """
        self.root_dir = Path(__file__).parent.parent
        self.data_dir = self.root_dir / "data"
        self.db_path = self.data_dir / "vanguard.db"
        self.log_path = self.root_dir / "logs" / "system.log"
        self.migrations_dir = self.root_dir / "src" / "vanguard" / "persistence" / "migrations"

        # Add src to path for relative imports
        src_path = str(self.root_dir / "src")
        if src_path not in sys.path:
            sys.path.append(src_path)

        self.data_dir.mkdir(exist_ok=True)
        (self.root_dir / "logs").mkdir(exist_ok=True)

        # Configure Logging (File + Stream)
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # Reset any existing handlers
        root_logger = logging.getLogger()
        if root_logger.hasHandlers():
            root_logger.handlers.clear()
            
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(self.log_path),
                logging.StreamHandler(sys.stdout)
            ]
        )

        # Initialize Persistence Engine
        self.engine = SQLiteEngine(self.db_path)

        # Apply Migrations
        self.migration_manager = MigrationManager(self.engine, self.migrations_dir)
        self.migration_manager.apply_all()

        # Initialize DAOs
        self.leads = LeadsDAO(self.engine)
        self.companies = CompaniesDAO(self.engine)

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

    def upsert_record(self, record_data: Union[Dict[str, Any], Lead]) -> None:
        """
        Ingest an entity record or update an existing entry.
        Validated against the Pydantic Lead model at the boundary.
        """
        try:
            # 1. Validation at the Boundary
            if isinstance(record_data, Lead):
                lead = record_data
            else:
                # Pre-flight check for minimal required fields
                if not record_data.get("title") or not record_data.get("company"):
                    raise ValueError("Payload missing required 'title' or 'company' fields.")
                
                lead = Lead(**record_data)

            # 2. Handoff to persistence (using validated model)
            self.leads.upsert_lead(lead)

        except Exception as e:
            logging.error(f"Ingestion failed for lead: {str(e)}")
            raise ValueError(f"Payload validation failed: {str(e)}")


core_engine = ScoutCore()
