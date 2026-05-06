import logging
import re
from typing import Optional
from urllib.parse import urlparse
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

logger = logging.getLogger("vanguard.domain_resolver")

class DomainResolver:
    """
    Utility to resolve a company name to its official root domain 
    using search-based heuristics.
    """

    # Domains to ignore during official site resolution
    BLOCKLIST = [
        r"linkedin\.com",
        r"glassdoor\.com",
        r"indeed\.com",
        r"ziprecruiter\.com",
        r"wikipedia\.org",
        r"facebook\.com",
        r"twitter\.com",
        r"x\.com",
        r"crunchbase\.com",
        r"bloomberg\.com",
        r"ycombinator\.com",
        r"reddit\.com",
        r"zhihu\.com",
        r"forbes\.com",
        r"reuters\.com",
        r"nytimes\.com",
        r"techcrunch\.com",
        r"businessinsider\.com",
        r"github\.com",
        r"youtube\.com",
        r"instagram\.com",
        r"pinterest\.com",
        r"medium\.com",
        r"quora\.com"
    ]

    def __init__(self):
        self.ddgs = DDGS()

    def resolve_company_domain(self, company_name: str) -> Optional[str]:
        """
        Searches for the official website of a company and returns the root domain.
        """
        if not company_name:
            return None

        # 0. Pre-check: If it looks like a domain already
        if "." in company_name and " " not in company_name:
            candidate = company_name.lower()
            if candidate.startswith("www."): candidate = candidate[4:]
            is_blocked = False
            for pattern in self.BLOCKLIST:
                if re.search(pattern, candidate):
                    is_blocked = True
                    break
            if not is_blocked:
                logger.info(f"Using direct domain candidate: {candidate}")
                return candidate

        try:
            # Query for the official site specifically
            query = f'"{company_name}" official website'
            logger.info(f"Resolving domain for: {company_name}")
            
            results = list(self.ddgs.text(query, max_results=10))
            
            if not results:
                # Try a broader query if specific one fails
                logger.debug(f"No results for specific query, trying broader: {company_name}")
                results = list(self.ddgs.text(company_name, max_results=10))

            for res in results:
                url = res.get("href")
                title = res.get("title", "").lower()
                if not url:
                    continue
                
                domain = urlparse(url).netloc.lower()
                if domain.startswith("www."):
                    domain = domain[4:]
                
                logger.debug(f"Candidate: {domain} - {title}")
                
                # Check against blocklist
                is_blocked = False
                for pattern in self.BLOCKLIST:
                    if re.search(pattern, domain):
                        is_blocked = True
                        break
                
                if is_blocked:
                    continue

                clean_name = re.sub(r"[^a-zA-Z0-9]", "", company_name).lower()
                clean_domain = re.sub(r"[^a-zA-Z0-9]", "", domain.split('.')[0])
                
                # Strong match: name is exactly the domain name or vice versa
                if clean_name == clean_domain or clean_name in clean_domain or clean_domain in clean_name:
                    logger.info(f"Resolved {company_name} -> {domain}")
                    return domain
                
                # Title match: "OpenAI: Official Site" or similar
                if clean_name in title.replace(" ", ""):
                    logger.info(f"Resolved (title match) {company_name} -> {domain}")
                    return domain
            
            # Final fallback: first non-blocked link
            for res in results:
                url = res.get("href")
                if not url: continue
                domain = urlparse(url).netloc.lower()
                if domain.startswith("www."): domain = domain[4:]
                is_blocked = False
                for pattern in self.BLOCKLIST:
                    if re.search(pattern, domain):
                        is_blocked = True
                        break
                if not is_blocked:
                    logger.info(f"Fallback resolution: {company_name} -> {domain}")
                    return domain

            logger.warning(f"Could not resolve official domain for: {company_name}")
            return None
            
        except Exception as e:
            logger.error(f"Domain resolution failed for {company_name}: {str(e)}")
            return None

    @staticmethod
    def get_base_url(domain: str) -> str:
        """Constructs a basic https URL from a domain."""
        return f"https://{domain}"
