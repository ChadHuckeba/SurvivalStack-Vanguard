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

    # Common career page paths with weights
    CAREER_PATHS = {
        "/jobs": 1.0,
        "/careers": 0.9,
        "/openings": 0.8,
        "/about/careers": 0.6,
        "/company/careers": 0.6,
        "/join-us": 0.5,
        "/work-with-us": 0.5
    }

    # Keywords that suggest a page is a true job portal
    PORTAL_KEYWORDS = ["jobs", "openings", "opportunities", "positions", "portal", "search"]
    
    # Keywords that suggest a page is NOT a job portal (cultural/diversity)
    REJECT_KEYWORDS = ["diversity", "inclusion", "benefits", "culture", "life at", "values", "belonging"]

    def __init__(self, target_url: str):
        """
        Initialize the parser with the company's career page URL or base domain.
        """
        self.target_url = target_url
        self.base_domain = urlparse(target_url).netloc
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }

    @classmethod
    def discover_career_page(cls, base_url: str) -> Optional[str]:
        """
        Attempts to guess and validate a career page URL from a base company URL
        using a weighted scoring heuristic.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        
        candidates = []

        # 1. Probe all common paths
        for path, path_weight in cls.CAREER_PATHS.items():
            candidate_url = urljoin(base_url, path)
            try:
                logger.debug(f"Probing career candidate: {candidate_url}")
                
                # Use GET because we need to inspect the HTML <title>
                response = requests.get(
                    candidate_url, 
                    headers=headers, 
                    impersonate="chrome", 
                    timeout=5,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    final_url = response.url
                    soup = BeautifulSoup(response.text, "html.parser")
                    title = soup.title.string.lower() if soup.title else ""
                    
                    score = path_weight
                    
                    # Title-based scoring adjustments
                    if any(kw in title for kw in cls.PORTAL_KEYWORDS):
                        score += 0.3
                        logger.debug(f"Found portal keywords in {candidate_url}")
                    
                    if any(kw in title for kw in cls.REJECT_KEYWORDS):
                        score -= 0.7
                        logger.debug(f"Found reject keywords in {candidate_url}")

                    # Check for ATS redirection in final URL
                    for ats, signature in cls.ATS_SIGNATURES.items():
                        if re.search(signature, final_url):
                            score += 0.5
                            logger.info(f"Detected ATS ({ats}) portal at {final_url}")
                            break

                    logger.debug(f"Candidate {candidate_url} scored: {score:.2f}")
                    candidates.append((score, final_url))
                    
            except Exception as e:
                logger.debug(f"Probe failed for {candidate_url}: {str(e)}")
                continue
        
        # 2. Return the highest scoring candidate above a threshold
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_score, best_url = candidates[0]
            
            if best_score >= 0.5:
                logger.info(f"Discovered best career page: {best_url} (Score: {best_score:.2f})")
                return best_url
        
        return None

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

    def find_deep_link(self, job_title: str) -> Optional[str]:
        """
        Attempts to find a direct link to a specific job posting on the career page.
        """
        html = self.fetch_html()
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        
        candidates = []
        clean_title = re.sub(r"[^a-z0-9]", "", job_title.lower())

        for link in links:
            href = link["href"]
            link_text = link.get_text(strip=True).lower()
            clean_link_text = re.sub(r"[^a-z0-9]", "", link_text)
            
            abs_url = self._sanitize_url(href)
            if not abs_url:
                continue

            # Check if it looks like a job posting URL
            is_job_link = False
            for pattern in self.HEURISTIC_PATTERNS:
                if re.search(pattern, abs_url, re.IGNORECASE):
                    is_job_link = True
                    break
            
            for signature in self.ATS_SIGNATURES.values():
                if re.search(signature, abs_url):
                    is_job_link = True
                    break
            
            if not is_job_link:
                continue

            # Calculate match score
            score = 0
            if clean_link_text and (clean_title in clean_link_text or clean_link_text in clean_title):
                score += 0.8
                logger.debug(f"Title match found: '{link_text}' score: {score}")
            
            # Penalize very short text (e.g., "apply")
            if len(link_text) < 5:
                score -= 0.2

            if score > 0:
                candidates.append((score, abs_url))

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_score, best_url = candidates[0]
            logger.info(f"Discovered deep link: {best_url} (Score: {best_score:.2f})")
            return best_url

        return None

    def extract_job_urls(self) -> Dict:
        """
        Orchestrates the extraction process: ATS detection followed by heuristic fallback.
        Returns a dictionary with status and metadata.
        """
        html = self.fetch_html()
        if not html:
            return {
                "urls": [],
                "status": "failed",
                "method": None,
                "error": "Failed to fetch HTML or empty response"
            }

        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        
        discovered_urls = set()
        method = None

        # Phase A: ATS Signature Detection
        for link in links:
            href = link["href"]
            for ats, signature in self.ATS_SIGNATURES.items():
                if re.search(signature, href):
                    abs_url = self._sanitize_url(href)
                    if abs_url:
                        discovered_urls.add(abs_url)
                        method = "ats_signature"
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
                            if not method:
                                method = "heuristic"
                            logger.debug(f"Heuristic match: {abs_url}")

        status = "verified" if len(discovered_urls) == 1 else "ambiguous" if len(discovered_urls) > 1 else "failed"
        error = None
        if status == "failed":
            error = "No URLs matched ATS signatures or heuristic patterns"
        elif status == "ambiguous":
            error = f"Found {len(discovered_urls)} potential job URLs"

        return {
            "urls": sorted(list(discovered_urls)),
            "status": status,
            "method": method,
            "error": error
        }

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
