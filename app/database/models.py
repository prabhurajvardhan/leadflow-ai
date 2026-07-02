from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, 
    ForeignKey, JSON, Float, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    pass


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    GOOGLE_MAPS_SEARCH = "google_maps_search"
    WEBSITE_CRAWL = "website_crawl"
    LEAD_ENRICHMENT = "lead_enrichment"
    AI_ANALYSIS = "ai_analysis"
    EMAIL_OUTREACH = "email_outreach"
    FULL_PIPELINE = "full_pipeline"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    ENRICHED = "enriched"
    ANALYZED = "analyzed"
    QUALIFIED = "qualified"
    REJECTED = "rejected"
    OUTREACH_SENT = "outreach_sent"
    REPLY_RECEIVED = "reply_received"
    CONVERTED = "converted"


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class EmailStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    workspaces = relationship("Workspace", back_populates="owner", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="workspaces")
    jobs = relationship("Job", back_populates="workspace", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="workspace", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="workspace", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(50), nullable=False)
    status = Column(String(20), default=JobStatus.PENDING.value)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    params = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    error_message = Column(Text)
    progress = Column(Integer, default=0)
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("Workspace", back_populates="jobs")

    __table_args__ = (
        Index("ix_jobs_workspace_status", "workspace_id", "status"),
        Index("ix_jobs_created_at", "created_at"),
    )


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    # Basic info
    name = Column(String(255))
    company_name = Column(String(255), index=True)
    domain = Column(String(255), index=True)
    description = Column(Text)
    
    # Location
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Contact info
    phone = Column(String(50))
    linkedin_url = Column(String(500))
    
    # Status & Scoring
    status = Column(String(20), default=LeadStatus.NEW.value, index=True)
    ai_score = Column(Float)
    quality_tier = Column(String(20))  # A, B, C, D
    
    # Source
    source = Column(String(50))
    source_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    workspace = relationship("Workspace", back_populates="leads")
    website = relationship("Website", back_populates="lead", uselist=False, cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="lead", cascade="all, delete-orphan")
    ai_report = relationship("AIReport", back_populates="lead", uselist=False, cascade="all, delete-orphan")
    social_profiles = relationship("SocialProfile", back_populates="lead", cascade="all, delete-orphan")
    sent_emails = relationship("SentEmail", back_populates="lead", cascade="all, delete-orphan")
    activities = relationship("ActivityLog", back_populates="lead", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_leads_workspace_status", "workspace_id", "status"),
        Index("ix_leads_company_domain", "company_name", "domain"),
        Index("ix_leads_ai_score", "ai_score"),
    )


class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    url = Column(String(500), nullable=False)
    title = Column(String(500))
    description = Column(Text)
    og_image = Column(String(500))
    
    # Tech stack
    technologies = Column(JSON, default=list)
    
    # Content
    meta_description = Column(Text)
    meta_keywords = Column(String(500))
    headers = Column(JSON, default=dict)
    
    # Stats
    page_count = Column(Integer, default=0)
    last_crawled = Column(DateTime(timezone=True))
    crawl_status = Column(String(20), default="pending")
    crawl_error = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    lead = relationship("Lead", back_populates="website")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), index=True)
    phone = Column(String(50))
    title = Column(String(255))
    department = Column(String(100))
    
    linkedin_url = Column(String(500))
    twitter_url = Column(String(500))
    
    is_primary = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    source = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    lead = relationship("Lead", back_populates="contacts")

    __table_args__ = (
        Index("ix_contacts_lead_email", "lead_id", "email"),
    )


class SocialProfile(Base):
    __tablename__ = "social_profiles"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    
    platform = Column(String(50), nullable=False)  # linkedin, twitter, facebook, etc.
    url = Column(String(500), nullable=False)
    handle = Column(String(100))
    followers_count = Column(Integer)
    following_count = Column(Integer)
    posts_count = Column(Integer)
    
    profile_data = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    lead = relationship("Lead", back_populates="social_profiles")

    __table_args__ = (
        UniqueConstraint("lead_id", "platform", name="uq_lead_platform"),
    )


