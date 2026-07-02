from typing import List, Dict, Any, Optional, Set
import re
import json
from dataclasses import dataclass
from app.core.logger import get_logger
import httpx

logger = get_logger("tech_detector")


@dataclass
class TechStack:
    """Represents a detected technology stack."""
    name: str
    category: str
    confidence: float  # 0-1
    version: Optional[str] = None


# Common technology signatures
TECH_SIGNATURES = {
    # JavaScript Frameworks
    "React": {"patterns": [r"react", r"react\.js", r"reactjs"], "files": ["react", "React"]},
    "Vue.js": {"patterns": [r"vue\.js", r"vuejs", r"vuejs\.org"], "files": ["vue", "Vue"]},
    "Angular": {"patterns": [r"angular", r"@angular/core"], "files": ["angular", "Angular"]},
    "Next.js": {"patterns": [r"next", r"next\.js", r"_next/"], "files": ["next", "nextjs"]},
    "Nuxt": {"patterns": [r"nuxt", r"nuxt\.js"], "files": ["nuxt", "Nuxt"]},
    "Svelte": {"patterns": [r"svelte", r"\.svelte"], "files": ["svelte", "Svelte"]},
    
    # Backend Frameworks
    "Django": {"patterns": [r"django", r"__init__\.py"], "files": ["django", "Django"]},
    "Flask": {"patterns": [r"flask", r"application\.wsgi"], "files": ["flask", "Flask"]},
    "FastAPI": {"patterns": [r"fastapi", r"FastAPI"], "files": ["fastapi", "FastAPI"]},
    "Express": {"patterns": [r"express", r"expressjs"], "files": ["express", "Express"]},
    "Spring": {"patterns": [r"spring", r"springframework"], "files": ["spring", "Spring"]},
    "Rails": {"patterns": [r"ruby-on-rails", r"Rails"], "files": ["rails", "Rails"]},
    "Laravel": {"patterns": [r"laravel", r"Laravel"], "files": ["laravel", "Laravel"]},
    
    # CMS
    "WordPress": {"patterns": [r"wordpress", r"wp-content", r"wp-includes"], "files": ["wordpress", "wp"]},
    "Shopify": {"patterns": [r"shopify", r"cdn\.shopify"], "files": ["shopify", "Shopify"]},
    "Wix": {"patterns": [r"wix\.com", r"wixsites"], "files": ["wix", "Wix"]},
    "Squarespace": {"patterns": [r"squarespace", r"sqsp\.com"], "files": ["squarespace", "Squarespace"]},
    "Webflow": {"patterns": [r"webflow\.io", r"wf"], "files": ["webflow", "Webflow"]},
    
    # Analytics
    "Google Analytics": {"patterns": [r"google-analytics\.com", r"gtag\(", r"ga\(['"], "files": ["analytics"]},
    "Google Tag Manager": {"patterns": [r"googletagmanager", r"gtm\.js"], "files": ["gtm"]},
    "Mixpanel": {"patterns": [r"mixpanel", r"mixpanel\.com"], "files": ["mixpanel"]},
    "Segment": {"patterns": [r"segment\.io", r"segment\.com"], "files": ["segment"]},
    "Hotjar": {"patterns": [r"hotjar", r"hj\.com"], "files": ["hotjar"]},
    "Amplitude": {"patterns": [r"amplitude", r"amplitude\.com"], "files": ["amplitude"]},
    
    # Marketing
    "Mailchimp": {"patterns": [r"mailchimp", r"list-manage", r"mc-"], "files": ["mailchimp"]},
    "HubSpot": {"patterns": [r"hubspot", r"hs-scripts", r"hubspotchat"], "files": ["hubspot"]},
    "Intercom": {"patterns": [r"intercom", r"widget\.intercom"], "files": ["intercom"]},
    "Drift": {"patterns": [r"drift", r"drift\.com"], "files": ["drift"]},
    "Zendesk": {"patterns": [r"zendesk", r"zd-static"], "files": ["zendesk"]},
    
    # Payment
    "Stripe": {"patterns": [r"stripe", r"js\.stripe", r"stripe\.com"], "files": ["stripe"]},
    "PayPal": {"patterns": [r"paypal", r"paypal\.com", r"paypalobjects"], "files": ["paypal"]},
    "Braintree": {"patterns": [r"braintree", r"braintree-api"], "files": ["braintree"]},
    
    # CDN & Infrastructure
    "Cloudflare": {"patterns": [r"cloudflare", r"cloudflareflare", r"__cf_"], "files": ["cloudflare"]},
    "AWS": {"patterns": [r"amazonaws", r"aws-", r"\.s3\.amazonaws"], "files": ["aws"]},
    "Google Cloud": {"patterns": [r"googlecloud", r"gcp", r"storage\.googleapis"], "files": ["gcp"]},
    "Azure": {"patterns": [r"azure", r"azurewebsites", r"\.azure\.com"], "files": ["azure"]},
    
    # Databases
    "MongoDB": {"patterns": [r"mongodb", r"mongo"], "files": ["mongodb"]},
    "PostgreSQL": {"patterns": [r"postgresql", r"postgres"], "files": ["postgresql"]},
    "Redis": {"patterns": [r"redis", r"redislabs"], "files": ["redis"]},
    "MySQL": {"patterns": [r"mysql"], "files": ["mysql"]},
    
    # Other Tools
    "jQuery": {"patterns": [r"jquery", r"jQuery"], "files": ["jquery"]},
    "Bootstrap": {"patterns": [r"bootstrap", r"cdn\.jsdelivr.*bootstrap"], "files": ["bootstrap"]},
    "Tailwind": {"patterns": [r"tailwind", r"tailwindcss"], "files": ["tailwind"]},
    "Font Awesome": {"patterns": [r"font-awesome", r"fontawesome", r"fa-"], "files": ["fontawesome"]},
    "Google Fonts": {"patterns": [r"fonts\.googleapis", r"fonts\.gstatic"], "files": ["google-fonts"]},
    "Disqus": {"patterns": [r"disqus", r"disqus\.com"], "files": ["disqus"]},
    "Typekit": {"patterns": [r"typekit", r"use\.typekit"], "files": ["typekit"]},
}


