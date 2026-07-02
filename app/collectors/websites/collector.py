from typing import List, Dict, Any, Optional
import re
from urllib.parse import urlparse
from app.collectors.base import BaseCollector, CollectedLead
from app.core.logger import get_logger
import httpx

logger = get_logger("website_collector")


class WebsiteCollector(BaseCollector):
    """Collector for extracting leads from a website.
    
    Can be used to process a list of domains and extract company information.
    """
    
    name = "website"
    source_type = "website"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.timeout = (config or {}).get("timeout", 30)
    
    async def collect(self, url: str, **kwargs) -> List[CollectedLead]:
        """Collect lead information from a website.
        
        Args:
            url: Website URL to analyze
            **kwargs: Additional parameters
        """
        self.logger.info(f"Collecting lead info from: {url}")
        
        lead = await self._extract_from_website(url)
        
        return [lead] if lead else []
    
    async def collect_batch(self, urls: List[str], 
                           **kwargs) -> List[CollectedLead]:
        """Collect from multiple websites.
        
        Args:
            urls: List of website URLs
            **kwargs: Additional parameters
        """
        leads = []
        
        for url in urls:
            lead = await self._extract_from_website(url)
            if lead:
                leads.append(lead)
        
        self.logger.info(f"Collected {len(leads)} leads from {len(urls)} URLs")
        return leads
    
    async def _extract_from_website(self, url: str) -> Optional[CollectedLead]:
        """Extract company information from a website."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "LeadFlow AI Bot (+https://leadflow.ai/bot)"
                }
            ) as client:
                response = await client.get(url)
                html = response.text
                
                domain = urlparse(url).netloc
                company_name = self._extract_company_name(html, domain)
                email = self._extract_email(html)
                phone = self._extract_phone(html)
                description = self._extract_description(html)
                
                return CollectedLead(
                    source=self.source_type,
                    company_name=company_name,
                    domain=domain,
                    email=email,
                    phone=phone,
                    description=description,
                    source_data={"url": url}
                )
                
        except Exception as e:
            self.logger.error(f"Failed to extract from {url}: {e}")
            return None
    
    def _extract_company_name(self, html: str, default_domain: str) -> str:
        """Extract company name from HTML."""
        # Try og:site_name first
        match = re.search(r'<meta[^>]*property=["\']og:site_name["\'][^>]*content=["\']([^"\']+)["\']', html)
        if match:
            return match.group(1)
        
        # Try <title> tag
        match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Clean common suffixes
            title = re.sub(r'\s*[-|]\s*.+$', '', title)
            return title
        
        return default_domain
    
    def _extract_email(self, html: str) -> Optional[str]:
        """Extract email address from HTML."""
        # Common patterns for email extraction
        patterns = [
            r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                email = match.group(1) if match.lastindex else match.group(0)
                # Filter out common non-contact emails
                if not any(x in email.lower() for x in ['noreply', 'no-reply', 'example']):
                    return email
        
        return None
    
    def _extract_phone(self, html: str) -> Optional[str]:
        """Extract phone number from HTML."""
        patterns = [
            r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'tel:([^\s"]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                phone = match.group(1) if match.lastindex else match.group(0)
                return phone.strip()
        
        return None
    
    def _extract_description(self, html: str) -> Optional[str]:
        """Extract meta description."""
        patterns = [
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
            r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']',
            r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
