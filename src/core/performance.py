"""
Performance optimization utilities for MCP servers.

This module provides utilities for optimizing the performance of MCP servers,
including caching, connection pooling, and request batching.
"""

import time
import functools
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Union, cast
from concurrent.futures import ThreadPoolExecutor
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta

# Type variables for generic functions
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Set up logging
logger = logging.getLogger(__name__)

# Thread pool for parallel execution
_thread_pool = ThreadPoolExecutor(max_workers=10)

@dataclass
class CacheEntry:
    """A cache entry with value and expiration time."""
    value: Any
    expires_at: Optional[datetime] = None

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class Cache:
    """A simple in-memory cache with expiration."""
    
    def __init__(self, default_ttl: Optional[int] = 300):
        """Initialize the cache.
        
        Args:
            default_ttl: Default time-to-live in seconds. None means no expiration.
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Any:
        """Get a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached value, or None if not found or expired.
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if entry.is_expired:
                del self._cache[key]
                return None
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Time-to-live in seconds. None means use default_ttl.
        """
        with self._lock:
            if ttl is None:
                ttl = self._default_ttl
            
            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            self._cache[key] = CacheEntry(value, expires_at)
    
    def delete(self, key: str) -> None:
        """Delete a value from the cache.
        
        Args:
            key: The cache key.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        """Clear the entire cache."""
        with self._lock:
            self._cache.clear()
    
    def cleanup(self) -> None:
        """Remove expired entries from the cache."""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.expires_at and entry.expires_at <= now
            ]
            for key in expired_keys:
                del self._cache[key]


# Global cache instance
_global_cache = Cache()


def cached(ttl: Optional[int] = None, key_prefix: str = "") -> Callable:
    """Decorator to cache function results.
    
    Args:
        ttl: Time-to-live in seconds. None means use default_ttl.
        key_prefix: Prefix for cache keys.
        
    Returns:
        Decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create a cache key from the function name, args, and kwargs
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = _global_cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    
    return decorator


def async_cached(ttl: Optional[int] = None, key_prefix: str = "") -> Callable:
    """Decorator to cache async function results.
    
    Args:
        ttl: Time-to-live in seconds. None means use default_ttl.
        key_prefix: Prefix for cache keys.
        
    Returns:
        Decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create a cache key from the function name, args, and kwargs
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = _global_cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call the function and cache the result
            result = await func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    
    return decorator


class ConnectionPool:
    """A pool of reusable connections."""
    
    def __init__(self, factory: Callable[[], Any], max_size: int = 10, ttl: Optional[int] = 300):
        """Initialize the connection pool.
        
        Args:
            factory: Function to create a new connection.
            max_size: Maximum number of connections in the pool.
            ttl: Time-to-live for connections in seconds. None means no expiration.
        """
        self._factory = factory
        self._max_size = max_size
        self._ttl = ttl
        self._pool: List[Tuple[Any, datetime]] = []
        self._lock = threading.RLock()
    
    def get(self) -> Any:
        """Get a connection from the pool.
        
        Returns:
            A connection.
        """
        with self._lock:
            now = datetime.now()
            
            # Remove expired connections
            if self._ttl is not None:
                self._pool = [
                    (conn, created_at) for conn, created_at in self._pool
                    if now - created_at < timedelta(seconds=self._ttl)
                ]
            
            # Return an existing connection if available
            if self._pool:
                return self._pool.pop()[0]
            
            # Create a new connection
            return self._factory()
    
    def put(self, conn: Any) -> None:
        """Return a connection to the pool.
        
        Args:
            conn: The connection to return.
        """
        with self._lock:
            # Only add to the pool if we're not at max size
            if len(self._pool) < self._max_size:
                self._pool.append((conn, datetime.now()))
    
    def clear(self) -> None:
        """Clear the connection pool."""
        with self._lock:
            self._pool.clear()


