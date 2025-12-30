import time
import threading
from collections import defaultdict
from typing import Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_second: float = 100.0
    burst_size: int = 50
    window_size: int = 60  # seconds
    cleanup_interval: int = 300  # seconds


class TokenBucket:
    """Token bucket algorithm for rate limiting"""
    
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: float = 1.0) -> bool:
        """Attempt to consume tokens"""
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now


class SlidingWindowCounter:
    """Sliding window counter for rate limiting"""
    
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.requests: Dict[int, int] = defaultdict(int)
        self.lock = threading.Lock()
    
    def add_request(self) -> None:
        """Record a request"""
        with self.lock:
            current_window = int(time.time()) // self.window_size
            self.requests[current_window] += 1
            self._cleanup()
    
    def get_request_count(self) -> int:
        """Get requests in current window"""
        with self.lock:
            current_window = int(time.time()) // self.window_size
            return self.requests.get(current_window, 0)
    
    def _cleanup(self) -> None:
        """Remove old windows"""
        cutoff = int(time.time()) // self.window_size - 2
        to_delete = [w for w in self.requests if w < cutoff]
        for window in to_delete:
            del self.requests[window]


class APIRateLimiter:
    """Advanced API rate limiter with multiple strategies"""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.buckets: Dict[str, TokenBucket] = {}
        self.windows: Dict[str, SlidingWindowCounter] = {}
        self.lock = threading.Lock()
        self.last_cleanup = time.time()
    
    def is_allowed(self, client_id: str, quota: float = 1.0) -> bool:
        """Check if request is allowed for client"""
        self._ensure_client(client_id)
        self._cleanup_if_needed()
        
        # Use token bucket algorithm
        bucket = self.buckets[client_id]
        if not bucket.consume(quota):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False
        
        return True
    
    def _ensure_client(self, client_id: str) -> None:
        """Ensure client has rate limit structures"""
        if client_id not in self.buckets:
            with self.lock:
                if client_id not in self.buckets:
                    capacity = self.config.burst_size
                    refill_rate = self.config.requests_per_second
                    self.buckets[client_id] = TokenBucket(capacity, refill_rate)
                    self.windows[client_id] = SlidingWindowCounter(
                        self.config.window_size
                    )
    
    def _cleanup_if_needed(self) -> None:
        """Cleanup old entries periodically"""
        now = time.time()
        if now - self.last_cleanup < self.config.cleanup_interval:
            return
        
        with self.lock:
            if now - self.last_cleanup < self.config.cleanup_interval:
                return
            
            # Remove inactive clients
            cutoff_time = now - (self.config.cleanup_interval * 2)
            inactive = []
            for client_id, bucket in self.buckets.items():
                if bucket.last_refill < cutoff_time:
                    inactive.append(client_id)
            
            for client_id in inactive:
                del self.buckets[client_id]
                del self.windows[client_id]
            
            self.last_cleanup = now
            logger.info(f"Cleaned up {len(inactive)} inactive clients")
    
    def get_remaining_quota(self, client_id: str) -> float:
        """Get remaining quota for client"""
        self._ensure_client(client_id)
        return self.buckets[client_id].tokens
    
    def reset_client(self, client_id: str) -> None:
        """Reset rate limit for client"""
        with self.lock:
            if client_id in self.buckets:
                self.buckets[client_id].tokens = self.config.burst_size


class RateLimitMiddleware:
    """Middleware for FastAPI/Flask applications"""
    
    def __init__(self, config: RateLimitConfig = None):
        self.limiter = APIRateLimiter(config)
    
    def check_rate_limit(
        self,
        client_id: str,
        quota: float = 1.0
    ) -> Tuple[bool, Dict[str, any]]:
        """Check rate limit and return response headers"""
        is_allowed = self.limiter.is_allowed(client_id, quota)
        remaining = self.limiter.get_remaining_quota(client_id)
        
        headers = {
            'X-RateLimit-Remaining': str(int(remaining)),
            'X-RateLimit-Reset': str(int(time.time()) + 60),
        }
        
        if not is_allowed:
            headers['Retry-After'] = '60'
        
        return is_allowed, headers


# Global rate limiter instance
_global_limiter = APIRateLimiter()


def check_rate_limit(client_id: str, quota: float = 1.0) -> bool:
    """Convenience function for rate limit checking"""
    return _global_limiter.is_allowed(client_id, quota)


if __name__ == '__main__':
    # Example usage
    config = RateLimitConfig(
        requests_per_second=10.0,
        burst_size=20,
    )
    limiter = APIRateLimiter(config)
    
    # Test rate limiting
    client_id = 'test-client'
    for i in range(25):
        allowed = limiter.is_allowed(client_id)
        print(f"Request {i+1}: {'Allowed' if allowed else 'Blocked'}, "
              f"Remaining: {limiter.get_remaining_quota(client_id):.1f}")
