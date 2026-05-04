from base_scout import BaseScout
import logging
import yaml
from pathlib import Path
from typing import List, Dict, Optional

try:
    from jobspy import scrape_jobs
except ImportError:
    logging.warning("jobspy not found. JobSpyScout will run in mock mode.")
    scrape_jobs = None

class JobSpyScout(BaseScout):
    """
    JobSpyScout wraps the JobSpy library to act as a Vanguard Research Bridge.
    It implements prioritized location logic and relocation heuristics based on YAML config.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize with config file path. Defaults to config/scout_settings.yaml.
        """
        super().__init__(scout_name="JobSpyScout", target_source="https://github.com/speedyapply/JobSpy")
        
        # Load Configuration
        self.root_dir = Path(__file__).parent.parent
        config_path = config_path or self.root_dir / "config" / "scout_settings.yaml"
        with open(config_path, 'r') as f:
            self.settings = yaml.safe_load(f)
            
        self.search_params = self.settings.get("search_parameters", {})
        self.loc_logic = self.settings.get("location_logic", {})
        self.relo_heuristics = self.settings.get("relocation_heuristics", {})

    def run(self):
        """
        Executes the JobSpy scrape with prioritized location logic.
        """
        if scrape_jobs is None:
            self.logger.error("JobSpy library not installed. Cannot run.")
            return

        # 1. First Pass: Remote Search (Global)
        if self.loc_logic.get("remote_allowed"):
            self._execute_search(is_remote=True, location=None)

        # 2. Second Pass: Austin Metroplex (Hybrid/In-Office)
        target_metro = self.loc_logic.get("target_metro")
        if target_metro:
            self._execute_search(is_remote=False, location=target_metro)

    def _execute_search(self, is_remote: bool, location: Optional[str]):
        """Internal search runner for specific location context."""
        context_str = "Remote" if is_remote else f"Local ({location})"
        self.logger.info(f"Starting {context_str} search pass...")
        
        try:
            jobs = scrape_jobs(
                site_name=self.search_params.get("sites", ["linkedin"]),
                search_term=self.search_params.get("term", "Software Engineer"),
                location=location,
                distance=self.loc_logic.get("metro_radius_miles", 35) if not is_remote else None,
                is_remote=is_remote,
                results_wanted=self.search_params.get("results_wanted", 20),
                hours_old=self.search_params.get("hours_old", 72),
                country_indeed='USA'
            )
            
            for _, row in jobs.iterrows():
                job_data = row.to_dict()
                self._process_and_report(job_data)

        except Exception as e:
            self.logger.error(f"Search pass failed: {str(e)}")

    def _process_and_report(self, job_data: dict):
        """Refines data and applies relocation heuristics before reporting."""
        entity_label = job_data.get("title", "Unknown Title")
        source_url = job_data.get("job_url", "unknown")
        
        # Apply Relocation Heuristic
        relo_prob = self._calculate_relo_probability(job_data)
        job_data["vanguard_relo_probability"] = relo_prob
        
        # Cleanup data for storage
        for key, value in job_data.items():
            if hasattr(value, 'isoformat'):
                job_data[key] = value.isoformat()
            elif isinstance(value, float) and (value != value):
                job_data[key] = None

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

    def _calculate_relo_probability(self, job_data: dict) -> float:
        """
        Calculates relocation probability (0.0 - 1.0) based on config keywords
        and metadata indicators.
        """
        score = 0.0
        desc = (job_data.get("description") or "").lower()
        
        # 1. Keyword Vector
        keywords = self.relo_heuristics.get("keywords", [])
        for kw in keywords:
            if kw.lower() in desc:
                score += 0.4
                break # Only count once
        
        # 2. Salary Vector (Heuristic: High-pay roles often include relo)
        min_sal = job_data.get("min_amount", 0) or 0
        threshold = self.relo_heuristics.get("min_salary_threshold", 120000)
        if min_sal >= threshold:
            score += 0.3
            
        # 3. Location Vector (Remote roles don't need relo)
        if job_data.get("is_remote"):
            return 0.0
            
        return min(score, 1.0)

    def _generate_custom_id(self, source_url: str, entity_label: str) -> str:
        from scout_core import core_engine
        return core_engine.generate_vanguard_id(source_url, entity_label)

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
