from app.collectors.base import BaseCollector, CollectedLead
from app.collectors.google_maps.collector import GoogleMapsCollector
from app.collectors.websites.collector import WebsiteCollector

__all__ = [
    "BaseCollector",
    "CollectedLead", 
    "GoogleMapsCollector",
    "WebsiteCollector"
]
