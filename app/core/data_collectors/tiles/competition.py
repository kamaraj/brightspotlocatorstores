"""
Tiles & Flooring Competition Collector
Analyzes nearby tile stores, flooring retailers, and home improvement centers
"""

import httpx
from typing import Dict, Any, List
from loguru import logger

from app.config import get_settings


class TilesCompetitionCollector:
    """
    Analyzes competition in the tiles and flooring sector:
    1. Direct Competitors: Tile stores, Ceramic tile dealers
    2. Indirect Competitors: Flooring stores, Carpet stores
    3. Big Box Competitors: Home Depot, Lowe's, Floor & Decor
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.google_maps_api_key
        
    async def collect(self, address: str, radius_miles: float = 5.0) -> Dict[str, Any]:
        """
        Identify competitors within the search radius
        """
        try:
            # Conversion: miles to meters
            radius_meters = radius_miles * 1609.34
            
            # Step 1: Search for Tile Stores
            tile_stores = await self._search_places("tile store", address, radius_meters)
            
            # Step 2: Search for Flooring Stores
            flooring_stores = await self._search_places("flooring store", address, radius_meters)
            
            # Step 3: Search for Home Improvement (Big Box)
            home_improvement = await self._search_places("home improvement store", address, radius_meters)
            
            # Combine and deduplicate
            all_competitors = self._merge_results([tile_stores, flooring_stores, home_improvement])
            
            return {
                "success": True,
                "competitor_count": len(all_competitors),
                "direct_competitors": len(tile_stores),
                "indirect_competitors": len(flooring_stores),
                "big_box_competitors": len(home_improvement),
                "competitors": all_competitors[:20], # Top 20 for display
                "market_saturation": self._calculate_saturation(len(all_competitors), radius_miles)
            }
            
        except Exception as e:
            logger.error(f"Tiles competition collection error: {e}")
            return {"success": False, "error": str(e)}

    async def _search_places(self, query: str, address: str, radius: float) -> List[Dict[str, Any]]:
        """Search for places using Google Places Text Search or Nearby Search"""
        try:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query + " near " + address,
                "radius": radius,
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
                
            results = []
            for item in data.get("results", []):
                results.append({
                    "name": item.get("name"),
                    "address": item.get("formatted_address"),
                    "rating": item.get("rating"),
                    "user_ratings_total": item.get("user_ratings_total"),
                    "location": item.get("geometry", {}).get("location")
                })
            return results
        except Exception:
            return []

    def _merge_results(self, lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        seen = set()
        merged = []
        for l in lists:
            for item in l:
                if item["name"] not in seen:
                    seen.add(item["name"])
                    merged.append(item)
        return merged

    def _calculate_saturation(self, count: int, radius: float) -> str:
        density = count / (radius * radius * 3.14)
        if density > 2.0: return "HIGH"
        if density > 0.5: return "MEDIUM"
        return "LOW"
