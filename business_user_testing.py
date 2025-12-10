"""
Business User Testing Framework
Tests childcare location intelligence with synthetic personas across Minnesota

Personas:
1. Sarah - First-time entrepreneur (risk-averse, budget-conscious)
2. Marcus - Experienced operator (expansion-focused, data-driven)
3. Emily - Premium brand owner (quality-focused, high-end market)
4. David - Community-focused (mission-driven, underserved areas)
5. Lisa - Franchise owner (standardized criteria, ROI-focused)
"""

import asyncio
import aiohttp
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import logging
from pdf_report_generator import generate_all_persona_pdfs, generate_comparison_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    priorities: List[str]  # Top 3 priorities
    risk_tolerance: str  # Low, Medium, High
    target_demographic: str
    decision_criteria: Dict[str, float]  # Category weights


# Define 5 distinct personas
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
            "accessibility": 0.15,
            "safety": 0.10
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


# ============================================================================
# MINNESOTA TEST LOCATIONS
# ============================================================================

# Diverse locations across Minnesota representing different market types
TEST_LOCATIONS = [
    # Minneapolis Metro (Urban Core)
    {
        "address": "Downtown Minneapolis, MN 55401",
        "city": "Minneapolis",
        "type": "Urban Core",
        "characteristics": "High density, professional workforce, premium pricing"
    },
    {
        "address": "Uptown Minneapolis, MN 55408",
        "city": "Minneapolis",
        "type": "Urban Trendy",
        "characteristics": "Young families, artistic community, walkable"
    },
    
    # St. Paul
    {
        "address": "Highland Park, St. Paul, MN 55116",
        "city": "St. Paul",
        "type": "Urban Residential",
        "characteristics": "Family-oriented, established neighborhoods"
    },
    
    # Affluent Suburbs
    {
        "address": "Edina, MN 55424",
        "city": "Edina",
        "type": "Affluent Suburb",
        "characteristics": "High income, excellent schools, low crime"
    },
    {
        "address": "Minnetonka, MN 55305",
        "city": "Minnetonka",
        "type": "Affluent Suburb",
        "characteristics": "Lakefront, upper-middle class, family-focused"
    },
    {
        "address": "Eden Prairie, MN 55344",
        "city": "Eden Prairie",
        "type": "Affluent Suburb",
        "characteristics": "Corporate headquarters, dual-income families"
    },
    
    # Growing Suburbs
    {
        "address": "Maple Grove, MN 55369",
        "city": "Maple Grove",
        "type": "Growing Suburb",
        "characteristics": "Rapid growth, new construction, young families"
    },
    {
        "address": "Lakeville, MN 55044",
        "city": "Lakeville",
        "type": "Growing Suburb",
        "characteristics": "Family-friendly, affordable housing, expanding"
    },
    {
        "address": "Woodbury, MN 55125",
        "city": "Woodbury",
        "type": "Growing Suburb",
        "characteristics": "Master-planned, diverse demographics"
    },
    
    # Working-Class Suburbs
    {
        "address": "Brooklyn Park, MN 55443",
        "city": "Brooklyn Park",
        "type": "Working-Class Suburb",
        "characteristics": "Diverse, moderate income, growing families"
    },
    {
        "address": "Burnsville, MN 55337",
        "city": "Burnsville",
        "type": "Working-Class Suburb",
        "characteristics": "Established, mixed-income, accessible"
    },
    
    # College Towns
    {
        "address": "Northfield, MN 55057",
        "city": "Northfield",
        "type": "College Town",
        "characteristics": "College professors, small-town feel"
    },
    
    # Regional Centers
    {
        "address": "Rochester, MN 55901",
        "city": "Rochester",
        "type": "Regional Center",
        "characteristics": "Mayo Clinic, medical professionals, stable"
    },
    {
        "address": "Duluth, MN 55802",
        "city": "Duluth",
        "type": "Regional Center",
        "characteristics": "Port city, tourism, university"
    },
    {
        "address": "St. Cloud, MN 56301",
        "city": "St. Cloud",
        "type": "Regional Center",
        "characteristics": "Manufacturing, healthcare, growing"
    },
    
    # Small Towns
    {
        "address": "Stillwater, MN 55082",
        "city": "Stillwater",
        "type": "Small Town",
        "characteristics": "Historic, tourism, commuter town"
    }
]


# ============================================================================
# ANALYSIS ENGINE
# ============================================================================

