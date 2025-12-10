# System Architecture: 66-Point Childcare Location Intelligence

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATIONS                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   Web UI     │  │  Mobile App  │  │   API Client │                 │
│  │ (Future)     │  │  (Future)    │  │   (Current)  │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
└─────────┼──────────────────┼──────────────────┼────────────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       FASTAPI APPLICATION                               │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    API Routes Layer                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │    │
│  │  │ /validate    │  │ /compare     │  │ /health      │        │    │
│  │  │ Single loc   │  │ Multi-loc    │  │ Status check │        │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────┘        │    │
│  └─────────┼──────────────────┼────────────────────────────────────┘    │
│            │                  │                                         │
│            └──────────┬───────┘                                         │
│                       ▼                                                 │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │            LOCATION ANALYSIS AGENT                           │      │
│  │  ┌────────────────────────────────────────────────────────┐ │      │
│  │  │  Microsoft Agent Framework + GitHub Models (GPT-4.1)   │ │      │
│  │  │  • Orchestrates data collection                        │ │      │
│  │  │  • Synthesizes insights                                │ │      │
│  │  │  • Generates recommendations                           │ │      │
│  │  └────────────────────────────────────────────────────────┘ │      │
│  └──────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   DATA           │ │   DATA       │ │   DATA           │
│   COLLECTORS     │ │   COLLECTORS │ │   COLLECTORS     │
│                  │ │              │ │                  │
│ 1. Demographics  │ │ 3. Safety    │ │ 5. Regulatory    │
│    (15 points)   │ │    (11 pts)  │ │    (8 points)    │
│                  │ │              │ │                  │
│ 2. Competition   │ │ 4. Economic  │ │ 6. Accessibility │
│    (12 points)   │ │    (10 pts)  │ │    (10 points)   │
└────────┬─────────┘ └──────┬───────┘ └────────┬─────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL APIs & DATA SOURCES                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ U.S. Census  │  │ Google Maps  │  │  GitHub      │                 │
│  │ Bureau API   │  │ Platform     │  │  Models API  │                 │
│  │              │  │              │  │              │                 │
│  │ • ACS Data   │  │ • Places     │  │ • GPT-4.1    │                 │
│  │ • Geocoder   │  │ • Geocoding  │  │ • Streaming  │                 │
│  │              │  │ • Distance   │  │              │                 │
│  └──────────────┘  │ • Directions │  └──────────────┘                 │
│                    └──────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Collection Flow (66-Point Analysis)

```
START: User submits address
  │
  ▼
┌────────────────────────────────────────┐
│  1. GEOCODING (All Collectors)         │
│  • Convert address to coordinates      │
│  • Get administrative info             │
│  Time: 1-2 seconds                     │
└──────────────┬─────────────────────────┘
               │
               ├──► PARALLEL EXECUTION ◄────────────────┐
               │                                         │
   ┌───────────┴────────┬───────────────┬───────────────┴────┬──────────────┬──────────────┐
   │                    │               │                    │              │              │
   ▼                    ▼               ▼                    ▼              ▼              ▼
┌──────────┐     ┌──────────┐   ┌──────────┐        ┌──────────┐   ┌──────────┐   ┌──────────┐
│ DEMO (15)│     │ COMP (12)│   │ ACCESS   │        │ SAFETY   │   │ ECONOMIC │   │ REGULATORY│
│          │     │          │   │ (10 pts) │        │ (11 pts) │   │ (10 pts) │   │ (8 points)│
│ Census   │     │ Places   │   │ Maps     │        │ Places   │   │ Places   │   │ Geocoding│
│ API      │     │ API +    │   │ Platform │        │ API +    │   │ API +    │   │ + Places │
│          │     │ Details  │   │ Multi-   │        │ Proxy    │   │ Market   │   │ + Admin  │
│ Real-time│     │ Real-time│   │ API      │        │ Indicators│   │ Signals  │   │ Data     │
│          │     │          │   │ Real-time│        │ Estimated│   │ Estimated│   │ Estimated│
│ 2-3 sec  │     │ 12-20 s  │   │ 20-30 s  │        │ 15-20 s  │   │ 10-15 s  │   │ 8-12 s   │
└──────────┘     └──────────┘   └──────────┘        └──────────┘   └──────────┘   └──────────┘
   │                    │               │                    │              │              │
   └────────────────────┴───────────────┴────────────────────┴──────────────┴──────────────┘
                                         │
                                         ▼
                        ┌────────────────────────────────┐
                        │  DATA AGGREGATION              │
                        │  • Compile all 66 data points  │
                        │  • Structure by category       │
                        │  Time: <1 second               │
                        └────────────┬───────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────────┐
                        │  AI AGENT SYNTHESIS            │
                        │  • Analyze patterns            │
                        │  • Calculate scores            │
                        │  • Generate insights           │
                        │  • Create recommendation       │
                        │  Time: 10-15 seconds           │
                        │  (GitHub Models GPT-4.1-mini)  │
                        └────────────┬───────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────────┐
                        │  RESPONSE GENERATION           │
                        │  • Format results              │
                        │  • Include justification       │
                        │  • Add metadata                │
                        │  Time: <1 second               │
                        └────────────┬───────────────────┘
                                     │
                                     ▼
                              RETURN TO CLIENT
                              
TOTAL TIME: 60-120 seconds
```

