"""
Circuit Breaker Pattern for API Resilience
Prevents cascading failures by failing fast when services are down
"""

import asyncio
import time
from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes needed to close from half-open
    timeout: float = 60.0  # Seconds before attempting recovery
    expected_exception: type = Exception


class CircuitBreaker:
    """
    Circuit breaker for protecting API calls
    
    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Too many failures, reject immediately
    - HALF_OPEN: Testing recovery, limited calls allowed
    
    Usage:
        breaker = CircuitBreaker("weather_api", failure_threshold=3)
        
        async with breaker:
            result = await api_call()
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker
        
        Args:
            name: Identifier for this circuit
            failure_threshold: Failures before opening circuit
            success_threshold: Successes to close from half-open
            timeout: Seconds before trying recovery
            expected_exception: Exception type to catch
        """
        self.name = name
        self.config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout=timeout,
            expected_exception=expected_exception
        )
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()
        
        logger.info(f"🔌 Circuit breaker created: {name}")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self._check_state()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with error handling"""
        if exc_type is None:
            # Success
            await self._on_success()
            return False
        
        if issubclass(exc_type, self.config.expected_exception):
            # Expected failure
            await self._on_failure()
            # Suppress exception if circuit is now open
            return self.state == CircuitState.OPEN
        
        # Unexpected exception, let it propagate
        return False
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Async function to call
            *args, **kwargs: Arguments for function
        
        Returns:
            Function result
        
        Raises:
            CircuitOpenError: If circuit is open
        """
        async with self:
            return await func(*args, **kwargs)
    
    async def _check_state(self):
        """Check and update circuit state"""
        if self.state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if self._should_attempt_reset():
                logger.info(f"🔄 {self.name}: Entering HALF_OPEN (timeout elapsed)")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.last_state_change = time.time()
            else:
                # Still open, reject immediately
                remaining = self.config.timeout - (time.time() - self.last_failure_time)
                raise CircuitOpenError(
                    f"{self.name} circuit is OPEN. "
                    f"Retry in {remaining:.1f}s"
                )
    
    async def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.debug(f"✅ {self.name}: Success in HALF_OPEN ({self.success_count}/{self.config.success_threshold})")
            
            if self.success_count >= self.config.success_threshold:
                # Enough successes, close circuit
                logger.info(f"✅ {self.name}: HALF_OPEN → CLOSED (recovered)")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.last_state_change = time.time()
        
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            if self.failure_count > 0:
                logger.debug(f"✅ {self.name}: Success, resetting failure count")
                self.failure_count = 0
    
    async def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            logger.warning(f"⚠️ {self.name}: Failure {self.failure_count}/{self.config.failure_threshold}")
            
            if self.failure_count >= self.config.failure_threshold:
                # Too many failures, open circuit
                logger.error(f"🔴 {self.name}: CLOSED → OPEN (threshold reached)")
                self.state = CircuitState.OPEN
                self.last_state_change = time.time()
        
        elif self.state == CircuitState.HALF_OPEN:
            # Failed during recovery, reopen circuit
            logger.error(f"🔴 {self.name}: HALF_OPEN → OPEN (recovery failed)")
            self.state = CircuitState.OPEN
            self.success_count = 0
            self.last_state_change = time.time()
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return False
        
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.timeout
    
    def get_status(self) -> dict:
        """Get circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": time.time() - self.last_failure_time if self.last_failure_time else None,
            "time_in_state": time.time() - self.last_state_change
        }


class CircuitOpenError(Exception):
    """Raised when circuit is open"""
    pass


class CircuitBreakerRegistry:
    """Manage multiple circuit breakers"""
    
    def __init__(self):
        self.breakers: dict[str, CircuitBreaker] = {}
    
    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: float = 60.0
    ) -> CircuitBreaker:
        """Get existing or create new circuit breaker"""
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                timeout=timeout
            )
        return self.breakers[name]
    
    def get_all_status(self) -> dict:
        """Get status of all circuit breakers"""
        return {
            name: breaker.get_status()
            for name, breaker in self.breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker.state = CircuitState.CLOSED
            breaker.failure_count = 0
            breaker.success_count = 0
        logger.info("🔄 All circuit breakers reset")


# Global registry
_registry = CircuitBreakerRegistry()


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """
    Get or create circuit breaker from global registry
    
    Usage:
        breaker = get_circuit_breaker("weather_api", failure_threshold=3)
        result = await breaker.call(fetch_weather, city="Boston")
    """
    return _registry.get_or_create(name, **kwargs)


def get_all_breakers_status() -> dict:
    """Get status of all registered circuit breakers"""
    return _registry.get_all_status()


# Example usage with exponential backoff
async def with_retry_and_breaker(
    func: Callable,
    circuit_name: str,
    max_retries: int = 3,
    *args,
    **kwargs
) -> Any:
    """
    Execute function with circuit breaker and exponential backoff
    
    Args:
        func: Async function to call
        circuit_name: Circuit breaker identifier
        max_retries: Maximum retry attempts
        *args, **kwargs: Function arguments
    
    Returns:
        Function result
    """
    breaker = get_circuit_breaker(circuit_name)
    
    for attempt in range(max_retries):
        try:
            return await breaker.call(func, *args, **kwargs)
        except CircuitOpenError:
            # Circuit is open, don't retry
            raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff
            wait_time = 2 ** attempt
            logger.warning(f"⏳ Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
            await asyncio.sleep(wait_time)


if __name__ == "__main__":
    # Test circuit breaker
    logging.basicConfig(level=logging.INFO)
    
    async def unstable_api(should_fail: bool = False):
        """Simulated API that can fail"""
        if should_fail:
            raise Exception("API Error")
        return {"status": "ok"}
    
    async def test():
        breaker = get_circuit_breaker("test_api", failure_threshold=3, timeout=5)
        
        print("\n1. Testing successful calls...")
        for i in range(3):
            try:
                result = await breaker.call(unstable_api, should_fail=False)
                print(f"✅ Call {i+1}: {result}")
            except Exception as e:
                print(f"❌ Call {i+1}: {e}")
        
        print(f"\nStatus: {breaker.get_status()}")
        
        print("\n2. Testing failures (circuit should open)...")
        for i in range(5):
            try:
                result = await breaker.call(unstable_api, should_fail=True)
                print(f"✅ Call {i+1}: {result}")
            except (Exception, CircuitOpenError) as e:
                print(f"❌ Call {i+1}: {type(e).__name__}")
        
        print(f"\nStatus: {breaker.get_status()}")
        
        print("\n3. Waiting for timeout...")
        await asyncio.sleep(6)
        
        print("\n4. Testing recovery (should enter HALF_OPEN)...")
        for i in range(3):
            try:
                result = await breaker.call(unstable_api, should_fail=False)
                print(f"✅ Call {i+1}: {result}")
            except Exception as e:
                print(f"❌ Call {i+1}: {e}")
        
        print(f"\nFinal Status: {breaker.get_status()}")
    
    asyncio.run(test())
