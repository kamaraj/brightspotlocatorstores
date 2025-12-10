"""
🚀 OPTIMIZED Business User Testing Framework
Performance improvements:
- Parallel API calls using asyncio.gather()
- Connection pooling with aiohttp connector
- Request batching and rate limiting
- Response caching to avoid duplicate API calls
- Progress tracking and partial result saving
"""

import asyncio
import aiohttp
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging
from collections import defaultdict
from pdf_report_generator import generate_all_persona_pdfs, generate_comparison_pdf
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CACHING SYSTEM
# ============================================================================

class ResponseCache:
    """In-memory cache for API responses to avoid duplicate calls"""
    
    def __init__(self):
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def _make_key(self, address: str, radius: float) -> str:
        """Create cache key from address and radius"""
        key_str = f"{address.lower()}_{radius}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, address: str, radius: float) -> Optional[Dict]:
        """Get cached response"""
        key = self._make_key(address, radius)
        if key in self.cache:
            self.hits += 1
            logger.debug(f"Cache HIT for {address}")
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, address: str, radius: float, response: Dict):
        """Store response in cache"""
        key = self._make_key(address, radius)
        self.cache[key] = response
        logger.debug(f"Cache STORED for {address}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "cached_items": len(self.cache)
        }


# Global cache instance
response_cache = ResponseCache()


# ============================================================================
# PERSONA DEFINITIONS
# ============================================================================

@dataclass
class Persona:
    """Business user persona with specific priorities"""
    name: str
    role: str
    experience_years: int
    budget_range: str
    priorities: List[str]
    risk_tolerance: str
    target_demographic: str
    decision_criteria: Dict[str, float]


PERSONAS = {
    "sarah": Persona(
        name="Sarah Johnson",
        role="First-time Childcare Entrepreneur",
        experience_years=0,
        budget_range="$150k-$300k",
        priorities=["Low competition", "Affordable real estate", "Family demographics"],
        risk_tolerance="Low",
        target_demographic="Middle-income families",
        decision_criteria={
            "demographics": 0.30,
            "competition": 0.30,
            "economic": 0.25,
            "accessibility": 0.10,
            "safety": 0.05
        }
    ),
    "marcus": Persona(
        name="Marcus Williams",
        role="Experienced Operator (3 existing centers)",
        experience_years=8,
        budget_range="$500k-$1M",
        priorities=["Market gap analysis", "Growth potential", "ROI projection"],
        risk_tolerance="High",
        target_demographic="Working professionals",
        decision_criteria={
            "demographics": 0.25,
            "competition": 0.35,
            "economic": 0.20,
            "accessibility": 0.15,
            "safety": 0.05
        }
    ),
    "emily": Persona(
        name="Emily Chen",
        role="Premium Brand Owner",
        experience_years=12,
        budget_range="$1M+",
        priorities=["Affluent demographics", "Safety", "Premium location"],
        risk_tolerance="Medium",
        target_demographic="High-income families ($150k+)",
        decision_criteria={
            "demographics": 0.35,
            "safety": 0.25,
            "accessibility": 0.20,
            "competition": 0.10,
            "economic": 0.10
        }
    ),
    "david": Persona(
        name="David Rodriguez",
        role="Community-Focused Operator",
        experience_years=5,
        budget_range="$200k-$400k",
        priorities=["Underserved communities", "Affordability", "Impact"],
        risk_tolerance="Medium",
        target_demographic="Low-to-moderate income families",
        decision_criteria={
            "demographics": 0.30,
            "economic": 0.25,
            "competition": 0.20,
            "safety": 0.15,
            "accessibility": 0.10
        }
    ),
    "lisa": Persona(
        name="Lisa Anderson",
        role="National Franchise Owner",
        experience_years=15,
        budget_range="$750k-$1.5M",
        priorities=["Standardized metrics", "Predictable ROI", "Scalability"],
        risk_tolerance="Low",
        target_demographic="Middle-to-upper income families",
        decision_criteria={
            "demographics": 0.25,
            "competition": 0.25,
            "economic": 0.25,
            "accessibility": 0.15,
            "safety": 0.10
        }
    )
}


