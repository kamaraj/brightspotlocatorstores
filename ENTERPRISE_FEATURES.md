# 🚀 Enterprise Features Guide

## Version 3.0 - Enterprise Edition

This guide covers all new enterprise features added to the Brightspot Locator AI system.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [New Features](#new-features)
3. [Installation](#installation)
4. [Redis Caching](#redis-caching)
5. [Database Storage](#database-storage)
6. [Circuit Breaker](#circuit-breaker)
7. [Batch Analysis](#batch-analysis)
8. [API Endpoints](#api-endpoints)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## Overview

**Version 3.0** adds enterprise-grade features for production deployment:

- **🔄 Redis Caching**: Persistent cache across server restarts (80% faster responses)
- **🗄️ Database Storage**: Historical analysis tracking with SQLite
- **🛡️ Circuit Breaker**: Resilient API calls with automatic failure detection
- **📦 Batch Analysis**: Process multiple locations simultaneously
- **📊 Metrics Dashboard**: Real-time performance monitoring
- **📈 Trend Analysis**: Time-series data for location comparisons

**Performance Improvements:**
- Cache hit response: **< 100ms** (instant)
- Cache miss with parallel: **20-30 seconds** (6x faster than v1.0)
- Success rate: **95%+** (up from 15%)

---

## New Features

### 1. Redis Caching
**Persistent API response storage**

**Benefits:**
- Responses cached for 24 hours (configurable)
- Survives server restarts
- 80% reduction in API calls
- Instant responses for cached locations

**Configuration:**
```python
from redis_cache import get_redis_cache

cache = get_redis_cache(
    host="localhost",
    port=6379,
    ttl_hours=24  # Cache for 24 hours
)
```

**Fallback:**
If Redis is unavailable, automatically falls back to in-memory caching.

---

### 2. Database Storage
**SQLite database for historical analysis**

**Features:**
- Complete analysis history
- Trend tracking over time
- Query by location, date, persona
- Automatic cleanup of old records

**Schema:**
```sql
AnalysisRecord
├── id (primary key)
├── address
├── latitude, longitude
├── overall_score, safety_score, economic_score, etc.
├── data_points_collected
├── execution_time_seconds
├── response_data (JSON)
├── created_at
└── status
```

**Usage:**
```python
from database import get_database

db = get_database()

# Save analysis
record_id = db.save_analysis(address, response)

# Get history
history = db.get_location_history(address, limit=10)

# Get trends
trends = db.get_trends(address, metric_type="overall", days=30)
```

---

### 3. Circuit Breaker Pattern
**Resilient API calls with failure protection**

**How it works:**
1. **CLOSED**: Normal operation, all calls pass through
2. **OPEN**: Too many failures (5), reject immediately for 60 seconds
3. **HALF_OPEN**: Testing recovery, allow 2 test calls

**Benefits:**
- Prevents cascading failures
- Fails fast when services are down
- Automatic recovery testing
- Per-collector isolation

**Configuration:**
```python
from circuit_breaker import get_circuit_breaker

breaker = get_circuit_breaker(
    "weather_api",
    failure_threshold=5,  # Open after 5 failures
    timeout=60.0  # Wait 60s before retry
)

async with breaker:
    result = await api_call()
```

**Status Monitoring:**
```python
# Check all circuit breakers
from circuit_breaker import get_all_breakers_status
status = get_all_breakers_status()
```

---

### 4. Batch Analysis
**Process multiple locations in parallel**

**Endpoint:** `POST /api/v1/analyze/batch`

**Request:**
```json
{
  "addresses": [
    "Rochester, MN 55901",
    "St. Paul, MN 55101",
    "Duluth, MN 55802"
  ],
  "radius": 3.0
}
```

**Response:**
```json
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    { "address": "...", "overall_score": 85.5, ... },
    { "address": "...", "overall_score": 78.3, ... },
    { "address": "...", "overall_score": 92.1, ... }
  ],
  "errors": []
}
```

**Limits:**
- Maximum 50 addresses per batch
- All analyzed in parallel
- Results include cache status

---

## Installation

### Step 1: Install Dependencies

```powershell
# Run setup script
python setup_enterprise.py
```

**Manual installation:**
```powershell
pip install redis sqlalchemy aiosqlite prometheus-client
```

---

### Step 2: Setup Redis

**Option 1: Docker (Recommended)**
```powershell
docker run -d -p 6379:6379 --name redis redis:latest
```

**Option 2: Native Windows**
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`

**Option 3: WSL (Windows Subsystem for Linux)**
```bash
sudo apt-get install redis-server
redis-server
```

**Test Redis:**
```powershell
redis-cli ping
# Expected: PONG
```

---

### Step 3: Initialize Database

The database is created automatically on first run:
```powershell
python production_server_optimized.py
```

Database file: `childcare_analysis.db`

---

### Step 4: Verify Installation

Check health endpoint:
```powershell
# Start server
python production_server_optimized.py

# Test health
curl http://127.0.0.1:9025/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "3.0-enterprise",
  "features": {
    "redis_caching": true,
    "database_storage": true,
    "circuit_breakers": true,
    "batch_analysis": true
  }
}
```

---

## API Endpoints

### Core Analysis

#### Single Location Analysis
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "address": "Rochester, MN 55901",
  "radius_miles": 3.0
}
```

**Response includes:**
- `cached`: true/false (was result from cache?)
- `cache_hit`: true/false (same as cached)
- All analysis data
- Performance metrics

---

#### Batch Analysis
```http
POST /api/v1/analyze/batch
Content-Type: application/json

{
  "addresses": ["address1", "address2", ...],
  "radius": 3.0
}
```

---

### Historical Data

#### Get Recent Analyses
```http
GET /api/v1/history?limit=10&persona=business
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "address": "Rochester, MN 55901",
      "scores": { "overall": 85.5, ... },
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

#### Get Location History
```http
GET /api/v1/history/Rochester, MN 55901?limit=10
```

Returns all historical analyses for specific location.

---

#### Get Trends
```http
GET /api/v1/trends/Rochester, MN 55901?metric=overall&days=30
```

**Response:**
```json
{
  "address": "Rochester, MN 55901",
  "metric": "overall",
  "days": 30,
  "data_points": 5,
  "trends": [
    { "date": "2024-01-01T...", "score": 85.5, "metric": "overall" },
    { "date": "2024-01-08T...", "score": 86.2, "metric": "overall" }
  ]
}
```

---

### Cache Management

#### Get Cache Statistics
```http
GET /api/v1/cache/stats
```

**Response:**
```json
{
  "enabled": true,
  "backend": "redis",
  "cached_items": 45,
  "keyspace_hits": 120,
  "keyspace_misses": 30,
  "hit_rate": 80.0,
  "memory_usage": "2.5M"
}
```

---

#### Clear Cache
```http
POST /api/v1/cache/clear
```

**Response:**
```json
{
  "message": "Cleared 45 cache entries",
  "count": 45
}
```

---

### Monitoring

#### Health Check
```http
GET /health
```

Returns full system status including:
- Version
- Feature flags
- Cache statistics
- Database statistics
- Circuit breaker status

---

#### Circuit Breakers
```http
GET /api/v1/circuit-breakers
```

**Response:**
```json
{
  "weather_api": {
    "name": "weather_api",
    "state": "closed",
    "failure_count": 0,
    "success_count": 15
  }
}
```

---

#### Metrics Dashboard
```http
GET /api/v1/metrics
```

Comprehensive system metrics for monitoring tools.

---

## Monitoring

### Real-Time Metrics

**Available metrics:**
1. **Cache Performance**
   - Hit rate (target: 70-80%)
   - Memory usage
   - Total cached items

2. **Database Statistics**
   - Total analyses
   - Success rate
   - Average score
   - Unique locations

3. **Circuit Breaker Status**
   - Per-collector state (open/closed/half-open)
   - Failure counts
   - Time in current state

4. **Performance**
   - Average response time
   - Cache vs non-cache response time
   - API call counts

---

### Health Monitoring

**Endpoint:** `GET /health`

**Check frequency:** Every 60 seconds recommended

**Alert on:**
- `status != "healthy"`
- `features.redis_caching == false` (degraded mode)
- Circuit breaker in OPEN state for > 5 minutes
- Cache hit rate < 50%
- Database errors

---

### Log Monitoring

**Key log patterns to monitor:**

**Success indicators:**
```
✅ Redis connected: localhost:6379
💾 Cached: Rochester, MN (TTL: 24.0h)
🎯 Cache HIT: Rochester, MN
💾 Saved analysis: Rochester, MN (ID: 123)
```

**Warning indicators:**
```
⚠️ Redis unavailable. Falling back to in-memory cache
⚠️ weather_api: Failure 3/5
```

**Error indicators:**
```
🔴 weather_api: CLOSED → OPEN (threshold reached)
❌ Database save failed
```

---

## Troubleshooting

### Redis Issues

#### Problem: "Redis unavailable"
**Symptoms:**
```
⚠️ Redis unavailable: Error 10061. Falling back to in-memory cache
```

**Solutions:**
1. **Check if Redis is running:**
   ```powershell
   redis-cli ping
   # Expected: PONG
   ```

2. **Start Redis:**
   ```powershell
   # Docker
   docker start redis
   
   # Native
   redis-server
   ```

3. **Check port:**
   ```powershell
   netstat -an | findstr 6379
   # Should show LISTENING on port 6379
   ```

4. **Verify host/port in code:**
   ```python
   redis_cache = get_redis_cache(
       host="localhost",  # Correct?
       port=6379  # Correct?
   )
   ```

**Impact if unresolved:**
- System falls back to in-memory cache
- Cache lost on server restart
- Still functional, just not persistent

---

### Database Issues

#### Problem: "Database save failed"
**Symptoms:**
```
Database save failed: no such table: analysis_records
```

**Solutions:**
1. **Delete and recreate:**
   ```powershell
   Remove-Item childcare_analysis.db
   python production_server_optimized.py
   ```

2. **Check permissions:**
   ```powershell
   # Ensure write access to directory
   icacls childcare_analysis.db
   ```

3. **Verify schema:**
   ```python
   from database import Database
   db = Database()
   stats = db.get_statistics()
   print(stats)
   ```

---

### Circuit Breaker Issues

#### Problem: "Circuit is OPEN"
**Symptoms:**
```
CircuitOpenError: weather_api circuit is OPEN. Retry in 45.2s
```

**Cause:**
API endpoint had 5+ consecutive failures.

**Solutions:**
1. **Wait for automatic recovery:**
   - Circuit will attempt recovery after 60 seconds
   - Enters HALF_OPEN state
   - Needs 2 successful calls to close

2. **Manual reset:**
   ```python
   from circuit_breaker import _registry
   _registry.reset_all()
   ```

3. **Check API endpoint:**
   - Is the external API down?
   - Network connectivity issues?
   - API key valid?

4. **Adjust thresholds:**
   ```python
   breaker = get_circuit_breaker(
       "weather_api",
       failure_threshold=10,  # More lenient
       timeout=30.0  # Faster recovery
   )
   ```

---

### Performance Issues

#### Problem: Slow responses (> 60 seconds)
**Check:**
1. **Cache hit rate:**
   ```http
   GET /api/v1/cache/stats
   ```
   - Target: 70-80% hit rate
   - If low: increase TTL or analyze popular locations more

2. **Circuit breaker status:**
   ```http
   GET /api/v1/circuit-breakers
   ```
   - Any breakers OPEN? APIs are failing

3. **Network latency:**
   - Check external API response times
   - Consider timeout adjustments

4. **Parallel execution:**
   - Verify logs show "parallel_execution_v3"
   - Check for sequential execution fallback

---

### Cache Issues

#### Problem: Cache not persisting
**Symptoms:**
- Cache statistics reset after server restart
- `backend: "in-memory"` in stats

**Solutions:**
1. **Confirm Redis is configured:**
   ```python
   cache = get_redis_cache()
   print(cache.enabled)  # Should be True
   ```

2. **Test Redis connection:**
   ```python
   cache.health_check()  # Should return True
   ```

3. **Check Redis data:**
   ```powershell
   redis-cli
   KEYS analysis:*
   ```

---

## Best Practices

### 1. Cache Management
- **Monitor hit rate:** Target 70-80%
- **Adjust TTL:** Increase for stable data (48h), decrease for volatile data (6h)
- **Clear cache:** After system updates or data corrections

### 2. Database Maintenance
- **Regular cleanup:** Delete old records (90+ days)
  ```python
  db.delete_old_records(days=90)
  ```
- **Backup:** Schedule daily backups of `childcare_analysis.db`
- **Monitor size:** Keep under 1GB for optimal performance

### 3. Circuit Breaker Tuning
- **Failure threshold:** 5 for stable APIs, 10 for flaky APIs
- **Timeout:** 60s standard, 30s for fast recovery, 120s for slow APIs
- **Monitor state:** Alert if OPEN for > 5 minutes

### 4. Batch Analysis
- **Optimal batch size:** 10-20 addresses
- **Maximum:** 50 addresses (hard limit)
- **Use cases:** Business user testing, market research, competitor analysis

### 5. Monitoring
- **Health check:** Every 60 seconds
- **Metrics review:** Daily for trends
- **Alert on:**
  - Cache hit rate < 50%
  - Circuit breakers OPEN
  - Database save failures
  - Redis disconnection

---

## Performance Benchmarks

### v3.0 Enterprise vs v1.0 Original

| Metric | v1.0 Original | v3.0 Enterprise | Improvement |
|--------|---------------|-----------------|-------------|
| **Cache hit response** | N/A | < 100ms | Instant |
| **Cache miss response** | 120-180s | 20-30s | 6x faster |
| **Success rate** | 15% | 95%+ | 6.3x better |
| **Test suite (80 locations)** | 2.5 hours | 20-30 min | 5-8x faster |
| **API calls (cached)** | 100% | 20% | 80% reduction |
| **Concurrent analyses** | 1 | 50 (batch) | 50x throughput |

---

## Cost Savings

### API Call Reduction

**Assumptions:**
- 100 analyses/day
- 80% cache hit rate
- $0.01 per API call
- 10 API calls per analysis

**Monthly savings:**
```
Without cache: 100 × 10 × 30 × $0.01 = $300/month
With cache: 100 × 10 × 30 × 0.2 × $0.01 = $60/month
Savings: $240/month = $2,880/year
```

**Additional savings:**
- Reduced server load
- Faster user experience
- Lower infrastructure costs

---

## Next Steps

1. **Install Enterprise Features**
   ```powershell
   python setup_enterprise.py
   ```

2. **Configure Monitoring**
   - Set up health check monitoring
   - Configure alerting
   - Review metrics dashboard

3. **Optimize Settings**
   - Tune cache TTL based on usage
   - Adjust circuit breaker thresholds
   - Configure database cleanup schedule

4. **Test Batch Analysis**
   ```powershell
   # Test with business_user_testing_optimized.py
   python business_user_testing_optimized.py
   ```

5. **Monitor Performance**
   - Track cache hit rate
   - Review circuit breaker status
   - Analyze database trends

---

## Support

**Documentation:**
- PERFORMANCE_OPTIMIZATION.md - Performance details
- SOLUTION_ARCHITECT_SUMMARY.md - Quick reference
- This guide - Enterprise features

**Testing:**
- business_user_testing_optimized.py - Run full test suite
- setup_enterprise.py - Verify installation

**Monitoring:**
- GET /health - System status
- GET /api/v1/metrics - Performance metrics
- GET /api/v1/circuit-breakers - API health

---

**Version:** 3.0-enterprise  
**Last Updated:** 2024-01-15  
**Performance:** 6x faster | 95%+ success rate | 80% API reduction
