"""
Redis Cache Integration for Persistent API Response Storage
Replaces in-memory cache with Redis backend
"""

import redis
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis-backed cache for API responses with TTL support"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        ttl_hours: int = 24,
        password: Optional[str] = None
    ):
        """
        Initialize Redis connection
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Database number
            ttl_hours: Time-to-live in hours for cached data
            password: Redis password (if required)
        """
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False,  # We'll handle JSON encoding
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            self.client.ping()
            self.ttl = timedelta(hours=ttl_hours)
            self.enabled = True
            logger.info(f"✅ Redis connected: {host}:{port} (TTL: {ttl_hours}h)")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"⚠️ Redis unavailable: {e}. Falling back to in-memory cache")
            self.enabled = False
            self.fallback_cache = {}
    
    def _make_key(self, address: str, radius: float) -> str:
        """Generate cache key from address and radius"""
        key_str = f"analysis:{address.lower()}:{radius}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, address: str, radius: float) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response
        
        Returns:
            Dict if found, None if not found
        """
        key = self._make_key(address, radius)
        
        if not self.enabled:
            # Fallback to in-memory
            return self.fallback_cache.get(key)
        
        try:
            data = self.client.get(key)
            if data:
                logger.debug(f"🎯 Cache HIT: {address}")
                return json.loads(data)
            logger.debug(f"❌ Cache MISS: {address}")
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def set(
        self,
        address: str,
        radius: float,
        response: Dict[str, Any],
        ttl_hours: Optional[int] = None
    ):
        """
        Store response in cache with TTL
        
        Args:
            address: Location address
            radius: Search radius
            response: API response data
            ttl_hours: Override default TTL
        """
        key = self._make_key(address, radius)
        
        if not self.enabled:
            # Fallback to in-memory
            self.fallback_cache[key] = response
            return
        
        try:
            ttl = timedelta(hours=ttl_hours) if ttl_hours else self.ttl
            data = json.dumps(response)
            self.client.setex(key, ttl, data)
            logger.debug(f"💾 Cached: {address} (TTL: {ttl.total_seconds()/3600:.1f}h)")
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
    
    def delete(self, address: str, radius: float) -> bool:
        """Delete specific cache entry"""
        key = self._make_key(address, radius)
        
        if not self.enabled:
            return self.fallback_cache.pop(key, None) is not None
        
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    def clear_all(self) -> int:
        """Clear all cached analysis data"""
        if not self.enabled:
            count = len(self.fallback_cache)
            self.fallback_cache.clear()
            return count
        
        try:
            # Delete all keys matching pattern
            keys = self.client.keys("analysis:*")
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis CLEAR error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled:
            return {
                "enabled": False,
                "backend": "in-memory",
                "cached_items": len(self.fallback_cache),
                "memory_usage": "N/A"
            }
        
        try:
            info = self.client.info("stats")
            keys = self.client.keys("analysis:*")
            
            return {
                "enabled": True,
                "backend": "redis",
                "cached_items": len(keys),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
                "memory_usage": self.client.info("memory").get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            logger.error(f"Redis STATS error: {e}")
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate percentage"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return round((hits / total * 100), 2) if total > 0 else 0.0
    
    def health_check(self) -> bool:
        """Check if Redis is healthy"""
        if not self.enabled:
            return False
        
        try:
            return self.client.ping()
        except Exception:
            return False


# Global instance
_redis_cache: Optional[RedisCache] = None


def get_redis_cache(
    host: str = "localhost",
    port: int = 6379,
    ttl_hours: int = 24
) -> RedisCache:
    """
    Get or create global Redis cache instance
    
    Usage:
        cache = get_redis_cache()
        result = cache.get(address, radius)
        if not result:
            result = await fetch_from_api()
            cache.set(address, radius, result)
    """
    global _redis_cache
    
    if _redis_cache is None:
        _redis_cache = RedisCache(host=host, port=port, ttl_hours=ttl_hours)
    
    return _redis_cache


if __name__ == "__main__":
    # Test Redis cache
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Redis Cache...")
    cache = RedisCache()
    
    # Test data
    test_address = "Test Location, MN 55401"
    test_data = {
        "address": test_address,
        "score": 85.5,
        "data_points": 66
    }
    
    # Set
    cache.set(test_address, 3.0, test_data)
    
    # Get
    result = cache.get(test_address, 3.0)
    print(f"Retrieved: {result}")
    
    # Stats
    stats = cache.get_stats()
    print(f"Cache stats: {json.dumps(stats, indent=2)}")
    
    # Clear
    cleared = cache.clear_all()
    print(f"Cleared {cleared} items")
