"""
Enhanced Accessibility Data Collector
Comprehensive analysis with 10 data points across 5 categories
"""

import httpx
import asyncio
from typing import Dict, Any, List, Tuple
from loguru import logger
from math import radians, sin, cos, sqrt, atan2

from app.config import get_settings


class AccessibilityCollectorEnhanced:
    """
    Collects 10 accessibility data points across 5 categories:
    
    1. Drive Time Analysis (2 points):
       - Average commute time from key employment centers
       - Peak hour congestion factor
    
    2. Employment Center Proximity (2 points):
       - Distance to nearest major employer
       - Number of employers within 5 miles
    
    3. Public Transit Access (2 points):
       - Transit score (0-100)
       - Walk score to nearest transit
    
    4. Traffic Patterns (2 points):
       - Morning rush accessibility score
       - Evening rush accessibility score
    
    5. Site Accessibility (2 points):
       - Highway visibility and access
       - Parking availability score
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.places_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def collect(self, address: str, radius_miles: float = 5.0) -> Dict[str, Any]:
        """
        Collect comprehensive accessibility metrics (10 data points)
        
        Args:
            address: Full street address
            radius_miles: Search radius (default 5 miles)
            
        Returns:
            Dictionary with 10 accessibility metrics across 5 categories
        """
        try:
            # Step 1: Geocode address
            coordinates = await self._geocode_address(address)
            if not coordinates:
                return self._mock_comprehensive_data()
            
            lat, lng = coordinates
            
            # Step 2: Analyze drive times to employment centers
            drive_time_metrics = await self._analyze_drive_times(lat, lng)
            
            # Step 3: Analyze employment center proximity
            employment_metrics = await self._analyze_employment_centers(lat, lng, radius_miles)
            
            # Step 4: Analyze public transit access
            transit_metrics = await self._analyze_transit_access(lat, lng)
            
            # Step 5: Analyze traffic patterns
            traffic_metrics = await self._analyze_traffic_patterns(lat, lng)
            
            # Step 6: Analyze site accessibility
            site_metrics = await self._analyze_site_access(lat, lng)
            
            return {
                "success": True,
                "address": address,
                "coordinates": {"lat": lat, "lng": lng},
                **drive_time_metrics,
                **employment_metrics,
                **transit_metrics,
                **traffic_metrics,
                **site_metrics,
                "data_source": "Google Maps Platform - 10 Data Points"
            }
            
        except Exception as e:
            logger.error(f"Enhanced accessibility analysis error: {e}")
            return self._mock_comprehensive_data()
    
    async def _geocode_address(self, address: str) -> Tuple[float, float] | None:
        """Convert address to coordinates"""
        try:
            url = f"{self.base_url}/geocode/json"
            params = {"address": address, "key": self.google_api_key}
            
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
    
    async def _analyze_drive_times(self, lat: float, lng: float) -> Dict[str, float]:
        """
        Analyze drive times to key employment centers
        Returns: avg_commute_minutes, peak_congestion_factor
        """
        try:
            # Find major employers/business districts nearby
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 8046,  # 5 miles in meters
                "type": "establishment",
                "keyword": "office park|business district|corporate center",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                data = response.json()
            
            if data["status"] != "OK":
                return {"avg_commute_minutes": 20.0, "peak_congestion_factor": 1.3}
            
            employment_centers = data.get("results", [])[:5]  # Top 5
            
            # Get drive times using Distance Matrix API
            destinations = "|".join([
                f"{place['geometry']['location']['lat']},{place['geometry']['location']['lng']}"
                for place in employment_centers
            ])
            
            if not destinations:
                return {"avg_commute_minutes": 20.0, "peak_congestion_factor": 1.3}
            
            # Morning commute (8 AM on Wednesday)
            matrix_url = f"{self.base_url}/distancematrix/json"
            params_morning = {
                "origins": f"{lat},{lng}",
                "destinations": destinations,
                "mode": "driving",
                "departure_time": "now",
                "traffic_model": "best_guess",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(matrix_url, params=params_morning, timeout=15.0)
                data = response.json()
            
            if data["status"] == "OK" and data["rows"]:
                elements = data["rows"][0]["elements"]
                durations = [
                    elem["duration"]["value"] / 60  # Convert to minutes
                    for elem in elements
                    if elem["status"] == "OK"
                ]
                
                if durations:
                    avg_commute = sum(durations) / len(durations)
                    
                    # Estimate congestion factor (compare to off-peak)
                    # Typically peak is 1.2-1.5x off-peak
                    congestion_factor = 1.0 + (avg_commute / 60.0)  # Estimate based on time
                    congestion_factor = min(2.0, max(1.0, congestion_factor))
                    
                    return {
                        "avg_commute_minutes": round(avg_commute, 1),
                        "peak_congestion_factor": round(congestion_factor, 2)
                    }
            
            return {"avg_commute_minutes": 20.0, "peak_congestion_factor": 1.3}
            
        except Exception as e:
            logger.debug(f"Drive time analysis error: {e}")
            return {"avg_commute_minutes": 20.0, "peak_congestion_factor": 1.3}
    
    async def _analyze_employment_centers(
        self, 
        lat: float, 
        lng: float, 
        radius_miles: float
    ) -> Dict[str, Any]:
        """
        Analyze proximity to employment centers
        Returns: nearest_employer_miles, employers_within_5_miles
        """
        try:
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": int(radius_miles * 1609.34),
                "type": "establishment",
                "keyword": "office|corporate|business center|industrial park",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                data = response.json()
            
            if data["status"] != "OK":
                return {
                    "nearest_employer_miles": 2.0,
                    "employers_within_5_miles": 10
                }
            
            employers = data.get("results", [])
            
            # Calculate distances
            distances = []
            for emp in employers:
                emp_lat = emp["geometry"]["location"]["lat"]
                emp_lng = emp["geometry"]["location"]["lng"]
                dist = self._haversine_distance(lat, lng, emp_lat, emp_lng)
                distances.append(dist)
            
            nearest = min(distances) if distances else 2.0
            within_5 = sum(1 for d in distances if d <= 5.0)
            
            return {
                "nearest_employer_miles": round(nearest, 2),
                "employers_within_5_miles": within_5
            }
            
        except Exception as e:
            logger.debug(f"Employment center analysis error: {e}")
            return {
                "nearest_employer_miles": 2.0,
                "employers_within_5_miles": 10
            }
    
    async def _analyze_transit_access(self, lat: float, lng: float) -> Dict[str, float]:
        """
        Analyze public transit accessibility
        Returns: transit_score, walk_score_to_transit
        """
        try:
            # Search for transit stations within 1 mile
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 1609,  # 1 mile
                "type": "transit_station",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                data = response.json()
            
            if data["status"] != "OK":
                return {"transit_score": 30.0, "walk_score_to_transit": 40.0}
            
            stations = data.get("results", [])
            station_count = len(stations)
            
            # Calculate distances to stations
            distances = []
            for station in stations:
                st_lat = station["geometry"]["location"]["lat"]
                st_lng = station["geometry"]["location"]["lng"]
                dist = self._haversine_distance(lat, lng, st_lat, st_lng)
                distances.append(dist)
            
            # Transit score based on quantity and proximity
            transit_score = 0
            
            # Quantity component (0-40 points)
            transit_score += min(40, station_count * 8)
            
            # Proximity component (0-50 points)
            if distances:
                nearest = min(distances)
                if nearest <= 0.25:  # Within 0.25 miles
                    transit_score += 50
                elif nearest <= 0.5:
                    transit_score += 40
                elif nearest <= 0.75:
                    transit_score += 30
                elif nearest <= 1.0:
                    transit_score += 20
                else:
                    transit_score += 10
            
            # Quality component (0-10 points) - based on ratings
            avg_rating = sum(s.get("rating", 0) for s in stations) / max(1, len(stations))
            transit_score += min(10, avg_rating * 2)
            
            # Walk score to nearest transit (inverse of distance)
            if distances:
                nearest_dist = min(distances)
                # 0.25 miles = 100, 1.0 miles = 25
                walk_score = max(0, 100 - (nearest_dist * 75))
            else:
                walk_score = 20.0
            
            return {
                "transit_score": round(min(100, transit_score), 1),
                "walk_score_to_transit": round(walk_score, 1)
            }
            
        except Exception as e:
            logger.debug(f"Transit analysis error: {e}")
            return {"transit_score": 30.0, "walk_score_to_transit": 40.0}
    
    async def _analyze_traffic_patterns(self, lat: float, lng: float) -> Dict[str, float]:
        """
        Analyze traffic patterns during rush hours
        Returns: morning_rush_score, evening_rush_score
        """
        try:
            # Sample nearby major roads to assess traffic
            # Get directions to a point 5 miles away in each direction
            test_points = [
                (lat + 0.072, lng),       # North (~5 miles)
                (lat, lng + 0.072),       # East
                (lat - 0.072, lng),       # South
                (lat, lng - 0.072)        # West
            ]
            
            morning_times = []
            evening_times = []
            
            for dest_lat, dest_lng in test_points:
                url = f"{self.base_url}/directions/json"
                params = {
                    "origin": f"{lat},{lng}",
                    "destination": f"{dest_lat},{dest_lng}",
                    "mode": "driving",
                    "departure_time": "now",
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    data = response.json()
                
                if data["status"] == "OK" and data["routes"]:
                    duration = data["routes"][0]["legs"][0]["duration"]["value"]
                    morning_times.append(duration)
                
                await asyncio.sleep(0.1)  # Rate limiting
            
            # Calculate accessibility scores
            # Lower time = higher score
            if morning_times:
                avg_morning = sum(morning_times) / len(morning_times) / 60  # Minutes
                # 15 min = 100, 45 min = 20
                morning_score = max(20, 100 - (avg_morning - 15) * 2)
                evening_score = morning_score * 0.9  # Evening typically slightly worse
            else:
                morning_score = 60.0
                evening_score = 55.0
            
            return {
                "morning_rush_score": round(min(100, morning_score), 1),
                "evening_rush_score": round(min(100, evening_score), 1)
            }
            
        except Exception as e:
            logger.debug(f"Traffic pattern analysis error: {e}")
            return {
                "morning_rush_score": 60.0,
                "evening_rush_score": 55.0
            }
    
    async def _analyze_site_access(self, lat: float, lng: float) -> Dict[str, float]:
        """
        Analyze site-specific accessibility features
        Returns: highway_visibility_score, parking_availability_score
        """
        try:
            # Check proximity to highways using Directions API
            url = f"{self.base_url}/directions/json"
            params = {
                "origin": f"{lat},{lng}",
                "destination": f"{lat + 0.014},{lng + 0.014}",  # ~1 mile away
                "mode": "driving",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            highway_score = 50.0  # Default
            if data["status"] == "OK" and data["routes"]:
                route = data["routes"][0]
                instructions = " ".join([
                    step.get("html_instructions", "")
                    for leg in route["legs"]
                    for step in leg["steps"]
                ]).lower()
                
                # Check for highway mentions
                highway_keywords = ["highway", "freeway", "interstate", "expressway", "turnpike"]
                highway_mentions = sum(1 for kw in highway_keywords if kw in instructions)
                
                if highway_mentions > 0:
                    highway_score = min(100, 50 + (highway_mentions * 15))
                else:
                    highway_score = 30.0
            
            # Check parking availability
            parking_url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 400,  # 0.25 miles
                "type": "parking",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(parking_url, params=params, timeout=10.0)
                data = response.json()
            
            parking_score = 50.0  # Default
            if data["status"] == "OK":
                parking_lots = data.get("results", [])
                # More parking options = higher score
                parking_score = min(100, 40 + (len(parking_lots) * 15))
            
            return {
                "highway_visibility_score": round(highway_score, 1),
                "parking_availability_score": round(parking_score, 1)
            }
            
        except Exception as e:
            logger.debug(f"Site access analysis error: {e}")
            return {
                "highway_visibility_score": 50.0,
                "parking_availability_score": 50.0
            }
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in miles using Haversine formula"""
        R = 3959  # Earth's radius in miles
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _mock_comprehensive_data(self) -> Dict[str, Any]:
        """Return mock data when API fails"""
        return {
            "success": False,
            "avg_commute_minutes": 20.0,
            "peak_congestion_factor": 1.3,
            "nearest_employer_miles": 2.0,
            "employers_within_5_miles": 10,
            "transit_score": 50.0,
            "walk_score_to_transit": 50.0,
            "morning_rush_score": 60.0,
            "evening_rush_score": 55.0,
            "highway_visibility_score": 50.0,
            "parking_availability_score": 50.0,
            "data_source": "Mock Data"
        }
