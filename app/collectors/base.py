from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.core.logger import get_logger

logger = get_logger("collector_base")


@dataclass
class CollectedLead:
    """Data class representing a collected lead."""
    source: str
    company_name: str
    domain: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    linkedin_url: Optional[str] = None
    description: Optional[str] = None
    source_data: Dict[str, Any] = None
    
    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "company_name": self.company_name,
            "domain": self.domain,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
            "linkedin_url": self.linkedin_url,
            "description": self.description,
            "source_data": self.source_data or {}
        }


class BaseCollector(ABC):
    """Base class for all lead collectors.
    
    Collectors are pluggable modules that can be replaced without affecting
    the rest of the application.
    """
    
    name: str = "base"
    source_type: str = "generic"
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = get_logger(f"collector_{self.name}")
    
    @abstractmethod
    async def collect(self, query: str, **kwargs) -> List[CollectedLead]:
        """Collect leads based on a query.
        
        Args:
            query: The search query (e.g., "restaurants in NYC", "SaaS companies")
            **kwargs: Additional collector-specific parameters
            
        Returns:
            List of CollectedLead objects
        """
        pass
    
    async def validate(self) -> bool:
        """Validate collector configuration.
        
        Returns:
            True if collector is properly configured
        """
        return True
    
    async def get_source_name(self) -> str:
        """Get the name of the data source."""
        return self.source_type
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} collector>"
