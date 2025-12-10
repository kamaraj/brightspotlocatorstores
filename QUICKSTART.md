# Childcare Location Intelligence System
# Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

**IMPORTANT:** The Microsoft Agent Framework requires the `--pre` flag:

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies (NOTE: --pre flag is CRITICAL for agent-framework)
pip install agent-framework-azure-ai --pre
pip install -r requirements.txt
```

### 2. Configure Environment

```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env and set these REQUIRED variables:
# - GITHUB_TOKEN (get from https://github.com/settings/tokens)
# - GOOGLE_MAPS_API_KEY (get from Google Cloud Console)
# - CENSUS_API_KEY (get from https://api.census.gov/data/key_signup.html)
```

**Minimum Required Configuration:**
```
GITHUB_TOKEN=ghp_your_token_here
GOOGLE_MAPS_API_KEY=your_google_api_key
CENSUS_API_KEY=your_census_api_key
SECRET_KEY=change_this_to_random_32_chars_minimum
```

### 3. Run the Application

```powershell
# Start the server
python run.py
```

The application will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

---

## 📋 Prerequisites

### Required

1. **Python 3.10+**
   ```powershell
   python --version  # Should be 3.10 or higher
   ```

2. **GitHub Personal Access Token**
   - Go to https://github.com/settings/tokens
   - Generate new token (classic)
   - Select scopes: `repo`, `read:org`
   - Copy token to `.env` as `GITHUB_TOKEN`

3. **Google Maps API Key**
   - Go to Google Cloud Console
   - Enable APIs: Geocoding, Places, Distance Matrix
   - Create API key
   - Copy to `.env` as `GOOGLE_MAPS_API_KEY`

4. **U.S. Census API Key** (Free)
   - Sign up at https://api.census.gov/data/key_signup.html
   - Copy key to `.env` as `CENSUS_API_KEY`

### Optional (for production)

- MySQL 8.0+ (location data storage)
- Redis 7+ (caching)
- ChromaDB (vector embeddings)

---

## 🧪 Test the API

### Using cURL (PowerShell)

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health"

# API info
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/info"

# Validate a location
$body = @{
    address = "123 Main St, San Francisco, CA 94102"
    additional_context = "Looking for infant care center"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/validate" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

### Using Python

```python
import requests

# Validate location
response = requests.post(
    "http://localhost:8000/api/v1/validate",
    json={
        "address": "123 Main St, San Francisco, CA 94102",
        "additional_context": "Budget $500K, infant care focus"
    }
)

