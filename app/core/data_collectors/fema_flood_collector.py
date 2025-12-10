"""
FEMA Flood Maps API Collector
Collects official flood zone data from FEMA National Flood Hazard Layer
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
import json


class FEMAFloodCollector:
    """Collect flood risk data from FEMA National Flood Hazard Layer"""
    
    def __init__(self):
        self.base_url = "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer"
        
    async def collect(self, address: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Collect flood zone and risk data for a location
        
        Args:
            address: Location address
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with flood risk metrics
        """
        
        if not latitude or not longitude:
            return self._get_fallback_data()
        
        # Query FEMA flood zones
        flood_zone = await self._get_flood_zone(latitude, longitude)
        
        if not flood_zone:
            return self._get_fallback_data()
        
        # Parse flood zone designation
        zone = flood_zone.get('zone', 'X')
        bfe = flood_zone.get('bfe', 0)  # Base Flood Elevation
        zone_subtype = flood_zone.get('zone_subtype', '')
        
        # Calculate risk metrics
        risk_score = self._calculate_risk_score(zone, zone_subtype)
        risk_level = self._get_risk_level(zone)
        insurance_required = self._is_insurance_required(zone)
        
        return {
            "flood_zone": zone,
            "flood_zone_subtype": zone_subtype,
            "base_flood_elevation": bfe,
            "flood_risk_score": risk_score,
            "flood_risk_level": risk_level,
            "flood_risk_indicator": risk_score,  # For compatibility
            "insurance_required": insurance_required,
            "special_flood_hazard_area": zone in ['A', 'AE', 'AH', 'AO', 'AR', 'V', 'VE'],
            "latitude": latitude,
            "longitude": longitude,
            "data_source": "FEMA National Flood Hazard Layer",
            "confidence": "HIGH",
            "last_updated": datetime.now().isoformat()
        }
    
    async def _get_flood_zone(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Query FEMA flood zone at specific coordinates"""
        try:
            # FEMA NFHL uses Web Mercator projection (WKID 3857)
            # But we can query with lat/lng (WKID 4326)
            
            # Layer 28 = Flood Zones
            layer_id = 28
            
            # Build query URL
            query_url = f"{self.base_url}/{layer_id}/query"
            
            params = {
                'geometry': f'{longitude},{latitude}',
                'geometryType': 'esriGeometryPoint',
                'inSR': '4326',  # WGS84 lat/lng
                'spatialRel': 'esriSpatialRelIntersects',
                'outFields': 'FLD_ZONE,ZONE_SUBTY,STATIC_BFE',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(query_url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'features' in data and len(data['features']) > 0:
                            # Get first matching feature
                            feature = data['features'][0]
                            attrs = feature.get('attributes', {})
                            
                            return {
                                'zone': attrs.get('FLD_ZONE', 'X'),
                                'zone_subtype': attrs.get('ZONE_SUBTY', ''),
                                'bfe': attrs.get('STATIC_BFE', 0) or 0
                            }
                        else:
                            # No flood zone found = Zone X (minimal risk)
                            return {
                                'zone': 'X',
                                'zone_subtype': '',
                                'bfe': 0
                            }
                    else:
                        return None
                        
        except Exception as e:
            print(f"FEMA API error: {e}")
            return None
    
    def _calculate_risk_score(self, zone: str, subtype: str) -> float:
        """
        Calculate flood risk score (0-100, higher is more risk)
        Based on FEMA flood zone designations
        """
        risk_scores = {
            # High Risk Zones (Special Flood Hazard Areas)
            'V': 95,    # Coastal with wave action
            'VE': 95,   # Coastal with BFE
            'A': 85,    # 1% annual chance
            'AE': 85,   # 1% with BFE
            'AH': 80,   # Shallow flooding
            'AO': 80,   # Sheet flow
            'AR': 75,   # Flood protection restored
            
            # Moderate Risk Zones
            'B': 40,    # 0.2% annual chance (Zones B/X500)
            'X500': 40,
            'C': 35,    # Moderate risk (Zone C/X)
            
            # Minimal Risk Zones
            'X': 10,    # Above 500-year flood
            'D': 20,    # Undetermined risk
        }
        
        base_score = risk_scores.get(zone, 50)
        
        # Adjust for subtypes
        if 'FLOODWAY' in subtype.upper():
            base_score = min(100, base_score + 10)
        
        return base_score
    
    def _get_risk_level(self, zone: str) -> str:
        """Convert flood zone to risk level description"""
        high_risk = ['A', 'AE', 'AH', 'AO', 'AR', 'V', 'VE']
        moderate_risk = ['B', 'X500', 'C']
        
        if zone in high_risk:
            return "High"
        elif zone in moderate_risk:
            return "Moderate"
        else:
            return "Low"
    
    def _is_insurance_required(self, zone: str) -> bool:
        """Determine if flood insurance is required for mortgages"""
        # Special Flood Hazard Areas require insurance
        sfha_zones = ['A', 'AE', 'AH', 'AO', 'AR', 'V', 'VE']
        return zone in sfha_zones
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Return fallback data when API fails"""
        return {
            "flood_zone": "X",
            "flood_zone_subtype": "",
            "base_flood_elevation": 0,
            "flood_risk_score": 25.0,  # Low-moderate default
            "flood_risk_level": "Low-Moderate",
            "flood_risk_indicator": 25.0,
            "insurance_required": False,
            "special_flood_hazard_area": False,
            "latitude": 0,
            "longitude": 0,
            "data_source": "Fallback estimate",
            "confidence": "LOW",
            "last_updated": datetime.now().isoformat()
        }
