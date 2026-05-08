from typing import Optional, List
from pydantic import BaseModel, field_validator


# Centralized list of job aggregators and third-party boards to block from official discovery
# We use lowercase keywords to catch both domains and company names
GLOBAL_AGGREGATOR_BLOCKLIST: List[str] = [
    "jooble",
    "lensa",
    "swooped",
    "monster",
    "dice.com",  # Using .com for dice to avoid blocking companies that might just have 'dice' in name
    "salary.com",
    "levels.fyi",
    "ziprecruiter",
]


def is_blocked_entity(identity: str) -> bool:
    """Utility to check if a URL or Name belongs to a blocked aggregator."""
    if not identity:
        return False
    identity_lower = identity.lower()
    return any(blocked in identity_lower for blocked in GLOBAL_AGGREGATOR_BLOCKLIST)


class DiscoveryResult(BaseModel):
    portal_url: Optional[str] = None
    deep_link: Optional[str] = None
    status: str = "pending"
    method: Optional[str] = None
    error: Optional[str] = None
    confidence_score: float = 0.0

    @field_validator("portal_url", "deep_link")
    @classmethod
    def check_not_blocked(cls, v: Optional[str]) -> Optional[str]:
        if v and is_blocked_entity(v):
            raise ValueError(f"URL matches a blocked aggregator: {v}")
        return v
