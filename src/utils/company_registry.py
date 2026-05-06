import logging
import re
from typing import Optional
from .domain_resolver import DomainResolver
from .career_page_parser import CareerPageParser

logger = logging.getLogger("vanguard.company_registry")

class CompanyRegistry:
    """
    Orchestrates company resolution and persistence.
    Caches results in the 'companies' table to prevent redundant searches.
    """

    def __init__(self, persistence):
        self.persistence = persistence
        self.resolver = DomainResolver()

    def resolve_company(self, company_name: str, force_refresh: bool = False) -> dict:
        """
        Returns verified company metadata, using the cache if available.
        """
        if not company_name:
            return {}

        # 1. Check Registry Cache
        if not force_refresh:
            cached = self.persistence.get_company(company_name)
            if cached and (cached.get("career_url") or cached.get("root_domain")):
                logger.info(f"Registry Hit: {company_name} -> {cached.get('root_domain')}")
                return cached

        # 2. Resolve Domain
        domain = self.resolver.resolve_company_domain(company_name)
        if not domain:
            logger.warning(f"Domain resolution failed for: {company_name}")
            return {}

        base_url = self.resolver.get_base_url(domain)

        # 3. Discover Career Page
        career_url = CareerPageParser.discover_career_page(base_url)
        
        # 4. Optional: Detect ATS (could be expanded)
        ats_provider = None
        if career_url:
            for ats, signature in CareerPageParser.ATS_SIGNATURES.items():
                if re.search(signature, career_url):
                    ats_provider = ats
                    break

        # 5. Persist to Registry
        company_data = {
            "company_name": company_name,
            "root_domain": domain,
            "career_url": career_url,
            "ats_provider": ats_provider
        }
        
        self.persistence.upsert_company(company_data)
        logger.info(f"Registry Update: {company_name} resolved and cached.")
        
        return company_data
