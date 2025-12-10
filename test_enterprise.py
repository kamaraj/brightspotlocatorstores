"""Quick test of all enterprise features"""
import asyncio
from redis_cache import RedisCache
from database import Database
from circuit_breaker import CircuitBreaker

async def test_circuit_breaker():
    """Test circuit breaker"""
    breaker = CircuitBreaker('test_api', failure_threshold=3)
    print(f"✅ Circuit breaker created: {breaker.name}")
    print(f"   State: {breaker.state.value}")
    return breaker.get_status()

def main():
    print("="*60)
    print("🧪 Testing Enterprise Features")
    print("="*60)
    
    # Test 1: Redis Cache
    print("\n1. Testing Redis Cache...")
    cache = RedisCache()
    backend = 'Redis' if cache.enabled else 'In-memory (fallback)'
    print(f"   ✅ Cache backend: {backend}")
    
    cache.set('test_location', 3.0, {'score': 85})
    result = cache.get('test_location', 3.0)
    print(f"   ✅ Cache get/set working: {result['score']}")
    
    # Test 2: Database
    print("\n2. Testing Database...")
    db = Database('test_enterprise.db')
    test_data = {
        'address': 'Test Location',
        'coordinates': {'latitude': 44.0, 'longitude': -93.0},
        'overall_scoring': {'overall_score': 85.5},
        'data_points_collected': 66
    }
    record_id = db.save_analysis('Test Location', test_data)
    print(f"   ✅ Database save working: Record ID {record_id}")
    
    stats = db.get_statistics()
    print(f"   ✅ Database stats: {stats['total_analyses']} analyses")
    
    # Test 3: Circuit Breaker
    print("\n3. Testing Circuit Breaker...")
    status = asyncio.run(test_circuit_breaker())
    print(f"   ✅ Circuit breaker status: {status}")
    
    print("\n" + "="*60)
    print("✅ All enterprise features are working!")
    print("="*60)
    print("\nReady to start production server:")
    print("   python production_server_optimized.py")
    print("="*60)

if __name__ == "__main__":
    main()
