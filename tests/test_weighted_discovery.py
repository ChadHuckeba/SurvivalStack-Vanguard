import logging
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.career_page_parser import CareerPageParser

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

def test_discovery(base_url: str, job_title: str = None):
    print(f"\n--- Testing Discovery for: {base_url} ---")
    discovered = CareerPageParser.discover_career_page(base_url)
    if discovered:
        print(f"SUCCESS (Portal): {discovered}")
        if job_title:
            print(f"Searching for deep link: '{job_title}'")
            parser = CareerPageParser(discovered)
            deep_link = parser.find_deep_link(job_title)
            if deep_link:
                print(f"SUCCESS (Deep Link): {deep_link}")
            else:
                print("FAILED to find deep link.")
    else:
        print("FAILED to discover career page.")

if __name__ == "__main__":
    test_cases = [
        ("https://veeva.com", "Operations Manager"),
        ("https://openai.com", "Software Engineer"),
        ("https://anthropic.com", "Product Manager"),
        ("https://cloudflare.com", "Systems Engineer")
    ]
    for url, title in test_cases:
        test_discovery(url, title)
