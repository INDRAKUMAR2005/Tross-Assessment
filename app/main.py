# app/main.py
import uuid
import time
import logging
from fastapi import FastAPI, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from app.config import Config
from app.api.health import router as health_router
from app.api.profile import router as profile_router

# Initialize Config validation
Config.validate()

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize FastAPI App
app = FastAPI(
    title="LinkedIn Profile Scraper API",
    description=(
        "A professional, self-hosted API that directly hits LinkedIn Voyager endpoints "
        "using HTTP requests and cookie-based authentication, bypassing browser-automation "
        "and returning normalized structured JSON."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key header security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if Config.API_KEY_ENABLED:
        if not api_key or api_key != Config.API_KEY:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "success": False,
                    "error": {
                        "code": "LINKEDIN_ACCESS_DENIED",
                        "message": "Access denied: Invalid API Key."
                    }
                }
            )

# Correlation Tracking and Request Tracing Middleware
@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next):
    # Retrieve request ID or generate one
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    start_time = time.time()
    logger.info(f"[{request_id}] HTTP request started: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    logger.info(f"[{request_id}] HTTP request finished: status {response.status_code} in {process_time:.4f}s")
    
    return response

# Root route returning welcome message
@app.get("/", status_code=status.HTTP_200_OK, include_in_schema=False)
def index():
    return {
        "message": "Welcome to the LinkedIn Profile Scraper API!",
        "documentation": "/docs",
        "health_check": "/health"
    }

# Register health router
app.include_router(health_router)

# Register profile router (secured with verify_api_key if enabled)
app.include_router(profile_router, dependencies=[Depends(verify_api_key)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=Config.HOST, port=Config.PORT, reload=True)
