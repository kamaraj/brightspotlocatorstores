"""
Location Analysis Agent - Core AI Agent Implementation
Uses Microsoft Agent Framework with GitHub Models for location validation
"""

import asyncio
from typing import List, Dict, Any, Optional, Annotated
from loguru import logger

# Try to import agent framework
AGENT_FRAMEWORK_AVAILABLE = False
try:
    from agent_framework import ChatAgent, Thread
    from agent_framework.openai import OpenAIChatClient
    from openai import AsyncOpenAI
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    logger.error(
        "agent-framework-azure-ai not installed. "
        "Run: pip install agent-framework-azure-ai --pre"
    )
    # Create stub classes to prevent NameError
    ChatAgent = None
    Thread = None
    OpenAIChatClient = None
    AsyncOpenAI = None

from app.config import get_settings
from app.core.data_collectors.demographics import DemographicsCollector
from app.core.data_collectors.competition import CompetitionCollector
from app.core.data_collectors.accessibility import AccessibilityCollector
from app.core.data_collectors.safety import SafetyCollector
from app.core.data_collectors.economic import EconomicCollector


class LocationAnalysisAgent:
    """
    AI Agent for analyzing childcare center locations
    
    Uses Microsoft Agent Framework with 15 core data points:
    - Demographics (4): Population density, children 0-5, median income, growth
    - Competition (3): Existing centers, capacity utilization, market gap
    - Accessibility (3): Public transit, highway access, parking availability
    - Safety (4): Crime rate, traffic accidents, environmental quality
    - Economic (2): Real estate costs, neighborhood stability
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.agent: Optional[ChatAgent] = None
        self.thread: Optional[Thread] = None
        
        # Initialize data collectors
        self.demographics = DemographicsCollector()
        self.competition = CompetitionCollector()
        self.accessibility = AccessibilityCollector()
        self.safety = SafetyCollector()
        self.economic = EconomicCollector()
        
        logger.info("LocationAnalysisAgent initialized")
    
    async def initialize(self):
        """Initialize the AI agent with tools"""
        llm_config = self.settings.get_llm_config()
        
        if llm_config["provider"] != "github":
            raise NotImplementedError(
                "Only GitHub Models supported currently. "
                "Set GITHUB_TOKEN environment variable."
            )
        
        # Create OpenAI client for GitHub Models
        openai_client = AsyncOpenAI(
            base_url=llm_config["base_url"],
            api_key=llm_config["api_key"],
        )
        
        # Create chat client
        chat_client = OpenAIChatClient(
            async_client=openai_client,
            model_id=llm_config["model"]
        )
        
        # Define agent instructions
        instructions = """You are an expert location analyst specializing in childcare center site selection.

Your goal is to help users validate location choices by analyzing 15 critical data points across 5 categories:

1. **Demographics** (4 points):
   - Population density (children per sq mile)
   - Children aged 0-5 count
   - Median household income
   - Population growth rate

2. **Competition** (3 points):
   - Number of existing childcare centers within 2 miles
   - Average capacity utilization
   - Market gap (demand vs supply)

3. **Accessibility** (3 points):
   - Public transit proximity score
   - Highway access distance
   - Parking availability score

4. **Safety** (3 points):
   - Crime rate index
   - Traffic accident frequency
   - Environmental quality score

5. **Economic** (2 points):
   - Real estate cost per sq ft
   - Neighborhood economic stability index

**Analysis Process:**
1. Collect data using available tools for each category
2. Score each data point (0-100)
3. Calculate weighted category scores
4. Generate overall location score (0-100)
5. Provide clear recommendations with justification

**Scoring Rubric:**
- 90-100: Excellent - Highly recommended location
- 75-89: Good - Recommended with minor considerations
- 60-74: Fair - Viable but has notable concerns
- 40-59: Poor - Not recommended unless specific circumstances
- 0-39: Very Poor - Strongly not recommended

**Output Format:**
Provide a structured analysis with:
- Executive Summary (2-3 sentences)
- Category Scores with justification
- Key Strengths (top 3)
- Key Concerns (top 3)
- Overall Recommendation
- Next Steps

