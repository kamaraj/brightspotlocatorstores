"""
Validation API Routes
Endpoint for single location validation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from loguru import logger
import asyncio

# Make agent import optional
try:
    from app.agents.location_agent import get_agent
    AGENT_AVAILABLE = True
except ImportError:
    logger.warning("Agent framework not available for validation routes")
    AGENT_AVAILABLE = False
    get_agent = None

from app.config import get_settings

router = APIRouter()
settings = get_settings()


# ============================================
# Request/Response Models
# ============================================

class LocationValidationRequest(BaseModel):
    """Request model for location validation"""
    address: str = Field(
        ...,
        description="Full street address to validate",
        examples=["123 Main St, San Francisco, CA 94102"]
    )
    additional_context: Optional[str] = Field(
        None,
        description="Optional context (target age group, budget, etc.)",
        examples=["Looking for location for infant care center, budget $500K"]
    )
    radius_miles: float = Field(
        default=2.0,
        ge=0.5,
        le=10.0,
        description="Analysis radius in miles (0.5-10)"
    )
    stream_response: bool = Field(
        default=False,
        description="Enable streaming response for real-time updates"
    )


class LocationValidationResponse(BaseModel):
    """Response model for location validation"""
    success: bool
    address: str
    analysis: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None


# ============================================
# Validation Endpoints
# ============================================

@router.post(
    "/validate",
    response_model=LocationValidationResponse,
    summary="Validate a childcare center location",
    description="Analyze a single location for childcare center suitability across 15 data points"
)
async def validate_location(
    request: LocationValidationRequest,
    background_tasks: BackgroundTasks
):
    """
    Validate a childcare center location
    
    **Analysis includes:**
    - Demographics (4 metrics)
    - Competition (3 metrics)
    - Accessibility (3 metrics)
    - Safety (3 metrics)
    - Economic (2 metrics)
    
    **Returns:**
    - Overall score (0-100)
    - Category scores with justification
    - Key strengths and concerns
    - Actionable recommendations
    """
    try:
        logger.info(f"Validation request for: {request.address}")
        
        # Get agent instance
        agent = await get_agent()
        
        # Set timeout
        timeout = settings.analysis_timeout_seconds
        
        # Run analysis with timeout
        try:
            result = await asyncio.wait_for(
                agent.analyze_location(
                    address=request.address,
                    additional_context=request.additional_context
                ),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Analysis timeout for: {request.address}")
            raise HTTPException(
                status_code=408,
                detail=f"Analysis timeout after {timeout} seconds"
            )
        
        # Log completion for analytics (background task)
        background_tasks.add_task(
            log_analysis_completion,
            address=request.address,
            success=result.get("success", False)
        )
        
        return LocationValidationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation failed for {request.address}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.post(
    "/validate/stream",
    summary="Validate location with streaming response",
    description="Real-time streaming analysis for immediate feedback"
)
async def validate_location_stream(request: LocationValidationRequest):
    """
    Streaming validation endpoint
    Returns analysis results as they're generated
    """
    try:
        logger.info(f"Streaming validation request for: {request.address}")
        
        # Get agent instance
        agent = await get_agent()
        
        # Create streaming response
        async def generate():
            try:
                async for chunk in agent.analyze_location_stream(
                    address=request.address,
                    additional_context=request.additional_context
                ):
                    # Stream chunks as server-sent events
                    yield f"data: {chunk}\n\n"
                
                # Send completion marker
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: [ERROR: {str(e)}]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Streaming validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Streaming validation failed: {str(e)}"
        )


@router.get(
    "/validate/status/{analysis_id}",
    summary="Check validation status",
    description="Check status of a background validation job"
)
async def check_validation_status(analysis_id: str):
    """
    Check status of validation analysis
    (To be implemented with database/cache)
    """
    # TODO: Implement with Redis cache or database
    return {
        "analysis_id": analysis_id,
        "status": "not_implemented",
        "message": "Status tracking coming soon"
    }


# ============================================
# Helper Functions
# ============================================

async def log_analysis_completion(address: str, success: bool):
    """
    Log analysis completion for analytics
    (Background task)
    """
    try:
        logger.info(f"Analysis completed - Address: {address}, Success: {success}")
        # TODO: Store in database for analytics
        # - Track usage per user
        # - Monitor API performance
        # - Generate usage reports
    except Exception as e:
        logger.error(f"Failed to log analysis completion: {e}")
