"""
FastAPI Application for Google Maps Scraper

Production-ready FastAPI application with security features:
- API key authentication
- Rate limiting
- Input validation
- CORS configuration
- Comprehensive error handling
- Anti-detection features (stealth browser, proxy support, CAPTCHA handling)
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Security, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from google_maps_scraper_agent import create_agent
from stealth_config import (
    StealthConfig,
    DetectionException,
    CaptchaException,
    AllMethodsFailedException,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Rate limiter configuration
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
limiter = Limiter(key_func=get_remote_address)

# API Key Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Get API key from environment
API_KEY = os.getenv("API_KEY", "")
if not API_KEY:
    logger.warning(
        "API_KEY not set in environment variables. API will be accessible without authentication."
    )


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> bool:
    """
    Verify API key from request header.

    Args:
        api_key: API key from request header

    Returns:
        True if API key is valid

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not API_KEY:
        # If no API key is configured, allow all requests
        return True

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing. Please provide X-API-Key header.",
        )

    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    return True


# Request/Response Models
class ScrapeRequest(BaseModel):
    """Request model for scraping Google Maps."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Search query (e.g., 'coffee shops', 'restaurants')",
    )
    location: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional location (e.g., 'New York, NY')",
    )
    max_results: int = Field(
        20,
        ge=1,
        le=100,
        description="Maximum number of results to scrape (1-100)",
    )
    enrich_with_website: bool = Field(
        False,
        description="Whether to visit business websites for additional info and emails",
    )

    @validator("query")
    def validate_query(cls, v):
        """Sanitize and validate query."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        # Remove potentially dangerous characters
        sanitized = v.strip()
        if len(sanitized) < 1:
            raise ValueError("Query must contain at least one character")
        return sanitized

    @validator("location")
    def validate_location(cls, v):
        """Sanitize location if provided."""
        if v:
            return v.strip()
        return v


class BusinessResult(BaseModel):
    """Business result model."""

    rank: int
    name: str
    rating: str
    reviews: str
    category: str
    price_level: str
    address: str
    phone: str
    website: str
    email: str
    url: str
    website_title: Optional[str] = None
    website_description: Optional[str] = None
    website_summary: Optional[str] = None
    website_emails: Optional[List[str]] = None


class ScrapeResponse(BaseModel):
    """Response model for scraping results."""

    status: str
    query: str
    location: Optional[str]
    total_found: int
    results: List[BusinessResult]
    processing_status: str


class StealthStatusResponse(BaseModel):
    """Stealth configuration status model."""

    stealth_enabled: bool
    human_simulation_enabled: bool
    proxy_configured: bool
    browserless_configured: bool
    captcha_service_configured: bool


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    message: str
    version: str = "1.0.0"
    stealth_status: Optional[StealthStatusResponse] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    error_type: Optional[str] = None


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the FastAPI app."""
    logger.info("Starting Google Maps Scraper API...")
    yield
    logger.info("Shutting down Google Maps Scraper API...")


# Create FastAPI app
app = FastAPI(
    title="Google Maps Scraper API",
    description="Production-ready API for scraping Google Maps search results",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
)
async def health_check():
    """
    Health check endpoint to verify API is running.

    Returns:
        Health status, API version, and stealth configuration status
    """
    stealth_status = StealthStatusResponse(
        stealth_enabled=StealthConfig.STEALTH_ENABLED,
        human_simulation_enabled=StealthConfig.HUMAN_SIMULATION_ENABLED,
        proxy_configured=StealthConfig.has_proxy(),
        browserless_configured=StealthConfig.has_browserless(),
        captcha_service_configured=StealthConfig.has_captcha_service(),
    )

    return HealthResponse(
        status="healthy",
        message="Google Maps Scraper API is running",
        version="1.0.0",
        stealth_status=stealth_status,
    )


@app.post(
    "/api/v1/scrape",
    response_model=ScrapeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Scraping"],
    summary="Scrape Google Maps search results",
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(
    f"{RATE_LIMIT_PER_MINUTE}/minute"
)  # Rate limit from environment variable
async def scrape_google_maps(
    request_data: ScrapeRequest,
    request: Request,
):
    """
    Scrape Google Maps search results.

    This endpoint:
    - Searches Google Maps for the given query
    - Extracts business information (name, rating, reviews, address, phone, website, email)
    - Optionally enriches results by visiting business websites

    Args:
        request_data: Scrape request with query, location, max_results, and enrich_with_website
        request: FastAPI Request object for rate limiting

    Returns:
        ScrapeResponse with results

    Raises:
        HTTPException: If scraping fails or request is invalid
    """
    try:
        logger.info(
            f"Received scrape request: query='{request_data.query}', "
            f"location='{request_data.location}', max_results={request_data.max_results}, "
            f"enrich_with_website={request_data.enrich_with_website}"
        )

        # Create agent instance
        agent = create_agent()

        # Process the scrape request
        result = await agent.process(
            query=request_data.query,
            location=request_data.location,
            max_results=request_data.max_results,
            enrich_with_website=request_data.enrich_with_website,
        )

        # Convert results to response model
        business_results = []
        for business in result.get("results", []):
            business_result = BusinessResult(
                rank=business.get("rank", 0),
                name=business.get("name", "N/A"),
                rating=business.get("rating", "N/A"),
                reviews=business.get("reviews", "N/A"),
                category=business.get("category", "N/A"),
                price_level=business.get("price_level", "N/A"),
                address=business.get("address", "N/A"),
                phone=business.get("phone", "N/A"),
                website=business.get("website", "N/A"),
                email=business.get("email", "N/A"),
                url=business.get("url", "N/A"),
                website_title=business.get("website_title"),
                website_description=business.get("website_description"),
                website_summary=business.get("website_summary"),
                website_emails=business.get("website_emails"),
            )
            business_results.append(business_result)

        logger.info(
            f"Successfully scraped {result.get('total_found', 0)} results for query: {request_data.query}"
        )

        return ScrapeResponse(
            status=result.get("status", "success"),
            query=result.get("query", request_data.query),
            location=result.get("location", request_data.location),
            total_found=result.get("total_found", 0),
            results=business_results,
            processing_status=result.get("processing_status", "completed"),
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    except CaptchaException as e:
        logger.error(f"CAPTCHA encountered: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"CAPTCHA challenge detected. Configure CAPTCHA_SERVICE and CAPTCHA_API_KEY to solve automatically, or try again later.",
        )
    except DetectionException as e:
        logger.error(f"Bot detection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Bot detection triggered. Consider using proxy rotation or waiting before retrying.",
        )
    except AllMethodsFailedException as e:
        logger.error(f"All scraping methods failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"All scraping methods failed. Please try again later or check your proxy configuration.",
        )
    except Exception as e:
        logger.error(f"Error scraping Google Maps: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}",
        )


@app.get(
    "/",
    tags=["Root"],
    summary="API root endpoint",
)
async def root():
    """
    Root endpoint with API information.

    Returns:
        API information and available endpoints
    """
    return {
        "name": "Google Maps Scraper API",
        "version": "1.0.0",
        "description": "Production-ready API for scraping Google Maps search results",
        "endpoints": {
            "health": "/health",
            "scrape": "/api/v1/scrape",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }


# if __name__ == "__main__":
#     import uvicorn

#     port = int(os.getenv("PORT", 8000))
#     host = os.getenv("HOST", "0.0.0.0")

#     uvicorn.run(
#         "app:app",
#         host=host,
#         port=port,
#         reload=os.getenv("DEBUG", "False").lower() == "true",
#         log_level="info",
#     )