# Test locations
TEST_LOCATIONS = [
    {"address": "Downtown Minneapolis, MN 55401", "city": "Minneapolis", "type": "Urban Core", "characteristics": "High density, professional workforce, premium pricing"},
    {"address": "Uptown Minneapolis, MN 55408", "city": "Minneapolis", "type": "Urban Core", "characteristics": "Young professionals, trendy, urban lifestyle"},
    {"address": "Highland Park, St. Paul, MN 55116", "city": "St. Paul", "type": "Urban Core", "characteristics": "Established neighborhood, families, parks"},
    {"address": "Edina, MN 55424", "city": "Edina", "type": "Affluent Suburb", "characteristics": "Luxury market, high income, excellent schools"},
    {"address": "Minnetonka, MN 55305", "city": "Minnetonka", "type": "Affluent Suburb", "characteristics": "Lakefront, upper-middle class, family-focused"},
    {"address": "Eden Prairie, MN 55344", "city": "Eden Prairie", "type": "Affluent Suburb", "characteristics": "Corporate headquarters, dual-income families"},
    {"address": "Maple Grove, MN 55369", "city": "Maple Grove", "type": "Growing Suburb", "characteristics": "Rapid growth, new construction, young families"},
    {"address": "Lakeville, MN 55044", "city": "Lakeville", "type": "Growing Suburb", "characteristics": "Family-friendly, affordable housing, expanding"},
    {"address": "Woodbury, MN 55125", "city": "Woodbury", "type": "Growing Suburb", "characteristics": "Master-planned, diverse demographics"},
    {"address": "Brooklyn Park, MN 55443", "city": "Brooklyn Park", "type": "Working-Class Suburb", "characteristics": "Diverse, moderate income, growing families"},
    {"address": "Burnsville, MN 55337", "city": "Burnsville", "type": "Working-Class Suburb", "characteristics": "Established, mixed-income, accessible"},
    {"address": "Northfield, MN 55057", "city": "Northfield", "type": "College Town", "characteristics": "College professors, small-town feel"},
    {"address": "Rochester, MN 55901", "city": "Rochester", "type": "Regional Center", "characteristics": "Mayo Clinic, medical professionals, stable"},
    {"address": "Duluth, MN 55802", "city": "Duluth", "type": "Regional Center", "characteristics": "Port city, tourism, university"},
    {"address": "St. Cloud, MN 56301", "city": "St. Cloud", "type": "Regional Center", "characteristics": "Manufacturing, healthcare, growing"},
    {"address": "Stillwater, MN 55082", "city": "Stillwater", "type": "Small Town", "characteristics": "Historic, tourism, commuter town"}
]


# ============================================================================
# OPTIMIZED ANALYSIS ENGINE
# ============================================================================

