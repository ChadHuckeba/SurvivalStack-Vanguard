from typing import Optional
from pydantic import BaseModel

class DiscoveryResult(BaseModel):
    portal_url: Optional[str] = None
    deep_link: Optional[str] = None
    status: str = "pending"
    method: Optional[str] = None
    error: Optional[str] = None
    confidence_score: float = 0.0
