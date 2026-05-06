import logging
import sys
import os
import re

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from scout_core import core_engine
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

def backfill_career_urls() -> None:
    """
    Iterates through entries and attempts to extract career URLs using a Company-First approach.
    """
    registry = CompanyRegistry(persistence_leads=core_engine.leads, persistence_companies=core_engine.companies)
    
    # Query all entries using the new modular engine
    leads_list = core_engine.leads.list_leads()

    if not leads_list:
        logger.info("No entries require career URL backfill.")
        return

    logger.info(f"Starting Company-First backfill for {len(leads_list)} entries...")

    for lead in leads_list:
        v_id = lead.vanguard_id
        company_name = lead.content.company
        
        # Determine if we should attempt domain resolution
        target_site = lead.content.company_url or lead.source_info.source_url
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
        job_title = lead.content.title
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
            
            lead.career_info.url = final_url
            lead.career_info.method = "weighted_discovery" if final_url != career_page else result["method"]
            lead.career_info.status = "verified" if final_url != career_page else result["status"]
            lead.career_info.error = result["error"]
            
            core_engine.leads.upsert_lead(lead)
            logger.info(f"Processed {v_id[:8]} ({company_name}): -> {final_url}")
        else:
            # Mark as failed if no career page could be found
            lead.career_info.url = None
            lead.career_info.method = "heuristic"
            lead.career_info.status = "failed"
            lead.career_info.error = f"Could not locate official career page for {company_name or 'Unknown Company'}"
            
            core_engine.leads.upsert_lead(lead)
            logger.warning(f"Failed to locate career page for {v_id[:8]} ({company_name})")

if __name__ == "__main__":
    backfill_career_urls()
