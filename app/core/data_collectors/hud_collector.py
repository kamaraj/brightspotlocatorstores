"""
HUD User API Data Collector
Collects real Fair Market Rent and real estate cost data
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime


class HUDCollector:
    """Collect real estate and rental data from HUD User API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://www.huduser.gov/hudapi/public"
        
    async def collect(self, address: str, zip_code: str, state: str = None) -> Dict[str, Any]:
        """
        Collect Fair Market Rent data for a location
        
        Args:
            address: Location address
            zip_code: ZIP code
            state: State abbreviation (optional)
            
        Returns:
            Dictionary with real estate metrics
        """
        
        if not zip_code or len(zip_code) < 5:
            return self._get_fallback_data()
        
        # Clean ZIP code (first 5 digits only)
        clean_zip = zip_code[:5]
        
        # Get current year
        current_year = datetime.now().year
        
        # Try current year, fall back to previous year if needed
        fmr_data = await self._get_fmr_data(clean_zip, current_year)
        
        if not fmr_data or 'error' in fmr_data:
            fmr_data = await self._get_fmr_data(clean_zip, current_year - 1)
        
        if not fmr_data or 'error' in fmr_data:
            return self._get_fallback_data()
        
        # Extract FMR values
        fmr_0 = fmr_data.get('fmr_0', 0)  # Studio
        fmr_1 = fmr_data.get('fmr_1', 0)  # 1BR
        fmr_2 = fmr_data.get('fmr_2', 0)  # 2BR
        fmr_3 = fmr_data.get('fmr_3', 0)  # 3BR
        fmr_4 = fmr_data.get('fmr_4', 0)  # 4BR
        
        # Calculate average FMR
        avg_fmr = (fmr_1 + fmr_2 + fmr_3) / 3 if (fmr_1 and fmr_2 and fmr_3) else 0
        
        # Estimate commercial real estate costs from residential FMR
        # Commercial is typically 60-80% of residential per sqft
        estimated_sqft_cost = self._estimate_commercial_cost(avg_fmr)
        
        # Calculate childcare center economics
        center_size_sqft = 5000  # Typical center size
        monthly_rent = center_size_sqft * (estimated_sqft_cost / 12)
        
        # Startup costs (real estate + renovations + equipment)
        startup_cost = (estimated_sqft_cost * center_size_sqft) + 75000
        
        # Operating costs (rent + utilities + insurance)
        monthly_operating = monthly_rent + (center_size_sqft * 2)  # $2/sqft for utilities
        
        return {
            "fmr_studio": fmr_0,
            "fmr_1br": fmr_1,
            "fmr_2br": fmr_2,
            "fmr_3br": fmr_3,
            "fmr_4br": fmr_4,
            "average_fmr": round(avg_fmr, 2),
            "real_estate_cost_per_sqft": round(estimated_sqft_cost, 2),
            "estimated_monthly_rent": round(monthly_rent, 2),
            "estimated_startup_cost": round(startup_cost, 2),
            "estimated_monthly_operating_cost": round(monthly_operating, 2),
            "zip_code": clean_zip,
            "year": fmr_data.get('year', current_year),
            "data_source": "HUD User API (Fair Market Rent)",
            "confidence": "HIGH",
            "last_updated": datetime.now().isoformat()
        }
    
    async def _get_fmr_data(self, zip_code: str, year: int) -> Optional[Dict[str, Any]]:
        """Get Fair Market Rent data from HUD API"""
        try:
            url = f"{self.base_url}/fmr/data/{zip_code}?year={year}"
            
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # HUD API returns data or error
                        if 'data' in data:
                            return data['data']
                        elif isinstance(data, dict) and 'fmr_0' in data:
                            return data
                        else:
                            return None
                    elif response.status == 401:
                        print("HUD API: Authentication required. Register at https://www.huduser.gov/portal/dataset/fmr-api.html")
                        return None
                    else:
                        return None
                        
        except Exception as e:
            print(f"HUD API error: {e}")
            return None
    
    def _estimate_commercial_cost(self, avg_residential_fmr: float) -> float:
        """
        Estimate commercial real estate cost per sqft from residential FMR
        
        Typical residential: $1000-2000/month for 800-1000 sqft = $1-2/sqft/month
        Commercial typically 70% of residential on per-sqft basis
        Annual cost = monthly × 12
        Purchase price typically = annual rent × 10-15 years
        """
        if avg_residential_fmr == 0:
            return 150.0  # Default fallback
        
        # Assume average apartment is 900 sqft
        residential_per_sqft_month = avg_residential_fmr / 900
        
        # Commercial is about 70% of residential
        commercial_per_sqft_month = residential_per_sqft_month * 0.7
        
        # Annual cost
        commercial_per_sqft_year = commercial_per_sqft_month * 12
        
        # Purchase/build cost (10x annual)
        purchase_cost_per_sqft = commercial_per_sqft_year * 10
        
        # Clamp to reasonable range
        return max(50, min(400, purchase_cost_per_sqft))
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Return fallback data when API fails"""
        return {
            "fmr_studio": 0,
            "fmr_1br": 0,
            "fmr_2br": 0,
            "fmr_3br": 0,
            "fmr_4br": 0,
            "average_fmr": 0,
            "real_estate_cost_per_sqft": 150.0,  # National average
            "estimated_monthly_rent": 62500,  # 5000 sqft × $150 / 12
            "estimated_startup_cost": 175000,
            "estimated_monthly_operating_cost": 72500,
            "zip_code": "unknown",
            "year": datetime.now().year,
            "data_source": "Fallback estimates",
            "confidence": "LOW",
            "last_updated": datetime.now().isoformat()
        }
