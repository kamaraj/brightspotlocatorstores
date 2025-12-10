"""
Multi-Domain Location Intelligence Platform
Single codebase supporting multiple industries
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, Any, Optional
from enum import Enum
import asyncio

# Domain enumeration
class Domain(str, Enum):
    CHILDCARE = "childcare"
    BANKING = "banking"
    INSURANCE = "insurance"
    EDUCATION = "education"
    RETAIL = "retail"
    HEALTHCARE = "healthcare"
    FITNESS = "fitness"
    RESTAURANT = "restaurant"


# Domain Configuration
DOMAIN_CONFIG = {
    "childcare": {
        "name": "Brightspot Locator AI",
        "tagline": "Find the Perfect Childcare Center Location",
        "icon": "🎯",
        "categories": {
            "demographics": {"weight": 0.25, "name": "Family Demographics"},
            "competition": {"weight": 0.20, "name": "Market Competition"},
            "accessibility": {"weight": 0.15, "name": "Parent Accessibility"},
            "safety": {"weight": 0.20, "name": "Safety & Environment"},
            "economic": {"weight": 0.10, "name": "Economic Viability"},
            "regulatory": {"weight": 0.10, "name": "Licensing & Compliance"}
        }
    },
    "banking": {
        "name": "BankSite Optimizer",
        "tagline": "Optimize Your Branch Network",
        "icon": "🏦",
        "categories": {
            "demographics": {"weight": 0.25, "name": "Wealth Demographics"},
            "competition": {"weight": 0.20, "name": "Banking Competition"},
            "accessibility": {"weight": 0.15, "name": "Customer Access"},
            "safety": {"weight": 0.20, "name": "Security & Risk"},
            "economic": {"weight": 0.10, "name": "Deposit Potential"},
            "regulatory": {"weight": 0.10, "name": "Banking Regulations"}
        }
    },
    "insurance": {
        "name": "InsurePlace Finder",
        "tagline": "Strategic Insurance Agency Locations",
        "icon": "🛡️",
        "categories": {
            "demographics": {"weight": 0.25, "name": "Insurance Demographics"},
            "competition": {"weight": 0.20, "name": "Agency Competition"},
            "accessibility": {"weight": 0.15, "name": "Client Accessibility"},
            "safety": {"weight": 0.20, "name": "Risk Assessment"},
            "economic": {"weight": 0.10, "name": "Premium Potential"},
            "regulatory": {"weight": 0.10, "name": "Insurance Compliance"}
        }
    },
    "education": {
        "name": "EduHub Locator",
        "tagline": "Find Ideal Learning Center Locations",
        "icon": "📚",
        "categories": {
            "demographics": {"weight": 0.25, "name": "Student Demographics"},
            "competition": {"weight": 0.20, "name": "Educational Landscape"},
            "accessibility": {"weight": 0.15, "name": "Student Accessibility"},
            "safety": {"weight": 0.20, "name": "Safety & Environment"},
            "economic": {"weight": 0.10, "name": "Market Opportunity"},
            "regulatory": {"weight": 0.10, "name": "Education Compliance"}
        }
    }
}


# Domain-specific data collectors factory
class CollectorFactory:
    """Factory pattern to create domain-specific collectors"""
    
    @staticmethod
    def get_demographics_collector(domain: Domain):
        if domain == Domain.CHILDCARE:
            from app.core.data_collectors.demographics import DemographicsCollector
            return DemographicsCollector()
        elif domain == Domain.BANKING:
            from app.core.data_collectors.banking.demographics import BankingDemographicsCollector
            return BankingDemographicsCollector()
        elif domain == Domain.INSURANCE:
            from app.core.data_collectors.insurance.demographics import InsuranceDemographicsCollector
            return InsuranceDemographicsCollector()
        # Add more domains...
    
    @staticmethod
    def get_competition_collector(domain: Domain):
        if domain == Domain.CHILDCARE:
            from app.core.data_collectors.competition_enhanced import CompetitionCollectorEnhanced
            return CompetitionCollectorEnhanced()
        elif domain == Domain.BANKING:
            from app.core.data_collectors.banking.competition import BankingCompetitionCollector
            return BankingCompetitionCollector()
        # Add more domains...


# Domain-specific scoring
class ScoringEngine:
    """Domain-aware scoring logic"""
    
    @staticmethod
    def calculate_category_score(domain: Domain, category: str, data: Dict[str, Any]) -> float:
        """Calculate score based on domain and category"""
        
        if domain == Domain.CHILDCARE:
            return ScoringEngine._score_childcare(category, data)
        elif domain == Domain.BANKING:
            return ScoringEngine._score_banking(category, data)
        elif domain == Domain.INSURANCE:
            return ScoringEngine._score_insurance(category, data)
        
        return 50.0  # Default fallback
    
    @staticmethod
    def _score_childcare(category: str, data: Dict[str, Any]) -> float:
        """Childcare-specific scoring"""
        if category == "demographics":
            return (
                min(100, data.get("children_0_5_count", 0) / 10) * 0.3 +
                min(100, data.get("median_household_income", 0) / 1000) * 0.3 +
                min(100, data.get("dual_income_rate", 0)) * 0.4
            )
        # ... other categories
        return 50.0
    
    @staticmethod
    def _score_banking(category: str, data: Dict[str, Any]) -> float:
        """Banking-specific scoring"""
        if category == "demographics":
            return (
                min(100, data.get("high_income_households", 0) / 100) * 0.4 +
                min(100, data.get("employed_population", 0) / 1000) * 0.3 +
                min(100, data.get("small_business_density", 0)) * 0.3
            )
        # ... other categories
        return 50.0
    
    @staticmethod
    def _score_insurance(category: str, data: Dict[str, Any]) -> float:
        """Insurance-specific scoring"""
        if category == "demographics":
            return (
                min(100, data.get("homeownership_rate", 0)) * 0.4 +
                min(100, data.get("vehicle_ownership_rate", 0)) * 0.3 +
                min(100, data.get("family_household_rate", 0)) * 0.3
            )
        # ... other categories
        return 50.0


# Multi-domain FastAPI app
app = FastAPI(title="Universal Location Intelligence Platform")


@app.get("/")
async def home(request: Request):
    """Landing page with domain selector"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Location Intelligence Platform</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; }
            .domain-card { 
                display: inline-block; 
                margin: 20px; 
                padding: 30px; 
                border: 2px solid #ddd;
                border-radius: 10px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            .domain-card:hover { transform: scale(1.05); }
            .icon { font-size: 48px; }
        </style>
    </head>
    <body>
        <h1>🌍 Universal Location Intelligence</h1>
        <p>Select your industry to analyze locations</p>
        
        <div class="domain-card" onclick="location.href='/childcare/dashboard'">
            <div class="icon">🎯</div>
            <h3>Childcare Centers</h3>
        </div>
        
        <div class="domain-card" onclick="location.href='/banking/dashboard'">
            <div class="icon">🏦</div>
            <h3>Bank Branches</h3>
        </div>
        
        <div class="domain-card" onclick="location.href='/insurance/dashboard'">
            <div class="icon">🛡️</div>
            <h3>Insurance Agencies</h3>
        </div>
        
        <div class="domain-card" onclick="location.href='/education/dashboard'">
            <div class="icon">📚</div>
            <h3>Learning Centers</h3>
        </div>
    </body>
    </html>
    """)


@app.get("/{domain}/dashboard", response_class=HTMLResponse)
async def domain_dashboard(request: Request, domain: Domain):
    """Domain-specific dashboard"""
    config = DOMAIN_CONFIG.get(domain.value, DOMAIN_CONFIG["childcare"])
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{config['name']}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container-fluid">
                <span class="navbar-brand">{config['icon']} {config['name']}</span>
                <span class="text-white">{config['tagline']}</span>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="card">
                <div class="card-body">
                    <h5>Analyze Location for {domain.value.title()}</h5>
                    <form id="analysisForm">
                        <input type="text" class="form-control mb-3" 
                               placeholder="Enter address..." id="address">
                        <button type="submit" class="btn btn-primary">Analyze</button>
                    </form>
                    <div id="results" class="mt-4"></div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('analysisForm').onsubmit = async (e) => {{
                e.preventDefault();
                const address = document.getElementById('address').value;
                
                const response = await fetch('/api/v1/analyze', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        domain: '{domain.value}',
                        address: address
                    }})
                }});
                
                const data = await response.json();
                document.getElementById('results').innerHTML = 
                    `<h4>Overall Score: ${{data.overall_score}}/100</h4>
                     <p>${{data.recommendation}}</p>`;
            }};
        </script>
    </body>
    </html>
    """)


