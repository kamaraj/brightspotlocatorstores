"""
Base Scoring Engine
Domain-specific scoring engines inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from shared.base.domain_config import DomainConfig


class BaseScoringEngine(ABC):
    """
    Abstract base class for domain-specific scoring engines
    
    Each domain implements its own scoring logic based on:
    - Domain-specific category weights
    - Industry-specific formulas
    - Custom business rules
    """
    
    def __init__(self, config: DomainConfig):
        """
        Initialize scoring engine with domain configuration
        
        Args:
            config: Domain-specific configuration
        """
        self.config = config
        self.domain = config.domain
    
    def calculate_overall_score(
        self,
        category_scores: Dict[str, float]
    ) -> float:
        """
        Calculate overall weighted score from category scores
        
        Args:
            category_scores: Dictionary of category_name -> score (0-100)
            
        Returns:
            Overall weighted score (0-100)
        """
        total_score = 0.0
        total_weight = 0.0
        
        for category_name, score in category_scores.items():
            weight = self.config.get_category_weight(category_name)
            if weight > 0:
                total_score += score * weight
                total_weight += weight
        
        # Normalize if weights don't sum to exactly 1.0
        if total_weight > 0:
            return total_score / total_weight
        
        return 0.0
    
    @abstractmethod
    def score_demographics(self, data: Dict[str, Any]) -> float:
        """
        Score demographics category (domain-specific logic)
        
        Args:
            data: Demographic data
            
        Returns:
            Score from 0-100
        """
        pass
    
    @abstractmethod
    def score_competition(self, data: Dict[str, Any]) -> float:
        """
        Score competition category (domain-specific logic)
        
        Args:
            data: Competition data
            
        Returns:
            Score from 0-100
        """
        pass
    
    @abstractmethod
    def score_accessibility(self, data: Dict[str, Any]) -> float:
        """
        Score accessibility category (domain-specific logic)
        
        Args:
            data: Accessibility data
            
        Returns:
            Score from 0-100
        """
        pass
    
    @abstractmethod
    def get_key_insights(
        self,
        category_scores: Dict[str, float],
        category_data: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        Generate domain-specific key insights
        
        Args:
            category_scores: Category scores
            category_data: Raw data for each category
            
        Returns:
            List of insight strings
        """
        pass
    
    def get_recommendation(self, overall_score: float) -> str:
        """
        Get recommendation text based on overall score
        
        Args:
            overall_score: Overall location score (0-100)
            
        Returns:
            Recommendation text
        """
        return self.config.get_recommendation(overall_score)
    
    def get_score_tier(self, score: float) -> str:
        """
        Get descriptive tier for a score
        
        Args:
            score: Score value (0-100)
            
        Returns:
            Tier name (Excellent, Good, Moderate, Poor, Critical)
        """
        if score >= self.config.excellent_threshold:
            return "Excellent"
        elif score >= self.config.good_threshold:
            return "Good"
        elif score >= self.config.moderate_threshold:
            return "Moderate"
        elif score >= self.config.poor_threshold:
            return "Poor"
        else:
            return "Critical"
    
    @staticmethod
    def normalize_score(
        value: float,
        min_val: float,
        max_val: float,
        inverse: bool = False
    ) -> float:
        """
        Normalize a value to 0-100 score
        
        Args:
            value: Value to normalize
            min_val: Minimum expected value
            max_val: Maximum expected value
            inverse: If True, higher values = lower scores (e.g., crime rate)
            
        Returns:
            Normalized score (0-100)
        """
        if max_val == min_val:
            return 50.0  # Middle score if no range
        
        # Clamp value to range
        value = max(min_val, min(max_val, value))
        
        # Normalize to 0-1
        normalized = (value - min_val) / (max_val - min_val)
        
        # Invert if needed
        if inverse:
            normalized = 1.0 - normalized
        
        # Scale to 0-100
        return normalized * 100.0