TECH_CATEGORIES = {
    "React": "frontend", "Vue.js": "frontend", "Angular": "frontend",
    "Next.js": "frontend", "Nuxt": "frontend", "Svelte": "frontend",
    "Django": "backend", "Flask": "backend", "FastAPI": "backend",
    "Express": "backend", "Spring": "backend", "Rails": "backend", "Laravel": "backend",
    "WordPress": "cms", "Shopify": "ecommerce", "Wix": "cms", "Squarespace": "cms", "Webflow": "cms",
    "Google Analytics": "analytics", "Google Tag Manager": "analytics", "Mixpanel": "analytics",
    "Segment": "analytics", "Hotjar": "analytics", "Amplitude": "analytics",
    "Mailchimp": "marketing", "HubSpot": "marketing", "Intercom": "marketing",
    "Drift": "marketing", "Zendesk": "support",
    "Stripe": "payment", "PayPal": "payment", "Braintree": "payment",
    "Cloudflare": "infrastructure", "AWS": "infrastructure", "Google Cloud": "infrastructure",
    "Azure": "infrastructure",
    "MongoDB": "database", "PostgreSQL": "database", "Redis": "database", "MySQL": "database",
    "jQuery": "javascript", "Bootstrap": "css", "Tailwind": "css",
    "Font Awesome": "icon", "Google Fonts": "font", "Disqus": "comments", "Typekit": "font",
}


class TechDetector:
    """Detects technologies used by a website."""
    
    def __init__(self):
        self.logger = logger
    
    async def detect(self, html: str, url: str, 
                    js_content: str = None) -> List[TechStack]:
        """Detect technologies from website content.
        
        Args:
            html: HTML content of the page
            url: URL of the page
            js_content: JavaScript content (optional)
            
        Returns:
            List of detected TechStack objects
        """
        detected: Dict[str, TechStack] = {}
        content = html.lower()
        js_content_lower = js_content.lower() if js_content else ""
        
        # Check for each technology
        for tech_name, signatures in TECH_SIGNATURES.items():
            confidence = 0.0
            
            # Check patterns in HTML
            for pattern in signatures.get("patterns", []):
                if re.search(pattern, content, re.IGNORECASE):
                    confidence = max(confidence, 0.7)
                    break
            
            # Check patterns in JavaScript
            for pattern in signatures.get("patterns", []):
                if js_content_lower and re.search(pattern, js_content_lower, re.IGNORECASE):
                    confidence = max(confidence, 0.9)
                    break
            
            # Check for files/scripts
            for file_sig in signatures.get("files", []):
                if file_sig.lower() in content or (js_content and file_sig.lower() in js_content_lower):
                    confidence = max(confidence, 0.8)
                    break
            
            if confidence > 0:
                category = TECH_CATEGORIES.get(tech_name, "other")
                detected[tech_name] = TechStack(
                    name=tech_name,
                    category=category,
                    confidence=confidence
                )
        
        result = list(detected.values())
        self.logger.info(f"Detected {len(result)} technologies from {url}")
        
        return result
    
    def detect_from_headers(self, headers: Dict[str, str]) -> List[TechStack]:
        """Detect technologies from HTTP headers."""
        detected = []
        
        header_str = str(headers).lower()
        
        for tech_name, signatures in TECH_SIGNATURES.items():
            for pattern in signatures.get("patterns", []):
                if re.search(pattern, header_str, re.IGNORECASE):
                    detected.append(TechStack(
                        name=tech_name,
                        category=TECH_CATEGORIES.get(tech_name, "other"),
                        confidence=0.6
                    ))
                    break
        
        return detected
    
    def detect_from_server_headers(self, headers: Dict[str, str]) -> List[TechStack]:
        """Detect server technologies from response headers."""
        detected = []
        
        server = headers.get("server", "").lower()
        x_powered_by = headers.get("x-powered-by", "").lower()
        
        # Server detection
        server_map = {
            "nginx": "Nginx",
            "apache": "Apache",
            "iis": "IIS",
            "cloudflare": "Cloudflare",
            "varnish": "Varnish",
        }
        
        for sig, name in server_map.items():
            if sig in server:
                detected.append(TechStack(
                    name=name,
                    category="server",
                    confidence=0.8
                ))
        
        # X-Powered-By detection
        power_map = {
            "php": "PHP",
            "asp.net": "ASP.NET",
            "express": "Express",
            "django": "Django",
            "rails": "Rails",
        }
        
        for sig, name in power_map.items():
            if sig in x_powered_by:
                detected.append(TechStack(
                    name=name,
                    category="backend",
                    confidence=0.7
                ))
        
        return detected
