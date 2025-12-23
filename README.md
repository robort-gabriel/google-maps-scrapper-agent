# 🗺️ Google Maps Scraper API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-orange.svg)](https://playwright.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Production-ready FastAPI application for scraping Google Maps search results without using the official Maps API. Features comprehensive anti-detection capabilities, CSV/JSON support, and file upload endpoints.

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
  - [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Rate Limiting](#rate-limiting)
  - [Error Handling](#error-handling)
- [Configuration](#-configuration)
- [Output Formats](#-output-formats)
- [Anti-Detection Features](#-anti-detection-features)
- [Examples](#-examples)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

## ✨ Features

### Core Features
- ✅ **Free Solution**: No Google Maps API key required
- 🌐 **Browser Automation**: Uses Playwright to render JavaScript and extract real data
- 📊 **Comprehensive Data Extraction**: Business name, rating, reviews, category, price level, address, phone number, website, email, and Google Maps URL
- 📞 **Phone & Email Extraction**: Extracts phone numbers and emails from Google Maps listings
- 🔍 **Website Enrichment** (Optional): Visit business websites to extract additional information and emails
- 🎯 **Smart Page Detection**: Automatically finds Contact and About pages for better data extraction
- 📄 **Pagination Support**: Automatically scrolls to load more results
- 📤 **File Upload Support**: Upload JSON or CSV files for enrichment
- 📈 **CSV Output**: Export results in CSV format for spreadsheet applications
- 🔄 **Flexible Input/Output**: Support for JSON and CSV formats for both input and output
- 🔗 **LangGraph Workflow**: Follows the same patterns as your other agents

### Anti-Detection Features
- 🕵️ **Stealth Browser Configuration**: Uses playwright-stealth to evade bot detection
- 🔄 **Proxy Rotation Support**: Configurable proxy rotation to avoid IP blocking (only when `PROXY_ENABLED=true`)
- 🤖 **Human Behavior Simulation**: Random delays, realistic mouse movements, natural scrolling
- 🌍 **Geo-Location Spoofing**: Timezone and geolocation matching based on search location
- 🔄 **User Agent Rotation**: Rotating realistic browser fingerprints
- 🧩 **CAPTCHA Handling**: Integration with 2Captcha/Anti-Captcha services
- 🔀 **Fallback Methods**: Multiple scraping methods with automatic failover
- 🍪 **Cookie Consent Handling**: Automatic handling of cookie popups

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Configure environment (optional)
# Create .env file with your settings

# 3. Start the API
python main.py
```

The API will be available at:
- 🌐 API: `http://localhost:8000`
- 📚 Interactive Docs: `http://localhost:8000/docs`
- 📖 ReDoc: `http://localhost:8000/redoc`

## 📦 Installation

### Step 1: Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Playwright browsers

```bash
playwright install chromium
```

This downloads the Chromium browser that Playwright will use for scraping.

## 💻 Usage

### Run as FastAPI Application (Recommended for Production)

The scraper is available as a production-ready FastAPI application with security features:

- 🔐 **API Key Authentication** - Secure your API with API key authentication
- 🚦 **Rate Limiting** - Built-in rate limiting (10 requests/minute by default)
- ✅ **Input Validation** - Comprehensive input validation and sanitization
- 🌐 **CORS Support** - Configurable CORS for cross-origin requests
- 📊 **Structured Responses** - Well-defined request/response models
- 🔍 **Interactive Documentation** - Auto-generated API docs at `/docs` and `/redoc`
- 🛡️ **Error Handling** - Comprehensive error handling with proper HTTP status codes

### Configuration

Create a `.env` file in the project root with your configuration:

```env
# ============================================================================
# API Configuration
# ============================================================================
API_KEY=your-secret-api-key-here
HOST=0.0.0.0
PORT=8000
DEBUG=False
CORS_ORIGINS=*
RATE_LIMIT_PER_MINUTE=10

# ============================================================================
# Anti-Detection Configuration
# ============================================================================
# Enable stealth browser mode (default: true)
STEALTH_ENABLED=true

# Enable human-like behavior simulation (default: true)
HUMAN_SIMULATION_ENABLED=true

# ============================================================================
# Proxy Configuration (Optional)
# ============================================================================
# Master switch to enable/disable proxy usage (default: false)
PROXY_ENABLED=false

# Single proxy URL (only used if PROXY_ENABLED=true)
PROXY_URL=http://proxy-host:port
PROXY_USERNAME=your-proxy-username
PROXY_PASSWORD=your-proxy-password

# Enable proxy rotation (default: false, only used if PROXY_ENABLED=true)
PROXY_ROTATION_ENABLED=false

# Comma-separated list of proxies for rotation (only used if PROXY_ENABLED=true)
PROXY_LIST=http://proxy1:port,http://proxy2:port,http://proxy3:port

# ============================================================================
# Browserless Fallback (Optional)
# ============================================================================
# Browserless.io token for fallback scraping method
BROWSERLESS_TOKEN=your-browserless-token
BROWSERLESS_BASE_URL=https://chrome.browserless.io

# ============================================================================
# CAPTCHA Solving (Optional)
# ============================================================================
# Service: "2captcha" or "anticaptcha"
CAPTCHA_SERVICE=2captcha
CAPTCHA_API_KEY=your-captcha-api-key
```

### API Endpoints

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Google Maps Scraper API is running",
  "version": "1.0.0",
  "stealth_status": {
    "stealth_enabled": true,
    "human_simulation_enabled": true,
    "proxy_configured": false,
    "browserless_configured": false,
    "captcha_service_configured": false
  }
}
```

#### Scrape Google Maps

```http
POST /api/v1/scrape
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "coffee shops",
  "location": "San Francisco, CA",
  "max_results": 20,
  "save_to_file": false,
  "output_file_type": "json",
  "fields": ["name", "website", "phone", "email"]
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query (e.g., "coffee shops", "restaurants") |
| `location` | string | No | null | Optional location (e.g., "New York, NY") |
| `max_results` | integer | No | 20 | Maximum number of results (1-100) |
| `save_to_file` | boolean | No | false | Whether to save results to output folder |
| `output_file_type` | string | No | "json" | Output file type when save_to_file is true. Options: "json" or "csv" |
| `fields` | array | No | null | Optional list of fields to extract. If not specified, all fields are returned |

**Response:**
```json
{
  "status": "success",
  "query": "coffee shops",
  "location": "San Francisco, CA",
  "total_found": 20,
  "processing_status": "completed",
  "results": [
    {
      "rank": 1,
      "name": "Blue Bottle Coffee",
      "rating": "4.5",
      "reviews": "1234",
      "category": "Coffee shop",
      "price_level": "$$",
      "address": "66 Mint St, San Francisco, CA",
      "phone": "+1 415-555-1234",
      "website": "https://www.bluebottlecoffee.com",
      "email": "contact@bluebottlecoffee.com",
      "url": "https://www.google.com/maps/..."
    }
  ]
}
```

#### Enrich Business Results

```http
POST /api/v1/enrich
X-API-Key: your-api-key-here
Content-Type: multipart/form-data
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | file | Yes | - | JSON or CSV file containing business results. Must include `name` and `website` fields |
| `save_to_file` | boolean | No | false | Whether to save enriched results to output folder |
| `output_file_type` | string | No | "json" | Output file type. Options: "json" or "csv" |

**Important Notes:**
- ⚠️ The input file **must** include `name` and `website` fields for each row
- ✅ Rows with missing or invalid `name` or `website` fields will be **skipped** (not cause an error)
- 🔗 The `website` field must be a valid URL starting with `http://` or `https://`
- 📤 Returns CSV or JSON based on `output_file_type` parameter

**Expected JSON File Format:**
```json
{
  "results": [
    {
      "name": "Company Name",
      "website": "https://example.com",
      "phone": "+1 555-1234",
      "email": "contact@example.com"
    }
  ]
}
```

**Expected CSV File Format:**
```csv
name,website,phone,email
Company Name,https://example.com,+1 555-1234,contact@example.com
```

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/enrich" \
  -H "X-API-Key: your-api-key" \
  -F "file=@results.csv" \
  -F "save_to_file=true" \
  -F "output_file_type=csv"
```

**Example Request (Python):**
```python
import requests

url = "http://localhost:8000/api/v1/enrich"
headers = {"X-API-Key": "your-api-key"}
files = {"file": open("results.csv", "rb")}
data = {
    "save_to_file": True,
    "output_file_type": "csv"
}

response = requests.post(url, headers=headers, files=files, data=data)

# Handle response based on output_file_type
if data["output_file_type"] == "csv":
    # Save CSV response
    with open("enriched_results.csv", "wb") as f:
        f.write(response.content)
    print("CSV file saved")
else:
    # Handle JSON response
    result = response.json()
    print(f"Enriched {result['total_found']} results")
```

**Response Format:**
- When `output_file_type="csv"`: Returns CSV file download with `Content-Type: text/csv`
- When `output_file_type="json"` (default): Returns JSON response with enriched results

#### Extract Website and Company Name

```http
POST /api/v1/extract
X-API-Key: your-api-key-here
Content-Type: multipart/form-data
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | JSON file containing results array |

**Response:**
```json
{
  "status": "success",
  "total_extracted": 10,
  "results": [
    {
      "website": "https://example.com",
      "companyName": "Company Name"
    }
  ]
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "X-API-Key: your-api-key" \
  -F "file=@results.json"
```

### Authentication

The API uses API key authentication via the `X-API-Key` header.

**Setting Up Authentication:**

1. Set `API_KEY` in your `.env` file:
   ```env
   API_KEY=your-secret-api-key-here
   ```

2. Include the API key in your requests:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/scrape" \
     -H "X-API-Key: your-secret-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{"query": "coffee shops", "location": "San Francisco, CA"}'
   ```

**Disabling Authentication:**

If `API_KEY` is not set in the environment, the API will be accessible without authentication (useful for development).

### Rate Limiting

The API implements rate limiting to prevent abuse:
- **Default**: 10 requests per minute per IP address
- **Configurable**: Set `RATE_LIMIT_PER_MINUTE` in `.env`

When rate limit is exceeded, you'll receive:
```json
{
  "detail": "Rate limit exceeded: 10 per 1 minute"
}
```

### Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid API key
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error during scraping
- `503 Service Unavailable` - Bot detection, CAPTCHA, or all methods failed

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

**Anti-Detection Related Errors:**

| Status Code | Error Type | Solution |
|-------------|------------|----------|
| 503 | CAPTCHA detected | Configure `CAPTCHA_SERVICE` and `CAPTCHA_API_KEY`, or try again later |
| 503 | Bot detection | Use proxy rotation, wait before retrying |
| 503 | All methods failed | Check proxy configuration, try again later |

## 📤 Output Formats

### JSON Format

```json
{
  "search_query": "coffee shops in San Francisco, CA",
  "location": "San Francisco, CA",
  "total_found": 20,
  "timestamp": "2024-11-30T10:30:00",
  "results": [
    {
      "rank": 1,
      "name": "Blue Bottle Coffee",
      "rating": "4.5",
      "reviews": "1234",
      "category": "Coffee shop",
      "price_level": "$$",
      "address": "66 Mint St, San Francisco, CA",
      "phone": "+1 415-555-1234",
      "website": "https://www.bluebottlecoffee.com",
      "email": "contact@bluebottlecoffee.com",
      "website_title": "Blue Bottle Coffee - Artisan Coffee Roasters",
      "website_description": "Premium coffee roasters specializing in single-origin beans",
      "website_summary": "Blue Bottle Coffee is a specialty coffee roaster...",
      "website_emails": ["contact@bluebottlecoffee.com", "info@bluebottlecoffee.com"],
      "url": "https://www.google.com/maps/..."
    }
  ]
}
```

### CSV Format

When `output_file_type="csv"`, results are saved as CSV files:

```csv
rank,name,rating,reviews,category,price_level,address,phone,website,email,url,website_title,website_description,website_summary,website_emails
1,Blue Bottle Coffee,4.5,1234,Coffee shop,$$,66 Mint St San Francisco CA,+1 415-555-1234,https://www.bluebottlecoffee.com,contact@bluebottlecoffee.com,https://www.google.com/maps/...,Blue Bottle Coffee - Artisan Coffee Roasters,Premium coffee roasters...,Blue Bottle Coffee is a specialty...,contact@bluebottlecoffee.com, info@bluebottlecoffee.com
```

**File Structure:**
- **`results_{query}_{timestamp}.json`** - Machine-readable JSON format for further processing
- **`results_{query}_{timestamp}.csv`** - CSV format for spreadsheet applications (when `output_file_type="csv"`)

## 🛡️ Anti-Detection Features

### Overview

This scraper includes comprehensive anti-detection features to bypass bot detection and ensure reliable operation:

| Feature | Description | Configuration |
|---------|-------------|---------------|
| Stealth Browser | Evades automation detection | `STEALTH_ENABLED=true` |
| Human Simulation | Random delays, natural scrolling | `HUMAN_SIMULATION_ENABLED=true` |
| Proxy Rotation | Rotate IP addresses | `PROXY_ENABLED=true`, `PROXY_URL`, `PROXY_LIST` |
| User Agent Rotation | Rotate browser fingerprints | Automatic |
| Timezone Spoofing | Match timezone to search location | Automatic |
| Geolocation Spoofing | Match coordinates to search location | Automatic |
| CAPTCHA Solving | Automatic CAPTCHA resolution | `CAPTCHA_SERVICE`, `CAPTCHA_API_KEY` |
| Cookie Consent | Auto-handle cookie popups | Automatic |

### Proxy Configuration

**Important:** Proxy is only used when `PROXY_ENABLED=true`. Set this to `false` to run without proxy.

For reliable operation at scale, configure proxy rotation:

```env
# Enable proxy usage
PROXY_ENABLED=true

# Single proxy
PROXY_URL=http://proxy.example.com:8080
PROXY_USERNAME=user
PROXY_PASSWORD=pass

# Multiple proxies with rotation
PROXY_ROTATION_ENABLED=true
PROXY_LIST=http://proxy1:8080,http://proxy2:8080,http://proxy3:8080
```

**To disable proxy (run direct connection):**
```env
PROXY_ENABLED=false
```

**Recommended Proxy Providers:**
- Bright Data (formerly Luminati)
- Oxylabs
- Smartproxy
- IPRoyal
- Webshare

### CAPTCHA Handling

If CAPTCHA challenges are frequent, integrate a solving service:

```env
# Using 2Captcha
CAPTCHA_SERVICE=2captcha
CAPTCHA_API_KEY=your-2captcha-key

# OR using Anti-Captcha
CAPTCHA_SERVICE=anticaptcha
CAPTCHA_API_KEY=your-anticaptcha-key
```

The scraper will automatically:
1. Detect CAPTCHA challenges
2. Submit to solving service
3. Wait for solution
4. Inject solution and continue

## 📝 Examples

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pizza restaurants",
    "location": "Chicago, IL",
    "max_results": 10,
    "save_to_file": true,
    "output_file_type": "csv"
  }'
```

### Using Python

```python
import requests

url = "http://localhost:8000/api/v1/scrape"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json"
}
data = {
    "query": "coffee shops",
    "location": "San Francisco, CA",
    "max_results": 20,
    "save_to_file": True,
    "output_file_type": "csv"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(f"Found {result['total_found']} results")
for business in result['results']:
    print(f"{business['rank']}. {business['name']} - {business['rating']} stars")
```

### Using JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

const url = 'http://localhost:8000/api/v1/scrape';
const headers = {
  'X-API-Key': 'your-api-key',
  'Content-Type': 'application/json'
};
const data = {
  query: 'coffee shops',
  location: 'San Francisco, CA',
  max_results: 20,
  save_to_file: true,
  output_file_type: 'csv'
};

fetch(url, {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(data)
})
  .then(res => res.json())
  .then(result => {
    console.log(`Found ${result.total_found} results`);
    result.results.forEach(business => {
      console.log(`${business.rank}. ${business.name} - ${business.rating} stars`);
    });
  });
```

## 🚀 Deployment

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t google-maps-scraper-api .
docker run -p 8000:8000 --env-file .env google-maps-scraper-api
```

### Using Gunicorn with Uvicorn Workers

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Security Best Practices

1. **Always set a strong API key** in production
2. **Use HTTPS** in production (configure reverse proxy like nginx)
3. **Restrict CORS origins** to your frontend domains
4. **Monitor rate limits** and adjust as needed
5. **Keep dependencies updated** regularly
6. **Use environment variables** for sensitive configuration
7. **Implement logging** and monitoring in production

## 🔧 Troubleshooting

### Playwright Installation Issues

If `playwright install chromium` fails:

```bash
# Try installing all browsers
playwright install

# Or use system browser
playwright install --with-deps chromium
```

### No Results Found

- Check your search query and location
- Verify internet connection
- Try a broader search term
- Check if Google Maps is accessible

### Rate Limiting / Bot Detection

If you get blocked or encounter CAPTCHA:

1. **Enable Stealth Mode** (if not already):
   ```env
   STEALTH_ENABLED=true
   HUMAN_SIMULATION_ENABLED=true
   ```

2. **Configure Proxy Rotation**:
   ```env
   PROXY_ENABLED=true
   PROXY_URL=http://your-proxy:port
   PROXY_ROTATION_ENABLED=true
   PROXY_LIST=http://proxy1:port,http://proxy2:port
   ```

3. **Add CAPTCHA Solving**:
   ```env
   CAPTCHA_SERVICE=2captcha
   CAPTCHA_API_KEY=your-api-key
   ```

4. **Additional Tips**:
   - Add longer delays between searches
   - Reduce `max_results`
   - Use different search queries
   - Wait 15-30 minutes before retrying
   - Use residential proxies instead of datacenter proxies

### API Key Not Working

- Verify `API_KEY` is set in `.env`
- Check that the header name is `X-API-Key` (case-sensitive)
- Ensure the API key matches exactly

### Scraping Failures

- Check internet connectivity
- Verify Playwright browser is installed: `playwright install chromium`
- Check logs for detailed error messages
- Google Maps may block excessive requests - add delays between requests

## 📊 Data Extracted

For each business, the agent extracts from Google Maps:

- **Name**: Business name
- **Rating**: Star rating (out of 5)
- **Reviews**: Number of reviews
- **Category**: Business type/category
- **Price Level**: Cost indicator ($, $$, $$$, $$$$)
- **Address**: Physical address
- **Phone**: Phone number (extracted from list view and detail panel)
- **Website**: Business website URL (extracted from list view)
- **Email**: Email address (extracted from detail panel)
- **URL**: Google Maps URL for the business

### Website Enrichment (Optional)

When using the `/api/v1/enrich` endpoint, the agent also:

- **Visits Business Websites**: Scrapes each business website for additional information
- **Finds Contact Pages**: Automatically detects and scrapes Contact/Contact Us pages for emails
- **Finds About Pages**: Automatically detects and scrapes About/About Us pages for better summaries
- **Extracts Website Metadata**:
  - Website title
  - Meta description
  - Website summary (from About page when available)
  - All email addresses found on the website
  - Additional phone numbers from the website

## 📚 API Endpoints Summary

| Endpoint | Method | Description | Input | Output |
|----------|--------|-------------|-------|--------|
| `/health` | GET | Health check | - | JSON |
| `/api/v1/scrape` | POST | Scrape Google Maps | JSON body | JSON/CSV file |
| `/api/v1/enrich` | POST | Enrich business results | JSON/CSV file upload | JSON/CSV response |
| `/api/v1/extract` | POST | Extract website & companyName | JSON file upload | JSON |

## 🎯 Use Cases

- **Local Business Research**: Find competitors in your area
- **Market Analysis**: Research business density by category
- **Lead Generation**: Extract contact information (phone, email, website) for outreach
- **Email Collection**: Automatically find business emails from websites and Contact pages
- **Data Analysis**: Analyze ratings, reviews, and pricing trends
- **Location Scouting**: Find businesses in specific areas
- **Contact Database Building**: Build comprehensive contact databases with phone, email, and website

## ⚠️ Limitations

- **Rate Limits**: Google may still block excessive requests even with anti-detection (use proxy rotation for scale)
- **CAPTCHA**: May appear if detection is triggered (configure CAPTCHA service for automatic resolution)
- **Data Accuracy**: Extracted data depends on Google Maps HTML structure which may change
- **JavaScript Required**: Must use browser automation; simple HTTP requests won't work
- **No API Features**: Can't access some API-only features (e.g., detailed hours, photos)
- **Proxy Quality**: Anti-detection effectiveness depends on proxy quality and rotation

## 🔮 Future Enhancements

Potential improvements:
- Extract photos and business hours
- Support for filtering results
- Parallel scraping for multiple queries
- Support for multiple languages
- Selenium undetected-chromedriver fallback
- Machine learning-based CAPTCHA detection
- Residential proxy pool integration

## 📄 License

This is a standalone agent template. Use and modify as needed for your projects.

**Note**: Web scraping may violate Google's Terms of Service. Use responsibly and consider using the official Google Places API for production applications.

---

**Made with ❤️ for developers who need reliable Google Maps scraping**
