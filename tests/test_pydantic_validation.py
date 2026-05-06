import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from scout_core import core_engine

def test_validation():
    print("\n--- Testing Lead Validation ---")
    
    # 1. Valid Payload
    valid_payload = {
        "vanguard_id": "test_id_123",
        "source_info": {
            "scout": "TestScout",
            "source_url": "https://example.com/job"
        },
        "content": {
            "title": "Software Engineer",
            "company": "TestCorp",
            "location": "Remote"
        }
    }
    
    print("Ingesting valid payload...")
    try:
        core_engine.upsert_record(valid_payload)
        print("SUCCESS: Valid payload ingested.")
    except Exception as e:
        print(f"FAILURE: Valid payload rejected: {e}")

    # 2. Invalid Payload (Missing company)
    invalid_payload = {
        "vanguard_id": "test_id_456",
        "source_info": {
            "scout": "TestScout",
            "source_url": "https://example.com/job"
        },
        "content": {
            "title": "Software Engineer"
            # Missing company
        }
    }
    
    print("\nIngesting invalid payload (missing company)...")
    try:
        core_engine.upsert_record(invalid_payload)
        print("FAILURE: Invalid payload accepted.")
    except ValueError as e:
        print(f"SUCCESS: Invalid payload rejected as expected: {e}")

if __name__ == "__main__":
    test_validation()
