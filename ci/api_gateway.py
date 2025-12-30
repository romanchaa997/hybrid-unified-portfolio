"""API Gateway with rate limiting, request validation, and routing."""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from datetime import datetime, timedelta
import time
import hashlib

logger = logging.getLogger(__name__)

class RequestMethod(Enum):
    GET, POST, PUT, DELETE, PATCH = "GET", "POST", "PUT", "DELETE", "PATCH"

@dataclass
class RateLimitConfig:
    requests_per_second: int = 100
    burst_size: int = 150
    window_seconds: int = 60

@dataclass
class APIRequest:
    request_id: str
    method: RequestMethod
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict] = None
    timestamp: datetime = field(default_factory=datetime.now)
    client_ip: str = ""

@dataclass
class APIResponse:
    status_code: int
    body: Dict[str, Any]
    headers: Dict[str, str] = field(default_factory=dict)
    latency_ms: float = 0.0

class RateLimiter:
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.clients = {}
    
    def check_rate_limit(self, client_id: str) -> bool:
        now = time.time()
        if client_id not in self.clients:
            self.clients[client_id] = {"tokens": self.config.burst_size, "last_update": now}
            return True
        
        client = self.clients[client_id]
        elapsed = now - client["last_update"]
        tokens = min(self.config.burst_size, 
                    client["tokens"] + elapsed * self.config.requests_per_second)
        
        if tokens >= 1:
            client["tokens"] = tokens - 1
            client["last_update"] = now
            return True
        return False

class RequestValidator:
    def __init__(self):
        self.schemas = {}
    
    def register_schema(self, path: str, method: RequestMethod, schema: Dict) -> None:
        key = f"{method.value}:{path}"
        self.schemas[key] = schema
    
    def validate(self, request: APIRequest) -> bool:
        key = f"{request.method.value}:{request.path}"
        if key not in self.schemas:
            return True  # No schema = valid
        
        schema = self.schemas[key]
        if request.body is None:
            return not schema.get("required_body", False)
        
        required_fields = schema.get("required_fields", [])
        return all(field in request.body for field in required_fields)

class APIGateway:
    def __init__(self, name: str = "APIGateway-001"):
        self.name = name
        self.rate_limiter = RateLimiter(RateLimitConfig())
        self.validator = RequestValidator()
        self.routes: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        self.request_log: List[APIRequest] = []
        logger.info(f"API Gateway {name} initialized")
    
    def register_route(self, path: str, method: RequestMethod, handler: Callable) -> None:
        key = f"{method.value}:{path}"
        self.routes[key] = handler
        logger.debug(f"Route registered: {key}")
    
    def add_middleware(self, middleware: Callable) -> None:
        self.middleware.append(middleware)
    
    async def process_request(self, request: APIRequest) -> APIResponse:
        start_time = time.time()
        request.request_id = hashlib.md5(f"{request.path}{start_time}".encode()).hexdigest()
        
        # Rate limiting
        if not self.rate_limiter.check_rate_limit(request.client_ip):
            return APIResponse(429, {"error": "Rate limit exceeded"})
        
        # Validation
        if not self.validator.validate(request):
            return APIResponse(400, {"error": "Invalid request"})
        
        # Middleware processing
        for mw in self.middleware:
            request = mw(request) or request
        
        # Route handling
        key = f"{request.method.value}:{request.path}"
        if key not in self.routes:
            return APIResponse(404, {"error": "Route not found"})
        
        handler = self.routes[key]
        response = handler(request) if callable(handler) else APIResponse(200, handler)
        response.latency_ms = (time.time() - start_time) * 1000
        
        self.request_log.append(request)
        return response
    
    def get_gateway_stats(self) -> Dict:
        return {"name": self.name, "total_requests": len(self.request_log),
                "routes": len(self.routes), "middleware_count": len(self.middleware)}
