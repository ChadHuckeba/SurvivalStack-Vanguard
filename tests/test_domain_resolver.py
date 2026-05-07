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

@pytest.mark.parametrize("company_name", [
    "OpenAI",
    "Anthropic",
    "Cloudflare",
    "Visa",
    "Apollo.io"
])
def test_resolution(company_name: str) -> None:
    print(f"\n--- Testing Resolution for: {company_name} ---")
    strategy = HeuristicStrategy()
    domain = strategy.resolve_domain(company_name)
    
    if domain:
        print(f"Success: {domain}")
        career_page_result = strategy.discover_portal(company_name, base_domain=domain)
        if career_page_result:
            print(f"Career Page Discovered: {career_page_result.portal_url}")
        else:
            print("Failed to discover career page.")
    else:
        print("Failed to resolve domain.")

if __name__ == "__main__":
    companies = [
        "OpenAI",
        "Anthropic",
        "Cloudflare",
        "Visa",
        "Apollo.io"
    ]
    
    for company in companies:
        test_resolution(company)
