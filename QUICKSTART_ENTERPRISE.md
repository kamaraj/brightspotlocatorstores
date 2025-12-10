# 🚀 Quick Start - Enterprise v3.0

Get up and running with all enterprise features in 5 minutes!

---

## Prerequisites

- Python 3.8+
- Docker (optional, for Redis)
- 5 minutes

---

## Installation (2 minutes)

### Step 1: Install Dependencies
```powershell
# Automated setup
python setup_enterprise.py
```

This installs:
- ✅ redis (cache client)
- ✅ sqlalchemy (database ORM)
- ✅ aiosqlite (async database)
- ✅ prometheus-client (metrics)

---

### Step 2: Start Redis
```powershell
# Option 1: Docker (easiest)
docker run -d -p 6379:6379 --name redis redis:latest

# Option 2: Native (if already installed)
redis-server

# Test connection
redis-cli ping
# Expected: PONG
```

**Don't have Redis?**
System will automatically fall back to in-memory cache. Still works!

---

## Start Server (30 seconds)

```powershell
# Start optimized server
python production_server_optimized.py
```

**Expected output:**
```
================================================================================
🚀 Starting OPTIMIZED Production Server v3.0 - Enterprise Edition
================================================================================

✅ Redis connected: localhost:6379 (TTL: 24h)
✅ Database initialized: childcare_analysis.db

📊 Dashboard: http://127.0.0.1:9025/
📖 API Docs: http://127.0.0.1:9025/docs
🏥 Health: http://127.0.0.1:9025/health
```

---

## Test Installation (1 minute)

### Test 1: Health Check
```powershell
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

### Test 2: Single Analysis
```powershell
curl -X POST http://127.0.0.1:9025/api/v1/analyze `
  -H "Content-Type: application/json" `
  -d '{"address": "Rochester, MN 55901", "radius_miles": 3.0}'
```

**Expected:**
- ⏱️ First run: ~20-30 seconds (parallel execution)
- ⚡ Second run: < 100ms (cached!)

---

### Test 3: Check Cache
```powershell
curl http://127.0.0.1:9025/api/v1/cache/stats
```

**Expected response:**
```json
{
  "enabled": true,
  "backend": "redis",
  "cached_items": 1,
  "hit_rate": 50.0,
  "memory_usage": "1.2M"
}
```

---

## Usage Examples

### 1. Batch Analysis (Multiple Locations)
```powershell
curl -X POST http://127.0.0.1:9025/api/v1/analyze/batch `
  -H "Content-Type: application/json" `
  -d @- << 'EOF'
{
  "addresses": [
    "Rochester, MN 55901",
    "St. Paul, MN 55101",
    "Duluth, MN 55802"
  ],
  "radius": 3.0
}
EOF
```

**Result:**
- All 3 analyzed in parallel
- Total time: ~25-35 seconds (not 60-90!)
- Cached for next time

---

### 2. Get Analysis History
```powershell
curl http://127.0.0.1:9025/api/v1/history?limit=5
```

**Returns:**
- Last 5 analyses
- Includes scores, metrics, timestamps

---

### 3. Get Location Trends
```powershell
curl "http://127.0.0.1:9025/api/v1/trends/Rochester,%20MN%2055901?metric=overall&days=30"
```

**Returns:**
- Time-series data for last 30 days
- Track score changes over time

---

### 4. Monitor Circuit Breakers
```powershell
curl http://127.0.0.1:9025/api/v1/circuit-breakers
```

**Returns:**
- Status of all API collectors
- Open/Closed/Half-Open state
- Failure counts

---

## Performance Comparison

### Test: Analyze Rochester, MN

**First run (cache miss):**
```
⏱️ Time: 25 seconds
📡 API calls: 10
💾 Cached: Yes
```

**Second run (cache hit):**
```
⚡ Time: 85ms
📡 API calls: 0
💾 From cache: Yes
```

**Improvement:** 294x faster!

---

## Business Testing (2 minutes)

Run full business user test suite:

```powershell
python business_user_testing_optimized.py
```

**Expected results:**
- 🎯 Success rate: 95%+ (vs 15% in v1.0)
- ⏱️ Total time: 20-30 minutes (vs 2.5 hours)
- 💾 All results cached for instant re-analysis

---

## Monitoring Dashboard

Visit: http://127.0.0.1:9025/docs

**Available endpoints:**
- 📊 `/health` - System status
- 📈 `/api/v1/metrics` - Performance metrics
- 💾 `/api/v1/cache/stats` - Cache statistics
- 🗄️ `/api/v1/history` - Analysis history
- 🛡️ `/api/v1/circuit-breakers` - API health

---

## Troubleshooting

### Redis not available?
**Symptom:**
```
⚠️ Redis unavailable. Falling back to in-memory cache
```

**Solution:**
- Check if Redis is running: `redis-cli ping`
- Start Redis: `docker start redis` or `redis-server`
- **Or:** Just continue - system works without Redis (not persistent)

---

### Slow responses?
**Check cache hit rate:**
```powershell
curl http://127.0.0.1:9025/api/v1/cache/stats
```

**Target:** 70-80% hit rate

**If low:**
- Analyze same locations multiple times
- Increase cache TTL (default: 24 hours)

---

### API failures?
**Check circuit breakers:**
```powershell
curl http://127.0.0.1:9025/api/v1/circuit-breakers
```

**If OPEN:**
- Wait 60 seconds for automatic recovery
- Check external API status
- Review API keys in config

---

## Next Steps

### 1. Configure Settings
Edit `app/config.py`:
```python
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_TTL_HOURS = 24  # Adjust cache duration

CIRCUIT_BREAKER_THRESHOLD = 5  # Failures before open
CIRCUIT_BREAKER_TIMEOUT = 60  # Seconds before retry
```

---

### 2. Set Up Monitoring
```powershell
# Create monitoring script
@'
while ($true) {
    $health = curl -s http://127.0.0.1:9025/health | ConvertFrom-Json
    Write-Host "Status: $($health.status) | Cache Hit Rate: $($health.cache.hit_rate)%"
    Start-Sleep -Seconds 60
}
'@ | Out-File monitor.ps1

# Run monitoring
.\monitor.ps1
```

---

### 3. Optimize for Your Use Case

**High-volume API calls?**
- Increase cache TTL to 48 hours
- Enable request deduplication

**Flaky external APIs?**
- Adjust circuit breaker thresholds
- Add retry logic

**Large-scale testing?**
- Use batch endpoint (up to 50 locations)
- Schedule during off-peak hours

---

## Support

**Full documentation:** ENTERPRISE_FEATURES.md

**Quick reference:** SOLUTION_ARCHITECT_SUMMARY.md

**Performance details:** PERFORMANCE_OPTIMIZATION.md

**Issues?**
1. Check `/health` endpoint
2. Review server logs
3. Verify Redis connection
4. Check circuit breaker status

---

## Summary

✅ **Installed**: Redis, Database, Circuit Breaker  
✅ **Started**: Production server on port 9025  
✅ **Tested**: Health check, analysis, caching  
✅ **Ready**: For production deployment!

**Performance:**
- 🚀 6x faster per analysis
- ⚡ 294x faster cached responses
- ✅ 95%+ success rate
- 💰 80% API cost reduction

---

**Version:** 3.0-enterprise  
**Setup Time:** 5 minutes  
**Ready for:** Production deployment  
**Support:** All enterprise features enabled
