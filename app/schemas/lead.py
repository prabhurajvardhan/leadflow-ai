from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class ContactBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int
    lead_id: int
    is_primary: bool
    is_verified: bool
    source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SocialProfileBase(BaseModel):
    platform: str
    url: str
    handle: Optional[str] = None


class SocialProfileResponse(SocialProfileBase):
    id: int
    lead_id: int
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    posts_count: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WebsiteBase(BaseModel):
    url: str


class WebsiteResponse(WebsiteBase):
    id: int
    lead_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    og_image: Optional[str] = None
    technologies: List[str] = []
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    headers: Dict[str, Any] = {}
    page_count: int = 0
    last_crawled: Optional[datetime] = None
    crawl_status: str = "pending"
    crawl_error: Optional[str] = None

    class Config:
        from_attributes = True


class AIReportBase(BaseModel):
    summary: Optional[str] = None
    pain_points: List[str] = []
    opportunities: List[str] = []
    recommendations: List[str] = []


class AIReportResponse(AIReportBase):
    id: int
    lead_id: int
    score_breakdown: Dict[str, Any] = {}
    quality_tier: Optional[str] = None
    company_size_estimate: Optional[str] = None
    industry: Optional[str] = None
    funding_stage: Optional[str] = None
    personalization_hints: Dict[str, Any] = {}
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LeadBase(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None


class LeadCreate(LeadBase):
    source: Optional[str] = None
    source_data: Dict[str, Any] = {}


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: Optional[str] = None


class LeadResponse(LeadBase):
    id: int
    workspace_id: int
    status: str
    ai_score: Optional[float] = None
    quality_tier: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeadDetailResponse(LeadResponse):
    website: Optional[WebsiteResponse] = None
    contacts: List[ContactResponse] = []
    social_profiles: List[SocialProfileResponse] = []
    ai_report: Optional[AIReportResponse] = None

    class Config:
        from_attributes = True


class LeadBulkCreate(BaseModel):
    leads: List[LeadCreate]


class LeadBulkStatusUpdate(BaseModel):
    lead_ids: List[int]
    status: str


class LeadStatsResponse(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_quality_tier: Dict[str, int]
    average_score: float


class LeadSearchResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    skip: int
    limit: int
