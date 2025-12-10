"""
FBI Crime Data Explorer API Collector
Collects real crime statistics from FBI's Crime Data Explorer
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime


class FBICrimeCollector:
    """Collect crime statistics from FBI Crime Data Explorer API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.usa.gov/crime/fbi/cde"
        
    async def collect(self, address: str, state: str, county: str = None, latitude: float = None, longitude: float = None) -> Dict[str, Any]:
        """
        Collect crime statistics for a location
        
        Args:
            address: Location address
            state: State abbreviation (e.g., "FL", "CA")
            county: County name (optional)
            latitude: Latitude (for fallback)
            longitude: Longitude (for fallback)
            
        Returns:
            Dictionary with crime metrics
        """
        
        if not state:
            return self._get_fallback_data()
        
        # Get state crime data
        state_data = await self._get_state_crime_data(state)
        
        # Try to get agency-specific data if we have location
        agency_data = None
        if county:
            agency_data = await self._get_agency_crime_data(state, county)
        
        # Use most specific data available
        crime_data = agency_data if agency_data else state_data
        
        if not crime_data:
            return self._get_fallback_data()
        
        # Calculate crime rate index (per 100k population)
        violent_crime_rate = crime_data.get('violent_crime_rate', 0)
        property_crime_rate = crime_data.get('property_crime_rate', 0)
        
        # Combined crime index (0-100 scale, lower is better)
        # National averages: ~400 violent, ~2500 property per 100k
        crime_index = self._calculate_crime_index(violent_crime_rate, property_crime_rate)
        
        # Safety score (inverse of crime index)
        safety_score = 100 - crime_index
        
        # Risk level
        risk_level = self._get_risk_level(crime_index)
        
        return {
            "violent_crime_rate": round(violent_crime_rate, 2),
            "property_crime_rate": round(property_crime_rate, 2),
            "murder_rate": crime_data.get('murder_rate', 0),
            "rape_rate": crime_data.get('rape_rate', 0),
            "robbery_rate": crime_data.get('robbery_rate', 0),
            "assault_rate": crime_data.get('assault_rate', 0),
            "burglary_rate": crime_data.get('burglary_rate', 0),
            "larceny_rate": crime_data.get('larceny_rate', 0),
            "vehicle_theft_rate": crime_data.get('vehicle_theft_rate', 0),
            "crime_rate_index": round(crime_index, 2),
            "neighborhood_safety_score": round(safety_score, 2),
            "risk_level": risk_level,
            "data_year": crime_data.get('year', datetime.now().year - 1),
            "state": state,
            "county": county or "State-wide",
            "data_source": "FBI Crime Data Explorer",
            "confidence": "HIGH" if agency_data else "MEDIUM",
            "last_updated": datetime.now().isoformat()
        }
    
    async def _get_state_crime_data(self, state: str) -> Optional[Dict[str, Any]]:
        """Get state-level crime statistics"""
        try:
            # FBI CDE API endpoint for state data
            # Get most recent year available (typically 2 years behind)
            year = datetime.now().year - 2
            
            url = f"{self.base_url}/summarized/state/{state}/{year}"
            
            headers = {}
            if self.api_key:
                headers['X-API-KEY'] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_crime_data(data)
                    elif response.status == 401:
                        print("FBI CDE API: API key required. Get one at https://api.data.gov/signup/")
                        return None
                    else:
                        return None
                        
        except Exception as e:
            print(f"FBI CDE API error: {e}")
            return None
    
    async def _get_agency_crime_data(self, state: str, county: str) -> Optional[Dict[str, Any]]:
        """Get agency/county-level crime statistics"""
        try:
            year = datetime.now().year - 2
            
            # Search for agencies in the county
            url = f"{self.base_url}/agencies/byStateAbbr/{state}"
            
            headers = {}
            if self.api_key:
                headers['X-API-KEY'] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                # Get list of agencies
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        return None
                    
                    agencies = await response.json()
                    
                    # Find agencies matching the county
                    county_agencies = [
                        a for a in agencies 
                        if county.lower() in a.get('agency_name', '').lower() 
                        or county.lower() in a.get('county_name', '').lower()
                    ]
                    
                    if not county_agencies:
                        return None
                    
                    # Get data for first matching agency
                    ori = county_agencies[0].get('ori')
                    if not ori:
                        return None
                    
                    crime_url = f"{self.base_url}/summarized/agencies/{ori}/{year}"
                    async with session.get(crime_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as crime_response:
                        if crime_response.status == 200:
                            data = await crime_response.json()
                            return self._parse_crime_data(data)
                        else:
                            return None
                        
        except Exception as e:
            print(f"FBI CDE agency API error: {e}")
            return None
    
    def _parse_crime_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse FBI CDE API response"""
        try:
            if not data or 'results' not in data:
                return None
            
            results = data['results'][0] if data['results'] else {}
            
            # Extract population
            population = results.get('population', 1)
            if population == 0:
                population = 1
            
            # Extract counts
            violent = results.get('violent_crime', 0)
            property_crime = results.get('property_crime', 0)
            murder = results.get('homicide', 0)
            rape = results.get('rape', 0)
            robbery = results.get('robbery', 0)
            assault = results.get('aggravated_assault', 0)
            burglary = results.get('burglary', 0)
            larceny = results.get('larceny', 0)
            vehicle_theft = results.get('motor_vehicle_theft', 0)
            
            # Calculate rates per 100k
            rate_multiplier = 100000 / population
            
            return {
                'violent_crime_rate': violent * rate_multiplier,
                'property_crime_rate': property_crime * rate_multiplier,
                'murder_rate': murder * rate_multiplier,
                'rape_rate': rape * rate_multiplier,
                'robbery_rate': robbery * rate_multiplier,
                'assault_rate': assault * rate_multiplier,
                'burglary_rate': burglary * rate_multiplier,
                'larceny_rate': larceny * rate_multiplier,
                'vehicle_theft_rate': vehicle_theft * rate_multiplier,
                'year': results.get('data_year', datetime.now().year - 2)
            }
            
        except Exception as e:
            print(f"Error parsing FBI crime data: {e}")
            return None
    
    def _calculate_crime_index(self, violent_rate: float, property_rate: float) -> float:
        """
        Calculate crime index (0-100, lower is better)
        Based on national averages: ~400 violent, ~2500 property per 100k
        """
        # Weight violent crime more heavily (4x)
        violent_score = min(100, (violent_rate / 400) * 100)
        property_score = min(100, (property_rate / 2500) * 100)
        
        # Combined: 60% violent, 40% property
        crime_index = (violent_score * 0.6) + (property_score * 0.4)
        
        return min(100, crime_index)
    
    def _get_risk_level(self, crime_index: float) -> str:
        """Convert crime index to risk level"""
        if crime_index < 20:
            return "Very Low"
        elif crime_index < 40:
            return "Low"
        elif crime_index < 60:
            return "Moderate"
        elif crime_index < 80:
            return "High"
        else:
            return "Very High"
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Return fallback data when API fails"""
        return {
            "violent_crime_rate": 400.0,  # National average
            "property_crime_rate": 2500.0,  # National average
            "murder_rate": 5.0,
            "rape_rate": 40.0,
            "robbery_rate": 100.0,
            "assault_rate": 250.0,
            "burglary_rate": 400.0,
            "larceny_rate": 1500.0,
            "vehicle_theft_rate": 250.0,
            "crime_rate_index": 50.0,  # Moderate
            "neighborhood_safety_score": 50.0,
            "risk_level": "Moderate",
            "data_year": datetime.now().year - 2,
            "state": "unknown",
            "county": "unknown",
            "data_source": "National averages (fallback)",
            "confidence": "LOW",
            "last_updated": datetime.now().isoformat()
        }
