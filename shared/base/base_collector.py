"""
Base Collector Abstract Class
All data collectors (shared and domain-specific) inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseCollector(ABC):
    """
    Abstract base class for all data collectors
    
    Provides common interface and utility methods for:
    - Data collection
    - Error handling  
    - Confidence scoring
    - Metadata tracking
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize collector with configuration
        
        Args:
            config: Dictionary with API keys, endpoints, settings
        """
        self.config = config
        self.name = self.__class__.__name__
        self.collect_start_time: Optional[datetime] = None
        self.collect_end_time: Optional[datetime] = None
    
    @abstractmethod
    async def collect(self, **kwargs) -> Dict[str, Any]:
        """
        Collect data from source (API, database, calculation)
        
        Returns:
            Dictionary with collected data and metadata
            Must include 'confidence' key: HIGH, MEDIUM, or LOW
        """
        pass
    
    def start_timer(self):
        """Start timing the collection"""
        self.collect_start_time = datetime.now()
    
    def end_timer(self) -> float:
        """End timing and return duration in milliseconds"""
        self.collect_end_time = datetime.now()
        if self.collect_start_time:
            delta = self.collect_end_time - self.collect_start_time
            return delta.total_seconds() * 1000
        return 0.0
    
    def create_response(
        self,
        data: Dict[str, Any],
        confidence: str = "MEDIUM",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Standardized response format
        
        Args:
            data: The collected data
            confidence: HIGH, MEDIUM, or LOW
            metadata: Additional context
            
        Returns:
            Standardized response dictionary
        """
        response = {
            **data,
            "confidence": confidence,
            "collector": self.name,
            "timestamp": datetime.now().isoformat()
        }
        
        if metadata:
            response["metadata"] = metadata
        
        return response
    
    def handle_error(
        self,
        error: Exception,
        fallback_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Standardized error handling
        
        Args:
            error: The exception that occurred
            fallback_data: Optional fallback data to return
            
        Returns:
            Error response with fallback data if provided
        """
        error_response = {
            "error": str(error),
            "error_type": type(error).__name__,
            "confidence": "LOW",
            "collector": self.name,
            "timestamp": datetime.now().isoformat()
        }
        
        if fallback_data:
            error_response.update(fallback_data)
            error_response["using_fallback"] = True
        
        return error_response
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required: list) -> bool:
        """
        Validate that all required fields are present
        
        Args:
            data: Dictionary to validate
            required: List of required field names
            
        Returns:
            True if all required fields present, False otherwise
        """
        return all(field in data for field in required)
