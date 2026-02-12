# Tile & Flooring Optimizer AI
Production-Ready Location Intelligence System for Tile Dealers & Distributors

## 📊 Six Core Insight Layers

| Insight Layer | API Source | Key Data Point | Status |
|--------------|-----------|----------------|--------|
| **Crime Risk** | FBI CDE | Violent crime rates per county | 🔄 Ready |
| **Environment Risk** | EPA / FEMA | Toxic sites & Flood history | 🔄 Ready |
| **Demographics** | US Census | Median Income & Population Growth | ✅ Active |
| **Rental Base** | HUD User | Fair Market Rent (FMR) prices | 🔄 Ready |
| **Neighborhood Vibe** | Yelp Fusion | Restaurant density & ratings | 🔄 Ready |
| **Walkability** | EPA Index | Walkability Score | 🔄 Ready |

> **📖 Complete API Integration Guide:** See [API_DATA_SOURCES.md](./API_DATA_SOURCES.md)

## 🏗️ Architecture

```
childcare-location-intelligence/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Configuration management
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── location_agent.py     # Main location analysis agent
│   │   └── tools.py               # Agent tools for data collection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── validation.py     # Single location validation
│   │   │   ├── comparison.py     # Multi-location comparison
│   │   │   └── discovery.py      # Market opportunity discovery
│   │   └── middleware/
│   │       ├── __init__.py
│       │       ├── auth.py           # Authentication
│   │       ├── rate_limit.py     # Rate limiting
│   │       └── pii_filter.py     # PII detection
│   ├── core/
│   │   ├── __init__.py
│   │   ├── data_collectors/
│   │   │   ├── __init__.py
│   │   │   ├── demographics.py   # Census API
│   │   │   ├── competition.py    # Google Places
│   │   │   ├── accessibility.py  # Google Distance Matrix
│   │   │   ├── safety.py         # Crime, EPA APIs
│   │   │   └── economic.py       # Real estate data
│   │   ├── scoring/
│   │   │   ├── __init__.py
│   │   │   └── calculator.py     # Score calculation
│   │   └── report/
│   │       ├── __init__.py
│   │       └── generator.py      # PDF/HTML report generation
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── crud.py                # Database operations
│   │   └── vector_store.py        # ChromaDB operations
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── requests.py            # API request schemas
│   │   └── responses.py           # API response schemas
│   └── utils/
│       ├── __init__.py
│       ├── cache.py               # Redis caching
│       ├── logger.py              # Logging configuration
│       └── security.py            # Security utilities
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── map.js
│   │   │   └── charts.js
│   │   └── img/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── validate.html
│       ├── compare.html
│       ├── results.html
│       └── report.html
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_api.py
│   └── test_collectors.py
├── scripts/
│   ├── init_db.py                 # Database initialization
│   └── seed_data.py               # Seed test data
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── docker-compose.yml
├── Dockerfile
├── README.md
└── run.py
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- Redis 7+
- GitHub Personal Access Token (for GitHub Models)

### Installation

```bash
# Clone repository
cd childcare-location-intelligence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies (NOTE: --pre flag required for Agent Framework)
pip install agent-framework-azure-ai --pre
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env with your API keys
# GITHUB_TOKEN=your_github_personal_access_token
# GOOGLE_MAPS_API_KEY=your_google_maps_key
# CENSUS_API_KEY=your_census_key
# ...

# Initialize database
python scripts/init_db.py

# Run application
python run.py
```

### Access
- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **Microsoft Agent Framework** - AI agent orchestration (NOTE: Use --pre flag)
- **GitHub Models** - GPT-4.1-mini for analysis
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM
- **httpx** - Async HTTP client

### Database
- **MySQL 8.0** - Primary data store with spatial extensions
- **Redis 7** - Caching and session management
- **ChromaDB** - Vector embeddings for location similarity

### Frontend
- **Bootstrap 5** - Responsive UI framework
- **Jinja2** - Server-side templates
- **Leaflet** - Interactive maps
- **Chart.js** - Data visualizations
- **Vanilla JavaScript** - Client-side logic

### Monitoring & Security
- **Loguru** - Structured logging
- **Prometheus** - Metrics collection
- **Presidio** - PII detection
- **slowapi** - Rate limiting

## 🔑 API Endpoints

### Validation
```bash
POST /api/v1/validate
# Validate single location
{
  "address": "123 Main St, Dallas, TX",
  "capacity": 100,
  "budget": 500000
}
```

### Comparison
```bash
POST /api/v1/compare
# Compare multiple locations
{
  "addresses": [
    "123 Main St, Dallas, TX",
    "456 Park Ave, Dallas, TX"
  ],
  "capacity": 100
}
```

### Discovery
```bash
POST /api/v1/discover
# Find market opportunities
{
  "city": "Dallas, TX",
  "min_children": 2000,
  "max_competition": 3
}
```

## 🧪 Testing

```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_agent.py -v
```

## 📦 Deployment

### Docker
```bash
# Build image
docker build -t childcare-location-intelligence .

# Run with docker-compose
docker-compose up -d
```

### Production
```bash
# Using systemd service
sudo systemctl start childcare-location

# Or using PM2
pm2 start run.py --name childcare-location
```

## 📈 Performance

- **Analysis Time**: 60-90 seconds per location
- **Concurrent Users**: 20-50 supported
- **API Cost**: ~$0.02 per analysis (GitHub Models)
- **Memory Usage**: ~500MB per worker

## 🔒 Security Features

- JWT authentication
- Rate limiting (10 requests/minute per IP)
- PII detection and redaction
- Input sanitization
- CORS protection
- SQL injection prevention
- XSS protection

## 📝 License

MIT License

## 🤝 Contributing

See CONTRIBUTING.md for details.

## 📞 Support

For issues and questions:
- GitHub Issues: [link]
- Email: support@example.com
- Documentation: [link]
