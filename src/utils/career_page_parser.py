import logging
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from curl_cffi import requests

# Configure logging
logger = logging.getLogger("vanguard.career_page_parser")

class CareerPageParser:
    """
    Lightweight, heuristic-based parser to extract job posting URLs 
    directly from company career pages.
    """

    ATS_SIGNATURES = {
        "greenhouse": r"(boards|job-boards)\.greenhouse\.io",
        "lever": r"jobs\.lever\.co",
        "workday": r"\.myworkdayjobs\.com",
        "ashby": r"jobs\.ashbyhq\.com",
        "bamboohr": r"\.bamboohr\.com/careers",
        "smartrecruiters": r"smartrecruiters\.com"
    }

    # Common URL patterns for job postings (heuristic fallback)
    HEURISTIC_PATTERNS = [
        r"/jobs/\d+",           # /jobs/12345
        r"/jobs/[a-z0-9-]+",    # /jobs/software-engineer
        r"/careers/\d+",        # /careers/12345
        r"/careers/[a-z0-9-]+", # /careers/software-engineer
        r"/posting/[a-z0-9-]+", # /posting/xyz
        r"/openings/[a-z0-9-]+", # /openings/xyz
        r"/apply/[a-z0-9-]+",   # /apply/xyz
    ]

    def __init__(self, target_url: str):
        """
        Initialize the parser with the company's career page URL.
        """
        self.target_url = target_url
        self.base_domain = urlparse(target_url).netloc
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }

    def fetch_html(self) -> Optional[str]:
        """
        Fetches the raw HTML of the career page using curl_cffi to bypass basic anti-bot.
        """
        try:
            logger.info(f"Fetching career page: {self.target_url}")
            response = requests.get(
                self.target_url, 
                headers=self.headers, 
                impersonate="chrome", 
                timeout=15
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {self.target_url}: {str(e)}")
            return None

    def extract_job_urls(self) -> List[str]:
        """
        Orchestrates the extraction process: ATS detection followed by heuristic fallback.
        """
        html = self.fetch_html()
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        
        discovered_urls = set()

        # Phase A: ATS Signature Detection
        for link in links:
            href = link["href"]
            for ats, signature in self.ATS_SIGNATURES.items():
                if re.search(signature, href):
                    abs_url = self._sanitize_url(href)
                    if abs_url:
                        discovered_urls.add(abs_url)
                        logger.debug(f"Detected ATS ({ats}) link: {abs_url}")

        # Phase B: Heuristic Fallback (if few ATS links found or for mixed sites)
        if len(discovered_urls) < 5:
            for link in links:
                href = link["href"]
                for pattern in self.HEURISTIC_PATTERNS:
                    if re.search(pattern, href, re.IGNORECASE):
                        abs_url = self._sanitize_url(href)
                        if abs_url:
                            discovered_urls.add(abs_url)
                            logger.debug(f"Heuristic match: {abs_url}")

        return sorted(list(discovered_urls))

    def _sanitize_url(self, href: str) -> Optional[str]:
        """
        Converts relative URLs to absolute and strips tracking parameters.
        """
        try:
            # 1. Resolve relative URLs
            full_url = urljoin(self.target_url, href)
            
            # 2. Parse and remove fragments/query params (sanitization)
            parsed = urlparse(full_url)
            sanitized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            # 3. Basic validation: must be http(s)
            if parsed.scheme not in ["http", "https"]:
                return None
                
            return sanitized.rstrip("/")
        except Exception:
            return None
