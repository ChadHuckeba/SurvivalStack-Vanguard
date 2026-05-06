import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from vanguard.persistence.engine import SQLiteEngine
from vanguard.persistence.companies_dao import CompaniesDAO
from utils.company_registry import CompanyRegistry

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_registry():
    db_path = Path("/home/chadh/survivalstack/Vanguard/data/vanguard.db")
    engine = SQLiteEngine(db_path)
    companies_dao = CompaniesDAO(engine)
    registry = CompanyRegistry(persistence_companies=companies_dao)

    companies = ["Veeva Systems", "OpenAI", "Anthropic", "Cloudflare"]    
    print("\n--- Phase 1: Initial Discovery (Force Refresh) ---")
    for company in companies:
        info = registry.resolve_company(company, force_refresh=True)
        print(f"Result for {company}: {info}")
        
    print("\n--- Phase 2: Cached Retrieval (Cache Hit) ---")
    for company in companies:
        info = registry.resolve_company(company)
        print(f"Result for {company}: {info}")

if __name__ == "__main__":
    test_registry()
