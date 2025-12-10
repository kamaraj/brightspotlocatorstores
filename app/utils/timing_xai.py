"""
Timing and Performance Tracking Utilities
Provides millisecond-precision timing for all data collection steps
"""

import time
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TimingMetric:
    """Single timing measurement"""
    step_name: str
    start_time: float
    end_time: float
    duration_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceTracker:
    """
    Tracks execution time for each step with millisecond precision
    
    Usage:
        tracker = PerformanceTracker()
        
        with tracker.track("geocoding"):
            # perform geocoding
            pass
        
        with tracker.track("census_api"):
            # call census API
            pass
        
        report = tracker.get_report()
    """
    
    def __init__(self):
        self.metrics: List[TimingMetric] = []
        self.start_time = time.perf_counter()
        
    @contextmanager
    def track(self, step_name: str, **metadata):
        """
        Context manager to track timing of a code block
        
        Args:
            step_name: Name of the step being tracked
            **metadata: Additional metadata to store
        """
        start = time.perf_counter()
        error = None
        success = True
        
        try:
            yield
        except Exception as e:
            error = str(e)
            success = False
            raise
        finally:
            end = time.perf_counter()
            duration_ms = (end - start) * 1000  # Convert to milliseconds
            
            metric = TimingMetric(
                step_name=step_name,
                start_time=start,
                end_time=end,
                duration_ms=round(duration_ms, 2),
                success=success,
                error=error,
                metadata=metadata
            )
            self.metrics.append(metric)
    
    def get_total_time_ms(self) -> float:
        """Get total elapsed time since tracker creation"""
        return round((time.perf_counter() - self.start_time) * 1000, 2)
    
    def get_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive timing report
        
        Returns:
            Dictionary with timing breakdowns and statistics
        """
        total_tracked = sum(m.duration_ms for m in self.metrics)
        
        # Group by category
        categories = {}
        for metric in self.metrics:
            category = metric.step_name.split('_')[0]  # First part is category
            if category not in categories:
                categories[category] = {
                    'steps': [],
                    'total_ms': 0,
                    'count': 0
                }
            categories[category]['steps'].append({
                'name': metric.step_name,
                'duration_ms': metric.duration_ms,
                'success': metric.success,
                'error': metric.error
            })
            categories[category]['total_ms'] += metric.duration_ms
            categories[category]['count'] += 1
        
        return {
            'total_time_ms': self.get_total_time_ms(),
            'tracked_time_ms': round(total_tracked, 2),
            'overhead_ms': round(self.get_total_time_ms() - total_tracked, 2),
            'steps_count': len(self.metrics),
            'successful_steps': sum(1 for m in self.metrics if m.success),
            'failed_steps': sum(1 for m in self.metrics if not m.success),
            'categories': categories,
            'detailed_steps': [
                {
                    'step': m.step_name,
                    'duration_ms': m.duration_ms,
                    'success': m.success,
                    'error': m.error,
                    'metadata': m.metadata
                }
                for m in self.metrics
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary"""
        report = self.get_report()
        
        lines = [
            "=" * 80,
            "PERFORMANCE REPORT",
            "=" * 80,
            f"Total Time: {report['total_time_ms']:.2f} ms",
            f"Tracked Time: {report['tracked_time_ms']:.2f} ms",
            f"Overhead: {report['overhead_ms']:.2f} ms",
            f"Steps: {report['steps_count']} ({report['successful_steps']} success, {report['failed_steps']} failed)",
            "",
            "Category Breakdown:",
            "-" * 80
        ]
        
        for category, data in sorted(report['categories'].items()):
            lines.append(f"  {category.upper()}: {data['total_ms']:.2f} ms ({data['count']} steps)")
        
        lines.extend(["", "Detailed Steps:", "-" * 80])
        
        for step in report['detailed_steps']:
            status = "✓" if step['success'] else "✗"
            lines.append(f"  {status} {step['step']}: {step['duration_ms']:.2f} ms")
            if step['error']:
                lines.append(f"     Error: {step['error']}")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)


