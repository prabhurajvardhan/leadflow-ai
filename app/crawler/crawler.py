from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from selectolax.parser import HTMLParser
import httpx
from app.crawler.tech_detector import TechDetector, TechStack
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("crawler")


@dataclass
class CrawledPage:
    """Represents a crawled page."""
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    headings: Dict[str, List[str]] = None  # h1, h2, h3, etc.
    links: List[str] = None
    images: List[str] = None
    content: Optional[str] = None
    status_code: int = 200
    error: Optional[str] = None
    crawled_at: datetime = None


@dataclass
class CrawlResult:
    """Result of crawling a website."""
    url: str
    pages: List[CrawledPage]
    technologies: List[TechStack]
    emails: List[str]
    phones: List[str]
    social_links: Dict[str, str]
    total_pages: int
    success: bool
    error: Optional[str] = None


class WebsiteCrawler:
    """Crawls websites to extract information."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.user_agent = self.config.get("user_agent", settings.CRAWLER_USER_AGENT)
        self.timeout = self.config.get("timeout", settings.CRAWLER_REQUEST_TIMEOUT)
        self.max_depth = self.config.get("max_depth", settings.CRAWLER_MAX_DEPTH)
        self.max_pages = self.config.get("max_pages", 50)
        self.tech_detector = TechDetector()
        self.visited: Set[str] = set()
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={"User-Agent": self.user_agent}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def crawl(self, url: str) -> CrawlResult:
        """Crawl a website starting from the given URL.
        
        Args:
            url: Starting URL to crawl
            
        Returns:
            CrawlResult with all extracted data
        """
        self.logger.info(f"Starting crawl of {url}")
        self.visited.clear()
        
        pages: List[CrawledPage] = []
        emails: Set[str] = set()
        phones: Set[str] = set()
        social_links: Dict[str, str] = {}
        all_technologies: List[TechStack] = []
        
        base_domain = urlparse(url).netloc
        
        async def crawl_page(page_url: str, depth: int = 0):
            if depth > self.max_depth or len(pages) >= self.max_pages:
                return
            
            normalized_url = self._normalize_url(page_url)
            if normalized_url in self.visited:
                return
            
            self.visited.add(normalized_url)
            
            page = await self._fetch_page(page_url)
            if not page:
                return
            
            pages.append(page)
            
            # Extract data
            emails.update(self._extract_emails(page.content or ""))
            phones.update(self._extract_phones(page.content or ""))
            social_links.update(self._extract_social_links(page.content or "", page_url))
            
            # Detect technologies
            techs = await self.tech_detector.detect(
                page.content or "", page_url
            )
            all_technologies.extend(techs)
            
            # Follow internal links
            if depth < self.max_depth:
                for link in page.links or []:
                    if urlparse(link).netloc == base_domain:
                        await crawl_page(link, depth + 1)
        
        try:
            await crawl_page(url)
            
            # Deduplicate technologies
            unique_techs = {}
            for tech in all_technologies:
                if tech.name not in unique_techs or tech.confidence > unique_techs[tech.name].confidence:
                    unique_techs[tech.name] = tech
            
            return CrawlResult(
                url=url,
                pages=pages,
                technologies=list(unique_techs.values()),
                emails=list(emails),
                phones=list(phones),
                social_links=social_links,
                total_pages=len(pages),
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Crawl failed for {url}: {e}")
            return CrawlResult(
                url=url,
                pages=pages,
                technologies=all_technologies,
                emails=list(emails),
                phones=list(phones),
                social_links=social_links,
                total_pages=len(pages),
                success=False,
                error=str(e)
            )
    
    async def _fetch_page(self, url: str) -> Optional[CrawledPage]:
        """Fetch and parse a single page."""
        try:
            response = await self.client.get(url)
            
            if response.status_code != 200:
                return CrawledPage(
                    url=url,
                    status_code=response.status_code,
                    error=f"HTTP {response.status_code}",
                    crawled_at=datetime.utcnow()
                )
            
            html = response.text
            parser = HTMLParser(html)
            
            # Extract metadata
            title = parser.css_first("title")
            title_text = title.text() if title else None
            
            meta_desc = parser.css_first('meta[name="description"]')
            desc_attr = meta_desc.attributes.get("content") if meta_desc else None
            
            meta_keywords = parser.css_first('meta[name="keywords"]')
            keywords_attr = meta_keywords.attributes.get("content") if meta_keywords else None
            
            # Extract headings
            headings: Dict[str, List[str]] = {}
            for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                headings[tag] = [node.text() for node in parser.css(tag)]
            
            # Extract links
            links = []
            for link in parser.css("a[href]"):
                href = link.attributes.get("href")
                if href:
                    full_url = urljoin(url, href)
                    if not full_url.startswith("javascript:") and not full_url.startswith("#"):
                        links.append(full_url)
            
            # Extract images
            images = []
            for img in parser.css("img[src]"):
                src = img.attributes.get("src")
                if src:
                    images.append(urljoin(url, src))
            
            # Extract main content
            content = self._extract_main_content(parser)
            
            # Detect technologies from headers
            techs = self.tech_detector.detect_from_server_headers(dict(response.headers))
            
            return CrawledPage(
                url=url,
                title=title_text,
                meta_description=desc_attr,
                meta_keywords=keywords_attr,
                headings=headings,
                links=links,
                images=images,
                content=html[:10000],  # Limit content size
                status_code=200,
                crawled_at=datetime.utcnow()
            )
            
        except httpx.TimeoutException:
            return CrawledPage(
                url=url,
                error="Timeout",
                crawled_at=datetime.utcnow()
            )
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return CrawledPage(
                url=url,
                error=str(e),
                crawled_at=datetime.utcnow()
            )
    
    def _extract_main_content(self, parser: HTMLParser) -> str:
        """Extract main content from HTML."""
        # Try common content containers
        selectors = [
            "article",
            "main",
            "[role='main']",
            ".content",
            "#content",
            ".post",
            ".article",
            "body"
        ]
        
        for selector in selectors:
            element = parser.css_first(selector)
            if element:
                return element.text()
        
        return ""
    
    def _extract_emails(self, content: str) -> Set[str]:
        """Extract email addresses from content."""
        emails = set()
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        for match in re.finditer(pattern, content):
            email = match.group()
            # Filter out common non-contact emails
            if not any(x in email.lower() for x in ['noreply', 'no-reply', 'example', 'test']):
                emails.add(email.lower())
        
        return emails
    
    def _extract_phones(self, content: str) -> Set[str]:
        """Extract phone numbers from content."""
        phones = set()
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{1,3}[-.\s]?\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                phone = match.group()
                if len(phone) >= 10:  # Filter out short matches
                    phones.add(phone)
        
        return phones
    
    def _extract_social_links(self, content: str, base_url: str) -> Dict[str, str]:
        """Extract social media links."""
        social = {}
        
        platforms = {
            "linkedin": r'linkedin\.com/in/[^\s"\'<>]+',
            "twitter": r'twitter\.com/[^\s"\'<>]+|x\.com/[^\s"\'<>]+',
            "facebook": r'facebook\.com/[^\s"\'<>]+',
            "instagram": r'instagram\.com/[^\s"\'<>]+',
            "youtube": r'youtube\.com/[^\s"\'<>]+|youtu\.be/[^\s"\'<>]+',
            "github": r'github\.com/[^\s"\'<>]+',
        }
        
        for platform, pattern in platforms.items():
            match = re.search(pattern, content)
            if match:
                url = match.group()
                if not url.startswith("http"):
                    url = f"https://{url}"
                social[platform] = url
        
        return social
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    @property
    def logger(self):
        return get_logger("crawler")
