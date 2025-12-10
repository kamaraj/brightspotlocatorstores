"""
EPA Envirofacts Data Collector
Collects real environmental data from EPA's public API
"""

import asyncio
import aiohttp
from typing import Dict, Any, List
from datetime import datetime


class EPACollector:
    """Collect environmental data from EPA Envirofacts API"""
    
    def __init__(self):
        self.base_url = "https://data.epa.gov/efservice"
        
    async def collect(self, address: str, latitude: float, longitude: float, radius_miles: float = 5.0) -> Dict[str, Any]:
        """
        Collect environmental data for a location
        
        Args:
            address: Location address
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_miles: Search radius in miles
            
        Returns:
            Dictionary with environmental metrics
        """
        
        # Calculate bounding box (approximate)
        lat_delta = radius_miles / 69.0  # 1 degree latitude ≈ 69 miles
        lng_delta = radius_miles / (69.0 * abs(float(latitude) / 90.0 + 0.01))
        
        lat_min = latitude - lat_delta
        lat_max = latitude + lat_delta
        lng_min = longitude - lng_delta
        lng_max = longitude + lng_delta
        
        # Collect data in parallel
        tasks = [
            self._get_tri_sites(lat_min, lat_max, lng_min, lng_max),
            self._get_superfund_sites(lat_min, lat_max, lng_min, lng_max),
            self._get_air_facilities(lat_min, lat_max, lng_min, lng_max)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        tri_sites = results[0] if not isinstance(results[0], Exception) else []
        superfund_sites = results[1] if not isinstance(results[1], Exception) else []
        air_facilities = results[2] if not isinstance(results[2], Exception) else []
        
        # Calculate metrics
        tri_count = len(tri_sites) if isinstance(tri_sites, list) else 0
        superfund_count = len(superfund_sites) if isinstance(superfund_sites, list) else 0
        air_facility_count = len(air_facilities) if isinstance(air_facilities, list) else 0
        
        # Calculate Air Quality Index estimate
        aqi = self._calculate_aqi(tri_count, superfund_count, air_facility_count)
        
        # Calculate environmental hazards score
        hazards_score = min(100, (tri_count * 15) + (superfund_count * 25) + (air_facility_count * 5))
        
        return {
            "tri_sites_count": tri_count,
            "superfund_sites_count": superfund_count,
            "air_facilities_count": air_facility_count,
            "air_quality_index": aqi,
            "environmental_hazards_score": hazards_score,
            "pollution_risk": self._get_pollution_risk_level(hazards_score),
            "data_source": "EPA Envirofacts",
            "confidence": "HIGH" if (tri_count > 0 or superfund_count > 0 or air_facility_count > 0) else "MEDIUM",
            "last_updated": datetime.now().isoformat()
        }
    
    async def _get_tri_sites(self, lat_min: float, lat_max: float, lng_min: float, lng_max: float) -> List[Dict]:
        """Get Toxic Release Inventory sites"""
        try:
            url = f"{self.base_url}/tri_facility/latitude_measure/>/={lat_min}/latitude_measure/<=/={lat_max}/JSON"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Filter by longitude manually since API doesn't support it well
                        if isinstance(data, list):
                            return [
                                site for site in data 
                                if lng_min <= float(site.get('longitude_measure', 0)) <= lng_max
                            ]
                        return []
                    return []
        except Exception as e:
            print(f"EPA TRI API error: {e}")
            return []
    
    async def _get_superfund_sites(self, lat_min: float, lat_max: float, lng_min: float, lng_max: float) -> List[Dict]:
        """Get Superfund (NPL) contamination sites"""
        try:
            # CERCLIS/Superfund sites
            url = f"{self.base_url}/SEMS_CERCLIS/latitude_measure/>/={lat_min}/latitude_measure/<=/={lat_max}/JSON"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list):
                            return [
                                site for site in data 
                                if lng_min <= float(site.get('longitude_measure', 0)) <= lng_max
                            ]
                        return []
                    return []
        except Exception as e:
            print(f"EPA Superfund API error: {e}")
            return []
    
    async def _get_air_facilities(self, lat_min: float, lat_max: float, lng_min: float, lng_max: float) -> List[Dict]:
        """Get air quality monitoring facilities"""
        try:
            # Air facility system
            url = f"{self.base_url}/AIR_FACILITY/latitude_measure/>/={lat_min}/latitude_measure/<=/={lat_max}/JSON"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list):
                            return [
                                facility for facility in data 
                                if lng_min <= float(facility.get('longitude_measure', 0)) <= lng_max
                            ]
                        return []
                    return []
        except Exception as e:
            print(f"EPA Air Facilities API error: {e}")
            return []
    
    def _calculate_aqi(self, tri_count: int, superfund_count: int, air_facilities: int) -> int:
        """
        Calculate Air Quality Index estimate
        AQI Scale: 0-50 (Good), 51-100 (Moderate), 101-150 (Unhealthy for Sensitive), 151+ (Unhealthy)
        """
        base_aqi = 50  # Start with moderate
        
        # TRI sites add pollution
        base_aqi += (tri_count * 8)
        
        # Superfund sites are serious contamination
        base_aqi += (superfund_count * 20)
        
        # Many air facilities might indicate industrial area
        if air_facilities > 5:
            base_aqi += 15
        
        return min(500, max(0, base_aqi))
    
    def _get_pollution_risk_level(self, score: int) -> str:
        """Get pollution risk level description"""
        if score < 20:
            return "Very Low - Minimal environmental concerns"
        elif score < 40:
            return "Low - Few environmental factors"
        elif score < 60:
            return "Moderate - Some environmental considerations"
        elif score < 80:
            return "High - Notable environmental concerns"
        else:
            return "Very High - Significant environmental risks"
