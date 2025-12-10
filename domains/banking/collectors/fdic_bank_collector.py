"""
FDIC Bank Finder API Collector
Collects existing bank branch data for competition analysis
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from shared.base import BaseCollector

logger = logging.getLogger(__name__)


class FDICBankCollector(BaseCollector):
    """
    Collects bank branch data from FDIC Bank Find API
    
    Provides:
    - Count of existing bank branches in radius
    - List of competitor banks with details
    - Market concentration (HHI index)
    - Deposit data by institution
    - Branch locations and services
    
    API: https://banks.data.fdic.gov/docs/
    Free, no key required
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = "https://banks.data.fdic.gov/api"
        self.timeout = 15.0
    
    async def collect(
        self,
        lat: float,
        lng: float,
        radius_miles: float = 5.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Collect bank branch data near location
        
        Args:
            lat: Latitude
            lng: Longitude
            radius_miles: Search radius in miles
            
        Returns:
            Dictionary with branch data and competition metrics
        """
        self.start_timer()
        
        try:
            # Search for branches in radius
            branches = await self._search_branches(lat, lng, radius_miles)
            
            if not branches:
                return self.create_response(
                    data=self._get_fallback_data(),
                    confidence="LOW",
                    metadata={"reason": "No FDIC data found for location"}
                )
            
            # Aggregate by institution
            institutions = self._aggregate_by_institution(branches)
            
            # Calculate competition metrics
            metrics = self._calculate_competition_metrics(branches, institutions)
            
            duration = self.end_timer()
            
            return self.create_response(
                data={
                    **metrics,
                    "branches": branches[:10],  # Top 10 for detail
                    "total_branches": len(branches),
                    "collection_time_ms": duration
                },
                confidence="HIGH",
                metadata={
                    "data_source": "FDIC Bank Find API",
                    "search_radius_miles": radius_miles,
                    "institutions_found": len(institutions)
                }
            )
            
        except Exception as e:
            logger.error(f"FDIC Bank collection error: {e}")
            return self.handle_error(e, self._get_fallback_data())
    
    async def _search_branches(
        self,
        lat: float,
        lng: float,
        radius_miles: float
    ) -> List[Dict[str, Any]]:
        """
        Search for bank branches using FDIC API
        
        FDIC API uses radius in meters
        """
        radius_meters = int(radius_miles * 1609.34)
        
        url = f"{self.api_base}/locations"
        params = {
            "filters": f"LATITUDE:{lat} AND LONGITUDE:{lng}",
            "radius": radius_meters,
            "limit": 100,
            "format": "json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        
        # Extract branch data
        branches = []
        for item in data.get("data", []):
            branch = {
                "cert": item.get("CERT"),
                "name": item.get("NAME"),
                "address": item.get("ADDRESS"),
                "city": item.get("CITY"),
                "state": item.get("STNAME"),
                "zip": item.get("ZIP"),
                "latitude": item.get("LATITUDE"),
                "longitude": item.get("LONGITUDE"),
                "branch_type": item.get("BRSERTYP"),  # Full service, limited service, etc.
                "established_date": item.get("ESTDATE"),
                "services": item.get("SERVTYPE", ""),
                "institution_name": item.get("NAMEFULL"),
                "institution_class": item.get("CLASS"),  # National bank, state bank, etc.
                "fdic_insured": item.get("FDICREGION") is not None
            }
            branches.append(branch)
        
        return branches
    
    def _aggregate_by_institution(
        self,
        branches: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate branches by institution
        
        Returns:
            Dictionary of cert -> institution data
        """
        institutions = {}
        
        for branch in branches:
            cert = branch["cert"]
            
            if cert not in institutions:
                institutions[cert] = {
                    "cert": cert,
                    "name": branch["institution_name"],
                    "class": branch["institution_class"],
                    "branch_count": 0,
                    "branches": []
                }
            
            institutions[cert]["branch_count"] += 1
            institutions[cert]["branches"].append(branch)
        
        return institutions
    
    def _calculate_competition_metrics(
        self,
        branches: List[Dict[str, Any]],
        institutions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate competition metrics from branch data
        """
        total_branches = len(branches)
        total_institutions = len(institutions)
        
        # Calculate market concentration (HHI)
        # HHI = sum of squared market shares (0-10000)
        if total_branches > 0:
            market_shares = [
                (inst["branch_count"] / total_branches) * 100
                for inst in institutions.values()
            ]
            hhi = sum(share ** 2 for share in market_shares)
        else:
            hhi = 0
        
        # Market concentration interpretation
        if hhi < 1500:
            concentration = "Competitive Market"
            competition_level = "HIGH"
        elif hhi < 2500:
            concentration = "Moderate Concentration"
            competition_level = "MEDIUM"
        else:
            concentration = "High Concentration"
            competition_level = "LOW"
        
        # Top 3 competitors
        top_competitors = sorted(
            institutions.values(),
            key=lambda x: x["branch_count"],
            reverse=True
        )[:3]
        
        # Branch type distribution
        full_service = sum(
            1 for b in branches 
            if b.get("branch_type") == "11"  # Full service code
        )
        
        # Calculate market saturation
        # Assume 1 branch per 3,000 people is ideal
        # This would be combined with demographics data in real scoring
        saturation_score = min(100, (total_branches / 10) * 100)  # Rough estimate
        
        return {
            "existing_branches_count": total_branches,
            "institutions_count": total_institutions,
            "hhi_index": round(hhi, 2),
            "market_concentration": concentration,
            "competition_level": competition_level,
            "top_competitor": top_competitors[0]["name"] if top_competitors else "N/A",
            "top_competitor_branches": top_competitors[0]["branch_count"] if top_competitors else 0,
            "full_service_branches": full_service,
            "limited_service_branches": total_branches - full_service,
            "market_saturation_index": round(saturation_score, 2),
            "top_competitors": [
                {
                    "name": comp["name"],
                    "branches": comp["branch_count"],
                    "market_share": round((comp["branch_count"] / total_branches) * 100, 1)
                }
                for comp in top_competitors
            ]
        }
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """
        Fallback data when FDIC API unavailable
        """
        return {
            "existing_branches_count": 0,
            "institutions_count": 0,
            "hhi_index": 0,
            "market_concentration": "Unknown",
            "competition_level": "UNKNOWN",
            "top_competitor": "Data unavailable",
            "top_competitor_branches": 0,
            "full_service_branches": 0,
            "limited_service_branches": 0,
            "market_saturation_index": 50.0,
            "top_competitors": [],
            "using_fallback": True
        }
