"""
Banking Domain Scoring Engine
Implements banking-specific scoring logic
"""

import logging
from typing import Dict, Any, List
from shared.base import BaseScoringEngine, DomainConfig, Domain

logger = logging.getLogger(__name__)


class BankingScoringEngine(BaseScoringEngine):
    """
    Scoring engine for banking branch location analysis
    
    Key differences from childcare:
    - Higher weight on wealth demographics (30% vs 25%)
    - Deposit potential calculation
    - Business district proximity matters more
    - CRA (Community Reinvestment Act) compliance
    - Less weight on safety (banks have security)
    - Market concentration analysis (HHI)
    """
    
    def __init__(self, config: DomainConfig):
        if config.domain != Domain.BANKING:
            raise ValueError(f"Expected banking config, got {config.domain}")
        super().__init__(config)
    
    def score_demographics(self, data: Dict[str, Any]) -> float:
        """
        Score demographics for banking (wealth-focused)
        
        Banking priorities:
        - Median income (higher is better)
        - High-income households (key target)
        - Homeownership rate (stability indicator)
        - Population density (foot traffic potential)
        - Business concentration (commercial accounts)
        """
        scores = []
        
        # 1. Median Income Score (30 points)
        median_income = data.get("median_household_income", 0)
        if median_income >= 100000:
            income_score = 100
        elif median_income >= 75000:
            income_score = 80 + ((median_income - 75000) / 25000) * 20
        elif median_income >= 50000:
            income_score = 60 + ((median_income - 50000) / 25000) * 20
        else:
            income_score = (median_income / 50000) * 60
        scores.append(income_score * 0.30)
        
        # 2. High-Income Households Score (25 points)
        # Households earning $100K+
        high_income_rate = data.get("high_income_rate", 0)  # Percentage
        high_income_score = min(100, high_income_rate * 2)  # 50% = 100 score
        scores.append(high_income_score * 0.25)
        
        # 3. Homeownership Rate (20 points)
        # Higher homeownership = stable market, mortgage business
        homeownership = data.get("homeownership_rate", 0)  # Percentage
        homeowner_score = homeownership  # 70% = 70 score
        scores.append(homeowner_score * 0.20)
        
        # 4. Population Density (15 points)
        # Moderate density is ideal (not too sparse, not too crowded)
        density = data.get("population_density", 0)
        if 3000 <= density <= 10000:
            density_score = 100  # Sweet spot
        elif density < 3000:
            density_score = (density / 3000) * 80
        else:
            density_score = max(60, 100 - ((density - 10000) / 1000) * 2)
        scores.append(density_score * 0.15)
        
        # 5. Business Presence (10 points)
        # Number of businesses (commercial banking potential)
        business_density = data.get("business_density_score", 50)
        scores.append(business_density * 0.10)
        
        return sum(scores)
    
    def score_competition(self, data: Dict[str, Any]) -> float:
        """
        Score competition for banking
        
        Uses HHI (Herfindahl-Hirschman Index) for market concentration
        Lower competition (high HHI) can be good if market is underserved
        """
        scores = []
        
        # 1. Branch Density Score (40 points)
        # Ideal: 1-3 branches within 5 miles (opportunity exists, not saturated)
        branch_count = data.get("existing_branches_count", 0)
        if branch_count == 0:
            branch_score = 60  # Risky - might be low demand
        elif 1 <= branch_count <= 3:
            branch_score = 100  # Sweet spot
        elif 4 <= branch_count <= 6:
            branch_score = 80
        elif 7 <= branch_count <= 10:
            branch_score = 60
        else:
            branch_score = max(30, 100 - (branch_count - 10) * 5)
        scores.append(branch_score * 0.40)
        
        # 2. Market Concentration (HHI) Score (30 points)
        # Low HHI (<1500) = competitive market = harder entry
        # High HHI (>2500) = concentrated market = potential opportunity
        hhi = data.get("hhi_index", 1500)
        if hhi < 1500:
            hhi_score = 60  # Very competitive
        elif hhi < 2000:
            hhi_score = 75
        elif hhi < 2500:
            hhi_score = 85
        else:
            hhi_score = 100  # Monopolistic - big opportunity if you can enter
        scores.append(hhi_score * 0.30)
        
        # 3. Top Competitor Market Share (20 points)
        # If one player dominates (>40% share), it's harder
        top_share = data.get("top_competitor_market_share", 0)
        if top_share > 50:
            share_score = 40  # Monopoly
        elif top_share > 40:
            share_score = 60
        elif top_share > 30:
            share_score = 80
        else:
            share_score = 100  # Fragmented market
        scores.append(share_score * 0.20)
        
        # 4. Service Type Distribution (10 points)
        # Mix of full-service and limited-service is healthy
        full_service = data.get("full_service_branches", 0)
        total_branches = data.get("existing_branches_count", 1)
        if total_branches > 0:
            full_service_ratio = full_service / total_branches
            service_score = 100 if 0.6 <= full_service_ratio <= 0.9 else 70
        else:
            service_score = 50
        scores.append(service_score * 0.10)
        
        return sum(scores)
    
    def score_accessibility(self, data: Dict[str, Any]) -> float:
        """
        Score accessibility for banking
        
        Banking priorities:
        - Business district proximity (commercial clients)
        - Parking availability (customers drive to banks)
        - Transit access (foot traffic)
        - Visibility from major roads
        """
        scores = []
        
        # 1. Transit Score (25 points)
        transit_score = data.get("transit_score", 0)
        scores.append(transit_score * 0.25)
        
        # 2. Parking Availability (35 points) - MORE important for banks
        parking_score = data.get("parking_availability_score", 0)
        scores.append(parking_score * 0.35)
        
        # 3. Business District Proximity (30 points)
        business_proximity = data.get("business_district_score", 50)
        scores.append(business_proximity * 0.30)
        
        # 4. Highway Access (10 points)
        highway_distance = data.get("highway_distance_miles", 10)
        if highway_distance < 0.5:
            highway_score = 100
        elif highway_distance < 2:
            highway_score = 80
        elif highway_distance < 5:
            highway_score = 60
        else:
            highway_score = 40
        scores.append(highway_score * 0.10)
        
        return sum(scores)
    
    def score_economic_potential(self, data: Dict[str, Any]) -> float:
        """
        Score economic potential for banking
        
        Focus on deposit potential, loan demand, and business activity
        """
        scores = []
        
        # 1. Deposit Potential (40 points)
        # Estimated based on income and population
        estimated_deposits = data.get("estimated_deposits_millions", 0)
        if estimated_deposits >= 100:
            deposit_score = 100
        elif estimated_deposits >= 50:
            deposit_score = 80
        elif estimated_deposits >= 20:
            deposit_score = 60
        else:
            deposit_score = (estimated_deposits / 20) * 60
        scores.append(deposit_score * 0.40)
        
        # 2. Loan Demand Score (30 points)
        loan_demand = data.get("loan_demand_score", 50)
        scores.append(loan_demand * 0.30)
        
        # 3. Business Activity (20 points)
        business_count = data.get("business_count", 0)
        if business_count >= 500:
            business_score = 100
        elif business_count >= 200:
            business_score = 80
        elif business_count >= 100:
            business_score = 60
        else:
            business_score = (business_count / 100) * 60
        scores.append(business_score * 0.20)
        
        # 4. Real Estate Cost (10 points)
        # Lower cost = better ROI (inverse of typical scoring)
        real_estate_cost = data.get("real_estate_cost_per_sqft", 200)
        if real_estate_cost < 100:
            cost_score = 100
        elif real_estate_cost < 200:
            cost_score = 80
        elif real_estate_cost < 300:
            cost_score = 60
        else:
            cost_score = max(30, 100 - (real_estate_cost - 300) / 10)
        scores.append(cost_score * 0.10)
        
        return sum(scores)
    
    def score_regulatory_compliance(self, data: Dict[str, Any]) -> float:
        """
        Score regulatory environment for banking
        
        Includes CRA requirements, zoning, FDIC compliance
        """
        scores = []
        
        # 1. CRA Zone Qualification (50 points)
        # Community Reinvestment Act - bonus for low-income areas
        cra_qualified = data.get("cra_qualified", False)
        cra_income_level = data.get("cra_income_level", "moderate")
        
        if cra_qualified and cra_income_level == "low":
            cra_score = 100  # Maximum CRA credit
        elif cra_qualified and cra_income_level == "moderate":
            cra_score = 85
        elif cra_qualified:
            cra_score = 70
        else:
            cra_score = 50  # Neutral
        scores.append(cra_score * 0.50)
        
        # 2. Zoning Compliance (30 points)
        zoning_permitted = data.get("zoning_permitted", False)
        zoning_score = 100 if zoning_permitted else 30
        scores.append(zoning_score * 0.30)
        
        # 3. FDIC Requirements (20 points)
        # Placeholder - would check actual FDIC rules
        fdic_compliant = data.get("fdic_compliant", True)
        fdic_score = 100 if fdic_compliant else 40
        scores.append(fdic_score * 0.20)
        
        return sum(scores)
    
    def get_key_insights(
        self,
        category_scores: Dict[str, float],
        category_data: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        Generate banking-specific key insights
        """
        insights = []
        
        # Demographics insights
        demo_data = category_data.get("demographics", {})
        median_income = demo_data.get("median_household_income", 0)
        if median_income >= 100000:
            insights.append(f"💎 High-wealth area: Median income ${median_income:,} (Excellent for private banking)")
        elif median_income >= 75000:
            insights.append(f"💰 Affluent demographics: Median income ${median_income:,}")
        
        # Competition insights
        comp_data = category_data.get("competition", {})
        branch_count = comp_data.get("existing_branches_count", 0)
        hhi = comp_data.get("hhi_index", 0)
        
        if branch_count == 0:
            insights.append("🎯 No existing branches - Blue ocean opportunity (validate demand)")
        elif branch_count <= 3:
            insights.append(f"✅ Moderate competition: {branch_count} branches (Room for new entrant)")
        elif branch_count >= 10:
            insights.append(f"⚠️ Saturated market: {branch_count} branches (Differentiation required)")
        
        if hhi > 2500:
            insights.append(f"📊 Concentrated market (HHI: {hhi:.0f}) - Potential to disrupt dominant players")
        elif hhi < 1500:
            insights.append(f"📊 Highly competitive market (HHI: {hhi:.0f}) - Strong differentiation needed")
        
        # Economic insights
        econ_data = category_data.get("economic", {})
        deposits = econ_data.get("estimated_deposits_millions", 0)
        if deposits >= 100:
            insights.append(f"💵 High deposit potential: ${deposits:.1f}M (Prime location)")
        elif deposits >= 50:
            insights.append(f"💵 Strong deposit potential: ${deposits:.1f}M")
        
        # Regulatory insights
        reg_data = category_data.get("regulatory", {})
        if reg_data.get("cra_qualified"):
            insights.append("⭐ CRA-qualified area - Community investment credit available")
        
        return insights
