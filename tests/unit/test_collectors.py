import pytest
from app.collectors.base import BaseCollector, CollectedLead
from app.collectors.websites.collector import WebsiteCollector


class TestCollectedLead:
    def test_collected_lead_creation(self):
        lead = CollectedLead(
            source="google_maps",
            company_name="Test Company",
            domain="test.com",
            email="contact@test.com",
            phone="+1234567890"
        )
        
        assert lead.source == "google_maps"
        assert lead.company_name == "Test Company"
        assert lead.domain == "test.com"
        assert lead.email == "contact@test.com"
        assert lead.phone == "+1234567890"
    
    def test_collected_lead_to_dict(self):
        lead = CollectedLead(
            source="google_maps",
            company_name="Test Company",
            domain="test.com",
            source_data={"place_id": "abc123"}
        )
        
        data = lead.to_dict()
        
        assert data["source"] == "google_maps"
        assert data["company_name"] == "Test Company"
        assert data["domain"] == "test.com"
        assert data["source_data"]["place_id"] == "abc123"


class TestBaseCollector:
    def test_base_collector_name(self):
        class TestCollector(BaseCollector):
            name = "test"
            
            async def collect(self, query: str, **kwargs):
                return []
        
        collector = TestCollector()
        
        assert collector.name == "test"
        assert collector.source_type == "generic"


class TestWebsiteCollector:
    def test_extract_company_name_from_title(self):
        collector = WebsiteCollector()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>ACME Corporation - Leading Solutions</title></head>
        <body></body>
        </html>
        """
        
        name = collector._extract_company_name(html, "acme.com")
        
        assert name == "ACME Corporation"
    
    def test_extract_email_from_html(self):
        collector = WebsiteCollector()
        
        html = """
        <html>
        <body>
            <a href="mailto:contact@company.com">Contact Us</a>
        </body>
        </html>
        """
        
        email = collector._extract_email(html)
        
        assert email == "contact@company.com"
    
    def test_extract_description(self):
        collector = WebsiteCollector()
        
        html = """
        <html>
        <head>
            <meta name="description" content="This is a test company description">
        </head>
        <body></body>
        </html>
        """
        
        desc = collector._extract_description(html)
        
        assert desc == "This is a test company description"
