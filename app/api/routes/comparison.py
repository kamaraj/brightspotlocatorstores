"""
Comparison API Routes
Endpoint for comparing multiple locations
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from loguru import logger
import asyncio

from app.agents.location_agent import get_agent
from app.config import get_settings

router = APIRouter()
settings = get_settings()


# ============================================
# Request/Response Models
# ============================================

class LocationComparisonRequest(BaseModel):
    """Request model for comparing multiple locations"""
    addresses: List[str] = Field(
        ...,
        description="List of 2-5 addresses to compare",
        min_length=2,
        max_length=5,
        examples=[
            [
                "123 Main St, San Francisco, CA 94102",
                "456 Oak Ave, Oakland, CA 94607"
            ]
        ]
    )
    additional_context: Optional[str] = Field(
        None,
        description="Optional context for comparison criteria"
    )
    
    @field_validator("addresses")
    @classmethod
    def validate_addresses(cls, v):
        """Ensure we have 2-5 unique addresses"""
        if len(v) < 2:
            raise ValueError("Need at least 2 addresses to compare")
        if len(v) > 5:
            raise ValueError("Maximum 5 addresses can be compared at once")
        if len(set(v)) != len(v):
            raise ValueError("All addresses must be unique")
        return v


class LocationComparisonResponse(BaseModel):
    """Response model for location comparison"""
    success: bool
    individual_analyses: List[dict]
    comparison: Optional[str] = None
    error: Optional[str] = None
    ranked_addresses: Optional[List[str]] = None


# ============================================
# Comparison Endpoints
# ============================================

@router.post(
    "/compare",
    response_model=LocationComparisonResponse,
    summary="Compare multiple locations",
    description="Side-by-side comparison of 2-5 childcare center locations"
)
async def compare_locations(
    request: LocationComparisonRequest,
    background_tasks: BackgroundTasks
):
    """
    Compare multiple locations for childcare centers
    
    **Process:**
    1. Analyze each location individually
    2. Generate comparative summary
    3. Rank locations from best to worst
    4. Highlight key differentiators
    
    **Returns:**
    - Individual analysis for each location
    - Comparative summary with rankings
    - Key differentiators explained
    """
    try:
        logger.info(f"Comparison request for {len(request.addresses)} locations")
        
        # Get agent instance
        agent = await get_agent()
        
        # Set timeout (longer for multiple locations)
        timeout = settings.analysis_timeout_seconds * len(request.addresses)
        
        # Run comparison with timeout
        try:
            result = await asyncio.wait_for(
                agent.compare_locations(request.addresses),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Comparison timeout after {timeout}s")
            raise HTTPException(
                status_code=408,
                detail=f"Comparison timeout after {timeout} seconds"
            )
        
        # Log completion
        background_tasks.add_task(
            log_comparison_completion,
            addresses=request.addresses,
            success=result.get("success", False)
        )
        
        return LocationComparisonResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )


@router.post(
    "/compare/quick",
    summary="Quick comparison (scores only)",
    description="Fast comparison returning scores without detailed analysis"
)
async def quick_compare_locations(request: LocationComparisonRequest):
    """
    Quick comparison returning only scores
    Faster than full comparison but less detail
    """
    try:
        logger.info(f"Quick comparison request for {len(request.addresses)} locations")
        
        # TODO: Implement quick scoring without full LLM analysis
        # - Run data collectors only
        # - Calculate scores algorithmically
        # - Return comparative table
        
        return {
            "success": False,
            "error": "Quick comparison not yet implemented",
            "message": "Use /compare endpoint for full analysis"
        }
        
    except Exception as e:
        logger.error(f"Quick comparison failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# Helper Functions
# ============================================

async def log_comparison_completion(addresses: List[str], success: bool):
    """Log comparison completion for analytics"""
    try:
        logger.info(
            f"Comparison completed - "
            f"Locations: {len(addresses)}, "
            f"Success: {success}"
        )
        # TODO: Store in database for analytics
    except Exception as e:
        logger.error(f"Failed to log comparison completion: {e}")