class RequestBatcher:
    """Batches individual requests into a single batch request."""
    
    def __init__(self, batch_size: int = 10, max_wait_time: float = 0.1):
        """Initialize the request batcher.
        
        Args:
            batch_size: Maximum number of requests in a batch.
            max_wait_time: Maximum time to wait for a batch to fill up, in seconds.
        """
        self._batch_size = batch_size
        self._max_wait_time = max_wait_time
        self._batch: List[Dict[str, Any]] = []
        self._batch_lock = threading.RLock()
        self._batch_event = threading.Event()
        self._batch_thread = threading.Thread(target=self._process_batches, daemon=True)
        self._batch_thread.start()
        self._processor: Optional[Callable[[List[Dict[str, Any]]], List[Any]]] = None
        self._running = True
    
    def set_processor(self, processor: Callable[[List[Dict[str, Any]]], List[Any]]) -> None:
        """Set the batch processor function.
        
        Args:
            processor: Function to process a batch of requests.
        """
        self._processor = processor
    
    def add_request(self, request: Dict[str, Any]) -> Any:
        """Add a request to the batch.
        
        Args:
            request: The request to add.
            
        Returns:
            The result of the request.
        """
        if self._processor is None:
            raise ValueError("Batch processor not set")
        
        result_future: asyncio.Future = asyncio.Future()
        request["_result_future"] = result_future
        
        with self._batch_lock:
            self._batch.append(request)
            
            # Signal the batch thread if we've reached the batch size
            if len(self._batch) >= self._batch_size:
                self._batch_event.set()
        
        # Wait for the result
        return asyncio.get_event_loop().run_until_complete(result_future)
    
    async def add_request_async(self, request: Dict[str, Any]) -> Any:
        """Add a request to the batch asynchronously.
        
        Args:
            request: The request to add.
            
        Returns:
            The result of the request.
        """
        if self._processor is None:
            raise ValueError("Batch processor not set")
        
        result_future: asyncio.Future = asyncio.Future()
        request["_result_future"] = result_future
        
        with self._batch_lock:
            self._batch.append(request)
            
            # Signal the batch thread if we've reached the batch size
            if len(self._batch) >= self._batch_size:
                self._batch_event.set()
        
        # Wait for the result
        return await result_future
    
    def _process_batches(self) -> None:
        """Process batches of requests."""
        while self._running:
            # Wait for the batch to fill up or the max wait time to elapse
            self._batch_event.wait(self._max_wait_time)
            self._batch_event.clear()
            
            with self._batch_lock:
                if not self._batch:
                    continue
                
                # Get the current batch and start a new one
                current_batch = self._batch
                self._batch = []
            
            # Process the batch
            try:
                if self._processor is not None:
                    results = self._processor(current_batch)
                    
                    # Set the results on the futures
                    for i, request in enumerate(current_batch):
                        if i < len(results):
                            request["_result_future"].set_result(results[i])
                        else:
                            request["_result_future"].set_exception(
                                ValueError(f"No result for request {i}")
                            )
            except Exception as e:
                # Set the exception on all futures
                for request in current_batch:
                    request["_result_future"].set_exception(e)
    
    def shutdown(self) -> None:
        """Shut down the batcher."""
        self._running = False
        self._batch_event.set()
        self._batch_thread.join(timeout=1.0)


