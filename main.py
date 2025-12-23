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

import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Security,
    status,
    Request,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, field_validator
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


# Available fields for extraction
AVAILABLE_FIELDS = {
    "name",
    "rating",
    "reviews",
    "category",
    "price_level",
    "address",
    "phone",
    "website",
    "email",
    "url",
    "website_title",
    "website_description",
    "website_summary",
    "website_emails",
}


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
    max_results: Optional[int] = Field(
        None,
        ge=1,
        le=500,
        description="Maximum number of results to scrape (1-500). If not specified, all available results will be scraped.",
    )
    save_to_file: bool = Field(
        False,
        description="Whether to save results to output folder",
    )
    output_file_type: Optional[str] = Field(
        "json",
        description="Output file type when save_to_file is true. Options: 'json' or 'csv'. Default: 'json'",
    )

    @field_validator("output_file_type")
    @classmethod
    def validate_output_file_type(cls, v: Optional[str]) -> str:
        """Validate output file type."""
        if v is None:
            return "json"
        v_lower = v.lower().strip()
        if v_lower not in ["json", "csv"]:
            raise ValueError("output_file_type must be 'json' or 'csv'")
        return v_lower

    fields: Optional[List[str]] = Field(
        None,
        description='List of fields to extract. Available fields: name, rating, reviews, category, price_level, address, phone, website, email, url, website_title, website_description, website_summary, website_emails. Example: ["name", "website", "phone"]. If not specified, all fields are extracted.',
    )

    @field_validator("fields")
    @classmethod
    def validate_fields(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and sanitize fields list."""
        if v is None or len(v) == 0:
            return None  # Extract all fields

        # Check if user passed placeholder values like "string"
        if isinstance(v, list) and len(v) == 1 and v[0].lower().strip() == "string":
            raise ValueError(
                "Please provide actual field names, not placeholder values. "
                f'Example: ["name", "website", "phone"]. '
                f"Available fields: {', '.join(sorted(AVAILABLE_FIELDS))}"
            )

        # Convert to lowercase and remove duplicates
        fields_lower = [f.lower().strip() for f in v]
        fields_lower = list(
            dict.fromkeys(fields_lower)
        )  # Preserve order, remove duplicates

        # Validate fields
        invalid_fields = [f for f in fields_lower if f not in AVAILABLE_FIELDS]
        if invalid_fields:
            raise ValueError(
                f"Invalid field(s): {', '.join(invalid_fields)}. "
                f"Available fields: {', '.join(sorted(AVAILABLE_FIELDS))}. "
                f'Example: ["name", "website", "phone"]'
            )

        return fields_lower

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Sanitize and validate query."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        # Remove potentially dangerous characters
        sanitized = v.strip()
        if len(sanitized) < 1:
            raise ValueError("Query must contain at least one character")
        return sanitized

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
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


class EnrichRequest(BaseModel):
    """Request model for enriching business results."""

    results: List[BusinessResult] = Field(
        ...,
        min_length=1,
        description="List of business results to enrich with website information",
    )
    location: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional location for context (e.g., 'New York, NY')",
    )
    save_to_file: bool = Field(
        False,
        description="Whether to save enriched results to output folder (JSON and Markdown formats)",
    )
    fields: Optional[List[str]] = Field(
        None,
        description='List of fields to extract. Available fields: name, rating, reviews, category, price_level, address, phone, website, email, url, website_title, website_description, website_summary, website_emails. Example: ["name", "website", "phone"]. If not specified, all fields are extracted.',
    )

    @field_validator("fields")
    @classmethod
    def validate_fields(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and sanitize fields list."""
        if v is None or len(v) == 0:
            return None  # Extract all fields

        # Check if user passed placeholder values like "string"
        if isinstance(v, list) and len(v) == 1 and v[0].lower().strip() == "string":
            raise ValueError(
                "Please provide actual field names, not placeholder values. "
                f'Example: ["name", "website", "phone"]. '
                f"Available fields: {', '.join(sorted(AVAILABLE_FIELDS))}"
            )

        # Convert to lowercase and remove duplicates
        fields_lower = [f.lower().strip() for f in v]
        fields_lower = list(
            dict.fromkeys(fields_lower)
        )  # Preserve order, remove duplicates

        # Validate fields
        invalid_fields = [f for f in fields_lower if f not in AVAILABLE_FIELDS]
        if invalid_fields:
            raise ValueError(
                f"Invalid field(s): {', '.join(invalid_fields)}. "
                f"Available fields: {', '.join(sorted(AVAILABLE_FIELDS))}. "
                f'Example: ["name", "website", "phone"]'
            )

        return fields_lower

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize location if provided."""
        if v:
            return v.strip()
        return v


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


# Utility Functions
def filter_business_fields(
    business: Dict[str, Any], fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Filter business data to include only specified fields.

    Args:
        business: Business data dictionary
        fields: List of field names to include (None = all fields)

    Returns:
        Filtered business dictionary
    """
    if fields is None or len(fields) == 0:
        return business  # Return all fields

    # Always include rank and name (required fields)
    filtered = {"rank": business.get("rank", 0)}

    # Map field names to business data keys
    field_mapping = {
        "name": "name",
        "rating": "rating",
        "reviews": "reviews",
        "category": "category",
        "price_level": "price_level",
        "address": "address",
        "phone": "phone",
        "website": "website",
        "email": "email",
        "url": "url",
        "website_title": "website_title",
        "website_description": "website_description",
        "website_summary": "website_summary",
        "website_emails": "website_emails",
    }

    # Add requested fields
    for field in fields:
        key = field_mapping.get(field)
        if key:
            value = business.get(key)
            if value is not None:
                filtered[key] = value
            elif field in ["name"]:  # Required fields that should always be present
                filtered[key] = business.get(key, "N/A")

    return filtered


def sanitize_filename(text: str) -> str:
    """Sanitize text for use in filename."""
    # Replace spaces and special characters with underscores
    sanitized = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text)
    # Remove multiple consecutive underscores
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    # Remove leading/trailing underscores
    return sanitized.strip("_")