@app.post("/api/v1/analyze")
async def analyze_location(request: Request):
    """Universal analysis endpoint with domain parameter"""
    body = await request.json()
    
    domain = body.get("domain", "childcare")
    address = body.get("address", "")
    radius = body.get("radius_miles", 2.0)
    
    if not address:
        raise HTTPException(status_code=400, detail="Address is required")
    
    # Convert to enum
    domain_enum = Domain(domain)
    
    # Get domain configuration
    config = DOMAIN_CONFIG[domain]
    
    # Create domain-specific collectors
    demographics = CollectorFactory.get_demographics_collector(domain_enum)
    competition = CollectorFactory.get_competition_collector(domain_enum)
    # ... other collectors
    
    # Collect data (same pattern, different collectors)
    results = {}
    results["demographics"] = await demographics.collect(address, radius_miles=radius)
    results["competition"] = await competition.collect(address, radius_miles=radius)
    # ... other categories
    
    # Calculate scores using domain-specific logic
    categories = {}
    for category, data in results.items():
        score = ScoringEngine.calculate_category_score(domain_enum, category, data)
        categories[category] = {
            "score": score,
            "data": data
        }
    
    # Calculate overall score with domain-specific weights
    overall_score = sum(
        categories[cat]["score"] * config["categories"][cat]["weight"]
        for cat in categories.keys()
    )
    
    return JSONResponse({
        "domain": domain,
        "address": address,
        "overall_score": round(overall_score, 1),
        "categories": categories,
        "recommendation": get_recommendation(domain_enum, overall_score)
    })


def get_recommendation(domain: Domain, score: float) -> str:
    """Domain-aware recommendations"""
    if score >= 75:
        messages = {
            Domain.CHILDCARE: "Excellent location for a childcare center",
            Domain.BANKING: "Prime location for a bank branch",
            Domain.INSURANCE: "Ideal location for an insurance agency",
            Domain.EDUCATION: "Perfect spot for a learning center"
        }
        return f"⭐⭐⭐⭐⭐ {messages.get(domain, 'Excellent location')}"
    # ... other score ranges
    return "Location assessment complete"


if __name__ == "__main__":
    import uvicorn
    print("\n🌍 Multi-Domain Location Intelligence Platform")
    print("="*60)
    print("📊 Home: http://127.0.0.1:9025/")
    print("🎯 Childcare: http://127.0.0.1:9025/childcare/dashboard")
    print("🏦 Banking: http://127.0.0.1:9025/banking/dashboard")
    print("🛡️ Insurance: http://127.0.0.1:9025/insurance/dashboard")
    print("📚 Education: http://127.0.0.1:9025/education/dashboard")
    print("="*60)
    
    uvicorn.run(app, host="127.0.0.1", port=9025)
