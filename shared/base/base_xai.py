"""
Base XAI (Explainable AI) System
Generates human-readable explanations for scoring decisions
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from shared.base.domain_config import DomainConfig


class BaseXAI(ABC):
    """
    Abstract base class for domain-specific XAI systems
    
    Generates explanations for:
    - Individual data point scores
    - Category scores
    - Overall recommendation
    - Key insights and warnings
    """
    
    def __init__(self, config: DomainConfig):
        """
        Initialize XAI system with domain configuration
        
        Args:
            config: Domain-specific configuration
        """
        self.config = config
        self.domain = config.domain
    
    @abstractmethod
    def explain_data_point(
        self,
        point_name: str,
        value: Any,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for a single data point
        
        Args:
            point_name: Name of the data point
            value: Value of the data point
            context: Additional context (category, related values, etc.)
            
        Returns:
            Human-readable explanation
        """
        pass
    
    @abstractmethod
    def explain_category_score(
        self,
        category_name: str,
        score: float,
        data: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for category score
        
        Args:
            category_name: Name of the category
            score: Category score (0-100)
            data: Category data used in scoring
            
        Returns:
            Human-readable explanation
        """
        pass
    
    @abstractmethod
    def explain_overall_score(
        self,
        overall_score: float,
        category_scores: Dict[str, float]
    ) -> str:
        """
        Generate explanation for overall score
        
        Args:
            overall_score: Overall location score
            category_scores: Individual category scores
            
        Returns:
            Human-readable explanation
        """
        pass
    
    def get_score_descriptor(self, score: float) -> str:
        """
        Get descriptive word for a score
        
        Args:
            score: Score value (0-100)
            
        Returns:
            Descriptor (excellent, very good, good, fair, poor, very poor)
        """
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "very good"
        elif score >= 70:
            return "good"
        elif score >= 60:
            return "fair"
        elif score >= 50:
            return "moderate"
        elif score >= 40:
            return "below average"
        else:
            return "poor"
    
    def generate_warning(
        self,
        category_name: str,
        issue: str,
        severity: str = "medium"
    ) -> Dict[str, str]:
        """
        Generate a warning message
        
        Args:
            category_name: Category with the issue
            issue: Description of the issue
            severity: low, medium, high
            
        Returns:
            Warning dictionary
        """
        icons = {
            "low": "ℹ️",
            "medium": "⚠️",
            "high": "🚨"
        }
        
        return {
            "category": category_name,
            "issue": issue,
            "severity": severity,
            "icon": icons.get(severity, "⚠️")
        }
    
    def generate_insight(
        self,
        insight_type: str,
        message: str
    ) -> Dict[str, str]:
        """
        Generate an insight
        
        Args:
            insight_type: positive, negative, neutral
            message: Insight message
            
        Returns:
            Insight dictionary
        """
        icons = {
            "positive": "✅",
            "negative": "❌",
            "neutral": "💡"
        }
        
        return {
            "type": insight_type,
            "message": message,
            "icon": icons.get(insight_type, "💡")
        }
