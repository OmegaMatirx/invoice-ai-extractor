"""
Rate limiting utilities
"""
import time
from typing import Dict, Optional
from collections import defaultdict, deque

class InMemoryRateLimiter:
    """Simple in-memory rate limiter for demo purposes"""
    
    def __init__(self, max_requests: int = 10, window_hours: int = 24):
        self.max_requests = max_requests
        self.window_seconds = window_hours * 3600
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, client_ip: str) -> tuple[bool, Optional[str]]:
        """
        Check if request is allowed for given IP
        Returns: (is_allowed, error_message)
        """
        now = time.time()
        client_requests = self.requests[client_ip]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] < now - self.window_seconds:
            client_requests.popleft()
        
        # Check if limit exceeded
        if len(client_requests) >= self.max_requests:
            return False, f"Rate limit exceeded. Maximum {self.max_requests} requests per 24 hours."
        
        # Add current request
        client_requests.append(now)
        return True, None
    
    def get_remaining_requests(self, client_ip: str) -> int:
        """Get remaining requests for IP"""
        now = time.time()
        client_requests = self.requests[client_ip]
        
        # Remove old requests
        while client_requests and client_requests[0] < now - self.window_seconds:
            client_requests.popleft()
        
        return max(0, self.max_requests - len(client_requests))
    
    def get_reset_time(self, client_ip: str) -> Optional[float]:
        """Get timestamp when rate limit resets for IP"""
        client_requests = self.requests[client_ip]
        if not client_requests:
            return None
        
        return client_requests[0] + self.window_seconds

# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()