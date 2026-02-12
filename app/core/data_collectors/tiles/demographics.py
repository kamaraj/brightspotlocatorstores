"""
Tiles & Flooring Demographics Collector
Collects population and demographic data relevant to tiles dealers and distributors
"""

import httpx
from typing import Dict, Any
from loguru import logger

from app.config import get_settings


class TilesDemographicsCollector:
    """
    Collects demographic data points relevant to Tiles & Flooring industry:
    
    1. Homeownership (Crucial for renovation/new installs)
    2. Income levels (Higher income = premium tiles)
    3. Housing Age (Older homes > 15 years = renovation potential)
    4. Population Growth (New construction potential)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.census_api_key = self.settings.census_api_key
        self.google_api_key = self.settings.google_maps_api_key
        
        # Census API endpoints
        self.census_base_url = "https://api.census.gov/data"
        self.acs5_url = f"{self.census_base_url}/2022/acs/acs5"
        
    async def collect(self, address: str, radius_miles: float = 5.0) -> Dict[str, Any]:
        """
        Collect demographic data for location
        """
        try:
            # Step 1: Geocode address to get coordinates
            coordinates = await self._geocode_address(address)
            if not coordinates:
                return self._error_response("Failed to geocode address")
            
            lat, lng = coordinates
            
            # Step 2: Get Census tract/block group
            census_geo = await self._get_census_geography(lat, lng)
            if not census_geo:
                return self._error_response("Failed to identify Census geography")
            
            # Step 3: Collect Census data
            demographics = await self._collect_census_data(census_geo, radius_miles)
            
            return {
                "success": True,
                "address": address,
                "coordinates": {"lat": lat, "lng": lng},
                "radius_miles": radius_miles,
                **demographics
            }
            
        except Exception as e:
            logger.error(f"Tiles demographics collection error: {e}")
            return self._error_response(str(e))
    
    async def _geocode_address(self, address: str) -> tuple[float, float] | None:
        """Convert address to latitude/longitude using Google Geocoding API"""
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
            else:
                logger.warning(f"Geocoding failed: {data.get('status')}")
                return None
                
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    async def _get_census_geography(self, lat: float, lng: float) -> Dict[str, str] | None:
        """Get Census tract and block group for coordinates"""
        try:
            url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            params = {
                "x": lng,
                "y": lat,
                "benchmark": "Public_AR_Current",
                "vintage": "Current_Current",
                "format": "json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            if data.get("result") and data["result"].get("geographies"):
                geographies = data["result"]["geographies"]
                census_tracts = geographies.get("Census Tracts", [])
                if census_tracts:
                    tract = census_tracts[0]
                    return {
                        "state": tract.get("STATE"),
                        "county": tract.get("COUNTY"),
                        "tract": tract.get("TRACT"),
                        "block_group": tract.get("BLKGRP", "")
                    }
            return None
        except Exception as e:
            logger.error(f"Census geography lookup error: {e}")
            return None
    
    async def _collect_census_data(self, census_geo: Dict[str, str], radius_miles: float) -> Dict[str, Any]:
        """Collect ceramic tile specific demographic data"""
        state = census_geo["state"]
        county = census_geo["county"]
        tract = census_geo["tract"]
        
        # Variables for Tiles industry:
        # B25003_001E: Total Occupied Housing Units
        # B25003_002E: Owner-occupied
        # B19013_001E: Median household income
        # B25034_001E: Total Housing Units (for age)
        # B25034_008E: Built 1990-1999 (Renovation potential)
        # B25034_009E: Built 1980-1989
        # B25034_010E: Built 1970-1979
        
        variables = [
            "B25003_001E", "B25003_002E", # Homeownership
            "B19013_001E",                # Median income
            "B25034_001E",                # Total units for age
            "B25034_008E", "B25034_009E", "B25034_010E", # Built 1970-1999
            "B01003_001E"                 # Total population
        ]
        
        try:
            params = {
                "get": ",".join(variables),
                "for": f"tract:{tract}",
                "in": f"state:{state} county:{county}",
                "key": self.census_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.acs5_url, params=params, timeout=15.0)
                if response.status_code != 200:
                    return self._mock_tiles_demographics()
                data = response.json()
            
            if len(data) < 2:
                return self._mock_tiles_demographics()
                
            headers = data[0]
            values = data[1]
            census_data = dict(zip(headers, values))
            
            total_units = int(census_data.get("B25003_001E", 0) or 0)
            owner_occupied = int(census_data.get("B25003_002E", 0) or 0)
            homeownership_rate = (owner_occupied / total_units * 100) if total_units > 0 else 0
            
            median_income = int(census_data.get("B19013_001E", 0) or 0)
            
            # Renovation potential (homes 25-55 years old)
            renovation_age_units = (
                int(census_data.get("B25034_008E", 0) or 0) +
                int(census_data.get("B25034_009E", 0) or 0) +
                int(census_data.get("B25034_010E", 0) or 0)
            )
            renovation_potential_rate = (renovation_age_units / total_units * 100) if total_units > 0 else 0
            
            return {
                "homeownership_rate": round(homeownership_rate, 2),
                "total_households": total_units,
                "owner_occupied_households": owner_occupied,
                "median_household_income": median_income,
                "renovation_potential_rate": round(renovation_potential_rate, 2),
                "population_total": int(census_data.get("B01003_001E", 0) or 0),
                "data_source": "U.S. Census Bureau ACS 5-Year (2022)"
            }
            
        except Exception:
            return self._mock_tiles_demographics()

    def _mock_tiles_demographics(self) -> Dict[str, Any]:
        return {
            "homeownership_rate": 65.0,
            "total_households": 4200,
            "owner_occupied_households": 2730,
            "median_household_income": 85000,
            "renovation_potential_rate": 35.0,
            "population_total": 12000,
            "data_source": "Mock Tiles Data (API Unavailable)"
        }

    def _error_response(self, error: str) -> Dict[str, Any]:
        return {"success": False, "error": error}
