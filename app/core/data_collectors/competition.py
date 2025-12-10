"""
Competition Data Collector
Analyzes childcare center competition using Google Places API
"""

import httpx
from typing import Dict, Any, List
from loguru import logger

from app.config import get_settings


class CompetitionCollector:
    """
    Collects 3 competition data points:
    1. Number of existing childcare centers within radius
    2. Average capacity utilization estimate
    3. Market gap score (demand vs supply)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.places_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def collect(self, address: str, radius_miles: float = 2.0) -> Dict[str, Any]:
        """
        Analyze competition around location
        
        Args:
            address: Full street address
            radius_miles: Search radius (default 2 miles)
            
        Returns:
            Dictionary with competition metrics
        """
        try:
            # Step 1: Geocode address
            coordinates = await self._geocode_address(address)
            if not coordinates:
                return self._error_response("Failed to geocode address")
            
            lat, lng = coordinates
            radius_meters = radius_miles * 1609.34  # Convert miles to meters
            
            # Step 2: Search for childcare centers
            centers = await self._search_childcare_centers(lat, lng, radius_meters)
            
            # Step 3: Calculate competition metrics
            metrics = self._calculate_metrics(centers, radius_miles)
            
            return {
                "success": True,
                "address": address,
                "coordinates": {"lat": lat, "lng": lng},
                "radius_miles": radius_miles,
                **metrics
            }
            
        except Exception as e:
            logger.error(f"Competition analysis error: {e}")
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
    
    async def _search_childcare_centers(
        self,
        lat: float,
        lng: float,
        radius_meters: float
    ) -> List[Dict[str, Any]]:
        """Search for childcare centers using Google Places API"""
        try:
            # Places API Nearby Search
            url = f"{self.base_url}/place/nearbysearch/json"
            
            centers = []
            next_page_token = None
            
            # Keywords for childcare centers
            keywords = ["daycare", "childcare", "child care", "preschool"]
            
            for keyword in keywords:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": int(radius_meters),
                    "keyword": keyword,
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=15.0)
                    response.raise_for_status()
                    data = response.json()
                
                if data["status"] == "OK":
                    results = data.get("results", [])
                    centers.extend(results)
                    
                    # Handle pagination (up to 60 results per keyword)
                    next_page_token = data.get("next_page_token")
                    if next_page_token:
                        # Note: Would need to implement pagination with delay
                        # Google requires ~2 sec wait before next_page_token is valid
                        pass
            
            # Remove duplicates based on place_id
            unique_centers = {center["place_id"]: center for center in centers}
            
            logger.info(f"Found {len(unique_centers)} childcare centers")
            return list(unique_centers.values())
            
        except Exception as e:
            logger.error(f"Places search error: {e}")
            return []
    
    def _calculate_metrics(
        self,
        centers: List[Dict[str, Any]],
        radius_miles: float
    ) -> Dict[str, Any]:
        """Calculate competition metrics from centers data"""
        
        centers_count = len(centers)
        
        # Estimate average capacity (industry standard: 60-80 children per center)
        avg_capacity_per_center = 70
        total_capacity = centers_count * avg_capacity_per_center
        
        # Estimate current utilization (industry average: 75-85%)
        # Use rating as proxy - higher rated centers likely fuller
        if centers:
            avg_rating = sum(c.get("rating", 4.0) for c in centers) / len(centers)
            # Scale rating (0-5) to utilization (60-95%)
            avg_utilization = 60 + (avg_rating / 5.0) * 35
        else:
            avg_utilization = 0.0
        
        # Calculate market gap score
        # Estimate demand: ~8% of population needs childcare (industry stat)
        # Assume 250 children per sq mile (would come from demographics in production)
        area_sq_miles = 3.14159 * (radius_miles ** 2)  # Circle area
        estimated_children = 250 * area_sq_miles
        estimated_demand = estimated_children * 0.08  # 8% need childcare
        
        current_supply = total_capacity * (avg_utilization / 100)
        gap = estimated_demand - current_supply
        
        # Market gap score (0-100)
        # Positive gap = opportunity, Negative gap = oversaturated
        if estimated_demand > 0:
            gap_ratio = gap / estimated_demand
            # Scale to 0-100 (0 = oversaturated, 50 = balanced, 100 = high opportunity)
            market_gap_score = max(0, min(100, 50 + (gap_ratio * 50)))
        else:
            market_gap_score = 50.0  # Default to balanced
        
        return {
            "childcare_centers_count": centers_count,
            "avg_capacity_utilization": round(avg_utilization, 1),
            "market_gap_score": round(market_gap_score, 1),
            "estimated_total_capacity": total_capacity,
            "estimated_demand": int(estimated_demand),
            "estimated_gap": int(gap),
            "centers_per_sq_mile": round(centers_count / area_sq_miles, 2) if area_sq_miles > 0 else 0,
            "data_source": "Google Places API",
            "centers_details": [
                {
                    "name": c.get("name"),
                    "rating": c.get("rating"),
                    "user_ratings_total": c.get("user_ratings_total"),
                    "vicinity": c.get("vicinity")
                }
                for c in centers[:10]  # Top 10 centers
            ]
        }
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            "success": False,
            "error": error,
            "childcare_centers_count": 0,
            "avg_capacity_utilization": 0.0,
            "market_gap_score": 0.0
        }
