import logging
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.domain_resolver import DomainResolver
from utils.career_page_parser import CareerPageParser

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
def test_resolution(company_name: str):
    print(f"\n--- Testing Resolution for: {company_name} ---")
    resolver = DomainResolver()
    domain = resolver.resolve_company_domain(company_name)
    
    if domain:
        print(f"Success: {domain}")
        base_url = resolver.get_base_url(domain)
        career_page = CareerPageParser.discover_career_page(base_url)
        if career_page:
            print(f"Career Page Discovered: {career_page}")
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
