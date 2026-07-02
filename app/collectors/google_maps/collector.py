from typing import List, Dict, Any, Optional
import asyncio
import re
from urllib.parse import urlencode, quote
from app.collectors.base import BaseCollector, CollectedLead
from app.core.logger import get_logger
from app.core.config import settings
import httpx

logger = get_logger("google_maps_collector")


class GoogleMapsCollector(BaseCollector):
    """Collector for Google Maps business listings.
    
    Uses Google Places API or web scraping to collect business information.
    """
    
    name = "google_maps"
    source_type = "google_maps"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.api_key = config.get("api_key") or settings.GOOGLE_MAPS_API_KEY
        self.use_api = bool(self.api_key)
    
    async def validate(self) -> bool:
        """Validate collector configuration."""
        if not self.use_api and not self.api_key:
            self.logger.warning("No Google Maps API key provided")
        return True
    
    async def collect(self, query: str, location: str = None, 
                     max_results: int = 100, **kwargs) -> List[CollectedLead]:
        """Collect leads from Google Maps.
        
        Args:
            query: Business type or keyword (e.g., "restaurants", "law firms")
            location: Location to search (e.g., "New York", "NYC")
            max_results: Maximum number of results to collect
            **kwargs: Additional parameters
        """
        self.logger.info(f"Collecting leads for query: {query}, location: {location}")
        
        if self.use_api:
            return await self._collect_via_api(query, location, max_results)
        else:
            return await self._collect_via_scrape(query, location, max_results)
    
    async def _collect_via_api(self, query: str, location: str,
                              max_results: int) -> List[CollectedLead]:
        """Collect using Google Places API."""
        leads = []
        
        try:
            # Text Search API
            search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": f"{query} {location}" if location else query,
                "key": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(search_url, params=params)
                data = response.json()
                
                for place in data.get("results", [])[:max_results]:
                    lead = self._parse_place_result(place)
                    leads.append(lead)
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
                    
                    # Fetch details for each place
                    if len(leads) < max_results and "place_id" in place:
                        detail_lead = await self._fetch_place_details(
                            place["place_id"], client
                        )
                        if detail_lead:
                            leads.append(detail_lead)
                            await asyncio.sleep(0.1)
            
            self.logger.info(f"Collected {len(leads)} leads via API")
            
        except Exception as e:
            self.logger.error(f"API collection failed: {e}")
        
        return leads[:max_results]
    
    async def _fetch_place_details(self, place_id: str, 
                                  client: httpx.AsyncClient) -> Optional[CollectedLead]:
        """Fetch detailed information for a place."""
        try:
            detail_url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,formatted_phone_number,website,url",
                "key": self.api_key
            }
            
            response = await client.get(detail_url, params=params)
            data = response.json()
            result = data.get("result", {})
            
            if result:
                return CollectedLead(
                    source=self.source_type,
                    company_name=result.get("name"),
                    phone=result.get("formatted_phone_number"),
                    address=result.get("formatted_address"),
                    website=result.get("website"),
                    source_data={"place_id": place_id, "type": "detail"}
                )
        except Exception as e:
            self.logger.error(f"Failed to fetch details for {place_id}: {e}")
        
        return None
    
    async def _collect_via_scrape(self, query: str, location: str,
                                  max_results: int) -> List[CollectedLead]:
        """Collect using web scraping (fallback method)."""
        leads = []
        
        try:
            # Build search URL
            search_query = f"{query} {location}" if location else query
            url = f"https://www.google.com/maps/search/{quote(search_query)}"
            
            # Note: Actual scraping requires Playwright setup
            # This is a simplified version for demonstration
            self.logger.warning("Web scraping requires Playwright setup")
            
        except Exception as e:
            self.logger.error(f"Scrape collection failed: {e}")
        
        return leads
    
    def _parse_place_result(self, place: Dict[str, Any]) -> CollectedLead:
        """Parse a Google Places result into a CollectedLead."""
        address = place.get("formatted_address", "")
        address_parts = address.split(", ")
        
        return CollectedLead(
            source=self.source_type,
            company_name=place.get("name"),
            domain=None,  # Would need to extract from website
            address=address,
            city=address_parts[0] if len(address_parts) > 0 else None,
            state=address_parts[-2] if len(address_parts) > 2 else None,
            country=address_parts[-1] if address_parts else None,
            phone=place.get("formatted_phone_number"),
            description=place.get("business_status"),
            source_data={
                "place_id": place.get("place_id"),
                "types": place.get("types", []),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total")
            }
        )
    
    def _extract_domain(self, website: str) -> Optional[str]:
        """Extract domain from website URL."""
        if not website:
            return None
        match = re.search(r'https?://([^/]+)', website)
        return match.group(1) if match else None
