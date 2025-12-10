"""
Economic Data Collector
Gathers real estate and economic indicators
"""

import httpx
from typing import Dict, Any
from loguru import logger

from app.config import get_settings


class EconomicCollector:
    """
    Collects 2 economic data points:
    1. Real estate cost per square foot
    2. Neighborhood economic stability index
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.google_maps_api_key
        self.real_estate_api_key = self.settings.real_estate_api_key
        
    async def collect(self, address: str) -> Dict[str, Any]:
        """
        Gather economic indicators for location
        
        Args:
            address: Full street address
            
        Returns:
            Dictionary with economic metrics
        """
        try:
            # Step 1: Geocode address
            coordinates = await self._geocode_address(address)
            if not coordinates:
                return self._error_response("Failed to geocode address")
            
            lat, lng = coordinates
            
            # Step 2: Get real estate costs
            real_estate_cost = await self._get_real_estate_cost(lat, lng, address)
            
            # Step 3: Calculate economic stability
            stability_index = await self._calculate_stability_index(lat, lng)
            
            return {
                "success": True,
                "address": address,
                "coordinates": {"lat": lat, "lng": lng},
                "real_estate_cost_per_sqft": real_estate_cost,
                "economic_stability_index": stability_index,
                "data_source": "Google Maps API, Real Estate APIs"
            }
            
        except Exception as e:
            logger.error(f"Economic data collection error: {e}")
            return self._error_response(str(e))
    
    async def _geocode_address(self, address: str) -> tuple[float, float] | None:
        """Convert address to coordinates and extract location details"""
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": address,
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
            
            return None
            
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    async def _get_real_estate_cost(
        self,
        lat: float,
        lng: float,
        address: str
    ) -> float:
        """
        Get real estate cost per square foot
        
        Note: In production, integrate with:
        - Zillow API
        - Realtor.com API
        - Redfin API
        - Local MLS data
        
        For now, using estimation based on area characteristics
        """
        try:
            # If real estate API is configured, use it
            if self.real_estate_api_key and self.settings.real_estate_api_base_url:
                return await self._fetch_real_estate_api(lat, lng, address)
            
            # Otherwise, estimate based on location characteristics
            cost_estimate = await self._estimate_real_estate_cost(lat, lng)
            
            return cost_estimate
            
        except Exception as e:
            logger.error(f"Real estate cost calculation error: {e}")
            return 150.0  # Default moderate cost
    
    async def _fetch_real_estate_api(
        self,
        lat: float,
        lng: float,
        address: str
    ) -> float:
        """
        Fetch real estate data from API
        (Implementation placeholder for when API is available)
        """
        try:
            # Example API call structure (actual implementation depends on provider)
            url = f"{self.settings.real_estate_api_base_url}/property/details"
            params = {
                "address": address,
                "api_key": self.real_estate_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            # Extract price per square foot
            price_per_sqft = data.get("pricePerSqft", 150.0)
            
            return round(price_per_sqft, 2)
            
        except Exception as e:
            logger.error(f"Real estate API fetch error: {e}")
            return 150.0
    
    async def _estimate_real_estate_cost(self, lat: float, lng: float) -> float:
        """
        Estimate real estate cost based on area characteristics
        Uses Google Places to identify neighborhood quality indicators
        """
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            # High-value indicators
            premium_types = ["shopping_mall", "university", "hospital"]
            premium_count = 0
            
            for place_type in premium_types:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": 3218,  # 2 miles
                    "type": place_type,
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        if data["status"] == "OK":
                            results = data.get("results", [])
                            # Weight by rating
                            for result in results:
                                rating = result.get("rating", 3.0)
                                if rating >= 4.0:
                                    premium_count += 1
            
            # Base cost for urban/suburban area
            base_cost = 120.0
            
            # Adjust based on premium amenities
            # Each premium amenity adds $15-30/sqft
            adjusted_cost = base_cost + (premium_count * 20)
            
            # Cap at reasonable range ($50-$400/sqft)
            adjusted_cost = max(50, min(400, adjusted_cost))
            
            return round(adjusted_cost, 2)
            
        except Exception as e:
            logger.error(f"Real estate cost estimation error: {e}")
            return 150.0
    
    async def _calculate_stability_index(self, lat: float, lng: float) -> float:
        """
        Calculate neighborhood economic stability index (0-100, higher is better)
        
        Factors:
        - Presence of established businesses
        - Diversity of commercial activity
        - Quality ratings of local businesses
        - Infrastructure investment indicators
        """
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            # Stability indicators - established business types
            stable_types = ["bank", "grocery_or_supermarket", "pharmacy", "restaurant"]
            
            stability_score = 50  # Start at moderate
            
            for place_type in stable_types:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": 1609,  # 1 mile
                    "type": place_type,
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    if response.status_code != 200:
                        continue
                    
                    data = response.json()
                    if data["status"] != "OK":
                        continue
                    
                    results = data.get("results", [])
                    
                    # Count high-quality establishments
                    quality_count = sum(
                        1 for r in results
                        if r.get("rating", 0) >= 4.0 and r.get("user_ratings_total", 0) >= 50
                    )
                    
                    # Each category with quality establishments adds to stability
                    if quality_count > 0:
                        stability_score += 8
                    
                    # Diversity bonus (more establishments = more stable)
                    if len(results) >= 5:
                        stability_score += 2
            
            # Check for recent development (new construction)
            # This could indicate investment in the area
            development_bonus = await self._check_development_activity(lat, lng)
            stability_score += development_bonus
            
            # Normalize to 0-100
            stability_score = max(0, min(100, stability_score))
            
            return round(stability_score, 1)
            
        except Exception as e:
            logger.error(f"Stability index calculation error: {e}")
            return 50.0  # Default to moderate
    
    async def _check_development_activity(self, lat: float, lng: float) -> float:
        """
        Check for development/construction activity as stability indicator
        Returns bonus points (0-10)
        """
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 1609,  # 1 mile
                "keyword": "new construction",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                if response.status_code != 200:
                    return 0.0
                
                data = response.json()
                if data["status"] != "OK":
                    return 0.0
                
                results = data.get("results", [])
                
                # Moderate development is good (3-10 projects)
                # Too much might indicate instability
                # Too little might indicate stagnation
                development_count = len(results)
                
                if 3 <= development_count <= 10:
                    return 5.0  # Optimal development
                elif 1 <= development_count < 3:
                    return 2.0  # Some development
                elif development_count > 10:
                    return 1.0  # Too much disruption
                else:
                    return 0.0  # No visible development
                    
        except Exception as e:
            logger.error(f"Development activity check error: {e}")
            return 0.0
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            "success": False,
            "error": error,
            "real_estate_cost_per_sqft": 0.0,
            "economic_stability_index": 0.0
        }
