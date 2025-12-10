"""
Accessibility Data Collector
Evaluates location accessibility using Google Maps APIs
"""

import httpx
from typing import Dict, Any
from loguru import logger

from app.config import get_settings


class AccessibilityCollector:
    """
    Collects 3 accessibility data points:
    1. Public transit proximity score
    2. Highway access distance
    3. Parking availability score
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.distance_matrix_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def collect(self, address: str) -> Dict[str, Any]:
        """
        Evaluate accessibility metrics for location
        
        Args:
            address: Full street address
            
        Returns:
            Dictionary with accessibility metrics
        """
        try:
            # Step 1: Geocode address
            coordinates = await self._geocode_address(address)
            if not coordinates:
                return self._error_response("Failed to geocode address")
            
            lat, lng = coordinates
            
            # Step 2: Find public transit options
            transit_score = await self._calculate_transit_score(lat, lng)
            
            # Step 3: Find nearest highway
            highway_distance = await self._find_nearest_highway(lat, lng)
            
            # Step 4: Assess parking availability
            parking_score = await self._assess_parking(lat, lng)
            
            return {
                "success": True,
                "address": address,
                "coordinates": {"lat": lat, "lng": lng},
                "public_transit_score": transit_score,
                "highway_distance_miles": highway_distance,
                "parking_availability_score": parking_score,
                "data_source": "Google Maps Platform APIs"
            }
            
        except Exception as e:
            logger.error(f"Accessibility evaluation error: {e}")
            return self._error_response(str(e))
    
    async def _geocode_address(self, address: str) -> tuple[float, float] | None:
        """Convert address to coordinates"""
        try:
            url = f"{self.base_url}/geocode/json"
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
    
    async def _calculate_transit_score(self, lat: float, lng: float) -> float:
        """
        Calculate public transit accessibility score (0-100)
        Based on proximity and frequency of transit options
        """
        try:
            # Search for transit stations within 1 mile
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 1609,  # 1 mile in meters
                "type": "transit_station",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            if data["status"] != "OK":
                return 0.0
            
            stations = data.get("results", [])
            
            if not stations:
                return 0.0
            
            # Calculate score based on:
            # - Number of stations (more is better)
            # - Proximity of nearest station (closer is better)
            # - Station ratings (higher is better)
            
            # Find nearest station
            nearest_distance = min(
                self._haversine_distance(lat, lng, s["geometry"]["location"]["lat"], s["geometry"]["location"]["lng"])
                for s in stations
            )
            
            # Distance score (0-50 points)
            # 0 miles = 50 points, 1 mile = 0 points
            distance_score = max(0, 50 * (1 - nearest_distance))
            
            # Quantity score (0-30 points)
            # 1 station = 10, 3+ stations = 30
            quantity_score = min(30, len(stations) * 10)
            
            # Quality score based on avg rating (0-20 points)
            avg_rating = sum(s.get("rating", 3.0) for s in stations[:5]) / min(len(stations), 5)
            quality_score = (avg_rating / 5.0) * 20
            
            transit_score = distance_score + quantity_score + quality_score
            
            return round(min(100, transit_score), 1)
            
        except Exception as e:
            logger.error(f"Transit score calculation error: {e}")
            return 50.0  # Default to moderate
    
    async def _find_nearest_highway(self, lat: float, lng: float) -> float:
        """
        Find distance to nearest highway/major road
        Returns distance in miles
        """
        try:
            # Use Directions API to find route to a point slightly north
            # This will reveal nearby highways in the route
            url = f"{self.base_url}/directions/json"
            
            # Create a point 5 miles north as destination
            dest_lat = lat + 0.0725  # ~5 miles north
            
            params = {
                "origin": f"{lat},{lng}",
                "destination": f"{dest_lat},{lng}",
                "key": self.google_api_key,
                "alternatives": "true"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            if data["status"] != "OK" or not data.get("routes"):
                return 5.0  # Default estimate
            
            # Parse route for highway mentions
            route = data["routes"][0]
            steps = route["legs"][0]["steps"]
            
            # Find first step mentioning highway/interstate
            highway_keywords = ["I-", "US-", "Highway", "Freeway", "Interstate"]
            
            for i, step in enumerate(steps):
                instructions = step.get("html_instructions", "")
                if any(keyword in instructions for keyword in highway_keywords):
                    # Highway found in step i
                    # Sum distance of steps before this
                    distance_meters = sum(steps[j]["distance"]["value"] for j in range(i))
                    distance_miles = distance_meters / 1609.34
                    return round(distance_miles, 2)
            
            # No highway found in route - likely distant
            return 10.0
            
        except Exception as e:
            logger.error(f"Highway distance calculation error: {e}")
            return 5.0  # Default estimate
    
    async def _assess_parking(self, lat: float, lng: float) -> float:
        """
        Assess parking availability (0-100 score)
        Based on nearby parking facilities and area characteristics
        """
        try:
            # Search for parking facilities within 500m
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 500,  # 500 meters
                "type": "parking",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            parking_facilities = data.get("results", []) if data["status"] == "OK" else []
            
            # Also check place details for original location
            # to see if it has parking info
            place_info = await self._get_place_details(lat, lng)
            
            # Calculate parking score
            # Base score from facilities (0-60 points)
            facilities_score = min(60, len(parking_facilities) * 15)
            
            # Bonus from place details (0-40 points)
            detail_score = 0
            if place_info:
                # Check for parking-related keywords in place types
                place_types = place_info.get("types", [])
                if "parking" in place_types:
                    detail_score += 20
                
                # Check vicinity description
                vicinity = place_info.get("vicinity", "").lower()
                if "parking" in vicinity:
                    detail_score += 20
            
            parking_score = facilities_score + detail_score
            
            return round(min(100, parking_score), 1)
            
        except Exception as e:
            logger.error(f"Parking assessment error: {e}")
            return 50.0  # Default to moderate
    
    async def _get_place_details(self, lat: float, lng: float) -> Dict[str, Any] | None:
        """Get place details for coordinates"""
        try:
            # First, find place_id for these coordinates
            url = f"{self.base_url}/geocode/json"
            params = {
                "latlng": f"{lat},{lng}",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                return data["results"][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Place details error: {e}")
            return None
    
    def _haversine_distance(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """
        Calculate distance between two points in miles using Haversine formula
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 3959  # Earth's radius in miles
        
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            "success": False,
            "error": error,
            "public_transit_score": 0.0,
            "highway_distance_miles": 0.0,
            "parking_availability_score": 0.0
        }
