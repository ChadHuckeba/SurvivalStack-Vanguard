import time
import random
from base_scout import BaseScout
import logging
import yaml  # type: ignore
import os
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv

# Load environment variables (USER_HOME_LOCATION)
load_dotenv()

try:
    from jobspy import scrape_jobs
except ImportError:
    logging.warning("jobspy not found. JobSpyScout will run in mock mode.")
    scrape_jobs = None

class JobSpyScout(BaseScout):  # type: ignore[misc]
    """
    JobSpyScout wraps the JobSpy library to act as a Vanguard Research Bridge.
    It implements prioritized location logic and relocation heuristics based on YAML config.
    """
    
    def __init__(self, config_path: Optional[str | Path] = None) -> None:
        """
        Initialize with config file path. Defaults to config/scouts/jobspy.yaml.
        """
        super().__init__(scout_name="JobSpyScout", target_source="https://github.com/speedyapply/JobSpy")
        
        # Load Configuration
        self.root_dir = Path(__file__).parent.parent
        resolved_config_path = config_path or self.root_dir / "config" / "scouts" / "jobspy.yaml"
        with open(resolved_config_path, 'r') as f:
            self.settings = yaml.safe_load(f)
            
        self.search_params = self.settings.get("search_parameters", {})
        self.loc_logic = self.settings.get("location_logic", {})
        self.relo_heuristics = self.settings.get("relocation_heuristics", {})
        self.user_home = os.getenv("USER_HOME_LOCATION", "")

    def run(self) -> None:
        """
        Executes the JobSpy scrape with prioritized location logic.
        """
        if scrape_jobs is None:
            self.logger.error("JobSpy library not installed. Cannot run.")
            return

        # 1. First Pass: Remote Search (Global)
        if self.loc_logic.get("remote_allowed"):
            self._execute_search(is_remote=True, location=None)

        # Randomized delay between passes
        time.sleep(random.uniform(10, 20))

        # 2. Second Pass: Austin Metroplex (Hybrid/In-Office)
        target_metro = self.loc_logic.get("target_metro")
        if target_metro:
            self._execute_search(is_remote=False, location=target_metro)

    def _execute_search(self, is_remote: bool, location: Optional[str]) -> None:
        """Internal search runner for specific location context."""
        context_str = "Remote" if is_remote else f"Local ({location})"
        sites = self.search_params.get("sites", ["linkedin"])
        
        self.logger.info(f"Starting {context_str} search pass for {len(sites)} sites...")
        
        for site in sites:
            try:
                self.logger.info(f"Querying {site}...")
                
                # Jitter: Random sleep before each site request to avoid bulk detection
                time.sleep(random.uniform(3, 8))

                jobs = scrape_jobs(
                    site_name=[site],
                    search_term=self.search_params.get("term", "Software Engineer"),
                    location=location,
                    distance=self.loc_logic.get("metro_radius_miles", 35) if not is_remote else None,
                    is_remote=is_remote,
                    results_wanted=self.search_params.get("results_wanted", 20),
                    hours_old=self.search_params.get("hours_old", 72),
                    country_indeed='USA'
                )
                
                if jobs is not None and not jobs.empty:
                    count = len(jobs)
                    self.logger.info(f"Found {count} jobs on {site}.")
                    for _, row in jobs.iterrows():
                        job_data = row.to_dict()
                        self._process_and_report(job_data)
                else:
                    self.logger.warning(f"No jobs found on {site} for {context_str} context.")

            except Exception as e:
                # Catch specific 403s if possible, or log broadly
                self.logger.error(f"Search failed for {site}: {str(e)}")

    def _process_and_report(self, job_data: dict[str, Any]) -> None:
        """Refines data and applies relocation heuristics before reporting."""
        entity_label = job_data.get("title", "Unknown Title")
        
        # 1. Determine Work Model
        work_model = self._determine_work_model(job_data)
        
        # 2. Apply Relocation Heuristic
        relo_prob = self._calculate_relo_probability(job_data, work_model)
        job_data["vanguard_relo_probability"] = relo_prob
        
        # Cleanup data for storage
        for key, value in job_data.items():
            if hasattr(value, 'isoformat'):
                job_data[key] = value.isoformat()
            elif isinstance(value, float) and (value != value):
                job_data[key] = None

        # 3. Report using BaseScout interface
        self.report_entity(
            entity_label=entity_label,
            raw_data=job_data,
            work_model=work_model
        )

    def _determine_work_model(self, job_data: dict[str, Any]) -> str:
        """Heuristic to determine work modality from JobSpy fields."""
        location = str(job_data.get("location") or "").lower()
        description = str(job_data.get("description") or "").lower()
        
        if job_data.get("is_remote") or "remote" in location:
            return "remote"
        
        if "hybrid" in location or "hybrid" in description:
            return "hybrid"
            
        if location:
            return "onsite"
            
        return "unknown"

    def _calculate_relo_probability(self, job_data: dict[str, Any], work_model: str) -> float:
        """
        Calculates relocation probability (0.0 - 1.0) based on config keywords
        and metadata indicators.
        """
        # 1. Exclusion Guards
        if work_model == "remote":
            return 0.0
            
        # Don't need relocation if the job is already in our home location
        job_loc = str(job_data.get("location") or "").lower()
        if self.user_home and job_loc:
            # Simple check: if city/state from user_home is in job_loc
            home_parts = [p.strip().lower() for p in self.user_home.split(",")]
            # e.g. ["HOME_STREET_ADDRESS", "HOME_CITY_STATE"]
            # We care about city/state
            if any(part in job_loc for part in home_parts[1:]):
                return 0.0

        score = 0.0
        desc = str(job_data.get("description") or "").lower()
        
        # 2. Keyword Vector
        keywords = self.relo_heuristics.get("keywords", [])
        for kw in keywords:
            if kw.lower() in desc:
                score += 0.5 # Increased weight for explicit mention
                break
        
        # 3. Salary Vector
        min_sal = job_data.get("min_amount", 0) or 0
        threshold = self.relo_heuristics.get("min_salary_threshold", 110000)
        if min_sal >= threshold:
            score += 0.3
            
        # 4. Company Size Heuristic (if available)
        # Larger companies are more likely to have relo budgets
        
        return min(score, 1.0)