def save_results_to_file(
    results: List[BusinessResult],
    query: str,
    location: Optional[str] = None,
    output_dir: str = "output",
    output_file_type: str = "json",
) -> Dict[str, str]:
    """
    Save results to output folder in specified format (JSON or CSV).

    Args:
        results: List of business results to save
        query: Search query
        location: Optional location
        output_dir: Output directory path
        output_file_type: File format - 'json' or 'csv'. Default: 'json'

    Returns:
        Dictionary with paths to saved files
    """
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename-safe query string
        query_safe = sanitize_filename(query)
        location_safe = sanitize_filename(location) if location else ""
        search_query = f"{query_safe}_{location_safe}" if location_safe else query_safe
        if not search_query:
            search_query = "results"

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Build full query string for filename
        filename_base = f"results_{search_query}_{timestamp}"

        saved_files = {}

        if output_file_type == "csv":
            import csv

            # Save CSV file
            csv_path = output_path / f"{filename_base}.csv"
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                # Define CSV columns
                fieldnames = [
                    "rank",
                    "name",
                    "rating",
                    "reviews",
                    "category",
                    "price_level",
                    "address",
                    "phone",
                    "website",
                    "email",
                    "url",
                    "website_title",
                    "website_description",
                    "website_summary",
                    "website_emails",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for result in results:
                    row = {
                        "rank": result.rank,
                        "name": result.name,
                        "rating": result.rating,
                        "reviews": result.reviews,
                        "category": result.category,
                        "price_level": result.price_level,
                        "address": result.address,
                        "phone": result.phone,
                        "website": result.website,
                        "email": result.email,
                        "url": result.url,
                        "website_title": result.website_title or "",
                        "website_description": result.website_description or "",
                        "website_summary": result.website_summary or "",
                        "website_emails": (
                            ", ".join(result.website_emails)
                            if result.website_emails
                            else ""
                        ),
                    }
                    writer.writerow(row)

            saved_files["csv_path"] = str(csv_path)
            logger.info(f"Results saved to CSV: {csv_path}")

        else:  # Default to JSON
            # Prepare data for JSON
            json_data = {
                "search_query": f"{query} in {location}" if location else query,
                "location": location,
                "total_found": len(results),
                "timestamp": datetime.now().isoformat(),
                "results": [result.model_dump() for result in results],
            }

            # Save JSON file
            json_path = output_path / f"{filename_base}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            saved_files["json_path"] = str(json_path)
            logger.info(f"Results saved to JSON: {json_path}")

        return saved_files

    except Exception as e:
        logger.error(f"Error saving results to file: {str(e)}", exc_info=True)
        raise


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
    - Returns basic business information without website enrichment

    Use the /api/v1/enrich endpoint to enrich results with additional website information.

    Args:
        request_data: Scrape request with query, location, and max_results
        request: FastAPI Request object for rate limiting

    Returns:
        ScrapeResponse with results

    Raises:
        HTTPException: If scraping fails or request is invalid
    """
    try:
        fields_info = (
            f", fields={request_data.fields}" if request_data.fields else ", fields=all"
        )
        max_results_info = (
            request_data.max_results if request_data.max_results else "all"
        )
        logger.info(
            f"Received scrape request: query='{request_data.query}', "
            f"location='{request_data.location}', max_results={max_results_info}{fields_info}"
        )

        # Create agent instance
        agent = create_agent()

        # Process the scrape request (without enrichment)
        # Pass None for max_results if not specified (will scrape all results)
        result = await agent.process(
            query=request_data.query,
            location=request_data.location,
            max_results=request_data.max_results,
            enrich_with_website=False,  # Always false for scraping endpoint
        )

        # Filter fields if specified
        fields_to_extract = request_data.fields

        # Convert results to response model
        business_results = []
        for business in result.get("results", []):
            # Build BusinessResult with all fields first
            business_result = BusinessResult(
                rank=business.get("rank", 0),
                name=(
                    business.get("name", "N/A")
                    if (fields_to_extract is None or "name" in fields_to_extract)
                    else "N/A"
                ),
                rating=(
                    business.get("rating", "N/A")
                    if (fields_to_extract is None or "rating" in fields_to_extract)
                    else "N/A"
                ),
                reviews=(
                    business.get("reviews", "N/A")
                    if (fields_to_extract is None or "reviews" in fields_to_extract)
                    else "N/A"
                ),
                category=(
                    business.get("category", "N/A")
                    if (fields_to_extract is None or "category" in fields_to_extract)
                    else "N/A"
                ),
                price_level=(
                    business.get("price_level", "N/A")
                    if (fields_to_extract is None or "price_level" in fields_to_extract)
                    else "N/A"
                ),
                address=(
                    business.get("address", "N/A")
                    if (fields_to_extract is None or "address" in fields_to_extract)
                    else "N/A"
                ),
                phone=(
                    business.get("phone", "N/A")
                    if (fields_to_extract is None or "phone" in fields_to_extract)
                    else "N/A"
                ),
                website=(
                    business.get("website", "N/A")
                    if (fields_to_extract is None or "website" in fields_to_extract)
                    else "N/A"
                ),
                email=(
                    business.get("email", "N/A")
                    if (fields_to_extract is None or "email" in fields_to_extract)
                    else "N/A"
                ),
                url=(
                    business.get("url", "N/A")
                    if (fields_to_extract is None or "url" in fields_to_extract)
                    else "N/A"
                ),
                website_title=(
                    business.get("website_title")
                    if (
                        fields_to_extract is None
                        or "website_title" in fields_to_extract
                    )
                    else None
                ),
                website_description=(
                    business.get("website_description")
                    if (
                        fields_to_extract is None
                        or "website_description" in fields_to_extract
                    )
                    else None
                ),
                website_summary=(
                    business.get("website_summary")
                    if (
                        fields_to_extract is None
                        or "website_summary" in fields_to_extract
                    )
                    else None
                ),
                website_emails=(
                    business.get("website_emails")
                    if (
                        fields_to_extract is None
                        or "website_emails" in fields_to_extract
                    )
                    else None
                ),
            )
            business_results.append(business_result)

        logger.info(
            f"Successfully scraped {result.get('total_found', 0)} results for query: {request_data.query}"
        )

        # Save to file if enabled
        saved_files = None
        if request_data.save_to_file:
            try:
                saved_files = save_results_to_file(
                    results=business_results,
                    query=request_data.query,
                    location=request_data.location,
                    output_file_type=request_data.output_file_type,
                )
                logger.info(f"Results saved to files: {saved_files}")
            except Exception as save_error:
                logger.error(f"Failed to save results to file: {str(save_error)}")
                # Don't fail the request if saving fails, just log the error

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
        error_msg = str(e)
        logger.error(f"Error scraping Google Maps: {error_msg}", exc_info=True)

        # Provide more helpful error messages for common issues
        if "closed" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Browser connection was lost during scraping. This may be due to network issues, Google Maps detection, or timeout. Please try again.",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {error_msg}",
        )


@app.post(
    "/api/v1/enrich",
    response_model=ScrapeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Enrichment"],
    summary="Enrich business results with website information",
    dependencies=[Depends(verify_api_key)],
)
@limiter.limit(
    f"{RATE_LIMIT_PER_MINUTE}/minute"
)  # Rate limit from environment variable
async def enrich_business_results(
    request: Request,
    file: UploadFile = File(..., description="JSON or CSV file containing results array"),
    save_to_file: bool = Form(
        False, description="Whether to save enriched results to output folder"
    ),
    output_file_type: Optional[str] = Form(
        "json",
        description="Output file type when save_to_file is true. Options: 'json' or 'csv'. Default: 'json'",
    ),
):
    """
    Enrich business results with website information and email addresses.

    This endpoint:
    - Accepts a JSON or CSV file upload with a list of business results
    - Requires 'name' and 'website' fields in the input file
    - Visits each business website to extract additional information
    - Extracts email addresses, website metadata, and additional contact information
    - Returns enriched results with website_title, website_description, website_summary, and website_emails

    Expected JSON file format:
    {
        "results": [
            {
                "name": "Company Name",
                "website": "https://example.com",
                ...
            },
            ...
        ]
    }

    Expected CSV file format:
    CSV should have columns: name, website (required), and optionally: rank, rating, reviews, category, price_level, address, phone, email, url

    Args:
        request: FastAPI Request object for rate limiting
        file: JSON or CSV file containing results array (must include 'name' and 'website' fields)
        save_to_file: Whether to save enriched results to output folder
        output_file_type: Output file type when save_to_file is true ('json' or 'csv')

    Returns:
        JSON or CSV response with enriched results (name and website are always included)

    Raises:
        HTTPException: If enrichment fails or request is invalid
    """
    try:
        import csv
        import io

        # Validate file type
        if not (file.filename.endswith(".json") or file.filename.endswith(".csv")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload a JSON or CSV file.",
            )

        # Read file content
        content = await file.read()
        content_str = content.decode("utf-8")

        # Parse based on file type
        if file.filename.endswith(".csv"):
            # Parse CSV file
            csv_file = io.StringIO(content_str)
            reader = csv.DictReader(csv_file)
            
            # Get column names (case-insensitive)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CSV file has no header row or is empty.",
                )
            
            # Create mapping of lowercase column names to original names
            column_map = {col.strip().lower(): col for col in fieldnames}
            
            results_list = []
            for idx, row in enumerate(reader, start=1):
                # Convert CSV row to dictionary with normalized keys
                result_dict = {}
                
                # Process each column
                for orig_key, value in row.items():
                    if orig_key is None:
                        continue
                    key_lower = orig_key.strip().lower()
                    value = value.strip() if value else ""
                    
                    # Handle special fields
                    if key_lower == "rank":
                        try:
                            result_dict[key_lower] = int(value) if value else idx
                        except ValueError:
                            result_dict[key_lower] = idx
                    elif key_lower == "website_emails":
                        # Split comma-separated emails and clean them
                        if value:
                            emails = [e.strip() for e in value.split(",") if e.strip() and "@" in e.strip()]
                            result_dict[key_lower] = emails if emails else []
                        else:
                            result_dict[key_lower] = []
                    elif key_lower in ["website_title", "website_description", "website_summary"]:
                        # Optional fields - use None if empty
                        result_dict[key_lower] = value if value else None
                    elif key_lower in ["name", "rating", "reviews", "category", "price_level", 
                                      "address", "phone", "website", "email", "url"]:
                        # Required fields - use "N/A" if empty
                        result_dict[key_lower] = value if value else "N/A"
                    else:
                        # Unknown fields - keep as is
                        result_dict[key_lower] = value
                
                # Ensure required fields exist with defaults
                if "rank" not in result_dict:
                    result_dict["rank"] = idx
                for required_field in ["name", "rating", "reviews", "category", "price_level", 
                                      "address", "phone", "website", "email", "url"]:
                    if required_field not in result_dict:
                        result_dict[required_field] = "N/A"
                
                # Ensure optional fields exist
                if "website_title" not in result_dict:
                    result_dict["website_title"] = None
                if "website_description" not in result_dict:
                    result_dict["website_description"] = None
                if "website_summary" not in result_dict:
                    result_dict["website_summary"] = None
                if "website_emails" not in result_dict:
                    result_dict["website_emails"] = []
                
                results_list.append(result_dict)
            
            if len(results_list) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CSV file is empty or contains no valid rows.",
                )
        else:
            # Parse JSON file
            try:
                data = json.loads(content_str)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid JSON format: {str(e)}",
                )

            # Extract results array
            results_list = data.get("results", [])
            if not isinstance(results_list, list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="JSON file must contain a 'results' array.",
                )

            if len(results_list) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Results array is empty.",
                )

        # Validate output_file_type
        if output_file_type:
            output_file_type = output_file_type.lower().strip()
            if output_file_type not in ["json", "csv"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="output_file_type must be 'json' or 'csv'",
                )
        else:
            output_file_type = "json"

        logger.info(
            f"Received enrich request from file '{file.filename}': {len(results_list)} results, "
            f"output_format='{output_file_type}'"
        )

        # Create agent instance
        agent = create_agent()

        # Convert results to dictionaries for processing
        # Skip rows without valid name or website
        results_dict = []
        skipped_count = 0
        for idx, result in enumerate(results_list, start=1):
            if not isinstance(result, dict):
                logger.warning(f"Row {idx}: Skipping invalid result - not a dictionary")
                skipped_count += 1
                continue

            # Validate name and website
            name = result.get("name", "").strip()
            website = result.get("website", "").strip()
            
            # Skip if name is missing or invalid
            if not name or name.lower() == "n/a" or name.lower() == "string":
                logger.warning(f"Row {idx}: Skipping - missing or invalid 'name' field: '{name}'")
                skipped_count += 1
                continue
            
            # Skip if website is missing or invalid
            if not website or website.lower() == "n/a" or website.lower() == "string" or not website.startswith("http"):
                logger.warning(f"Row {idx}: Skipping - missing or invalid 'website' field: '{website}'")
                skipped_count += 1
                continue

            # Ensure website_emails is always a list
            website_emails = result.get("website_emails")
            if isinstance(website_emails, str):
                # If it's a string, split by comma
                website_emails = [e.strip() for e in website_emails.split(",") if e.strip() and "@" in e.strip()]
            elif not isinstance(website_emails, list):
                # If it's not a list, make it an empty list
                website_emails = []
            
            results_dict.append(
                {
                    "rank": result.get("rank", 0),
                    "name": name,
                    "rating": result.get("rating", "N/A"),
                    "reviews": result.get("reviews", "N/A"),
                    "category": result.get("category", "N/A"),
                    "price_level": result.get("price_level", "N/A"),
                    "address": result.get("address", "N/A"),
                    "phone": result.get("phone", "N/A"),
                    "website": website,
                    "email": result.get("email", "N/A"),
                    "url": result.get("url", "N/A"),
                    "website_title": result.get("website_title"),
                    "website_description": result.get("website_description"),
                    "website_summary": result.get("website_summary"),
                    "website_emails": website_emails,
                }
            )
        
        # Check if we have any valid results after filtering
        if len(results_dict) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No valid rows found. All {len(results_list)} rows were skipped due to missing or invalid 'name' or 'website' fields.",
            )
        
        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} row(s) with missing or invalid name/website fields")

        # Enrich results (no location parameter)
        enriched_results = await agent.enrich_results(
            results=results_dict,
            location=None,
        )

        # Convert enriched results back to response model
        # Always include name and website, include all other fields
        business_results = []
        for business in enriched_results:
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

        logger.info(f"Successfully enriched {len(business_results)} results")

        # Save to file if enabled
        saved_files = None
        if save_to_file:
            try:
                # Use "enriched" prefix with first result's name for filename
                if business_results:
                    query_for_file = f"enriched_{business_results[0].name}"
                else:
                    query_for_file = "enriched_results"

                saved_files = save_results_to_file(
                    results=business_results,
                    query=query_for_file,
                    location=None,
                    output_file_type=output_file_type,
                )
                logger.info(f"Enriched results saved to files: {saved_files}")
            except Exception as save_error:
                logger.error(
                    f"Failed to save enriched results to file: {str(save_error)}"
                )
                # Don't fail the request if saving fails, just log the error

        # Return response based on output_file_type
        if output_file_type == "csv":
            # Return CSV response
            import csv
            import io
            
            output = io.StringIO()
            fieldnames = [
                "rank", "name", "rating", "reviews", "category", "price_level",
                "address", "phone", "website", "email", "url",
                "website_title", "website_description", "website_summary", "website_emails"
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in business_results:
                row = {
                    "rank": result.rank,
                    "name": result.name,
                    "rating": result.rating,
                    "reviews": result.reviews,
                    "category": result.category,
                    "price_level": result.price_level,
                    "address": result.address,
                    "phone": result.phone,
                    "website": result.website,
                    "email": result.email,
                    "url": result.url,
                    "website_title": result.website_title or "",
                    "website_description": result.website_description or "",
                    "website_summary": result.website_summary or "",
                    "website_emails": (
                        ", ".join(result.website_emails)
                        if result.website_emails
                        else ""
                    ),
                }
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=enriched_results.csv"
                }
            )
        else:
            # Return JSON response
            response = ScrapeResponse(
                status="success",
                query="",  # Not applicable for enrichment
                location=None,
                total_found=len(business_results),
                results=business_results,
                processing_status="enriched",
            )
            return response

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error enriching results: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enrichment failed: {str(e)}",
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
            "enrich": "/api/v1/enrich",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_level="info",
    )
