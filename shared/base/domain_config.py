"""
Domain Configuration System
Defines domain-specific settings, weights, and behaviors
"""

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass, field


class Domain(str, Enum):
    """Supported domains"""
    CHILDCARE = "childcare"
    BANKING = "banking"
    INSURANCE = "insurance"
    EDUCATION = "education"
    RETAIL = "retail"
    HEALTHCARE = "healthcare"
    FITNESS = "fitness"
    RESTAURANT = "restaurant"


@dataclass
class CategoryConfig:
    """Configuration for a single analysis category"""
    name: str  # Display name
    weight: float  # Weight in overall score (0-1, sum to 1.0)
    description: str  # Short description
    data_points: List[str]  # List of expected data point names
    icon: str = "📊"  # Icon for UI
    
    def __post_init__(self):
        """Validate configuration"""
        if not 0 <= self.weight <= 1:
            raise ValueError(f"Weight must be between 0 and 1, got {self.weight}")


@dataclass
class DomainConfig:
    """
    Complete configuration for a domain
    
    Defines:
    - Category structure and weights
    - UI branding (name, tagline, colors)
    - Scoring formulas
    - XAI templates
    - API requirements
    """
    
    # Identity
    domain: Domain
    name: str  # Display name (e.g., "BankSite Optimizer")
    tagline: str
    icon: str  # Emoji
    
    # UI Branding
    primary_color: str  # CSS color
    secondary_color: str
    accent_color: str
    
    # Analysis Categories
    categories: Dict[str, CategoryConfig] = field(default_factory=dict)
    
    # Scoring Configuration
    scoring_formula: str = "weighted_average"  # weighted_average, custom
    min_score: float = 0.0
    max_score: float = 100.0
    
    # Recommendation Thresholds
    excellent_threshold: float = 80.0
    good_threshold: float = 65.0
    moderate_threshold: float = 50.0
    poor_threshold: float = 35.0
    
    # API Requirements
    required_apis: List[str] = field(default_factory=list)
    optional_apis: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate configuration"""
        # Validate category weights sum to 1.0
        total_weight = sum(cat.weight for cat in self.categories.values())
        if not 0.99 <= total_weight <= 1.01:  # Allow small floating point error
            raise ValueError(f"Category weights must sum to 1.0, got {total_weight}")
    
    def get_category_weight(self, category_name: str) -> float:
        """Get weight for a category"""
        return self.categories.get(category_name, CategoryConfig("", 0, "", [])).weight
    
    def get_recommendation(self, score: float) -> str:
        """Get recommendation text based on score"""
        if score >= self.excellent_threshold:
            return "Excellent"
        elif score >= self.good_threshold:
            return "Good"
        elif score >= self.moderate_threshold:
            return "Moderate"
        elif score >= self.poor_threshold:
            return "Poor"
        else:
            return "Not Recommended"


# ============================================================================
# PRE-CONFIGURED DOMAINS
# ============================================================================

def get_childcare_config() -> DomainConfig:
    """Configuration for childcare location intelligence"""
    return DomainConfig(
        domain=Domain.CHILDCARE,
        name="Brightspot Locator AI",
        tagline="Find the perfect location for your childcare center",
        icon="🎯",
        primary_color="#FF6B6B",
        secondary_color="#4ECDC4",
        accent_color="#FFE66D",
        categories={
            "demographics": CategoryConfig(
                name="Family Demographics",
                weight=0.25,
                description="Children population, income, working parents",
                data_points=[
                    "children_0_5_count", "median_household_income",
                    "dual_income_rate", "population_density"
                ],
                icon="👨‍👩‍👧‍👦"
            ),
            "competition": CategoryConfig(
                name="Market Competition",
                weight=0.20,
                description="Existing centers, market saturation",
                data_points=[
                    "existing_centers_count", "market_saturation_index",
                    "market_gap_score"
                ],
                icon="🏫"
            ),
            "accessibility": CategoryConfig(
                name="Accessibility",
                weight=0.15,
                description="Transit, parking, commute times",
                data_points=[
                    "transit_score", "parking_availability",
                    "average_commute_minutes"
                ],
                icon="🚗"
            ),
            "safety": CategoryConfig(
                name="Safety & Environment",
                weight=0.20,
                description="Crime, air quality, flood risk",
                data_points=[
                    "crime_rate_index", "air_quality_index",
                    "flood_risk_score"
                ],
                icon="🛡️"
            ),
            "economic": CategoryConfig(
                name="Economic Viability",
                weight=0.15,
                description="Costs, revenue potential, break-even",
                data_points=[
                    "real_estate_cost_per_sqft", "startup_cost_estimate",
                    "revenue_potential"
                ],
                icon="💰"
            ),
            "regulatory": CategoryConfig(
                name="Regulatory Compliance",
                weight=0.05,
                description="Zoning, licensing requirements",
                data_points=[
                    "zoning_permitted", "licensing_requirements"
                ],
                icon="📋"
            )
        },
        required_apis=["google_maps", "census"],
        optional_apis=["epa", "fbi_crime", "fema", "hud"]
    )


def get_banking_config() -> DomainConfig:
    """Configuration for banking branch location intelligence"""
    return DomainConfig(
        domain=Domain.BANKING,
        name="BankSite Optimizer",
        tagline="Identify high-potential branch locations with precision",
        icon="🏦",
        primary_color="#1E3A8A",  # Dark blue
        secondary_color="#3B82F6",  # Blue
        accent_color="#10B981",  # Green (money)
        categories={
            "demographics": CategoryConfig(
                name="Wealth Demographics",
                weight=0.30,  # Higher weight for banking
                description="Income levels, homeownership, population density",
                data_points=[
                    "median_household_income", "high_income_households",
                    "homeownership_rate", "population_density"
                ],
                icon="💎"
            ),
            "competition": CategoryConfig(
                name="Banking Competition",
                weight=0.25,
                description="Existing branches, market share, FDIC data",
                data_points=[
                    "existing_branches_count", "competitor_deposits",
                    "market_concentration"
                ],
                icon="🏛️"
            ),
            "accessibility": CategoryConfig(
                name="Foot Traffic & Access",
                weight=0.15,
                description="Transit hubs, parking, business districts",
                data_points=[
                    "transit_score", "parking_availability",
                    "business_district_proximity"
                ],
                icon="🚶"
            ),
            "economic": CategoryConfig(
                name="Market Potential",
                weight=0.20,
                description="Deposit potential, loan demand, business activity",
                data_points=[
                    "estimated_deposits", "loan_demand_score",
                    "business_count"
                ],
                icon="📈"
            ),
            "regulatory": CategoryConfig(
                name="Banking Regulations",
                weight=0.10,
                description="CRA requirements, zoning, compliance",
                data_points=[
                    "cra_zone", "zoning_permitted", "fdic_requirements"
                ],
                icon="⚖️"
            )
        },
        excellent_threshold=85.0,
        good_threshold=70.0,
        moderate_threshold=55.0,
        poor_threshold=40.0,
        required_apis=["google_maps", "census"],
        optional_apis=["fdic", "census_business"]
    )


def get_domain_config(domain: Domain) -> DomainConfig:
    """Factory function to get configuration for a domain"""
    configs = {
        Domain.CHILDCARE: get_childcare_config,
        Domain.BANKING: get_banking_config
    }
    
    config_func = configs.get(domain)
    if not config_func:
        raise ValueError(f"No configuration found for domain: {domain}")
    
    return config_func()
