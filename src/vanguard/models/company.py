from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from .discovery import is_blocked_entity


class Company(BaseModel):
    company_name: str = Field(..., min_length=1)
    root_domain: Optional[str] = None
    career_url: Optional[str] = None
    ats_provider: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("company_name", "root_domain", "career_url")
    @classmethod
    def check_not_blocked(cls, v: Optional[str]) -> Optional[str]:
        if v and is_blocked_entity(v):
            raise ValueError(f"Entity identity matches a blocked aggregator: {v}")
        return v
