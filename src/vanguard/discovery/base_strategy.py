from abc import ABC, abstractmethod
from typing import Optional
from vanguard.models.discovery import DiscoveryResult

class BaseDiscoveryStrategy(ABC):
    """
    Abstract base class for all discovery strategies.
    """

    @abstractmethod
    def discover_portal(self, company_name: str, base_domain: str) -> Optional[DiscoveryResult]:
        """
        Attempts to find the official career portal for a company.
        """
        pass

    @abstractmethod
    def find_job_link(self, portal_url: str, job_title: str) -> Optional[str]:
        """
        Attempts to find a direct link to a specific job posting.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """The identifier for this strategy."""
        pass