result = response.json()
print(result["analysis"])
```

### Using Interactive Docs

Visit http://localhost:8000/api/docs for interactive API documentation with built-in testing interface.

---

## 📊 API Endpoints

### Validation

**POST /api/v1/validate**
- Validates a single location
- Returns comprehensive analysis with scores
- Average response time: 60-90 seconds

**POST /api/v1/validate/stream**
- Streaming validation for real-time updates
- Returns analysis chunks as they're generated

### Comparison

**POST /api/v1/compare**
- Compare 2-5 locations side-by-side
- Returns ranked results with differentiators
- Response time: 2-7 minutes (depending on location count)

---

## 🏗️ Project Structure

```
childcare-location-intelligence/
├── app/
│   ├── agents/
│   │   └── location_agent.py      # AI agent with Microsoft Agent Framework
│   ├── api/
│   │   └── routes/
│   │       ├── validation.py      # Validation endpoints
│   │       └── comparison.py      # Comparison endpoints
│   ├── core/
│   │   └── data_collectors/       # Data collection modules
│   │       ├── demographics.py    # Census data
│   │       ├── competition.py     # Google Places
│   │       ├── accessibility.py   # Transit & parking
│   │       ├── safety.py          # Crime & environment
│   │       └── economic.py        # Real estate data
│   ├── config.py                  # Configuration management
│   └── main.py                    # FastAPI application
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── run.py                         # Application launcher
```

---

## 🔧 Configuration Options

### LLM Provider Selection

The system supports multiple LLM providers (priority order):

1. **GitHub Models** (Default, Free Tier)
   ```
   GITHUB_TOKEN=ghp_xxx
   GITHUB_MODEL_ID=gpt-4.1-mini
   ```

2. **Azure OpenAI**
   ```
   AZURE_OPENAI_API_KEY=xxx
   AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT=gpt-4
   ```

3. **OpenAI Direct**
   ```
   OPENAI_API_KEY=sk-xxx
   OPENAI_MODEL=gpt-4o-mini
   ```

### Performance Tuning

```
ANALYSIS_TIMEOUT_SECONDS=90       # Max analysis time
MAX_CONCURRENT_ANALYSES=20        # Concurrent requests
DATA_COLLECTION_TIMEOUT_SECONDS=30  # Per data collector timeout
```

### Feature Flags

```
ENABLE_DISCOVERY_MODE=True        # Location discovery feature
ENABLE_COMPARISON_MODE=True       # Multi-location comparison
ENABLE_BATCH_ANALYSIS=False       # Batch processing (premium)
ENABLE_EXPORT_PDF=True            # PDF report generation
```

---

## 🐛 Troubleshooting

### Error: "agent-framework-azure-ai not found"

**Solution:** Install with `--pre` flag:
```powershell
pip install agent-framework-azure-ai --pre
```

### Error: "No LLM API key configured"

**Solution:** Ensure `.env` has at least one of:
- `GITHUB_TOKEN`
- `AZURE_OPENAI_API_KEY`
- `OPENAI_API_KEY`

### Error: "Geocoding failed" or "API quota exceeded"

**Solution:** Check Google Maps API:
- Verify API key in `.env`
- Enable required APIs in Google Cloud Console
- Check billing/quota limits

### Error: "Census data unavailable"

**Solution:** Check Census API:
- Verify `CENSUS_API_KEY` in `.env`
- Test key at https://api.census.gov/data/2022/acs/acs5?get=B01001_001E&for=state:*&key=YOUR_KEY

### Slow Analysis (>2 minutes)

**Causes:**
- External API rate limits
- Network latency
- Model processing time

**Solutions:**
- Increase `ANALYSIS_TIMEOUT_SECONDS`
- Use faster model (gpt-4.1-mini instead of gpt-4.1)
- Enable caching with Redis

---

## 📖 Next Steps

### For Development

1. **Add Database** (MySQL + Redis)
   ```powershell
   # Using Docker
   docker-compose up -d mysql redis
   ```

2. **Enable Caching**
   ```
   REDIS_HOST=localhost
   CACHE_ENABLED=True
   CACHE_TTL_SECONDS=3600
   ```

3. **Add Authentication**
   - Implement JWT auth in `app/api/middleware/`
   - Protect endpoints with dependencies

### For Production

1. **Environment Setup**
   ```
   ENVIRONMENT=production
   DEBUG=False
   LOG_LEVEL=INFO
   ```

2. **Security Hardening**
   - Set strong `SECRET_KEY` (32+ chars)
   - Enable HTTPS (`FORCE_HTTPS=True`)
   - Configure CORS properly
   - Enable rate limiting

3. **Monitoring**
   - Enable Prometheus metrics
   - Set up Grafana dashboards
   - Configure Sentry for error tracking

4. **Deployment**
   - Use Docker: `docker-compose up -d`
   - Or deploy to cloud (AWS, Azure, GCP)
   - Set up load balancer for multiple workers

---

## 💡 Usage Examples

### Example 1: Single Location Validation

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/validate",
    json={
        "address": "456 Market St, San Francisco, CA 94111",
        "additional_context": "Preschool for ages 3-5",
        "radius_miles": 2.0
    }
)

result = response.json()
if result["success"]:
    print(f"Analysis:\n{result['analysis']}")
    print(f"\nModel: {result['metadata']['model']}")
    print(f"Tool calls: {result['metadata']['tool_calls']}")
```

### Example 2: Compare Multiple Locations

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/compare",
    json={
        "addresses": [
            "123 Main St, Oakland, CA 94607",
            "456 Broadway, Oakland, CA 94612",
            "789 Telegraph Ave, Oakland, CA 94609"
        ],
        "additional_context": "Best location for 100-child center"
    }
)

result = response.json()
if result["success"]:
    print("Individual Analyses:")
    for analysis in result["individual_analyses"]:
        print(f"\n- {analysis['address']}")
    
    print(f"\n\nComparative Summary:\n{result['comparison']}")
```

### Example 3: Streaming Analysis

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/validate/stream",
    json={"address": "123 Main St, San Francisco, CA 94102"},
    stream=True
)

print("Streaming analysis:")
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

---

## 📞 Support

For issues or questions:
- Check documentation in `/docs`
- Review API docs at `/api/docs`
- Enable debug mode: `DEBUG=True` in `.env`

---

## 📄 License

[Add your license here]

---

## 🎯 Key Features

✅ **15 Core Data Points** - Pareto-optimized analysis framework  
✅ **AI-Powered Analysis** - Using GPT-4.1-mini via GitHub Models  
✅ **Real-time Streaming** - Get results as they're generated  
✅ **Multi-location Comparison** - Compare up to 5 locations  
✅ **Explainable AI** - Transparent scoring and recommendations  
✅ **Production-Ready** - FastAPI, async, type-safe, tested  
✅ **Cost-Effective** - $0.02 per analysis using GitHub free tier  

---

**Built with:**
- Microsoft Agent Framework (Python)
- FastAPI
- GitHub Models (GPT-4.1-mini)
- Google Maps Platform APIs
- U.S. Census Bureau API
