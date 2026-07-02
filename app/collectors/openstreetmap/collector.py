from typing import List, Dict, Any, Optional
import httpx
from app.collectors.base import BaseCollector, CollectedLead
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("openstreetmap_collector")


class OpenStreetMapCollector(BaseCollector):
    """OpenStreetMap collector for lead discovery.
    
    Uses Nominatim (geocoding) and Overpass (POI search) APIs
    to find businesses without requiring API keys or payment.
    
    Rate limits:
    - Nominatim: 1 request/second
    - Overpass: 2 requests/second
    """
    
    name = "openstreetmap"
    source_type = "osm"
    
    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
    OVERPASS_BASE_URL = "https://overpass-api.de/api/interpreter"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.rate_limit_delay = self.config.get("rate_limit_delay", 1.1)
        self.max_results = self.config.get("max_results", 50)
        self._last_request_time = 0
        self.timeout = self.config.get("timeout", 30)
    
    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        import asyncio
        import time
        
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    async def _nominatim_search(self, query: str, limit: int = 50) -> List[Dict]:
        """Search using Nominatim (geocoding service)."""
        await self._rate_limit()
        
        params = {
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": limit,
            "extratags": 1
        }
        
        headers = {"User-Agent": "LeadFlowAI/1.0 (https://leadflow.ai)"}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.NOMINATIM_BASE_URL}/search",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    async def _overpass_query(self, query: str, location: str = None) -> List[Dict]:
        """Query using Overpass API for Points of Interest."""
        await self._rate_limit()
        
        if location:
            geo_results = await self._nominatim_search(location, limit=1)
            if not geo_results:
                return []
            
            center = geo_results[0]
            lat, lon = center.get("lat"), center.get("lon")
            
            overpass_query = f"""
            [out:json][timeout:30];
            (
              node["name"~"{query}", i](around:10000,{lat},{lon});
              way["name"~"{query}", i](around:10000,{lat},{lon});
            );
            out body;
            """
        else:
            overpass_query = f"""
            [out:json][timeout:30];
            (
              node["name"~"{query}", i];
              way["name"~"{query}", i];
            );
            out body;
            """
        
        headers = {"User-Agent": "LeadFlowAI/1.0 (https://leadflow.ai)"}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.OVERPASS_BASE_URL,
                data={"data": overpass_query},
                headers=headers
            )
            response.raise_for_status()
            return response.json().get("elements", [])
    
    async def collect(self, query: str, location: str = None, **kwargs) -> List[CollectedLead]:
        """Collect leads from OpenStreetMap.
        
        Args:
            query: Search query (e.g., "software company", "restaurant")
            location: Optional location filter (e.g., "San Francisco, CA")
            
        Returns:
            List of CollectedLead objects
        """
        self.logger.info(f"Collecting from OSM: query='{query}', location='{location}'")
        
        leads = []
        
        try:
            search_query = query
            if location:
                search_query = f"{query} in {location}"
            
            results = await self._nominatim_search(search_query, limit=self.max_results)
            
            for result in results:
                try:
                    lead = self._parse_result(result)
                    if lead:
                        leads.append(lead)
                except Exception as e:
                    self.logger.warning(f"Failed to parse result: {e}")
                    continue
            
            if not leads:
                self.logger.info("No Nominatim results, trying Overpass...")
                overpass_results = await self._overpass_query(query, location)
                
                for element in overpass_results[:self.max_results]:
                    try:
                        if "id" in element and "type" in element:
                            details = await self._get_place_details(element["id"], element["type"])
                            if details:
                                lead = self._parse_result(details)
                                if lead:
                                    leads.append(lead)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse Overpass result: {e}")
                        continue
            
            self.logger.info(f"Collected {len(leads)} leads from OSM")
            return leads
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error during OSM collection: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error collecting from OSM: {e}")
            return []
    
    async def _get_place_details(self, osm_id: int, osm_type: str) -> Optional[Dict]:
        """Get details for a specific OSM place."""
        await self._rate_limit()
        
        headers = {"User-Agent": "LeadFlowAI/1.0 (https://leadflow.ai)"}
        
        endpoint = f"{self.NOMINATIM_BASE_URL}/lookup"
        params = {
            "osm_ids": f"{osm_type[0].upper()}{osm_id}",
            "format": "json",
            "addressdetails": 1,
            "extratags": 1
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(endpoint, params=params, headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                return results[0] if results else None
            return None
    
    def _parse_result(self, result: Dict) -> Optional[CollectedLead]:
        """Parse a Nominatim/OSM result into a CollectedLead."""
        
        address = result.get("address", {})
        extratags = result.get("extratags", {})
        
        name = (
            result.get("display_name", "").split(",")[0] or
            result.get("name") or
            extratags.get("name") or
            extratags.get("brand:name")
        )
        
        if not name or len(name) < 2:
            return None
        
        website = result.get("website") or extratags.get("website")
        if website:
            domain = website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        else:
            domain = None
        
        phone = result.get("phone") or extratags.get("phone") or extratags.get("contact:phone")
        email = extratags.get("email") or extratags.get("contact:email")
        
        address_parts = []
        for part in ["house_number", "road", "city", "town", "village", "state", "postcode"]:
            if address.get(part):
                address_parts.append(address[part])
        address_str = ", ".join(address_parts) if address_parts else None
        
        country = address.get("country", "")
        city = address.get("city") or address.get("town") or address.get("village") or address.get("state")
        
        return CollectedLead(
            source="openstreetmap",
            company_name=name,
            domain=domain,
            phone=phone,
            email=email,
            address=address_str,
            city=city,
            country=country,
            source_data={
                "osm_id": result.get("osm_id"),
                "osm_type": result.get("type"),
                "lat": result.get("lat"),
                "lon": result.get("lon"),
                "display_name": result.get("display_name"),
                "extratags": extratags
            }
        )
    
    async def reverse_geocode(self, lat: float, lon: float) -> Optional[Dict]:
        """Reverse geocode coordinates to address."""
        await self._rate_limit()
        
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1
        }
        
        headers = {"User-Agent": "LeadFlowAI/1.0 (https://leadflow.ai)"}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.NOMINATIM_BASE_URL}/reverse",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
