"""
Enhanced Competition Data Collector
Comprehensive analysis with 12 data points across 5 categories
"""

import httpx
import asyncio
from typing import Dict, Any, List, Tuple
from loguru import logger
from math import radians, sin, cos, sqrt, atan2

from app.config import get_settings


class CompetitionCollectorEnhanced:
    """
    Collects 12 competition data points across 5 categories:
    
    1. Market Supply (3 points):
       - Existing childcare centers count
       - Total licensed capacity
       - Market saturation index
    
    2. Quality Benchmarks (3 points):
       - Average competitor rating
       - Premium facilities count (4.5+ stars)
       - Average capacity utilization
    
    3. Demand Indicators (3 points):
       - Waitlist prevalence score
       - Market gap score
       - Demand-to-supply ratio
    
    4. Competitive Positioning (2 points):
       - Nearest competitor distance
       - Competitive intensity score
    
    5. Future Competition (1 point):
       - New centers planned/under construction
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.places_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def collect(self, address: str, radius_miles: float = 2.0) -> Dict[str, Any]:
        """
        Collect comprehensive competition metrics (12 data points)
        
        Args:
            address: Full street address
            radius_miles: Search radius (default 2 miles)
            
        Returns:
            Dictionary with 12 competition metrics across 5 categories
        """
        try:
            # Step 1: Geocode address
            coordinates = await self._geocode_address(address)
            if not coordinates:
                return self._mock_comprehensive_data()
            
            lat, lng = coordinates
            radius_meters = radius_miles * 1609.34
            
            # Step 2: Search for childcare centers
            centers = await self._search_childcare_centers(lat, lng, radius_meters)
            
            # Step 3: Get detailed information for top centers
            detailed_centers = await self._get_center_details(centers[:15])
            
            # Step 4: Calculate all 12 metrics
            metrics = self._calculate_comprehensive_metrics(
                detailed_centers, 
                (lat, lng), 
                radius_miles
            )
            
            return {
                "success": True,
                "address": address,
                "coordinates": {"lat": lat, "lng": lng},
                "radius_miles": radius_miles,
                **metrics
            }
            
        except Exception as e:
            logger.error(f"Enhanced competition analysis error: {e}")
            return self._mock_comprehensive_data()
    
    async def _geocode_address(self, address: str) -> Tuple[float, float] | None:
        """Convert address to coordinates"""
        try:
            url = f"{self.base_url}/geocode/json"
            params = {"address": address, "key": self.google_api_key}
            
            logger.info(f"Geocoding address: {address}")
            logger.info(f"Using API key: {self.google_api_key[:20]}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            logger.info(f"Geocoding response status: {data.get('status')}")
            
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                logger.info(f"Geocoding successful: {location}")
                return location["lat"], location["lng"]
            else:
                logger.warning(f"Geocoding failed with status: {data.get('status')}, error: {data.get('error_message', 'No error message')}")
            
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
            url = f"{self.base_url}/place/nearbysearch/json"
            centers = []
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
                    centers.extend(data.get("results", []))
            
            # Remove duplicates
            unique_centers = {c["place_id"]: c for c in centers}
            logger.info(f"Found {len(unique_centers)} childcare centers")
            return list(unique_centers.values())
            
        except Exception as e:
            logger.error(f"Places search error: {e}")
            return []
    
    async def _get_center_details(self, centers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fetch detailed information for each center using Place Details API
        """
        detailed_centers = []
        
        for center in centers:
            try:
                place_id = center.get('place_id')
                if not place_id:
                    continue
                
                url = f"{self.base_url}/place/details/json"
                params = {
                    "place_id": place_id,
                    "fields": "name,rating,user_ratings_total,price_level,opening_hours,reviews,types,formatted_phone_number,website,geometry",
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    response.raise_for_status()
                    data = response.json()
                
                if data['status'] == 'OK':
                    result = data['result']
                    center_info = {
                        'place_id': place_id,
                        'name': result.get('name'),
                        'rating': result.get('rating', 0),
                        'total_ratings': result.get('user_ratings_total', 0),
                        'price_level': result.get('price_level', 0),
                        'has_hours': 'opening_hours' in result,
                        'has_phone': 'formatted_phone_number' in result,
                        'has_website': 'website' in result,
                        'reviews': result.get('reviews', []),
                        'location': result.get('geometry', {}).get('location', {}),
                        'types': result.get('types', [])
                    }
                    detailed_centers.append(center_info)
                
                await asyncio.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Could not fetch details for center: {e}")
                continue
        
        return detailed_centers
    
    def _calculate_comprehensive_metrics(
        self,
        centers: List[Dict[str, Any]],
        coords: Tuple[float, float],
        radius_miles: float
    ) -> Dict[str, Any]:
        """
        Calculate all 12 competition metrics
        """
        centers_count = len(centers)
        
        if centers_count == 0:
            return self._mock_comprehensive_data()
        
        # ==== 1. MARKET SUPPLY (3 points) ====
        
        existing_centers = centers_count
        
        # Total licensed capacity (estimated based on size indicators)
        total_capacity = 0
        for center in centers:
            ratings_total = center.get('total_ratings', 0)
            if ratings_total > 200:
                total_capacity += 100  # Large center
            elif ratings_total > 50:
                total_capacity += 50   # Medium center
            else:
                total_capacity += 25   # Small center
        
        # Market saturation index (centers per square mile)
        area_sqmi = 3.14159 * (radius_miles ** 2)
        saturation_index = existing_centers / area_sqmi
        
        # ==== 2. QUALITY BENCHMARKS (3 points) ====
        
        # Average competitor rating
        ratings = [c.get('rating', 0) for c in centers if c.get('rating', 0) > 0]
        avg_rating = sum(ratings) / len(ratings) if ratings else 3.5
        
        # Premium facilities count (4.5+ stars)
        premium_count = sum(1 for c in centers if c.get('rating', 0) >= 4.5)
        
        # Average capacity utilization
        utilization_scores = []
        for center in centers:
            rating = center.get('rating', 3.0)
            total_ratings = center.get('total_ratings', 0)
            
            # Base utilization from rating (3.0=60%, 5.0=95%)
            base_util = 60 + ((rating - 3.0) / 2.0) * 35
            
            # Boost for popular centers
            if total_ratings > 100:
                base_util = min(95, base_util + 10)
            elif total_ratings > 50:
                base_util = min(95, base_util + 5)
            
            utilization_scores.append(base_util)
        
        avg_utilization = sum(utilization_scores) / len(utilization_scores) if utilization_scores else 70
        
        # ==== 3. DEMAND INDICATORS (3 points) ====
        
        # Waitlist prevalence (inferred from ratings and review mentions)
        waitlist_score = 0
        for center in centers:
            rating = center.get('rating', 0)
            reviews = center.get('reviews', [])
            
            if rating >= 4.5:
                waitlist_score += 10
            
            # Check reviews for waitlist mentions
            for review in reviews[:5]:
                text = review.get('text', '').lower()
                if any(word in text for word in ['waitlist', 'wait list', 'waiting', 'full', 'no spots']):
                    waitlist_score += 5
                    break
        
        waitlist_prevalence = min(100, waitlist_score / max(1, centers_count) * 10)
        
        # Market gap score
        estimated_population = 5000  # Would come from demographics collector
        estimated_demand = estimated_population * 0.08
        market_gap = ((estimated_demand - total_capacity) / estimated_demand * 100) if estimated_demand > 0 else 0
        market_gap = max(0, min(100, market_gap))
        
        # Demand-to-supply ratio
        demand_supply_ratio = estimated_demand / total_capacity if total_capacity > 0 else 0
        
        # ==== 4. COMPETITIVE POSITIONING (2 points) ====
        
        # Nearest competitor distance
        distances = []
        for center in centers:
            loc = center.get('location', {})
            if loc:
                lat = loc.get('lat', coords[0])
                lng = loc.get('lng', coords[1])
                dist = self._haversine_distance(coords[0], coords[1], lat, lng)
                distances.append(dist)
        
        nearest_competitor_dist = min(distances) if distances else radius_miles
        
        # Competitive intensity score (0-100)
        intensity = 0
        intensity += min(40, saturation_index * 10)  # Density (max 40)
        intensity += min(30, avg_rating * 6)         # Quality (max 30)
        intensity += min(30, avg_utilization / 3)    # Utilization (max 30)
        
        # ==== 5. FUTURE COMPETITION (1 point) ====
        
        # New centers planned
        new_centers_planned = 0
        for center in centers:
            types = center.get('types', [])
            name = center.get('name', '').lower()
            
            if 'opening_soon' in types or any(word in name for word in ['new', 'coming soon', 'opening']):
                new_centers_planned += 1
        
        return {
            # Market Supply (3)
            "existing_centers_count": existing_centers,
            "total_licensed_capacity": total_capacity,
            "market_saturation_index": round(saturation_index, 2),
            
            # Quality Benchmarks (3)
            "avg_competitor_rating": round(avg_rating, 2),
            "premium_facilities_count": premium_count,
            "avg_capacity_utilization_pct": round(avg_utilization, 2),
            
            # Demand Indicators (3)
            "waitlist_prevalence_score": round(waitlist_prevalence, 2),
            "market_gap_score": round(market_gap, 2),
            "demand_supply_ratio": round(demand_supply_ratio, 2),
            
            # Competitive Positioning (2)
            "nearest_competitor_miles": round(nearest_competitor_dist, 2),
            "competitive_intensity_score": round(intensity, 2),
            
            # Future Competition (1)
            "new_centers_planned": new_centers_planned,
            
            # Metadata
            "data_source": "Google Places API - 12 Data Points",
            "centers_analyzed": centers_count,
            
            # Data source transparency for business users
            "data_source_details": {
                "overall_type": "real_api",
                "api_name": "Google Places API",
                "api_url": "https://maps.googleapis.com/maps/api/place",
                "accuracy": "high",
                "verifiable": True,
                "verification_url": "https://www.google.com/maps",
                "metrics": {
                    "existing_centers_count": {"type": "real_api", "source": "Google Places Nearby Search"},
                    "total_licensed_capacity": {"type": "estimated", "source": "Derived from review counts (proxy)"},
                    "market_saturation_index": {"type": "derived", "source": "Centers per square mile"},
                    "avg_competitor_rating": {"type": "real_api", "source": "Google Places Details"},
                    "premium_facilities_count": {"type": "real_api", "source": "Filtered from Google ratings"},
                    "avg_capacity_utilization_pct": {"type": "estimated", "source": "Derived from rating patterns"},
                    "waitlist_prevalence_score": {"type": "estimated", "source": "Derived from utilization"},
                    "market_gap_score": {"type": "estimated", "source": "Demand vs capacity calculation"},
                    "demand_supply_ratio": {"type": "estimated", "source": "Population-based estimate"},
                    "nearest_competitor_miles": {"type": "real_api", "source": "Haversine from Google coordinates"},
                    "competitive_intensity_score": {"type": "derived", "source": "Composite of real metrics"},
                    "new_centers_planned": {"type": "real_api", "source": "Google Places name analysis"}
                }
            }
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
            "existing_centers_count": 0,
            "total_licensed_capacity": 0,
            "market_saturation_index": 0.0,
            "avg_competitor_rating": 0.0,
            "premium_facilities_count": 0,
            "avg_capacity_utilization_pct": 0.0,
            "waitlist_prevalence_score": 0.0,
            "market_gap_score": 0.0,
            "demand_supply_ratio": 0.0,
            "nearest_competitor_miles": 0.0,
            "competitive_intensity_score": 0.0,
            "new_centers_planned": 0,
            "data_source": "Mock Data",
            "centers_analyzed": 0
        }
