import logging
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from vanguard.persistence.engine import SQLiteEngine
from vanguard.persistence.companies_dao import CompaniesDAO
from vanguard.persistence.migration_manager import MigrationManager
from vanguard.discovery.orchestrator import DiscoveryOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_registry() -> None:
    db_path = Path(__file__).parent.parent / "data" / "test_registry.db"
    db_path.parent.mkdir(exist_ok=True)
    if db_path.exists():
        db_path.unlink()
        
    engine = SQLiteEngine(db_path)
    migrations_dir = Path(__file__).parent.parent / "src" / "vanguard" / "persistence" / "migrations"
    MigrationManager(engine, migrations_dir).apply_all()
    
    companies_dao = CompaniesDAO(engine)
    orchestrator = DiscoveryOrchestrator(companies_dao=companies_dao)

    companies = ["Veeva Systems", "OpenAI", "Anthropic", "Cloudflare"]    
    print("\n--- Phase 1: Initial Discovery (Force Refresh) ---")
    for company in companies:
        info = orchestrator.resolve_company_portal(company, force_refresh=True)
        print(f"Result for {company}: {info.career_url if info else 'None'}")
        
    print("\n--- Phase 2: Cached Retrieval (Cache Hit) ---")
    for company in companies:
        info = orchestrator.resolve_company_portal(company)
        print(f"Result for {company}: {info.career_url if info else 'None'}")

if __name__ == "__main__":
    test_registry()
