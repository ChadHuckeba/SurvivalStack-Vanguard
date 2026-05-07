import logging
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from vanguard.discovery.strategies.heuristics import HeuristicStrategy
import pytest

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

@pytest.mark.parametrize("url, job_title", [
    ("https://openai.com/careers", "Software Engineer"),
    ("https://jobs.lever.co/openai", "Engineer"),
    ("https://www.anthropic.com/careers", "Product"),
    ("https://boards.greenhouse.io/anthropic", "Researcher"),
    ("https://www.cloudflare.com/careers/jobs/", "Manager")
])
def test_parser(url: str, job_title: str) -> None:
    print(f"\n--- Testing: {url} ---")
    strategy = HeuristicStrategy()
    link = strategy.find_job_link(url, job_title)
    
    if link:
        print(f"Found deep link for {job_title}: {link}")
    else:
        print(f"No deep link found for {job_title}.")

if __name__ == "__main__":
    test_cases = [
        ("https://openai.com/careers", "Software Engineer"),
        ("https://jobs.lever.co/openai", "Engineer"),
        ("https://www.anthropic.com/careers", "Product"),
        ("https://boards.greenhouse.io/anthropic", "Researcher"),
        ("https://www.cloudflare.com/careers/jobs/", "Manager")
    ]
    for url, title in test_cases:
        test_parser(url, title)
