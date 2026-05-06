import logging
import sys
import os
import sqlite3
import json
import re
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from persistence_interface import SQLitePersistence
from utils.career_page_parser import CareerPageParser
from utils.company_registry import CompanyRegistry

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("vanguard.migration")

# Known aggregators that we should not crawl directly
AGGREGATORS = [
    r"glassdoor\.com",
    r"linkedin\.com",
    r"indeed\.com",
    r"ziprecruiter\.com"
]

def backfill_career_urls():
    """
    Iterates through entries and attempts to extract career URLs using a Company-First approach.
    """
    db_path = Path("/home/chadh/survivalstack/Vanguard/data/vanguard.db")
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return

    persistence = SQLitePersistence(db_path)
    registry = CompanyRegistry(persistence)
    
    # Query entries that need extraction or might have stale URLs
    with persistence._get_connection() as conn:
        rows = conn.execute("""
            SELECT vanguard_id, entry_data, provider_id, career_extraction_status
            FROM entries 
        """).fetchall()

    if not rows:
        logger.info("No entries require career URL backfill.")
        return

    logger.info(f"Starting Company-First backfill for {len(rows)} entries...")

    for row in rows:
        v_id = row["vanguard_id"]
        data = json.loads(row["entry_data"])
        company_name = data.get("company")
        
        # Determine if we should attempt domain resolution
        target_site = data.get("company_url") or data.get("source_url")
        is_aggregator = False
        if target_site:
            for pattern in AGGREGATORS:
                if re.search(pattern, target_site):
                    is_aggregator = True
                    break

        career_page = None
        
        # 1. Domain & Career Resolution via Registry
        if not target_site or is_aggregator:
            if company_name:
                company_info = registry.resolve_company(company_name)
                career_page = company_info.get("career_url")
            else:
                logger.debug(f"Skipping domain resolution for {v_id[:8]} (no company name)")
        else:
            # If we have a direct site, use it (could be a career page or home page)
            if any(p in target_site.lower() for p in ["/careers", "/jobs", "/openings"]):
                career_page = target_site
            else:
                career_page = CareerPageParser.discover_career_page(target_site)

        # 2. Deep Link Discovery (Job Specific)
        job_title = data.get("title") or data.get("label")
        final_url = career_page
        
        if career_page and job_title:
            parser = CareerPageParser(career_page)
            deep_link = parser.find_deep_link(job_title)
            if deep_link:
                final_url = deep_link
                logger.info(f"Deep link discovered for {v_id[:8]}: {final_url}")

        # 3. Persistence Update
        if career_page:
            # Re-parse for metadata (ATS detection)
            temp_parser = CareerPageParser(career_page)
            result = temp_parser.extract_job_urls()
            
            persistence.upsert_entry({
                "vanguard_id": v_id,
                "career_info": {
                    "url": final_url,
                    "method": "weighted_discovery" if final_url != career_page else result["method"],
                    "status": "verified" if final_url != career_page else result["status"],
                    "error": result["error"]
                }
            })
            logger.info(f"Processed {v_id[:8]} ({company_name}): -> {final_url}")
        else:
            # Mark as failed if no career page could be found
            persistence.upsert_entry({
                "vanguard_id": v_id,
                "career_info": {
                    "url": None,
                    "method": "heuristic",
                    "status": "failed",
                    "error": f"Could not locate official career page for {company_name or 'Unknown Company'}"
                }
            })
            logger.warning(f"Failed to locate career page for {v_id[:8]} ({company_name})")

if __name__ == "__main__":
    backfill_career_urls()