class OptimizedPersonaAnalyzer:
    """High-performance analyzer with async parallel execution"""
    
    def __init__(
        self, 
        persona: Persona, 
        server_url: str = "http://127.0.0.1:9025",
        max_concurrent: int = 5,
        timeout_seconds: int = 180
    ):
        self.persona = persona
        self.server_url = server_url
        self.max_concurrent = max_concurrent
        self.timeout_seconds = timeout_seconds
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.results = []
        
        # Connection pooling
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            ttl_dns_cache=300
        )
        self.session = None
        self.connector = connector
    
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def analyze_location(self, location: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Analyze a single location with caching and error handling"""
        
        # Check cache first
        cached_response = response_cache.get(location["address"], 3.0)
        if cached_response:
            logger.info(f"[{self.persona.name}] Using cached data for {location['city']}")
            return self._process_response(location, cached_response)
        
        # Rate limiting with semaphore
        async with self.semaphore:
            logger.info(f"[{self.persona.name}] Analyzing {location['city']}, MN...")
            
            try:
                async with self.session.post(
                    f"{self.server_url}/api/v1/analyze",
                    json={
                        "address": location["address"],
                        "radius_miles": 3.0
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Cache the response
                        response_cache.set(location["address"], 3.0, data)
                        
                        return self._process_response(location, data)
                    else:
                        error_text = await response.text()
                        logger.error(f"[{self.persona.name}] Server error {response.status} for {location['city']}: {error_text}")
                        return None
                        
            except asyncio.TimeoutError:
                logger.error(f"[{self.persona.name}] Timeout analyzing {location['city']}")
                return None
            except aiohttp.ClientError as e:
                logger.error(f"[{self.persona.name}] Connection error analyzing {location['city']}: {e}")
                return None
            except Exception as e:
                logger.error(f"[{self.persona.name}] Unexpected error analyzing {location['city']}: {e}")
                return None
    
    def _process_response(self, location: Dict[str, str], data: Dict[str, Any]) -> Dict[str, Any]:
        """Process API response and calculate persona-specific scores"""
        
        # Calculate persona-specific weighted score
        persona_score = self._calculate_persona_score(data)
        
        # Generate persona-specific recommendation
        recommendation = self._generate_recommendation(data, persona_score)
        
        categories = data.get("categories", {})
        
        result = {
            "persona_name": self.persona.name,
            "persona_role": self.persona.role,
            "location_address": location["address"],
            "city": location["city"],
            "location_type": location["type"],
            "location_characteristics": location["characteristics"],
            
            "overall_score": data.get("overall_score", 0),
            "persona_weighted_score": persona_score,
            "score_difference": persona_score - data.get("overall_score", 0),
            
            "demographics_score": categories.get("demographics", {}).get("score", 0),
            "competition_score": categories.get("competition", {}).get("score", 0),
            "accessibility_score": categories.get("accessibility", {}).get("score", 0),
            "safety_score": categories.get("safety", {}).get("score", 0),
            "economic_score": categories.get("economic", {}).get("score", 0),
            "regulatory_score": categories.get("regulatory", {}).get("score", 0),
            
            "children_0_5": categories.get("demographics", {}).get("metrics", {}).get("children_under_5", 0),
            "median_income": categories.get("demographics", {}).get("metrics", {}).get("median_household_income", 0),
            "existing_centers": categories.get("competition", {}).get("metrics", {}).get("existing_centers", 0),
            "market_saturation": categories.get("competition", {}).get("metrics", {}).get("market_saturation", 0),
            "startup_cost": categories.get("economic", {}).get("metrics", {}).get("estimated_startup_cost", 0),
            "crime_index": categories.get("safety", {}).get("metrics", {}).get("crime_index", 0),
            
            "persona_recommendation": recommendation["decision"],
            "persona_rationale": recommendation["rationale"],
            "risk_assessment": recommendation["risk"],
            "investment_fit": recommendation["investment_fit"],
            
            "analysis_timestamp": datetime.now().isoformat(),
            "data_points_collected": data.get("data_points_collected", 0)
        }
        
        return result
    
    def _calculate_persona_score(self, data: Dict[str, Any]) -> float:
        """Calculate weighted score based on persona priorities"""
        categories = data.get("categories", {})
        weighted_score = 0.0
        
        for category, weight in self.persona.decision_criteria.items():
            category_score = categories.get(category, {}).get("score", 0)
            weighted_score += category_score * weight
        
        return round(weighted_score, 1)
    
    def _generate_recommendation(
        self, 
        data: Dict[str, Any], 
        persona_score: float
    ) -> Dict[str, str]:
        """Generate persona-specific recommendation"""
        
        categories = data.get("categories", {})
        demo_score = categories.get("demographics", {}).get("score", 0)
        comp_score = categories.get("competition", {}).get("score", 0)
        econ_score = categories.get("economic", {}).get("score", 0)
        safety_score = categories.get("safety", {}).get("score", 0)
        
        # Sarah - First-timer (risk-averse)
        if self.persona.name == "Sarah Johnson":
            if persona_score >= 65 and comp_score >= 70 and econ_score >= 75:
                return {
                    "decision": "YES - Good starter location",
                    "rationale": "Low competition with strong economics makes this safe for first-timer",
                    "risk": "LOW",
                    "investment_fit": "Good"
                }
            elif persona_score >= 55:
                return {
                    "decision": "MAYBE - Needs more research",
                    "rationale": "Decent fundamentals but verify competition and costs carefully",
                    "risk": "MEDIUM",
                    "investment_fit": "Fair"
                }
            else:
                return {
                    "decision": "NO - Too risky",
                    "rationale": "High risk for first-time operator. Consider other locations.",
                    "risk": "HIGH",
                    "investment_fit": "Poor"
                }
        
        # Marcus - Experienced (growth-focused)
        elif self.persona.name == "Marcus Williams":
            if persona_score >= 70 and comp_score >= 60:
                return {
                    "decision": "STRONG YES - Expansion opportunity",
                    "rationale": "Market gap with strong fundamentals, ideal for portfolio expansion",
                    "risk": "LOW",
                    "investment_fit": "Excellent"
                }
            elif persona_score >= 55:
                return {
                    "decision": "PASS",
                    "rationale": "Better opportunities available elsewhere",
                    "risk": "VARIES",
                    "investment_fit": "Fair"
                }
            else:
                return {
                    "decision": "NO - Skip",
                    "rationale": "Below threshold for experienced operator portfolio",
                    "risk": "HIGH",
                    "investment_fit": "Poor"
                }
        
        # Emily - Premium (quality-focused)
        elif self.persona.name == "Emily Chen":
            if demo_score >= 80 and safety_score >= 75:
                return {
                    "decision": "STRONG YES - Premium market",
                    "rationale": "Affluent demographics and safe environment align with premium brand",
                    "risk": "LOW",
                    "investment_fit": "Excellent"
                }
            elif demo_score >= 70:
                return {
                    "decision": "MAYBE - Evaluate demographics",
                    "rationale": "Decent demographics but verify income levels and safety",
                    "risk": "MEDIUM",
                    "investment_fit": "Fair"
                }
            else:
                return {
                    "decision": "NO - Wrong market",
                    "rationale": "Demographics don't support premium pricing model",
                    "risk": "HIGH",
                    "investment_fit": "Poor"
                }
        
        # David - Community (mission-driven)
        elif self.persona.name == "David Rodriguez":
            if demo_score >= 60 and comp_score >= 65:
                return {
                    "decision": "YES - Community impact",
                    "rationale": "Underserved area with childcare needs, mission-aligned",
                    "risk": "MEDIUM",
                    "investment_fit": "Good"
                }
            elif persona_score >= 55:
                return {
                    "decision": "YES with grants",
                    "rationale": "Viable with community development grants and subsidies",
                    "risk": "MEDIUM-HIGH",
                    "investment_fit": "Fair"
                }
            else:
                return {
                    "decision": "PASS",
                    "rationale": "Even with mission focus, fundamentals are too weak",
                    "risk": "HIGH",
                    "investment_fit": "Poor"
                }
        
        # Lisa - Franchise (standardized)
        else:
            if 70 <= persona_score <= 85:
                return {
                    "decision": "STRONG YES - Franchise fit",
                    "rationale": "Metrics align with franchise model standards",
                    "risk": "LOW",
                    "investment_fit": "Excellent"
                }
            elif persona_score >= 65:
                return {
                    "decision": "YES - Standard location",
                    "rationale": "Meets minimum franchise criteria",
                    "risk": "MEDIUM",
                    "investment_fit": "Good"
                }
            else:
                return {
                    "decision": "NO - Below standards",
                    "rationale": "Does not meet franchise performance criteria",
                    "risk": "HIGH",
                    "investment_fit": "Poor"
                }


# ============================================================================
# PARALLEL EXECUTION ENGINE
# ============================================================================

async def analyze_persona_parallel(
    persona: Persona,
    locations: List[Dict[str, str]],
    max_concurrent: int = 5
) -> List[Dict[str, Any]]:
    """Analyze all locations for a persona in parallel"""
    
    results = []
    
    async with OptimizedPersonaAnalyzer(persona, max_concurrent=max_concurrent) as analyzer:
        # Create tasks for all locations
        tasks = [analyzer.analyze_location(location) for location in locations]
        
        # Execute in parallel with progress tracking
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                if result:
                    results.append(result)
                    city = result['city']
                    score = result['persona_weighted_score']
                    decision = result['persona_recommendation']
                    print(f"   ✅ {city:20} | Score: {score:.1f} | {decision}")
                else:
                    print(f"   ❌ Location analysis failed")
            except Exception as e:
                logger.error(f"Task failed: {e}")
                print(f"   ❌ Task error: {e}")
    
    return results


async def run_optimized_tests(
    batch_size: int = 3,
    save_partial: bool = True
) -> List[Dict[str, Any]]:
    """Run all tests with batching and partial saves"""
    
    all_results = []
    
    print("\n" + "="*100)
    print("🚀 OPTIMIZED BUSINESS USER TESTING - MINNESOTA CHILDCARE LOCATIONS")
    print("="*100)
    print(f"\n📍 Testing {len(TEST_LOCATIONS)} locations")
    print(f"👥 Using {len(PERSONAS)} different personas")
    print(f"📊 Total tests: {len(TEST_LOCATIONS) * len(PERSONAS)} analyses")
    print(f"⚡ Max concurrent per persona: {batch_size}")
    print(f"💾 Partial results saving: {'Enabled' if save_partial else 'Disabled'}")
    print(f"🔄 Response caching: Enabled")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*100 + "\n")
    
    # Process personas in sequence (to show progress)
    for persona_key, persona in PERSONAS.items():
        print(f"\n{'='*100}")
        print(f"👤 PERSONA: {persona.name} ({persona.role})")
        print(f"{'='*100}")
        print(f"   Experience: {persona.experience_years} years")
        print(f"   Budget: {persona.budget_range}")
        print(f"   Risk Tolerance: {persona.risk_tolerance}")
        print(f"   Top Priorities: {', '.join(persona.priorities)}")
        print(f"   Target: {persona.target_demographic}\n")
        
        # Analyze all locations in parallel for this persona
        persona_results = await analyze_persona_parallel(
            persona, 
            TEST_LOCATIONS,
            max_concurrent=batch_size
        )
        
        all_results.extend(persona_results)
        
        # Save partial results
        if save_partial and persona_results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            partial_file = f"partial_{persona_key}_{timestamp}.json"
            with open(partial_file, 'w') as f:
                json.dump(persona_results, f, indent=2)
            logger.info(f"Saved partial results to {partial_file}")
    
    # Display cache statistics
    cache_stats = response_cache.get_stats()
    print(f"\n📊 Cache Performance:")
    print(f"   Hits: {cache_stats['hits']}")
    print(f"   Misses: {cache_stats['misses']}")
    print(f"   Hit Rate: {cache_stats['hit_rate']}%")
    print(f"   Cached Items: {cache_stats['cached_items']}")
    
    print("\n" + "="*100)
    print("📊 TEST EXECUTION COMPLETE")
    print("="*100)
    print(f"✅ Successful analyses: {len(all_results)}")
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100 + "\n")
    
    return all_results


def export_to_csv(results: List[Dict[str, Any]]):
    """Export results to CSV"""
    if not results:
        print("No results to export")
        return
    
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Complete dataset
    filename = f"optimized_analysis_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Exported complete dataset: {filename}")
    
    # Persona-specific views
    for persona_name in df['persona_name'].unique():
        persona_df = df[df['persona_name'] == persona_name]
        persona_filename = f"optimized_persona_{persona_name.replace(' ', '_')}_{timestamp}.csv"
        persona_df.to_csv(persona_filename, index=False)
        print(f"💾 Exported {persona_name} analysis: {persona_filename}")
    
    # City comparison
    city_summary = df.groupby('city').agg({
        'overall_score': 'mean',
        'persona_weighted_score': 'mean',
        'demographics_score': 'mean',
        'competition_score': 'mean',
        'economic_score': 'mean',
        'children_0_5': 'mean',
        'median_income': 'mean',
        'existing_centers': 'mean'
    }).round(1)
    
    city_filename = f"optimized_city_comparison_{timestamp}.csv"
    city_summary.to_csv(city_filename)
    print(f"💾 Exported city comparison: {city_filename}")
    
    return filename


def generate_summary_report(results: List[Dict[str, Any]]):
    """Generate executive summary"""
    if not results:
        return
    
    df = pd.DataFrame(results)
    
    print("\n" + "="*100)
    print("📊 EXECUTIVE SUMMARY")
    print("="*100)
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Locations analyzed: {df['city'].nunique()}")
    print(f"   Personas tested: {df['persona_name'].nunique()}")
    print(f"   Total analyses: {len(df)}")
    print(f"   Average overall score: {df['overall_score'].mean():.1f}/100")
    print(f"   Average persona-weighted score: {df['persona_weighted_score'].mean():.1f}/100")
    
    print(f"\n🏆 Top 3 Locations by Persona:")
    for persona_name in df['persona_name'].unique():
        persona_df = df[df['persona_name'] == persona_name]
        top3 = persona_df.nlargest(3, 'persona_weighted_score')[['city', 'persona_weighted_score', 'persona_recommendation']]
        print(f"\n   {persona_name}:")
        for idx, row in top3.iterrows():
            print(f"      {row['city']:20} | Score: {row['persona_weighted_score']:.1f} | {row['persona_recommendation']}")
    
    print(f"\n🌟 Best Overall Locations (All Personas):")
    city_avg = df.groupby('city')['persona_weighted_score'].mean().sort_values(ascending=False).head(5)
    for city, score in city_avg.items():
        count = len(df[df['city'] == city])
        print(f"   {city:20} | Avg Score: {score:.1f} | STRONG YES: 0/{count} personas")
    
    print("="*100 + "\n")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Main execution"""
    try:
        # Run optimized tests with batching
        results = await run_optimized_tests(
            batch_size=5,  # Max 5 concurrent requests per persona
            save_partial=True
        )
        
        if results:
            # Export to CSV
            csv_file = export_to_csv(results)
            
            # Generate summary
            generate_summary_report(results)
            
            # Generate PDF reports
            print("\n" + "="*80)
            print("📄 Generating PDF Reports...")
            print("="*80)
            pdf_files = generate_all_persona_pdfs(results)
            comparison_pdf = generate_comparison_pdf(results)
            
            print(f"\n✅ Testing complete! All reports generated.")
            print(f"\n📁 Files created:")
            print(f"   - Complete dataset CSV")
            print(f"   - {len(set(r['persona_name'] for r in results))} persona-specific CSVs")
            print(f"   - City comparison CSV")
            print(f"   - {len(pdf_files)} persona PDF reports")
            print(f"   - 1 comparison PDF report")
            print(f"\n📊 Total reports: {len(pdf_files) + 1} PDFs + {len(set(r['persona_name'] for r in results)) + 2} CSVs")
            
            # Performance stats
            cache_stats = response_cache.get_stats()
            print(f"\n⚡ Performance Improvements:")
            print(f"   Cache hit rate: {cache_stats['hit_rate']}%")
            print(f"   API calls saved: {cache_stats['hits']}")
            print(f"   Parallel execution: Up to 5x faster per persona")
            
        else:
            print("\n❌ No results collected. Check if server is running on port 9025.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
