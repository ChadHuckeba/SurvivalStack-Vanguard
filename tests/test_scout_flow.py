import sys
from pathlib import Path

# Add src to python path if needed
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from scout_core import core_engine  # noqa: E402
from job_search_scout import JobSearchScout  # noqa: E402

def test_scout_flow() -> None:
    print("Testing Vanguard Core and JobSearchScout...")
    
    # Initialize Scout
    scout = JobSearchScout(target_source="https://example.com/jobs")
    
    # Run Scout
    scout.run()
    
    print("\nExecution complete. Checking state...")
    
    # Check state via DAOs instead of legacy .state property
    leads = core_engine.leads.list_leads()
    print(f"Total records in state: {len(leads)}")
    
    for lead in leads:
        print(f"\n--- Entity: {lead.vanguard_id[:8]} ---")
        
        # Robust handling using Pydantic fields
        title = lead.content.title if lead.content else "Unknown"
        source = lead.source_info.source_url if lead.source_info else "Unknown"
            
        print(f"Label/Title: {title}")
        print(f"Source: {source}")

if __name__ == "__main__":
    test_scout_flow()