class AIReport(Base):
    __tablename__ = "ai_reports"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Analysis results
    summary = Column(Text)
    pain_points = Column(JSON, default=list)
    opportunities = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    
    # Lead scoring
    score_breakdown = Column(JSON, default=dict)
    quality_tier = Column(String(10))
    
    # Company insights
    company_size_estimate = Column(String(50))
    industry = Column(String(100))
    funding_stage = Column(String(50))
    
    # Personalization hints
    personalization_hints = Column(JSON, default=dict)
    
    # Raw response
    raw_response = Column(JSON, default=dict)
    
    # Model info
    ai_provider = Column(String(50))
    ai_model = Column(String(100))
    tokens_used = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    lead = relationship("Lead", back_populates="ai_report")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    subject = Column(String(500))
    email_body = Column(Text)
    
    status = Column(String(20), default=CampaignStatus.DRAFT.value)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Stats
    total_leads = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    replied_count = Column(Integer, default=0)
    bounced_count = Column(Integer, default=0)
    
    settings = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    workspace = relationship("Workspace", back_populates="campaigns")
    sent_emails = relationship("SentEmail", back_populates="campaign", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_campaigns_workspace_status", "workspace_id", "status"),
    )


class SentEmail(Base):
    __tablename__ = "sent_emails"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    
    to_email = Column(String(255), nullable=False)
    from_email = Column(String(255))
    subject = Column(String(500))
    body = Column(Text)
    
    status = Column(String(20), default=EmailStatus.PENDING.value)
    
    # Tracking
    message_id = Column(String(500))  # SMTP message ID
    tracking_id = Column(String(100), unique=True)  # Custom tracking ID
    
    # Events
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    replied_at = Column(DateTime(timezone=True))
    bounced_at = Column(DateTime(timezone=True))
    
    # Error handling
    error_message = Column(Text)
    
    # Metadata
    smtp_response = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="sent_emails")
    campaign = relationship("Campaign", back_populates="sent_emails")
    replies = relationship("EmailReply", back_populates="sent_email", cascade="all, delete-orphan")
    followups = relationship("Followup", back_populates="sent_email", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_sent_emails_campaign_status", "campaign_id", "status"),
        Index("ix_sent_emails_lead_status", "lead_id", "status"),
        Index("ix_sent_emails_tracking_id", "tracking_id"),
    )


class EmailReply(Base):
    __tablename__ = "email_replies"

    id = Column(Integer, primary_key=True, index=True)
    sent_email_id = Column(Integer, ForeignKey("sent_emails.id", ondelete="CASCADE"), nullable=False)
    
    from_email = Column(String(255), nullable=False)
    subject = Column(String(500))
    body = Column(Text)
    
    raw_headers = Column(JSON, default=dict)
    raw_body = Column(Text)
    
    # AI analysis
    intent = Column(String(50))  # positive, negative, neutral, out_of_office
    sentiment = Column(String(20))
    summary = Column(Text)
    
    is_processed = Column(Boolean, default=False)
    
    received_at = Column(DateTime(timezone=True))
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sent_email = relationship("SentEmail", back_populates="replies")


class Followup(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    sent_email_id = Column(Integer, ForeignKey("sent_emails.id", ondelete="CASCADE"), nullable=False)
    
    sequence_number = Column(Integer, nullable=False)  # 1, 2, 3...
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    
    subject = Column(String(500))
    body = Column(Text)
    
    status = Column(String(20), default=EmailStatus.PENDING.value)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sent_email = relationship("SentEmail", back_populates="followups")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    activity_type = Column(String(50), nullable=False)
    description = Column(Text)
    extra_data = Column("metadata", JSON, default=dict)  # Renamed to avoid SQLAlchemy conflict
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="activities")
    workspace = relationship("Workspace")
    user = relationship("User")

    __table_args__ = (
        Index("ix_activity_logs_workspace_created", "workspace_id", "created_at"),
        Index("ix_activity_logs_lead_created", "lead_id", "created_at"),
    )
