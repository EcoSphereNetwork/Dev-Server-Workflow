# main.py - verbesserte Sicherheitskonfiguration

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .api.router import router
from .utils.logger import setup_logging
from .core.config import settings

# Configure logging
logger = setup_logging()

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# API key security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Create FastAPI app with security middleware
middleware = [
    Middleware(
        CORSMiddleware,
        # Define allowed origins instead of allowing all (*) 
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
]

app = FastAPI(
    title="n8n MCP Server",
    description="A MCP server for n8n workflow automation",
    version=settings.APP_VERSION,
    middleware=middleware,
)

# Add rate limiting exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add router with rate limiting
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# Add the router
app.include_router(router)
