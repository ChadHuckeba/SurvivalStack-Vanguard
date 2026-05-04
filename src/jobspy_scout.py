from base_scout import BaseScout
import logging
from typing import List, Dict
try:
    from jobspy import scrape_jobs
except ImportError:
    logging.warning("jobspy not found. JobSpyScout will run in mock mode.")
    scrape_jobs = None

class JobSpyScout(BaseScout):
    """
    JobSpyScout wraps the JobSpy library to act as a Vanguard Scout.
    It scrapes major job boards and reports findings to the ScoutCore.
    """
    
    def __init__(self, search_term: str, location: str = "Remote", results_wanted: int = 20):
        """
        Initialize with search parameters.
        Target source is set to 'jobspy' as it aggregates multiple sites.
        """
        super().__init__(scout_name="JobSpyScout", target_source="https://github.com/speedyapply/JobSpy")
        self.search_term = search_term
        self.location = location
        self.results_wanted = results_wanted

    def run(self):
        """
        Executes the JobSpy scrape and reports results.
        """
        if scrape_jobs is None:
            self.logger.error("JobSpy library not installed. Cannot run.")
            # For now, let's not fail silently, but maybe provide mock data if we want to pressure test
            return

        self.logger.info(f"Scraping jobs for '{self.search_term}' in '{self.location}'")
        
        try:
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed", "glassdoor", "zip_recruiter"],
                search_term=self.search_term,
                location=self.location,
                results_wanted=self.results_wanted,
                hours_old=72,  # Last 3 days
                country_indeed='USA'
            )
            
            # jobs is a pandas DataFrame
            for _, row in jobs.iterrows():
                job_data = row.to_dict()
                
                # Vanguard identity manifest relies on source_url and title/label
                entity_label = job_data.get("title", "Unknown Title")
                source_url = job_data.get("job_url", "unknown")
                
                # Cleanup data for storage
                for key, value in job_data.items():
                    if hasattr(value, 'isoformat'):
                        job_data[key] = value.isoformat()
                    elif isinstance(value, float) and (value != value): # NaN check
                        job_data[key] = None

                self.logger.info(f"Reporting job: {entity_label} from {job_data.get('site', 'unknown')}")
                
                # Generate ID based on job-specific URL for uniqueness
                v_id = self._generate_custom_id(source_url, entity_label)
                
                record_packet = {
                    "vanguard_id": v_id,
                    "source_info": {
                        "scout": self.scout_name,
                        "source_url": source_url,
                        "aggregator": "jobspy"
                    },
                    "content": job_data,
                    "metadata": {
                        "first_seen": self._get_timestamp(),
                        "last_seen": self._get_timestamp(),
                        "hit_count": 1
                    }
                }
                
                from scout_core import core_engine
                core_engine.upsert_record(record_packet)

        except Exception as e:
            self.logger.error(f"Scrape failed: {str(e)}")

    def _generate_custom_id(self, source_url: str, entity_label: str) -> str:
        from scout_core import core_engine
        return core_engine.generate_vanguard_id(source_url, entity_label)

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