Always cite data sources and be transparent about data quality/limitations."""

        # Create agent with tools
        self.agent = ChatAgent(
            chat_client=chat_client,
            name="LocationAnalysisAgent",
            instructions=instructions,
            tools=[
                self.get_demographics,
                self.get_competition,
                self.get_accessibility,
                self.get_safety_data,
                self.get_economic_data,
            ]
        )
        
        # Create conversation thread
        self.thread = await Thread.create()
        
        logger.info(f"Agent initialized with model: {llm_config['model']}")
    
    # ============================================
    # Agent Tools - Data Collection Functions
    # ============================================
    
    async def get_demographics(
        self,
        address: Annotated[str, "Full street address to analyze"],
        radius_miles: Annotated[float, "Search radius in miles"] = 2.0
    ) -> str:
        """
        Collect demographic data for the location
        
        Returns JSON string with:
        - population_density: Children per square mile
        - children_0_5_count: Number of children aged 0-5 in radius
        - median_household_income: Median income in area
        - population_growth_rate: Annual growth percentage
        """
        try:
            logger.info(f"Collecting demographics for: {address}")
            data = await self.demographics.collect(address, radius_miles)
            return str(data)
        except Exception as e:
            logger.error(f"Demographics collection failed: {e}")
            return f"Error collecting demographics: {str(e)}"
    
    async def get_competition(
        self,
        address: Annotated[str, "Full street address to analyze"],
        radius_miles: Annotated[float, "Search radius in miles"] = 2.0
    ) -> str:
        """
        Analyze competition in the area
        
        Returns JSON string with:
        - childcare_centers_count: Number of existing centers
        - avg_capacity_utilization: Average utilization (0-100%)
        - market_gap_score: Demand vs supply gap (0-100)
        """
        try:
            logger.info(f"Analyzing competition for: {address}")
            data = await self.competition.collect(address, radius_miles)
            return str(data)
        except Exception as e:
            logger.error(f"Competition analysis failed: {e}")
            return f"Error analyzing competition: {str(e)}"
    
    async def get_accessibility(
        self,
        address: Annotated[str, "Full street address to analyze"]
    ) -> str:
        """
        Evaluate location accessibility
        
        Returns JSON string with:
        - public_transit_score: Proximity to transit (0-100)
        - highway_distance_miles: Distance to nearest highway
        - parking_availability_score: Parking options (0-100)
        """
        try:
            logger.info(f"Evaluating accessibility for: {address}")
            data = await self.accessibility.collect(address)
            return str(data)
        except Exception as e:
            logger.error(f"Accessibility evaluation failed: {e}")
            return f"Error evaluating accessibility: {str(e)}"
    
    async def get_safety_data(
        self,
        address: Annotated[str, "Full street address to analyze"],
        radius_miles: Annotated[float, "Search radius in miles"] = 1.0
    ) -> str:
        """
        Assess safety metrics for the location
        
        Returns JSON string with:
        - crime_rate_index: Crime index (lower is better, 0-100)
        - traffic_accidents_per_year: Annual accident count
        - environmental_quality_score: Air quality, hazards (0-100)
        """
        try:
            logger.info(f"Assessing safety for: {address}")
            data = await self.safety.collect(address, radius_miles)
            return str(data)
        except Exception as e:
            logger.error(f"Safety assessment failed: {e}")
            return f"Error assessing safety: {str(e)}"
    
    async def get_economic_data(
        self,
        address: Annotated[str, "Full street address to analyze"]
    ) -> str:
        """
        Gather economic indicators for the location
        
        Returns JSON string with:
        - real_estate_cost_per_sqft: Average cost per square foot
        - economic_stability_index: Neighborhood stability (0-100)
        """
        try:
            logger.info(f"Gathering economic data for: {address}")
            data = await self.economic.collect(address)
            return str(data)
        except Exception as e:
            logger.error(f"Economic data collection failed: {e}")
            return f"Error collecting economic data: {str(e)}"
    
    # ============================================
    # Main Analysis Methods
    # ============================================
    
    async def analyze_location(
        self,
        address: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive location analysis
        
        Args:
            address: Full street address to analyze
            additional_context: Optional user-provided context
            
        Returns:
            Dictionary with analysis results including scores and recommendations
        """
        if not self.agent or not self.thread:
            await self.initialize()
        
        # Construct analysis prompt
        prompt = f"""Please analyze this childcare center location:

Address: {address}

{f"Additional Context: {additional_context}" if additional_context else ""}

Perform a complete analysis using all available tools to collect data across all 5 categories.
Provide a comprehensive report with scores, strengths, concerns, and clear recommendations."""

        try:
            logger.info(f"Starting analysis for: {address}")
            
            # Run agent analysis
            response = await self.agent.run(
                thread=self.thread,
                input_messages=prompt
            )
            
            # Extract response content
            analysis_text = response.messages[-1].content if response.messages else ""
            
            result = {
                "success": True,
                "address": address,
                "analysis": analysis_text,
                "metadata": {
                    "model": self.settings.github_model_id,
                    "iterations": len(response.messages),
                    "tool_calls": self._count_tool_calls(response),
                }
            }
            
            logger.info(f"Analysis completed for: {address}")
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Analysis timeout for: {address}")
            return {
                "success": False,
                "error": "Analysis timeout - operation took too long",
                "address": address
            }
        except Exception as e:
            logger.error(f"Analysis failed for {address}: {e}")
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    async def analyze_location_stream(
        self,
        address: str,
        additional_context: Optional[str] = None
    ):
        """
        Perform streaming location analysis for real-time updates
        
        Yields chunks of analysis as they're generated
        """
        if not self.agent or not self.thread:
            await self.initialize()
        
        prompt = f"""Please analyze this childcare center location:

Address: {address}

{f"Additional Context: {additional_context}" if additional_context else ""}

Perform a complete analysis using all available tools to collect data across all 5 categories.
Provide a comprehensive report with scores, strengths, concerns, and clear recommendations."""

        try:
            logger.info(f"Starting streaming analysis for: {address}")
            
            async for chunk in self.agent.run_stream(
                thread=self.thread,
                input_messages=prompt
            ):
                # Yield text chunks as they arrive
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            logger.error(f"Streaming analysis failed: {e}")
            yield f"\n\n[Error: {str(e)}]"
    
    async def compare_locations(
        self,
        addresses: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple locations side-by-side
        
        Args:
            addresses: List of 2-5 addresses to compare
            
        Returns:
            Comparative analysis with rankings
        """
        if len(addresses) < 2:
            return {
                "success": False,
                "error": "Need at least 2 addresses to compare"
            }
        
        if len(addresses) > 5:
            return {
                "success": False,
                "error": "Maximum 5 addresses can be compared at once"
            }
        
        # Analyze each location
        results = []
        for address in addresses:
            result = await self.analyze_location(address)
            results.append(result)
        
        # Generate comparative summary
        comparison_prompt = f"""Based on these {len(addresses)} location analyses, provide a comparative summary:

{self._format_comparison_data(results)}

Rank the locations from best to worst and explain the key differentiators."""

        try:
            response = await self.agent.run(
                thread=self.thread,
                input_messages=comparison_prompt
            )
            
            comparison_text = response.messages[-1].content if response.messages else ""
            
            return {
                "success": True,
                "individual_analyses": results,
                "comparison": comparison_text
            }
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "individual_analyses": results
            }
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def _count_tool_calls(self, response) -> int:
        """Count number of tool calls made during analysis"""
        count = 0
        for message in response.messages:
            if hasattr(message, "tool_calls") and message.tool_calls:
                count += len(message.tool_calls)
        return count
    
    def _format_comparison_data(self, results: List[Dict]) -> str:
        """Format multiple analysis results for comparison"""
        formatted = []
        for i, result in enumerate(results, 1):
            if result.get("success"):
                formatted.append(f"\n--- Location {i}: {result['address']} ---\n{result['analysis']}")
            else:
                formatted.append(f"\n--- Location {i}: {result['address']} ---\nError: {result.get('error')}")
        return "\n".join(formatted)
    
    async def close(self):
        """Cleanup resources"""
        logger.info("Closing LocationAnalysisAgent")
        # Thread and agent cleanup handled by framework


# Singleton instance for app usage
_agent_instance: Optional[LocationAnalysisAgent] = None

async def get_agent() -> LocationAnalysisAgent:
    """Get or create singleton agent instance"""
    global _agent_instance
    
    if not AGENT_FRAMEWORK_AVAILABLE:
        raise ImportError(
            "Agent framework is not available. "
            "Install with: pip install agent-framework-azure-ai --pre"
        )
    
    if _agent_instance is None:
        _agent_instance = LocationAnalysisAgent()
        await _agent_instance.initialize()
    return _agent_instance

