from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SourceInfo(BaseModel):
    scout: str = Field(..., description="The name of the scout that discovered the lead")
    source_url: str = Field(..., description="The original URL of the job lead")

class Metadata(BaseModel):
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    hit_count: int = 1

class CareerInfo(BaseModel):
    url: Optional[str] = None
    method: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None

class LeadContent(BaseModel):
    id: Optional[str] = None
    site: Optional[str] = None
    job_url: Optional[str] = None
    job_url_direct: Optional[str] = None
    title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    location: Optional[str] = "Remote"
    date_posted: Optional[str] = None
    job_type: Optional[str] = None
    description: Optional[str] = None
    company_url: Optional[str] = None
    vanguard_relo_probability: float = 0.0

class Lead(BaseModel):
    vanguard_id: str
    source_info: SourceInfo
    content: LeadContent
    work_model: str = "unknown"
    career_info: CareerInfo = Field(default_factory=CareerInfo)
    metadata: Metadata = Field(default_factory=Metadata)
    status: str = "active"