def run_in_thread(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to run a function in a separate thread.
    
    Args:
        func: The function to run in a thread.
        
    Returns:
        Decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return _thread_pool.submit(func, *args, **kwargs).result()
    
    return wrapper


def run_in_thread_async(func: Callable[..., T]) -> Callable[..., asyncio.Future[T]]:
    """Decorator to run a function in a separate thread and return a future.
    
    Args:
        func: The function to run in a thread.
        
    Returns:
        Decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> asyncio.Future[T]:
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        def _run_and_set_result() -> None:
            try:
                result = func(*args, **kwargs)
                loop.call_soon_threadsafe(future.set_result, result)
            except Exception as e:
                loop.call_soon_threadsafe(future.set_exception, e)
        
        _thread_pool.submit(_run_and_set_result)
        return future
    
    return wrapper


class RateLimiter:
    """Rate limiter to prevent too many requests in a short time."""
    
    def __init__(self, max_calls: int, period: float):
        """Initialize the rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed in the period.
            period: Time period in seconds.
        """
        self._max_calls = max_calls
        self._period = period
        self._calls: List[float] = []
        self._lock = threading.RLock()
    
    def acquire(self, block: bool = True) -> bool:
        """Acquire a rate limit token.
        
        Args:
            block: Whether to block until a token is available.
            
        Returns:
            True if a token was acquired, False otherwise.
        """
        with self._lock:
            now = time.time()
            
            # Remove expired calls
            self._calls = [t for t in self._calls if now - t <= self._period]
            
            # Check if we're at the limit
            if len(self._calls) >= self._max_calls:
                if not block:
                    return False
                
                # Calculate how long to wait
                oldest_call = min(self._calls)
                wait_time = self._period - (now - oldest_call)
                if wait_time > 0:
                    time.sleep(wait_time)
                
                # Try again after waiting
                return self.acquire(block=False)
            
            # Add the current call
            self._calls.append(now)
            return True
    
    async def acquire_async(self, block: bool = True) -> bool:
        """Acquire a rate limit token asynchronously.
        
        Args:
            block: Whether to block until a token is available.
            
        Returns:
            True if a token was acquired, False otherwise.
        """
        with self._lock:
            now = time.time()
            
            # Remove expired calls
            self._calls = [t for t in self._calls if now - t <= self._period]
            
            # Check if we're at the limit
            if len(self._calls) >= self._max_calls:
                if not block:
                    return False
                
                # Calculate how long to wait
                oldest_call = min(self._calls)
                wait_time = self._period - (now - oldest_call)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                
                # Try again after waiting
                return await self.acquire_async(block=False)
            
            # Add the current call
            self._calls.append(now)
            return True


def rate_limited(max_calls: int, period: float) -> Callable:
    """Decorator to rate limit a function.
    
    Args:
        max_calls: Maximum number of calls allowed in the period.
        period: Time period in seconds.
        
    Returns:
        Decorated function.
    """
    limiter = RateLimiter(max_calls, period)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            limiter.acquire()
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def async_rate_limited(max_calls: int, period: float) -> Callable:
    """Decorator to rate limit an async function.
    
    Args:
        max_calls: Maximum number of calls allowed in the period.
        period: Time period in seconds.
        
    Returns:
        Decorated function.
    """
    limiter = RateLimiter(max_calls, period)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            await limiter.acquire_async()
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class CircuitBreaker:
    """Circuit breaker to prevent calls to failing services."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        expected_exceptions: Tuple[type, ...] = (Exception,),
    ):
        """Initialize the circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening the circuit.
            recovery_timeout: Time to wait before trying again, in seconds.
            expected_exceptions: Exceptions that count as failures.
        """
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._expected_exceptions = expected_exceptions
        self._failures = 0
        self._last_failure_time: Optional[float] = None
        self._lock = threading.RLock()
    
    def __call__(self, func: Callable) -> Callable:
        """Decorate a function with the circuit breaker.
        
        Args:
            func: The function to decorate.
            
        Returns:
            Decorated function.
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with self._lock:
                # Check if the circuit is open
                if self._failures >= self._failure_threshold:
                    if self._last_failure_time is not None:
                        if time.time() - self._last_failure_time < self._recovery_timeout:
                            raise CircuitBreakerOpenError(
                                f"Circuit breaker is open for {func.__name__}"
                            )
                    
                    # Reset failures to allow one request through
                    self._failures = 0
            
            try:
                result = func(*args, **kwargs)
                
                # Reset failures on success
                with self._lock:
                    self._failures = 0
                
                return result
            except self._expected_exceptions as e:
                # Increment failures on expected exceptions
                with self._lock:
                    self._failures += 1
                    self._last_failure_time = time.time()
                
                raise
        
        return wrapper


class CircuitBreakerOpenError(Exception):
    """Exception raised when a circuit breaker is open."""
    pass


def async_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    expected_exceptions: Tuple[type, ...] = (Exception,),
) -> Callable:
    """Decorator to apply a circuit breaker to an async function.
    
    Args:
        failure_threshold: Number of failures before opening the circuit.
        recovery_timeout: Time to wait before trying again, in seconds.
        expected_exceptions: Exceptions that count as failures.
        
    Returns:
        Decorated function.
    """
    breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        expected_exceptions=expected_exceptions,
    )
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            with breaker._lock:
                # Check if the circuit is open
                if breaker._failures >= breaker._failure_threshold:
                    if breaker._last_failure_time is not None:
                        if time.time() - breaker._last_failure_time < breaker._recovery_timeout:
                            raise CircuitBreakerOpenError(
                                f"Circuit breaker is open for {func.__name__}"
                            )
                    
                    # Reset failures to allow one request through
                    breaker._failures = 0
            
            try:
                result = await func(*args, **kwargs)
                
                # Reset failures on success
                with breaker._lock:
                    breaker._failures = 0
                
                return result
            except breaker._expected_exceptions as e:
                # Increment failures on expected exceptions
                with breaker._lock:
                    breaker._failures += 1
                    breaker._last_failure_time = time.time()
                
                raise
        
        return wrapper
    
    return decorator


def timed(func: Callable) -> Callable:
    """Decorator to time a function.
    
    Args:
        func: The function to time.
        
    Returns:
        Decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.debug(
            f"Function {func.__name__} took {end_time - start_time:.6f} seconds"
        )
        
        return result
    
    return wrapper


