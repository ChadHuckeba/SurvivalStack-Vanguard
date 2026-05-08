import sys
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from vanguard.scouts.jobspy import JobSpyScout
from vanguard.core import core_engine

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def run_research():
    """
    Executes the primary lead discovery and research cycle.
    """
    print("\n--- VANGUARD: RESEARCH CYCLE ---")
    try:
        # Initialize the JobSpy specialized scout
        scout = JobSpyScout()

        # Run the discovery pass
        scout.run()

        # Report results
        leads = core_engine.leads.list_leads()
        print(f"\nDiscovery complete. Current database state: {len(leads)} leads.")

        # Show new/recent leads (Relocation prioritized)
        print("\n--- PRIORITY LEADS (Top 5 Relo Priority) ---")
        sorted_leads = sorted(leads, key=lambda x: x.content.vanguard_relo_probability, reverse=True)
        for lead in sorted_leads[:5]:
            title = lead.content.title
            company = lead.content.company
            location = lead.content.location or "Unknown"
            relo = getattr(lead.content, "vanguard_relo_probability", 0.0)
            print(f"- {title} @ {company} [{location}] (Relo Prob: {relo})")

    except Exception as e:
        logging.error(f"Research run failed: {str(e)}")


if __name__ == "__main__":
    run_research()
