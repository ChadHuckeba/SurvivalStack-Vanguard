import logging
from typing import Optional
from vanguard.persistence.companies_dao import CompaniesDAO
from vanguard.models.company import Company
from vanguard.models.discovery import is_blocked_entity
from .strategies.heuristics import HeuristicStrategy

logger = logging.getLogger("vanguard.discovery.orchestrator")


class DiscoveryOrchestrator:
    """
    The entry point for all discovery tasks.
    Coordinates multiple strategies and manages registry caching.
    """

    def __init__(self, companies_dao: CompaniesDAO):
        self.companies = companies_dao
        # Strategy list in order of precedence
        self.strategies = [HeuristicStrategy()]

    def resolve_company_portal(self, company_name: str, force_refresh: bool = False) -> Optional[Company]:
        """
        Ensures a company has a verified portal URL in the registry.
        Implements Audit-on-Access to purge contaminated cache entries.
        """
        if not force_refresh:
            cached = self.companies.get_company(company_name)
            if cached:
                # Continuous Validation: check if cached identity or URL is now blocked
                if is_blocked_entity(cached.company_name) or is_blocked_entity(cached.career_url) or is_blocked_entity(cached.root_domain):
                    logger.warning(f"Purging contaminated registry entry for {company_name}: {cached.career_url}")
                    # Force re-discovery by falling through
                    pass
                elif cached.career_url:
                    return cached

        # Try strategies
        for strategy in self.strategies:
            logger.info(f"Attempting discovery for '{company_name}' using strategy: {strategy.name}")
            result = strategy.discover_portal(company_name)

            if result and result.portal_url:
                try:
                    company_obj = Company(
                        company_name=company_name,
                        career_url=result.portal_url,
                        ats_provider=result.method if result.method != "heuristic" else None,
                    )
                    self.companies.upsert_company(company_obj)
                    return company_obj
                except ValueError as e:
                    logger.error(f"Discovery resulted in blocked entity for {company_name}: {e}")
                    continue

        return None

    def find_deep_link(self, portal_url: str, job_title: str) -> Optional[str]:
        """
        Finds a direct job link using the best available strategy.
        """
        for strategy in self.strategies:
            link = strategy.find_job_link(portal_url, job_title)
            if link:
                return link
        return None