def async_timed(func: Callable) -> Callable:
    """Decorator to time an async function.
    
    Args:
        func: The function to time.
        
    Returns:
        Decorated function.
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        logger.debug(
            f"Async function {func.__name__} took {end_time - start_time:.6f} seconds"
        )
        
        return result
    
    return wrapper


class Profiler:
    """Profiler to track function call times."""
    
    def __init__(self):
        """Initialize the profiler."""
        self._call_times: Dict[str, List[float]] = {}
        self._lock = threading.RLock()
    
    def record_call(self, func_name: str, duration: float) -> None:
        """Record a function call.
        
        Args:
            func_name: Name of the function.
            duration: Duration of the call in seconds.
        """
        with self._lock:
            if func_name not in self._call_times:
                self._call_times[func_name] = []
            
            self._call_times[func_name].append(duration)
    
    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get profiling statistics.
        
        Returns:
            Dictionary of function statistics.
        """
        with self._lock:
            stats = {}
            
            for func_name, times in self._call_times.items():
                if not times:
                    continue
                
                stats[func_name] = {
                    "count": len(times),
                    "total": sum(times),
                    "min": min(times),
                    "max": max(times),
                    "avg": sum(times) / len(times),
                }
            
            return stats
    
    def reset(self) -> None:
        """Reset the profiler."""
        with self._lock:
            self._call_times.clear()


# Global profiler instance
_profiler = Profiler()


def profiled(func: Callable) -> Callable:
    """Decorator to profile a function.
    
    Args:
        func: The function to profile.
        
    Returns:
        Decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        _profiler.record_call(func.__name__, end_time - start_time)
        
        return result
    
    return wrapper


def async_profiled(func: Callable) -> Callable:
    """Decorator to profile an async function.
    
    Args:
        func: The function to profile.
        
    Returns:
        Decorated function.
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        _profiler.record_call(func.__name__, end_time - start_time)
        
        return result
    
    return wrapper


def get_profiler_stats() -> Dict[str, Dict[str, float]]:
    """Get profiling statistics.
    
    Returns:
        Dictionary of function statistics.
    """
    return _profiler.get_stats()


def reset_profiler() -> None:
    """Reset the profiler."""
    _profiler.reset()


class MemoryCache:
    """Memory-efficient cache using weak references."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize the memory cache.
        
        Args:
            max_size: Maximum number of items in the cache.
        """
        self._cache: Dict[str, Any] = {}
        self._max_size = max_size
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Any:
        """Get a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached value, or None if not found.
        """
        with self._lock:
            return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
        """
        with self._lock:
            # If we're at max size, remove the oldest item
            if len(self._cache) >= self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            
            self._cache[key] = value
    
    def delete(self, key: str) -> None:
        """Delete a value from the cache.
        
        Args:
            key: The cache key.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        """Clear the entire cache."""
        with self._lock:
            self._cache.clear()


# Global memory cache instance
_memory_cache = MemoryCache()


def memoized(func: Callable) -> Callable:
    """Decorator to memoize a function.
    
    Args:
        func: The function to memoize.
        
    Returns:
        Decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Create a cache key from the function name, args, and kwargs
        key_parts = [func.__name__]
        key_parts.extend([str(arg) for arg in args])
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        cache_key = ":".join(key_parts)
        
        # Try to get from cache
        cached_value = _memory_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        # Call the function and cache the result
        result = func(*args, **kwargs)
        _memory_cache.set(cache_key, result)
        return result
    
    return wrapper


def async_memoized(func: Callable) -> Callable:
    """Decorator to memoize an async function.
    
    Args:
        func: The function to memoize.
        
    Returns:
        Decorated function.
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Create a cache key from the function name, args, and kwargs
        key_parts = [func.__name__]
        key_parts.extend([str(arg) for arg in args])
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        cache_key = ":".join(key_parts)
        
        # Try to get from cache
        cached_value = _memory_cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        
        # Call the function and cache the result
        result = await func(*args, **kwargs)
        _memory_cache.set(cache_key, result)
        return result
    
    return wrapper