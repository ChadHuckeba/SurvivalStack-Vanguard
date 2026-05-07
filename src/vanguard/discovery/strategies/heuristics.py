import logging
import re
from typing import Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from curl_cffi import requests
from ddgs import DDGS
from vanguard.models.discovery import DiscoveryResult
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
    REJECT_KEYWORDS = ["diversity", "inclusion", "benefits", "culture", "life at", "values", "belonging"]

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
                domain = str(urlparse(url).netloc).lower()
                if domain.startswith("www."):
                    domain = domain[4:]

                # Simple check: name in domain
                clean_name = re.sub(r"[^a-z0-9]", "", company_name.lower())
                clean_domain = re.sub(r"[^a-z0-9]", "", domain.split(".")[0])

                if clean_name in clean_domain or clean_domain in clean_name:
                    return domain
            return None
        except Exception:
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

                    score = path_weight
                    if any(kw in title for kw in self.PORTAL_KEYWORDS):
                        score += 0.3
                    if any(kw in title for kw in self.REJECT_KEYWORDS):
                        score -= 0.7

                    candidates.append((score, response.url))
            except Exception:
                continue

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_score, best_url = candidates[0]
            if best_score >= 0.5:
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
