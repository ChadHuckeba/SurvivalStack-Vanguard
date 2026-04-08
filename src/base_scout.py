from abc import ABC, abstractmethod
import logging
from datetime import datetime
from core.scout_core import core_engine

class BaseScout(ABC):
    """
    Abstract Base Class for all Vanguard specialized agents (Spokes).
    
    Provides the standardized interface for data ingestion and 
    communication with the ScoutCore (Hub).
    """

    def __init__(self, scout_name: str, target_source: str):
        """
        Initialize the scout with a unique name and its primary data source.
        """
        self.scout_name = scout_name
        self.target_source = target_source
        self.logger = logging.getLogger(f"vanguard.{scout_name}")

    @abstractmethod
    def run(self):
        """
        The primary execution loop for the scout.
        Must be implemented by all specialized subclasses.
        """
        pass

    def report_entity(self, entity_label: str, raw_data: dict):
        """
        Standardized method to hand data back to the ScoutCore.
        
        Args:
            entity_label (str): The primary name/title of the entity found.
            raw_data (dict): The full payload of data discovered.
        """
        # Generate the unique Vanguard ID using the Hub's logic
        vanguard_id = core_engine.generate_vanguard_id(
            source_url=self.target_source, 
            entity_label=entity_label
        )
        
        # Prepare the standardized record packet
        record_packet = {
            "vanguard_id": vanguard_id,
            "source_info": {
                "scout": self.scout_name,
                "source_url": self.target_source
            },
            "content": raw_data,
            "metadata": {
                "first_seen": datetime.utcnow().isoformat() + "Z",
                "last_seen": datetime.utcnow().isoformat() + "Z",
                "hit_count": 1
            }
        }
        
        self.logger.info(f"Reporting entity: {entity_label} ({vanguard_id[:8]})")
        
        # Hand the packet to the Singleton Hub
        core_engine.upsert_record(record_packet)