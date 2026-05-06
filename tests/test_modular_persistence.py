import sys
import os
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from scout_core import core_engine

def test_modular_persistence():
    print("\n--- Testing Modular Persistence ---")
    
    # 1. Upsert a lead
    payload = {
        "vanguard_id": "modular_test_001",
        "source_info": {
            "scout": "ModularScout",
            "source_url": "https://modular.test/job"
        },
        "content": {
            "title": "Modular Engineer",
            "company": "ModuCorp",
            "location": "Remote"
        }
    }
    
    print("Upserting lead...")
    core_engine.upsert_record(payload)
    
    # 2. Retrieve the lead
    print("Retrieving lead...")
    lead = core_engine.leads.get_lead("modular_test_001")
    
    if lead and lead.content.company == "ModuCorp":
        print(f"SUCCESS: Retrieved lead for {lead.content.company}")
        print(f"Lead status: {lead.status}")
    else:
        print("FAILURE: Could not retrieve lead or data mismatch.")

    # 3. Test Company Registry
    from vanguard.models.company import Company
    print("\nTesting Company Registry...")
    company = Company(company_name="ModuCorp", root_domain="modu.corp", career_url="https://modu.corp/jobs")
    core_engine.companies.upsert_company(company)
    
    retrieved_company = core_engine.companies.get_company("ModuCorp")
    if retrieved_company and retrieved_company.root_domain == "modu.corp":
        print(f"SUCCESS: Retrieved company {retrieved_company.company_name}")
    else:
        print("FAILURE: Could not retrieve company metadata.")

if __name__ == "__main__":
    # Ensure logs are visible
    logging.getLogger().setLevel(logging.INFO)
    test_modular_persistence()
