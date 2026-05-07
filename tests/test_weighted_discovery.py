import logging
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from vanguard.discovery.strategies.heuristics import HeuristicStrategy
import pytest

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

@pytest.mark.parametrize("company_name, job_title", [
    ("Veeva Systems", "Operations Manager"),
    ("OpenAI", "Software Engineer"),
    ("Anthropic", "Product Manager"),
    ("Cloudflare", "Systems Engineer")
])
def test_discovery(company_name: str, job_title: str) -> None:
    print(f"\n--- Testing Discovery for: {company_name} ---")
    strategy = HeuristicStrategy()
    discovered = strategy.discover_portal(company_name)
    if discovered:
        print(f"SUCCESS (Portal): {discovered.portal_url}")
        if job_title:
            print(f"Searching for deep link: '{job_title}'")
            deep_link = strategy.find_job_link(discovered.portal_url, job_title)
            if deep_link:
                print(f"SUCCESS (Deep Link): {deep_link}")
            else:
                print("FAILED to find deep link.")
    else:
        print("FAILED to discover career page.")

if __name__ == "__main__":
    test_cases = [
        ("Veeva Systems", "Operations Manager"),
        ("OpenAI", "Software Engineer"),
        ("Anthropic", "Product Manager"),
        ("Cloudflare", "Systems Engineer")
    ]
    for name, title in test_cases:
        test_discovery(name, title)