## Data Collector Architecture

### 1. Demographics Collector (15 Points)

```
┌──────────────────────────────────────────────┐
│         Demographics Collector               │
├──────────────────────────────────────────────┤
│                                              │
│  Input: Address, Radius (2 miles)           │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Step 1: Geocode Address                │ │
│  │ → Get lat/lng coordinates              │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Step 2: Get Census Geography           │ │
│  │ → State, County, Tract                 │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Step 3: Query ACS 5-Year Data          │ │
│  │ → 20+ Census variables                 │ │
│  │ → B01001, B19013, B23008, etc.         │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Step 4: Calculate Metrics               │ │
│  │ → Population density                    │ │
│  │ → Birth rate                            │ │
│  │ → Income distribution                   │ │
│  │ → Working parent rates                  │ │
│  │ → Growth projections                    │ │
│  │ → Educational attainment                │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Output: 15 data points + metadata          │
│                                              │
└──────────────────────────────────────────────┘
```

### 2. Competition Collector (12 Points)

```
┌──────────────────────────────────────────────┐
│         Competition Collector (Enhanced)     │
├──────────────────────────────────────────────┤
│                                              │
│  Input: Address, Radius (2 miles)           │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Step 1: Search Childcare Centers       │ │
│  │ → Keywords: daycare, childcare, etc.   │ │
│  │ → Google Places Nearby Search          │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Step 2: Get Place Details              │ │
│  │ → Ratings, reviews, hours, phone       │ │
│  │ → Google Places Details API            │ │
│  │ → Top 15 centers analyzed              │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Step 3: Analyze Metrics                 │ │
│  │ → Count & capacity estimation           │ │
│  │ → Market saturation index               │ │
│  │ → Quality benchmarks (4.5+ stars)       │ │
│  │ → Utilization from ratings              │ │
│  │ → Waitlist prevalence from reviews     │ │
│  │ → Demand-supply ratio                   │ │
│  │ → Competitive intensity                 │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Output: 12 data points + center details    │
│                                              │
└──────────────────────────────────────────────┘
```

## Scoring System

