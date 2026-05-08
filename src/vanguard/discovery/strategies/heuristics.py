import logging
import re
from typing import Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from curl_cffi import requests
from ddgs import DDGS
from vanguard.models.discovery import DiscoveryResult, is_blocked_entity
from ..base_strategy import BaseDiscoveryStrategy

logger = logging.getLogger("vanguard.discovery.heuristics")


class HeuristicStrategy(BaseDiscoveryStrategy):
    """
    Standard search and path-probing discovery strategy.
    """

    CAREER_PATHS = {
        "/jobs": 1.0,
        "/careers": 0.9,
        "/openings": 0.8,
        "/about/careers": 0.6,
        "/company/careers": 0.6,
        "/join-us": 0.5,
        "/work-with-us": 0.5,
    }

    PORTAL_KEYWORDS = ["jobs", "openings", "opportunities", "positions", "portal", "search"]

    # Aggressive rejection for corporate/informational pages that are NOT job boards
    REJECT_KEYWORDS = [
        "diversity",
        "inclusion",
        "benefits",
        "culture",
        "life at",
        "values",
        "belonging",
        "contact",
        "support",
        "privacy",
        "terms",
        "about-us",
        "press",
        "investors",
        "mission",
    ]

    def __init__(self) -> None:
        self.ddgs = DDGS()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }

    @property
    def name(self) -> str:
        return "heuristic"

    def resolve_domain(self, company_name: str) -> Optional[str]:
        """Resolves a company name to a root domain."""
        try:
            query = f'"{company_name}" official website'
            results = list(self.ddgs.text(query, max_results=10))

            for res in results:
                url = res.get("href")
                if not url:
                    continue

                domain_parts = urlparse(url).netloc.lower().split(".")
                domain = ".".join(domain_parts[-2:]) if len(domain_parts) >= 2 else domain_parts[0]

                # Check Centralized Blocklist
                if is_blocked_entity(url):
                    logger.warning(f"Skipping blocked aggregator domain: {domain}")
                    continue

                full_domain = str(urlparse(url).netloc).lower()
                clean_domain = full_domain[4:] if full_domain.startswith("www.") else full_domain

                # Simple check: name in domain
                clean_name = re.sub(r"[^a-z0-9]", "", company_name.lower())
                name_in_domain = re.sub(r"[^a-z0-9]", "", clean_domain.split(".")[0])

                if clean_name in name_in_domain or name_in_domain in clean_name:
                    return clean_domain
            return None
        except Exception as e:
            logger.error(f"Domain resolution failed for {company_name}: {e}")
            return None

    def discover_portal(self, company_name: str, base_domain: Optional[str] = None) -> Optional[DiscoveryResult]:
        domain = base_domain or self.resolve_domain(company_name)
        if not domain:
            return None

        base_url = f"https://{domain}"
        candidates = []

        for path, path_weight in self.CAREER_PATHS.items():
            candidate_url = urljoin(base_url, path)
            try:
                response = requests.get(candidate_url, headers=self.headers, impersonate="chrome", timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    title = str(soup.title.string).lower() if (soup.title and soup.title.string) else ""
                    body_text = soup.get_text().lower()[:2000]  # Check first 2k chars

                    score = path_weight
                    if any(kw in title for kw in self.PORTAL_KEYWORDS):
                        score += 0.3

                    # Penalty for non-career keywords (Increased weight)
                    if any(kw in title for kw in self.REJECT_KEYWORDS):
                        score -= 1.2

                    # Reward for finding 'search' or 'apply' in body
                    if "apply now" in body_text or "search jobs" in body_text:
                        score += 0.2

                    candidates.append((score, response.url))
            except Exception:
                continue

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_score, best_url = candidates[0]
            if best_score >= 0.6:  # Increased threshold for verification
                return DiscoveryResult(
                    portal_url=str(best_url),
                    status="verified" if best_score >= 1.0 else "ambiguous",
                    method=self.name,
                    confidence_score=float(best_score),
                )
        return None

    def find_job_link(self, portal_url: str, job_title: str) -> Optional[str]:
        try:
            response = requests.get(portal_url, headers=self.headers, impersonate="chrome", timeout=5)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)

            clean_title = re.sub(r"[^a-z0-9]", "", job_title.lower())
            for link in links:
                text = link.get_text(strip=True).lower()
                if clean_title in re.sub(r"[^a-z0-9]", "", text):
                    href = link["href"]
                    return urljoin(portal_url, str(href))
            return None
        except Exception:
            return None