class DataPointExplainer:
    """
    Provides Explainable AI (XAI) justifications for each data point
    """
    
    @staticmethod
    def explain_data_point(
        category: str,
        data_point_name: str,
        value: Any,
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate explanation for a specific data point
        
        Args:
            category: Category name (demographics, competition, etc.)
            data_point_name: Name of the data point
            value: Calculated value
            raw_data: Raw data used in calculation
            
        Returns:
            Dictionary with explanation details
        """
        
        explanations = {
            # Demographics explanations
            "children_0_5_count": {
                "what": "Total number of children aged 0-5 years in the area",
                "how": "Calculated by summing Census variables B01001_003E (males <5) + B01001_027E (females <5)",
                "why": "Direct measure of target market size for childcare services",
                "source": "U.S. Census Bureau ACS 5-Year Estimates",
                "confidence": "HIGH - Direct census data"
            },
            "population_density": {
                "what": "Number of children (0-5) per square mile",
                "how": "children_0_5_count / land_area_sqmi",
                "why": "Indicates market concentration - higher density means more potential customers in smaller radius",
                "source": "Calculated from Census data",
                "confidence": "HIGH - Based on official census data"
            },
            "birth_rate": {
                "what": "Annual births per 1,000 population",
                "how": "(children_0_5 / 5 years) / total_population * 1000",
                "why": "Future demand indicator - shows pipeline of children entering target age",
                "source": "Estimated from Census age distribution",
                "confidence": "MEDIUM - Estimation based on age cohorts"
            },
            "median_household_income": {
                "what": "Median income of households in the area",
                "how": "Direct from Census variable B19013_001E",
                "why": "Ability to pay for childcare services - higher income = higher affordability",
                "source": "U.S. Census Bureau ACS 5-Year",
                "confidence": "HIGH - Direct census data"
            },
            
            # Competition explanations
            "existing_centers_count": {
                "what": "Number of childcare centers within search radius",
                "how": "Google Places API search for keywords: daycare, childcare, preschool (deduplicated by place_id)",
                "why": "Direct measure of competitive intensity - more centers = more competition",
                "source": "Google Places API",
                "confidence": "HIGH - Real-time business data"
            },
            "market_saturation_index": {
                "what": "Childcare centers per square mile",
                "how": "existing_centers_count / (π × radius²)",
                "why": "Density of competition - values >2.0 indicate saturated market",
                "source": "Calculated from Places API data",
                "confidence": "HIGH - Based on verified business locations"
            },
            "avg_competitor_rating": {
                "what": "Average Google rating of competing centers",
                "how": "Sum of all competitor ratings / number of centers with ratings",
                "why": "Quality benchmark - must exceed this to compete effectively",
                "source": "Google Places API ratings",
                "confidence": "HIGH - Based on customer reviews"
            },
            "market_gap_score": {
                "what": "Unmet demand score (0-100, higher = more opportunity)",
                "how": "((estimated_demand - current_supply) / estimated_demand) × 100",
                "why": "Opportunity indicator - score >60 suggests undersupplied market",
                "source": "Calculated from population and capacity data",
                "confidence": "MEDIUM - Based on industry benchmarks (8% need rate)"
            },
            
            # Accessibility explanations
            "transit_score": {
                "what": "Public transit accessibility score (0-100)",
                "how": "Quantity (40pts) + Proximity (50pts) + Quality (10pts) based on transit stations within 1 mile",
                "why": "Parents rely on transit - higher score = more accessible to working parents",
                "source": "Google Places API + Distance calculations",
                "confidence": "HIGH - Based on verified transit locations"
            },
            "avg_commute_minutes": {
                "what": "Average commute time from employment centers",
                "how": "Google Distance Matrix API to major employers, averaged",
                "why": "Drop-off convenience - <20min is ideal for working parents",
                "source": "Google Distance Matrix API",
                "confidence": "HIGH - Real-time traffic data"
            },
            
            # Safety explanations
            "crime_rate_index": {
                "what": "Crime risk score (0-100, lower is better)",
                "how": "Proxy calculation: (risk_indicators × 5) - (safe_indicators × 2), scaled to 0-100",
                "why": "Parent safety concern - score <30 is excellent, >70 is concerning",
                "source": "Estimated from Google Places (schools, bars, etc.)",
                "confidence": "MEDIUM - Proxy indicators, not direct crime data"
            },
            "air_quality_index": {
                "what": "Air quality score (0-500 AQI scale, lower is better)",
                "how": "Base 60 + (pollution_sources × 3) - (parks × 5)",
                "why": "Children's health concern - AQI <100 is acceptable",
                "source": "Estimated from pollution sources (gas stations) and parks",
                "confidence": "LOW - Estimation only, recommend EPA AirNow API for production"
            },
            
            # Economic explanations
            "real_estate_cost_per_sqft": {
                "what": "Commercial real estate cost ($ per square foot)",
                "how": "Base $120 + (premium_amenities × $20), capped at $50-400",
                "why": "Major cost factor - affects rent/purchase decisions",
                "source": "Estimated from neighborhood amenities",
                "confidence": "MEDIUM - Proxy estimation, recommend Zillow/CoStar API"
            },
            "childcare_worker_availability_score": {
                "what": "Labor availability score (0-100, higher = more workers)",
                "how": "50 + (schools × 5) - (existing_centers × 3)",
                "why": "Staffing is critical - score >60 indicates adequate labor pool",
                "source": "Calculated from schools and competitor count",
                "confidence": "MEDIUM - Proxy based on educational institutions"
            },
            
            # Regulatory explanations
            "zoning_compliance_score": {
                "what": "Zoning compatibility score (0-100, higher is better)",
                "how": "Base 50 + (existing_childcare × 10) + (compatible_uses × 3) - (industrial × 10)",
                "why": "Regulatory feasibility - score >60 means likely compliant",
                "source": "Inferred from land use patterns",
                "confidence": "LOW - Estimation only, verify with city zoning office"
            },
            "licensing_difficulty_score": {
                "what": "Licensing complexity score (0-100, lower is easier)",
                "how": "State-based scoring: CA=80, TX=50, etc. + urban adjustment",
                "why": "Time-to-market indicator - score >70 means 120+ days",
                "source": "Historical patterns by state/city",
                "confidence": "MEDIUM - Based on known regulations by jurisdiction"
            }
        }
        
        # Get explanation or provide generic one
        explanation = explanations.get(data_point_name, {
            "what": f"Data point: {data_point_name}",
            "how": "See data collector source code for calculation method",
            "why": "Contributing factor to location suitability",
            "source": f"Category: {category}",
            "confidence": "MEDIUM"
        })
        
        # Add interpretation based on value
        interpretation = DataPointExplainer._interpret_value(
            data_point_name, 
            value
        )
        
        return {
            "data_point": data_point_name,
            "category": category,
            "value": value,
            "explanation": explanation,
            "interpretation": interpretation,
            "raw_data_keys": list(raw_data.keys())[:10]  # Show sources used
        }
    
    @staticmethod
    def _interpret_value(data_point_name: str, value: Any) -> str:
        """Interpret the value (good/fair/poor)"""
        
        # Numeric interpretations
        interpretations = {
            "children_0_5_count": [
                (2000, "EXCELLENT - Large target market"),
                (1000, "GOOD - Adequate target market"),
                (500, "FAIR - Small target market"),
                (0, "POOR - Very limited market")
            ],
            "median_household_income": [
                (100000, "EXCELLENT - High affordability"),
                (75000, "GOOD - Target income range"),
                (50000, "FAIR - Moderate affordability"),
                (0, "POOR - Limited affordability")
            ],
            "crime_rate_index": [  # Inverse - lower is better
                (30, "EXCELLENT - Very safe area"),
                (50, "GOOD - Safe area"),
                (70, "FAIR - Moderate safety concerns"),
                (100, "POOR - High crime area")
            ],
            "market_gap_score": [
                (70, "EXCELLENT - High unmet demand"),
                (50, "GOOD - Balanced market"),
                (30, "FAIR - Competitive market"),
                (0, "POOR - Oversaturated market")
            ],
            "transit_score": [
                (75, "EXCELLENT - Highly accessible"),
                (60, "GOOD - Good transit access"),
                (40, "FAIR - Limited transit"),
                (0, "POOR - No transit access")
            ]
        }
        
        if data_point_name in interpretations:
            if isinstance(value, (int, float)):
                for threshold, interpretation in interpretations[data_point_name]:
                    if value >= threshold:
                        return interpretation
        
        return "See explanation for details"
    
    @staticmethod
    def generate_category_explanation(
        category: str,
        data_points: Dict[str, Any],
        score: float
    ) -> Dict[str, Any]:
        """
        Generate explanation for entire category
        
        Args:
            category: Category name
            data_points: All data points in category
            score: Calculated category score (0-100)
            
        Returns:
            Comprehensive category explanation
        """
        
        # Identify key drivers (top 3 influential points)
        key_drivers = []
        
        if category == "demographics":
            key_drivers = [
                ("children_0_5_count", "Target market size"),
                ("median_household_income", "Affordability"),
                ("dual_income_rate", "Working parent demand")
            ]
        elif category == "competition":
            key_drivers = [
                ("market_gap_score", "Unmet demand"),
                ("market_saturation_index", "Competition density"),
                ("avg_competitor_rating", "Quality benchmark")
            ]
        elif category == "accessibility":
            key_drivers = [
                ("transit_score", "Public transit access"),
                ("avg_commute_minutes", "Commute convenience"),
                ("parking_availability_score", "Vehicle access")
            ]
        elif category == "safety":
            key_drivers = [
                ("crime_rate_index", "Safety perception"),
                ("air_quality_index", "Environmental health"),
                ("neighborhood_safety_perception", "Community quality")
            ]
        elif category == "economic":
            key_drivers = [
                ("real_estate_cost_per_sqft", "Property costs"),
                ("childcare_worker_availability_score", "Labor supply"),
                ("economic_growth_indicator", "Market trends")
            ]
        elif category == "regulatory":
            key_drivers = [
                ("zoning_compliance_score", "Zoning feasibility"),
                ("licensing_difficulty_score", "Regulatory burden"),
                ("avg_permit_processing_days", "Time to market")
            ]
        
        # Score interpretation
        if score >= 75:
            score_interpretation = "EXCELLENT - Strong indicators across category"
        elif score >= 60:
            score_interpretation = "GOOD - Favorable indicators with minor concerns"
        elif score >= 45:
            score_interpretation = "FAIR - Mixed indicators, requires mitigation"
        else:
            score_interpretation = "POOR - Significant challenges in this category"
        
        return {
            "category": category,
            "score": score,
            "interpretation": score_interpretation,
            "key_drivers": key_drivers,
            "data_points_count": len(data_points),
            "recommendation": DataPointExplainer._get_category_recommendation(
                category, 
                score
            )
        }
    
    @staticmethod
    def _get_category_recommendation(category: str, score: float) -> str:
        """Get actionable recommendation based on category score"""
        
        recommendations = {
            "demographics": {
                "high": "Demographics strongly support childcare demand. Proceed with confidence.",
                "medium": "Demographics are adequate. Consider targeted marketing to working families.",
                "low": "Demographics are weak. Consider alternative locations or specialized niche."
            },
            "competition": {
                "high": "Competition is manageable with clear market gaps. Differentiate on quality.",
                "medium": "Moderate competition. Focus on unique value propositions.",
                "low": "High competition or saturated market. Requires premium positioning or reconsider."
            },
            "accessibility": {
                "high": "Excellent accessibility for parents. Highlight convenience in marketing.",
                "medium": "Adequate access. Consider shuttle services to improve convenience.",
                "low": "Poor accessibility. Address parking and transit options or choose better location."
            },
            "safety": {
                "high": "Safe environment is a strong selling point. Emphasize in marketing.",
                "medium": "Safety is acceptable. Monitor ongoing trends and implement security measures.",
                "low": "Safety concerns present. Invest heavily in security or reconsider location."
            },
            "economic": {
                "high": "Economics are favorable. Budget conservatively and proceed.",
                "medium": "Economics are workable. Seek incentives and negotiate costs.",
                "low": "Economics are challenging. Reconsider or seek significant cost reductions."
            },
            "regulatory": {
                "high": "Regulatory path is clear. Begin permit process promptly.",
                "medium": "Regulatory complexity is manageable. Hire experienced consultants.",
                "low": "Regulatory challenges are significant. Extended timeline and costs expected."
            }
        }
        
        level = "high" if score >= 65 else "medium" if score >= 45 else "low"
        return recommendations.get(category, {}).get(level, "Review detailed data points for specific guidance.")
