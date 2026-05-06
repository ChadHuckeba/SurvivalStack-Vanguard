import sys
from pathlib import Path

# Add src to python path if needed
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from scout_core import core_engine  # noqa: E402
from job_search_scout import JobSearchScout  # noqa: E402

def main():
    print("Testing Vanguard Core and JobSearchScout...")
    
    # Initialize Scout
    scout = JobSearchScout(target_source="https://example.com/jobs")
    
    # Run Scout
    scout.run()
    
    print("\nExecution complete. Checking state...")
    
    # Check state
    state = core_engine.state
    print(f"Total records in state: {state['state_metadata']['total_records']}")
    
    for v_id, entity in state['entities'].items():
        print(f"\n--- Entity: {v_id[:8]} ---")
        
        # Robust handling of different schemas
        if "content" in entity:
            title = entity["content"].get("title", "Unknown")
            source = entity["source_info"].get("source_url", "Unknown")
        else:
            title = entity.get("label", "Unknown")
            source = entity.get("source", "Unknown")
            
        print(f"Label/Title: {title}")
        print(f"Source: {source}")
        print(f"Hit Count: {entity['metadata'].get('hit_count', 0)}")

if __name__ == "__main__":
    main()
