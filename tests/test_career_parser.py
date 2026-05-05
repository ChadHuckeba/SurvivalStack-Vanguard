import logging
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.career_page_parser import CareerPageParser

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_parser(url: str):
    print(f"\n--- Testing: {url} ---")
    parser = CareerPageParser(url)
    urls = parser.extract_job_urls()
    
    if urls:
        print(f"Found {len(urls)} job URLs:")
        for u in urls[:10]:  # Show first 10
            print(f"  - {u}")
        if len(urls) > 10:
            print(f"  ... and {len(urls) - 10} more.")
    else:
        print("No job URLs found.")

if __name__ == "__main__":
    # Test cases representing different ATS and page structures
    test_urls = [
        "https://openai.com/careers",           # Landing page
        "https://jobs.lever.co/openai",         # Direct Lever Board
        "https://www.anthropic.com/careers",    # Landing page
        "https://boards.greenhouse.io/anthropic", # Direct Greenhouse Board
        "https://www.cloudflare.com/careers/jobs/" # Hybrid page
    ]
    
    for url in test_urls:
        test_parser(url)
