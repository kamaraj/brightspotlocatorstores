"""
Regulatory & Zoning Data Collector
Analysis with 8 data points across 4 categories
"""

import httpx
import asyncio
from typing import Dict, Any, List
from loguru import logger

from app.config import get_settings


class RegulatoryCollector:
    """
    Collects 8 regulatory & zoning data points across 4 categories:
    
    1. Zoning Requirements (3 points):
       - Zoning compliance score
       - Conditional use permit required
       - Rezoning feasibility
    
    2. Building Code Requirements (2 points):
       - Building code complexity score
       - ADA compliance cost estimate
    
    3. Licensing Requirements (2 points):
       - Licensing difficulty score
       - Time to obtain license (days)
    
    4. Processing Timelines (1 point):
       - Average permit processing time (days)
    
    Note: This collector uses estimation algorithms as direct access to
    municipal databases requires integration with each city's systems.
    Production version should integrate with:
    - Local zoning databases
    - Building department APIs
    - State licensing boards
    - Municipal permit tracking systems
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.places_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def collect(self, address: str, radius_miles: float = 1.0) -> Dict[str, Any]:
        """
        Collect regulatory & zoning metrics (8 data points)
        
        Args:
            address: Full street address
            radius_miles: Search radius (default 1 mile)
            
        Returns:
            Dictionary with 8 regulatory metrics across 4 categories
        """
        try:
            # Step 1: Geocode address and get place details
            coordinates = await self._geocode_address(address)
            if not coordinates:
                return self._mock_comprehensive_data()
            
            lat, lng = coordinates
            
            # Step 2: Get administrative area information
            admin_info = await self._get_administrative_info(lat, lng)
            
            # Step 3: Analyze zoning requirements
            zoning_metrics = await self._analyze_zoning(lat, lng, radius_miles, admin_info)
            
            # Step 4: Analyze building code requirements
            building_metrics = await self._analyze_building_codes(lat, lng, admin_info)
            
            # Step 5: Analyze licensing requirements
            licensing_metrics = await self._analyze_licensing(admin_info)
            
            # Step 6: Analyze processing timelines
            timeline_metrics = await self._analyze_processing_times(admin_info, lat, lng)
            
            return {
                "success": True,
                "address": address,
                "coordinates": {"lat": lat, "lng": lng},
                "jurisdiction": admin_info.get("city", "Unknown"),
                "state": admin_info.get("state", "Unknown"),
                **zoning_metrics,
                **building_metrics,
                **licensing_metrics,
                **timeline_metrics,
                "data_source": "Google Geocoding API + Estimations - 8 Data Points",
                "note": "Estimates based on general patterns. Verify with local authorities."
            }
            
        except Exception as e:
            logger.error(f"Regulatory analysis error: {e}")
            return self._mock_comprehensive_data()
    
    async def _geocode_address(self, address: str) -> tuple[float, float] | None:
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
    
    async def _get_administrative_info(self, lat: float, lng: float) -> Dict[str, str]:
        """
        Get administrative area information (city, county, state)
        """
        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                "latlng": f"{lat},{lng}",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            if data["status"] != "OK" or not data["results"]:
                return {}
            
            # Extract administrative components
            admin_info = {
                "city": None,
                "county": None,
                "state": None,
                "state_short": None,
                "country": None,
                "zip": None
            }
            
            for result in data["results"]:
                for component in result.get("address_components", []):
                    types = component.get("types", [])
                    
                    if "locality" in types and not admin_info["city"]:
                        admin_info["city"] = component.get("long_name")
                    elif "administrative_area_level_2" in types and not admin_info["county"]:
                        admin_info["county"] = component.get("long_name")
                    elif "administrative_area_level_1" in types and not admin_info["state"]:
                        admin_info["state"] = component.get("long_name")
                        admin_info["state_short"] = component.get("short_name")
                    elif "country" in types:
                        admin_info["country"] = component.get("long_name")
                    elif "postal_code" in types and not admin_info["zip"]:
                        admin_info["zip"] = component.get("long_name")
            
            return admin_info
            
        except Exception as e:
            logger.debug(f"Administrative info error: {e}")
            return {}
    
    async def _analyze_zoning(
        self, 
        lat: float, 
        lng: float, 
        radius_miles: float,
        admin_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Analyze zoning requirements
        Returns: zoning_compliance_score, conditional_use_required, rezoning_feasibility_score
        """
        try:
            # Check land use indicators in the area
            url = f"{self.base_url}/place/nearbysearch/json"
            
            # Check for existing childcare centers (indicates compatible zoning)
            params = {
                "location": f"{lat},{lng}",
                "radius": int(radius_miles * 1609.34),
                "keyword": "childcare|daycare|preschool",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            existing_childcare = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # Check for compatible uses (schools, community centers)
            params["keyword"] = "school|community center|library"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            compatible_uses = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # Check for potentially conflicting uses (industrial, heavy commercial)
            params["keyword"] = "industrial|factory|warehouse|truck|manufacturing"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            industrial_uses = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # Zoning compliance score (0-100, higher = better compliance)
            # More existing childcare = better zoning compatibility
            # More compatible uses = residential/mixed use area (good for childcare)
            # Industrial uses = potential zoning conflict
            
            compliance_score = 50  # Base score
            compliance_score += min(30, existing_childcare * 10)  # Up to 30 points
            compliance_score += min(20, compatible_uses * 3)      # Up to 20 points
            compliance_score -= min(40, industrial_uses * 10)     # Penalty for industrial
            compliance_score = max(10, min(100, compliance_score))
            
            # Conditional use permit (CUP) requirement estimation
            # If score < 60, likely needs CUP
            conditional_use_required = compliance_score < 60
            
            # Rezoning feasibility score (0-100)
            # Based on compatible uses and existing patterns
            if existing_childcare > 0:
                rezoning_feasibility = 90  # Already has childcare
            elif compatible_uses > 3:
                rezoning_feasibility = 75  # Compatible neighborhood
            elif industrial_uses > 2:
                rezoning_feasibility = 20  # Industrial area, difficult
            else:
                rezoning_feasibility = 50  # Moderate feasibility
            
            # Adjust for city size (larger cities = more complex zoning)
            city = admin_info.get("city", "")
            if city:
                # Major cities have more complex zoning
                major_cities = [
                    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
                    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"
                ]
                if any(major in city for major in major_cities):
                    compliance_score -= 10
                    rezoning_feasibility -= 15
            
            return {
                "zoning_compliance_score": round(max(0, min(100, compliance_score)), 1),
                "conditional_use_permit_required": conditional_use_required,
                "rezoning_feasibility_score": round(max(0, min(100, rezoning_feasibility)), 1)
            }
            
        except Exception as e:
            logger.debug(f"Zoning analysis error: {e}")
            return {
                "zoning_compliance_score": 60.0,
                "conditional_use_permit_required": False,
                "rezoning_feasibility_score": 65.0
            }
    
    async def _analyze_building_codes(
        self, 
        lat: float, 
        lng: float,
        admin_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Analyze building code requirements
        Returns: building_code_complexity_score, ada_compliance_cost_estimate
        """
        try:
            state = admin_info.get("state_short", "")
            
            # Building code complexity by state/region
            # States with stricter codes: CA, NY, MA, WA, OR, CO
            strict_code_states = ["CA", "NY", "MA", "WA", "OR", "CO", "NJ", "CT"]
            moderate_code_states = ["TX", "FL", "IL", "PA", "OH", "GA", "NC", "VA"]
            
            if state in strict_code_states:
                complexity_score = 75  # High complexity
                ada_base_cost = 25000
            elif state in moderate_code_states:
                complexity_score = 55  # Moderate complexity
                ada_base_cost = 18000
            else:
                complexity_score = 45  # Standard complexity
                ada_base_cost = 15000
            
            # Adjust for urban vs rural (estimate from surrounding development)
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 1609,  # 1 mile
                "type": "establishment",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            establishment_count = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # High density areas have more complex codes
            if establishment_count > 40:  # Urban
                complexity_score += 15
                ada_base_cost += 8000
            elif establishment_count > 20:  # Suburban
                complexity_score += 8
                ada_base_cost += 4000
            
            # ADA compliance cost for typical 5,000 sqft childcare center
            # Includes: ramps, accessible restrooms, doorways, parking, signage
            # Range: $15,000 - $40,000 depending on existing structure
            ada_cost = min(40000, ada_base_cost)
            
            return {
                "building_code_complexity_score": round(min(100, complexity_score), 1),
                "ada_compliance_cost_estimate": round(ada_cost, 0)
            }
            
        except Exception as e:
            logger.debug(f"Building code analysis error: {e}")
            return {
                "building_code_complexity_score": 55.0,
                "ada_compliance_cost_estimate": 20000.0
            }
    
    async def _analyze_licensing(self, admin_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze licensing requirements
        Returns: licensing_difficulty_score, time_to_license_days
        """
        try:
            state = admin_info.get("state_short", "")
            
            # Licensing difficulty by state (based on known regulations)
            # More regulated states: CA, NY, MA, CT, NJ, MD, WA
            strict_licensing = {
                "CA": (80, 180),  # (difficulty score, days to license)
                "NY": (75, 150),
                "MA": (75, 160),
                "CT": (70, 140),
                "NJ": (70, 135),
                "MD": (65, 130),
                "WA": (65, 125)
            }
            
            moderate_licensing = {
                "TX": (50, 90),
                "FL": (50, 85),
                "IL": (55, 100),
                "PA": (55, 95),
                "OH": (50, 90),
                "GA": (45, 80),
                "NC": (45, 85),
                "VA": (50, 90)
            }
            
            if state in strict_licensing:
                difficulty, days = strict_licensing[state]
            elif state in moderate_licensing:
                difficulty, days = moderate_licensing[state]
            else:
                difficulty, days = (40, 75)  # Default less strict
            
            # Add variability based on urban/rural (urban takes longer)
            city = admin_info.get("city", "")
            if city:
                major_cities = [
                    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
                    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
                    "Boston", "Seattle", "Denver", "San Francisco", "Portland"
                ]
                if any(major in city for major in major_cities):
                    difficulty += 10
                    days += 30
            
            return {
                "licensing_difficulty_score": round(min(100, difficulty), 1),
                "time_to_obtain_license_days": round(days, 0)
            }
            
        except Exception as e:
            logger.debug(f"Licensing analysis error: {e}")
            return {
                "licensing_difficulty_score": 55.0,
                "time_to_obtain_license_days": 90.0
            }
    
    async def _analyze_processing_times(
        self, 
        admin_info: Dict[str, str],
        lat: float,
        lng: float
    ) -> Dict[str, float]:
        """
        Analyze permit processing timelines
        Returns: avg_permit_processing_days
        """
        try:
            state = admin_info.get("state_short", "")
            city = admin_info.get("city", "")
            
            # Base processing time by region
            base_days = 60  # Standard 2 months
            
            # Adjust for state efficiency
            fast_states = ["TX", "FL", "AZ", "TN", "NC", "GA", "IN"]
            slow_states = ["CA", "NY", "MA", "NJ", "CT", "IL", "WA"]
            
            if state in fast_states:
                base_days = 45
            elif state in slow_states:
                base_days = 90
            
            # Adjust for city size (larger = slower)
            # Check building department indicators
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 16093,  # 10 miles
                "keyword": "city hall|municipal building|building department",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            govt_buildings = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # More government buildings = larger bureaucracy = longer times
            if govt_buildings > 5:
                base_days += 30  # Major city
            elif govt_buildings > 2:
                base_days += 15  # Medium city
            
            # Add construction activity factor (busier = longer waits)
            params["keyword"] = "construction|new development"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            construction_activity = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            if construction_activity > 15:
                base_days += 20  # High demand on permit office
            elif construction_activity > 8:
                base_days += 10
            
            processing_days = min(180, max(30, base_days))
            
            return {
                "avg_permit_processing_days": round(processing_days, 0)
            }
            
        except Exception as e:
            logger.debug(f"Processing time analysis error: {e}")
            return {
                "avg_permit_processing_days": 75.0
            }
    
    def _mock_comprehensive_data(self) -> Dict[str, Any]:
        """Return mock data when API fails"""
        return {
            "success": False,
            "jurisdiction": "Unknown",
            "state": "Unknown",
            "zoning_compliance_score": 60.0,
            "conditional_use_permit_required": False,
            "rezoning_feasibility_score": 65.0,
            "building_code_complexity_score": 55.0,
            "ada_compliance_cost_estimate": 20000.0,
            "licensing_difficulty_score": 55.0,
            "time_to_obtain_license_days": 90.0,
            "avg_permit_processing_days": 75.0,
            "data_source": "Mock Data"
        }
