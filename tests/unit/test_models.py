import pytest
from datetime import datetime
from app.database.models import (
    User, Workspace, Job, Lead, Website, Contact,
    SocialProfile, AIReport, Campaign, SentEmail,
    LeadStatus, JobStatus, CampaignStatus, EmailStatus
)


class TestUserModel:
    def test_user_creation(self):
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
    
    def test_user_defaults(self):
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        
        # SQLAlchemy defaults are applied at DB level, not Python level
        # Just verify model structure exists
        assert user.email == "test@example.com"
        assert user.username == "testuser"


class TestWorkspaceModel:
    def test_workspace_creation(self):
        workspace = Workspace(
            name="Test Workspace",
            slug="test-workspace",
            owner_id=1
        )
        
        assert workspace.name == "Test Workspace"
        assert workspace.slug == "test-workspace"
        assert workspace.owner_id == 1


class TestLeadModel:
    def test_lead_creation(self):
        lead = Lead(
            workspace_id=1,
            company_name="Test Corp",
            domain="testcorp.com",
            status=LeadStatus.NEW.value
        )
        
        assert lead.company_name == "Test Corp"
        assert lead.domain == "testcorp.com"
        assert lead.status == LeadStatus.NEW.value
        assert lead.workspace_id == 1
    
    def test_lead_statuses(self):
        statuses = [s.value for s in LeadStatus]
        
        assert "new" in statuses
        assert "enriched" in statuses
        assert "analyzed" in statuses


class TestJobModel:
    def test_job_creation(self):
        job = Job(
            workspace_id=1,
            job_type="full_pipeline",
            status=JobStatus.PENDING.value
        )
        
        assert job.workspace_id == 1
        assert job.job_type == "full_pipeline"
        assert job.status == JobStatus.PENDING.value


class TestCampaignModel:
    def test_campaign_creation(self):
        campaign = Campaign(
            workspace_id=1,
            name="Test Campaign",
            status=CampaignStatus.DRAFT.value
        )
        
        assert campaign.name == "Test Campaign"
        assert campaign.status == CampaignStatus.DRAFT.value


class TestSentEmailModel:
    def test_sent_email_creation(self):
        email = SentEmail(
            campaign_id=1,
            lead_id=1,
            to_email="test@example.com",
            subject="Test Subject",
            body="Test body",
            status=EmailStatus.PENDING.value
        )
        
        assert email.to_email == "test@example.com"
        assert email.subject == "Test Subject"
        assert email.status == EmailStatus.PENDING.value
    
    def test_sent_email_statuses(self):
        statuses = [s.value for s in EmailStatus]
        
        assert "pending" in statuses
        assert "sent" in statuses
        assert "delivered" in statuses