class PersonaAnalyzer:
    """Analyzes locations from a specific persona's perspective"""
    
    def __init__(self, persona: Persona, server_url: str = "http://127.0.0.1:9025"):
        self.persona = persona
        self.server_url = server_url
        self.results = []
    
    async def analyze_location(self, location: Dict[str, str]) -> Dict[str, Any]:
        """Analyze a single location from persona's perspective"""
        logger.info(f"[{self.persona.name}] Analyzing {location['city']}, MN...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.server_url}/api/v1/analyze",
                    json={
                        "address": location["address"],
                        "radius_miles": 3.0
                    },
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Calculate persona-specific weighted score
                        persona_score = self._calculate_persona_score(data)
                        
                        # Generate persona-specific recommendation
                        recommendation = self._generate_recommendation(data, persona_score)
                        
                        result = {
                            "persona_name": self.persona.name,
                            "persona_role": self.persona.role,
                            "location_address": location["address"],
                            "city": location["city"],
                            "location_type": location["type"],
                            "location_characteristics": location["characteristics"],
                            
                            # Standard scores
                            "overall_score": data.get("overall_score", 0),
                            
                            # Persona-weighted score
                            "persona_weighted_score": persona_score,
                            "score_difference": persona_score - data.get("overall_score", 0),
                            
                            # Category scores
                            "demographics_score": data.get("categories", {}).get("demographics", {}).get("score", 0),
                            "competition_score": data.get("categories", {}).get("competition", {}).get("score", 0),
                            "accessibility_score": data.get("categories", {}).get("accessibility", {}).get("score", 0),
                            "safety_score": data.get("categories", {}).get("safety", {}).get("score", 0),
                            "economic_score": data.get("categories", {}).get("economic", {}).get("score", 0),
                            "regulatory_score": data.get("categories", {}).get("regulatory", {}).get("score", 0),
                            
                            # Key metrics
                            "children_0_5": data.get("categories", {}).get("demographics", {}).get("data", {}).get("children_0_5_count", 0),
                            "median_income": data.get("categories", {}).get("demographics", {}).get("data", {}).get("median_household_income", 0),
                            "existing_centers": data.get("categories", {}).get("competition", {}).get("data", {}).get("existing_centers_count", 0),
                            "market_saturation": data.get("categories", {}).get("competition", {}).get("data", {}).get("market_saturation_index", 0),
                            "startup_cost": data.get("categories", {}).get("economic", {}).get("data", {}).get("startup_cost_estimate", 0),
                            "crime_index": data.get("categories", {}).get("safety", {}).get("data", {}).get("crime_rate_index", 0),
                            
                            # Persona-specific
                            "persona_recommendation": recommendation["decision"],
                            "persona_rationale": recommendation["rationale"],
                            "risk_assessment": recommendation["risk"],
                            "investment_fit": recommendation["investment_fit"],
                            
                            # Metadata
                            "analysis_timestamp": datetime.now().isoformat(),
                            "data_points_collected": data.get("data_points_collected", 0)
                        }
                        
                        self.results.append(result)
                        return result
                        
                    else:
                        logger.error(f"API error: {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout analyzing {location['city']}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing {location['city']}: {e}")
            return None
    
    def _calculate_persona_score(self, data: Dict[str, Any]) -> float:
        """Calculate weighted score based on persona's priorities"""
        categories = data.get("categories", {})
        total_score = 0.0
        
        for category, weight in self.persona.decision_criteria.items():
            category_score = categories.get(category, {}).get("score", 0)
            total_score += category_score * weight
        
        return round(total_score, 1)
    
    def _generate_recommendation(self, data: Dict[str, Any], persona_score: float) -> Dict[str, str]:
        """Generate persona-specific recommendation"""
        categories = data.get("categories", {})
        
        # Extract key metrics
        demo_score = categories.get("demographics", {}).get("score", 0)
        comp_score = categories.get("competition", {}).get("score", 0)
        econ_score = categories.get("economic", {}).get("score", 0)
        safety_score = categories.get("safety", {}).get("score", 0)
        
        # Persona-specific logic
        if self.persona.name == "Sarah Johnson":  # First-timer
            if persona_score >= 75 and comp_score >= 70 and econ_score >= 65:
                return {
                    "decision": "STRONG YES",
                    "rationale": "Low competition, affordable costs, good demographics - ideal for first center",
                    "risk": "LOW",
                    "investment_fit": "Excellent"
                }
            elif persona_score >= 65:
                return {
                    "decision": "YES with caution",
                    "rationale": "Acceptable metrics but review competition and costs carefully",
                    "risk": "MEDIUM",
                    "investment_fit": "Good"
                }
            else:
                return {
                    "decision": "NO - Too risky",
                    "rationale": "High risk for first-time operator. Consider other locations.",
                    "risk": "HIGH",
                    "investment_fit": "Poor"
                }
        
        elif self.persona.name == "Marcus Williams":  # Experienced
            if persona_score >= 70 and comp_score <= 60:  # Market gap opportunity
                return {
                    "decision": "STRONG YES - Expansion target",
                    "rationale": "Market gap identified, strong ROI potential for experienced operator",
                    "risk": "MEDIUM",
                    "investment_fit": "Excellent"
                }
            elif persona_score >= 65:
                return {
                    "decision": "YES - Worth exploring",
                    "rationale": "Solid fundamentals, consider as expansion location",
                    "risk": "MEDIUM",
                    "investment_fit": "Good"
                }
            else:
                return {
                    "decision": "PASS",
                    "rationale": "Better opportunities available elsewhere",
                    "risk": "VARIES",
                    "investment_fit": "Fair"
                }
        
        elif self.persona.name == "Emily Chen":  # Premium
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
        
        elif self.persona.name == "David Rodriguez":  # Community
            if demo_score >= 60 and comp_score >= 65:  # Underserved + need
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
        
        else:  # Lisa - Franchise
            if 70 <= persona_score <= 85:  # Goldilocks zone
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
# MAIN TEST EXECUTION
# ============================================================================

async def run_all_persona_tests():
    """Run all personas across all locations"""
    all_results = []
    
    print("\n" + "="*100)
    print("🎭 BUSINESS USER TESTING - MINNESOTA CHILDCARE LOCATIONS")
    print("="*100)
    print(f"\n📍 Testing {len(TEST_LOCATIONS)} locations")
    print(f"👥 Using {len(PERSONAS)} different personas")
    print(f"📊 Total tests: {len(TEST_LOCATIONS) * len(PERSONAS)} analyses")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*100 + "\n")
    
    # Test each persona
    for persona_key, persona in PERSONAS.items():
        print(f"\n{'='*100}")
        print(f"👤 PERSONA: {persona.name} ({persona.role})")
        print(f"{'='*100}")
        print(f"   Experience: {persona.experience_years} years")
        print(f"   Budget: {persona.budget_range}")
        print(f"   Risk Tolerance: {persona.risk_tolerance}")
        print(f"   Top Priorities: {', '.join(persona.priorities)}")
        print(f"   Target: {persona.target_demographic}\n")
        
        analyzer = PersonaAnalyzer(persona)
        
        # Analyze each location
        for location in TEST_LOCATIONS:
            result = await analyzer.analyze_location(location)
            if result:
                all_results.append(result)
                print(f"   ✅ {location['city']:20} | Score: {result['persona_weighted_score']:.1f} | {result['persona_recommendation']}")
            else:
                print(f"   ❌ {location['city']:20} | FAILED")
            
            # Small delay between requests
            await asyncio.sleep(0.5)
    
    print("\n" + "="*100)
    print("📊 TEST EXECUTION COMPLETE")
    print("="*100)
    print(f"✅ Successful analyses: {len(all_results)}")
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100 + "\n")
    
    return all_results


