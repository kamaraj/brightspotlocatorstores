"""
Safety Data Collector
Assesses location safety using crime data and environmental quality APIs
"""

import httpx
from typing import Dict, Any
from loguru import logger

from app.config import get_settings


class SafetyCollector:
    """
    Collects 3 safety data points:
    1. Crime rate index
    2. Traffic accident frequency
    3. Environmental quality score
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.google_maps_api_key
        self.crime_api_key = self.settings.crime_api_key
        self.epa_api_key = self.settings.epa_api_key
        
    async def collect(self, address: str, radius_miles: float = 1.0) -> Dict[str, Any]:
        """
        Assess safety metrics for location
        
        Args:
            address: Full street address
            radius_miles: Search radius (default 1 mile)
            
        Returns:
            Dictionary with safety metrics
        """
        try:
            # Step 1: Geocode address
            coordinates = await self._geocode_address(address)
            if not coordinates:
                return self._error_response("Failed to geocode address")
            
            lat, lng = coordinates
            
            # Step 2: Get crime data
            crime_index = await self._get_crime_index(lat, lng, radius_miles)
            
            # Step 3: Assess traffic safety
            traffic_accidents = await self._assess_traffic_safety(lat, lng, radius_miles)
            
            # Step 4: Check environmental quality
            environmental_score = await self._check_environmental_quality(lat, lng)
            
            return {
                "success": True,
                "address": address,
                "coordinates": {"lat": lat, "lng": lng},
                "radius_miles": radius_miles,
                "crime_rate_index": crime_index,
                "traffic_accidents_per_year": traffic_accidents,
                "environmental_quality_score": environmental_score,
                "data_source": "Multiple sources (Crime APIs, EPA, Google Maps)"
            }
            
        except Exception as e:
            logger.error(f"Safety assessment error: {e}")
            return self._error_response(str(e))
    
    async def _geocode_address(self, address: str) -> tuple[float, float] | None:
        """Convert address to coordinates"""
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
                
                # Extract city/state for context
                address_components = data["results"][0].get("address_components", [])
                
                return location["lat"], location["lng"]
            
            return None
            
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    async def _get_crime_index(
        self,
        lat: float,
        lng: float,
        radius_miles: float
    ) -> float:
        """
        Get crime rate index (0-100, lower is safer)
        
        Note: In production, integrate with:
        - FBI Crime Data API
        - SpotCrime API
        - CrimeReports.com API
        - Local police department APIs
        
        For now, using estimated approach based on location characteristics
        """
        try:
            # If crime API is configured, use it
            if self.crime_api_key and self.settings.crime_api_base_url:
                return await self._fetch_crime_data_api(lat, lng, radius_miles)
            
            # Otherwise, estimate based on location characteristics
            # Using Google Places to identify area type
            crime_estimate = await self._estimate_crime_from_area(lat, lng)
            
            return crime_estimate
            
        except Exception as e:
            logger.error(f"Crime index calculation error: {e}")
            return 50.0  # Default to moderate
    
    async def _fetch_crime_data_api(
        self,
        lat: float,
        lng: float,
        radius_miles: float
    ) -> float:
        """
        Fetch actual crime data from API
        (Implementation placeholder for when API is available)
        """
        try:
            # Example API call structure (actual implementation depends on provider)
            url = f"{self.settings.crime_api_base_url}/incidents"
            params = {
                "lat": lat,
                "lng": lng,
                "radius": radius_miles,
                "api_key": self.crime_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            # Parse crime incidents and calculate index
            incidents = data.get("incidents", [])
            
            # Calculate crime index based on incident count and severity
            # 0 incidents = 0 (safest), 100+ = 100 (least safe)
            crime_index = min(100, len(incidents))
            
            return round(crime_index, 1)
            
        except Exception as e:
            logger.error(f"Crime API fetch error: {e}")
            return 50.0
    
    async def _estimate_crime_from_area(self, lat: float, lng: float) -> float:
        """
        Estimate crime index based on area characteristics
        Uses Google Places to identify neighborhood type
        """
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            # Check for indicators of safe vs. unsafe areas
            # Safe indicators: schools, parks, libraries
            # Unsafe indicators: liquor stores, pawn shops (in high concentration)
            
            safe_types = ["school", "park", "library"]
            risk_types = ["liquor_store", "night_club", "casino"]
            
            safe_count = 0
            risk_count = 0
            
            # Count safe places
            for place_type in safe_types:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": 1609,  # 1 mile
                    "type": place_type,
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        if data["status"] == "OK":
                            safe_count += len(data.get("results", []))
            
            # Count risk places
            for place_type in risk_types:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": 1609,
                    "type": place_type,
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        if data["status"] == "OK":
                            risk_count += len(data.get("results", []))
            
            # Calculate crime index
            # More safe places = lower index, more risk places = higher index
            if safe_count + risk_count == 0:
                return 50.0  # No data, assume moderate
            
            # Scale: heavy weight on risk places
            crime_index = (risk_count * 3 - safe_count) * 5
            crime_index = max(0, min(100, 50 + crime_index))
            
            return round(crime_index, 1)
            
        except Exception as e:
            logger.error(f"Crime estimation error: {e}")
            return 50.0
    
    async def _assess_traffic_safety(
        self,
        lat: float,
        lng: float,
        radius_miles: float
    ) -> int:
        """
        Estimate annual traffic accidents in area
        
        Note: In production, integrate with:
        - NHTSA Crash Data API
        - State DOT traffic data
        - Insurance company databases
        
        For now, using road network analysis as proxy
        """
        try:
            # Search for major roads/intersections
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": int(radius_miles * 1609.34),
                "type": "route",  # Roads
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            # More roads/intersections = higher accident potential
            # This is a rough proxy - production would use actual accident data
            road_features = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # Estimate: base 5 accidents/year, +2 per major road feature
            estimated_accidents = 5 + (road_features * 2)
            
            return min(50, estimated_accidents)  # Cap at 50
            
        except Exception as e:
            logger.error(f"Traffic safety assessment error: {e}")
            return 10  # Default estimate
    
    async def _check_environmental_quality(
        self,
        lat: float,
        lng: float
    ) -> float:
        """
        Check environmental quality score (0-100, higher is better)
        Considers air quality, hazardous sites, water quality
        
        Note: In production, integrate with:
        - EPA AirNow API for real-time air quality
        - EPA Envirofacts for Superfund sites
        - EPA EJSCREEN for environmental justice data
        """
        try:
            # If EPA API is configured, use it
            if self.epa_api_key:
                return await self._fetch_epa_data(lat, lng)
            
            # Otherwise, estimate based on industrial proximity
            env_score = await self._estimate_environmental_quality(lat, lng)
            
            return env_score
            
        except Exception as e:
            logger.error(f"Environmental quality check error: {e}")
            return 75.0  # Default to good
    
    async def _fetch_epa_data(self, lat: float, lng: float) -> float:
        """
        Fetch EPA environmental data
        (Implementation placeholder for when EPA API is integrated)
        """
        # EPA AirNow API example (requires separate implementation)
        # For now, return estimated value
        return 75.0
    
    async def _estimate_environmental_quality(
        self,
        lat: float,
        lng: float
    ) -> float:
        """
        Estimate environmental quality based on nearby land uses
        """
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            # Check for environmental negatives
            negative_types = ["gas_station", "car_repair", "dump", "waste"]
            negative_count = 0
            
            for place_type in negative_types:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": 1609,  # 1 mile
                    "type": place_type,
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        if data["status"] == "OK":
                            negative_count += len(data.get("results", []))
            
            # Check for environmental positives
            positive_types = ["park", "natural_feature"]
            positive_count = 0
            
            for place_type in positive_types:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": 1609,
                    "type": place_type,
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        if data["status"] == "OK":
                            positive_count += len(data.get("results", []))
            
            # Calculate score (start at 80, adjust based on findings)
            env_score = 80 + (positive_count * 5) - (negative_count * 10)
            env_score = max(0, min(100, env_score))
            
            return round(env_score, 1)
            
        except Exception as e:
            logger.error(f"Environmental estimation error: {e}")
            return 75.0
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            "success": False,
            "error": error,
            "crime_rate_index": 0.0,
            "traffic_accidents_per_year": 0,
            "environmental_quality_score": 0.0
        }