```
┌──────────────────────────────────────────────────────────────────┐
│                    CATEGORY SCORING (0-100)                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Raw Data Points                                                 │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────┐                                        │
│  │ Normalization       │  Convert to 0-100 scale                │
│  │ • Min-Max scaling   │                                        │
│  │ • Percentile rank   │                                        │
│  └──────┬──────────────┘                                        │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────┐                                        │
│  │ Category Score      │  Weighted average within category      │
│  │ Demographics: 78.5  │  (weighted by data point importance)   │
│  │ Competition:  65.2  │                                        │
│  │ Accessibility: 82.1 │                                        │
│  │ Safety:       73.8  │                                        │
│  │ Economic:     59.4  │                                        │
│  │ Regulatory:   68.7  │                                        │
│  └──────┬──────────────┘                                        │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────┐                                        │
│  │ Weighted Overall    │  Category weights applied:             │
│  │ Score Calculation   │  • Demographics: 90%                   │
│  │                     │  • Competition:  75%                   │
│  │ Formula:            │  • Accessibility: 65%                  │
│  │ Σ(Cat_Score * Wt)   │  • Safety:       70%                   │
│  │ ─────────────────   │  • Economic:     55%                   │
│  │   Σ(Weights)        │  • Regulatory:   50%                   │
│  │                     │                                        │
│  │ Result: 72.3/100    │  Total weight: 405%                    │
│  └──────┬──────────────┘                                        │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────┐                                        │
│  │ Recommendation      │  Score-based recommendation:           │
│  │                     │  • 75-100: EXCELLENT                   │
│  │ 72.3 = "GOOD"       │  • 60-74:  GOOD                        │
│  │                     │  • 45-59:  FAIR                        │
│  │ "Suitable location  │  • 0-44:   POOR                        │
│  │  with minor         │                                        │
│  │  considerations"    │                                        │
│  └─────────────────────┘                                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    TECHNOLOGY LAYERS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Presentation Layer                                  │    │
│  │ • FastAPI (REST API)                               │    │
│  │ • OpenAPI/Swagger (Auto-generated docs)            │    │
│  │ • CORS middleware (Cross-origin support)           │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Business Logic Layer                                │    │
│  │ • Microsoft Agent Framework (Python preview)        │    │
│  │ • Pydantic (Data validation)                       │    │
│  │ • Async/await (Concurrent processing)              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Data Collection Layer                               │    │
│  │ • httpx (Async HTTP client)                        │    │
│  │ • 6 specialized collectors                         │    │
│  │ • Error handling & fallbacks                       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ AI/ML Layer                                         │    │
│  │ • OpenAI SDK (GitHub Models)                       │    │
│  │ • GPT-4.1-mini (Cost-optimized)                    │    │
│  │ • Streaming support                                │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ External Services                                   │    │
│  │ • U.S. Census Bureau API                           │    │
│  │ • Google Maps Platform                             │    │
│  │ • GitHub Models API                                │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture (Future)

```
┌──────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Load Balancer (Azure Load Balancer / Nginx)       │     │
│  └──────────────┬─────────────────────────────────────┘     │
│                 │                                            │
│     ┌───────────┴───────────┬──────────────┐                │
│     │                       │              │                │
│     ▼                       ▼              ▼                │
│  ┌──────┐              ┌──────┐       ┌──────┐             │
│  │ API  │              │ API  │       │ API  │             │
│  │ Pod 1│              │ Pod 2│       │ Pod 3│             │
│  └──┬───┘              └──┬───┘       └──┬───┘             │
│     │                     │              │                 │
│     └─────────────────────┼──────────────┘                 │
│                           │                                │
│  ┌────────────────────────┴─────────────────────────┐      │
│  │            Shared Services                       │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │      │
│  │  │ Redis    │  │ MySQL    │  │ ChromaDB │       │      │
│  │  │ (Cache)  │  │ (Data)   │  │ (Vector) │       │      │
│  │  └──────────┘  └──────────┘  └──────────┘       │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │            Monitoring & Logging                  │       │
│  │  • Prometheus (Metrics)                          │       │
│  │  • Grafana (Dashboards)                          │       │
│  │  • Loguru → Cloud Logging                        │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

This architecture supports:
- **Scalability**: Multiple API pods behind load balancer
- **Caching**: Redis for repeated analyses
- **Persistence**: MySQL for historical data
- **Monitoring**: Real-time metrics and logging
- **Cost Optimization**: Shared cache reduces API calls