def export_to_csv(results: List[Dict[str, Any]]):
    """Export results to CSV for analysis"""
    if not results:
        print("No results to export")
        return
    
    df = pd.DataFrame(results)
    
    # Export complete dataset
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"minnesota_childcare_analysis_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Exported complete dataset: {filename}")
    
    # Export persona-specific views
    for persona_name in df['persona_name'].unique():
        persona_df = df[df['persona_name'] == persona_name]
        persona_filename = f"persona_{persona_name.replace(' ', '_')}_{timestamp}.csv"
        persona_df.to_csv(persona_filename, index=False)
        print(f"💾 Exported {persona_name} analysis: {persona_filename}")
    
    # Export city comparison
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
    
    city_filename = f"city_comparison_{timestamp}.csv"
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
    
    # Overall statistics
    print(f"\n📈 Overall Statistics:")
    print(f"   Locations analyzed: {df['city'].nunique()}")
    print(f"   Personas tested: {df['persona_name'].nunique()}")
    print(f"   Total analyses: {len(df)}")
    print(f"   Average overall score: {df['overall_score'].mean():.1f}/100")
    print(f"   Average persona-weighted score: {df['persona_weighted_score'].mean():.1f}/100")
    
    # Top locations by persona
    print(f"\n🏆 Top 3 Locations by Persona:")
    for persona_name in df['persona_name'].unique():
        persona_df = df[df['persona_name'] == persona_name]
        top3 = persona_df.nlargest(3, 'persona_weighted_score')[['city', 'persona_weighted_score', 'persona_recommendation']]
        print(f"\n   {persona_name}:")
        for idx, row in top3.iterrows():
            print(f"      {row['city']:20} | Score: {row['persona_weighted_score']:.1f} | {row['persona_recommendation']}")
    
    # Best overall locations
    print(f"\n🌟 Best Overall Locations (All Personas):")
    city_avg = df.groupby('city')['persona_weighted_score'].mean().sort_values(ascending=False).head(5)
    for city, score in city_avg.items():
        strong_yes = len(df[(df['city'] == city) & (df['persona_recommendation'].str.contains('STRONG YES'))])
        print(f"   {city:20} | Avg Score: {score:.1f} | STRONG YES: {strong_yes}/5 personas")
    
    # Consensus picks (good for all personas)
    print(f"\n🎯 Consensus Locations (Good for All Personas):")
    consensus = df.groupby('city')['persona_weighted_score'].agg(['mean', 'min']).sort_values('min', ascending=False).head(5)
    for city, row in consensus.iterrows():
        print(f"   {city:20} | Avg: {row['mean']:.1f} | Min: {row['min']:.1f}")
    
    print("\n" + "="*100 + "\n")


async def main():
    """Main execution"""
    try:
        # Run all tests
        results = await run_all_persona_tests()
        
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
            print(f"   - 5 persona-specific CSVs")
            print(f"   - City comparison CSV")
            print(f"   - {len(pdf_files)} persona PDF reports")
            print(f"   - 1 comparison PDF report")
            print(f"\n📊 Total reports: {len(pdf_files) + 1} PDFs + 7 CSVs")
            
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
