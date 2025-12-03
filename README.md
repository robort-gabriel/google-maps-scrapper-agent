# Google Maps Scraper LangGraph Agent

Production-ready LangGraph agent for scraping Google Maps search results without using the official Maps API. This advanced agent uses Playwright for browser automation with **comprehensive anti-detection features** to extract business information reliably.

## Features

### Core Features
- **Free Solution**: No Google Maps API key required
- **Browser Automation**: Uses Playwright to render JavaScript and extract real data
- **Comprehensive Data Extraction**: Business name, rating, reviews, category, price level, address, phone number, website, email, and Google Maps URL
- **Phone & Email Extraction**: Extracts phone numbers and emails from Google Maps listings
- **Website Enrichment** (Optional): Visit business websites to extract additional information and emails
- **Smart Page Detection**: Automatically finds Contact and About pages for better data extraction
- **Pagination Support**: Automatically scrolls to load more results
- **LangGraph Workflow**: Follows the same patterns as your other agents

### Anti-Detection Features
- **🕵️ Stealth Browser Configuration**: Uses playwright-stealth to evade bot detection
- **🔄 Proxy Rotation Support**: Configurable proxy rotation to avoid IP blocking
- **🤖 Human Behavior Simulation**: Random delays, realistic mouse movements, natural scrolling
- **🌍 Geo-Location Spoofing**: Timezone and geolocation matching based on search location
- **🔄 User Agent Rotation**: Rotating realistic browser fingerprints
- **🧩 CAPTCHA Handling**: Integration with 2Captcha/Anti-Captcha services
- **🔀 Fallback Methods**: Multiple scraping methods with automatic failover
- **🍪 Cookie Consent Handling**: Automatic handling of cookie popups

## Workflow

The agent follows a streamlined workflow:

1. **Scrape** - Uses Playwright to navigate to Google Maps and extract search results (including phone numbers and websites from list view)
2. **Enrich** - (Optional) Clicks on each business to extract phone numbers and emails from detail panels
3. **Process** - Structures and cleans the scraped data
4. **Enrich Websites** - (Optional) Visits business websites to extract additional information, emails, and summaries
5. **Save** - Outputs results in markdown and JSON formats

## Installation

### Step 1: Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Playwright browsers

```bash
playwright install chromium
```

This downloads the Chromium browser that Playwright will use for scraping.

## Usage

### Run as FastAPI Application (Recommended for Production)

The scraper is now available as a production-ready FastAPI application with security features:

- 🔐 **API Key Authentication** - Secure your API with API key authentication
- 🚦 **Rate Limiting** - Built-in rate limiting (10 requests/minute by default)
- ✅ **Input Validation** - Comprehensive input validation and sanitization
- 🌐 **CORS Support** - Configurable CORS for cross-origin requests
- 📊 **Structured Responses** - Well-defined request/response models
- 🔍 **Interactive Documentation** - Auto-generated API docs at `/docs` and `/redoc`
- 🛡️ **Error Handling** - Comprehensive error handling with proper HTTP status codes

#### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Configure environment (optional)
# Create .env file with your settings (see Environment Variables section below)

# 3. Start the API
python app.py
```

#### Environment Variables

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
# Proxy Configuration (Optional but Recommended)
# ============================================================================
# Single proxy URL
PROXY_URL=http://proxy-host:port
PROXY_USERNAME=your-proxy-username
PROXY_PASSWORD=your-proxy-password

# Enable proxy rotation (default: false)
PROXY_ROTATION_ENABLED=false

# Comma-separated list of proxies for rotation
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

Or with uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

For production:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### API Endpoints

**Health Check:**

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Google Maps Scraper API is running",
  "version": "1.0.0"
}
```

**Scrape Google Maps:**

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
  "enrich_with_website": false
}
```

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
      "url": "https://www.google.com/maps/...",
      "website_title": "Blue Bottle Coffee - Artisan Coffee Roasters",
      "website_description": "Premium coffee roasters...",
      "website_summary": "Blue Bottle Coffee is a specialty...",
      "website_emails": ["contact@bluebottlecoffee.com"]
    }
  ]
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query (e.g., "coffee shops", "restaurants") |
| `location` | string | No | null | Optional location (e.g., "New York, NY") |
| `max_results` | integer | No | 20 | Maximum number of results (1-100) |
| `enrich_with_website` | boolean | No | false | Visit business websites for additional info and emails |

#### Authentication

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

#### Rate Limiting

The API implements rate limiting to prevent abuse:
- **Default**: 10 requests per minute per IP address
- **Configurable**: Set `RATE_LIMIT_PER_MINUTE` in `.env`

When rate limit is exceeded, you'll receive:
```json
{
  "detail": "Rate limit exceeded: 10 per 1 minute"
}
```

#### CORS Configuration

Configure allowed origins in `.env`:

```env
# Allow all origins (not recommended for production)
CORS_ORIGINS=*

# Allow specific origins
CORS_ORIGINS=https://example.com,https://app.example.com
```

#### Error Handling

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
```

#### Example Usage

**Using cURL:**

```bash
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pizza restaurants",
    "location": "Chicago, IL",
    "max_results": 10,
    "enrich_with_website": true
  }'
```

**Using Python:**

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
    "enrich_with_website": False
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(f"Found {result['total_found']} results")
for business in result['results']:
    print(f"{business['rank']}. {business['name']} - {business['rating']} stars")
```

**Using JavaScript/Node.js:**

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
  enrich_with_website: false
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

#### Production Deployment

**Using Docker:**

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
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t google-maps-scraper-api .
docker run -p 8000:8000 --env-file .env google-maps-scraper-api
```

**Using Gunicorn with Uvicorn Workers:**

```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Security Best Practices

1. **Always set a strong API key** in production
2. **Use HTTPS** in production (configure reverse proxy like nginx)
3. **Restrict CORS origins** to your frontend domains
4. **Monitor rate limits** and adjust as needed
5. **Keep dependencies updated** regularly
6. **Use environment variables** for sensitive configuration
7. **Implement logging** and monitoring in production

#### API Troubleshooting

**API Key Not Working:**
- Verify `API_KEY` is set in `.env`
- Check that the header name is `X-API-Key` (case-sensitive)
- Ensure the API key matches exactly

**Rate Limit Issues:**
- Increase `RATE_LIMIT_PER_MINUTE` in `.env`
- Check if multiple clients are using the same IP
- Consider implementing per-user rate limiting

**Scraping Failures:**
- Check internet connectivity
- Verify Playwright browser is installed: `playwright install chromium`
- Check logs for detailed error messages
- Google Maps may block excessive requests - add delays between requests

### Run as Standalone Script

```bash
python google_maps_scraper_agent.py
```

Or run as a module:

```bash
python -m google_maps_scraper_agent
```

### Customize the Search

Edit the `example_usage()` function in the script to customize:

- **query**: What to search for (e.g., "restaurants", "coffee shops", "hair salons")
- **location**: Where to search (e.g., "New York, NY", "San Francisco, CA")
- **max_results**: How many results to extract (default: 20)
- **enrich_with_website**: Whether to visit business websites for additional info (default: False)

Example:

```python
result = await agent.process(
    query="pizza restaurants",
    location="Chicago, IL",
    max_results=30,
    enrich_with_website=True,  # Enable website scraping
)
```

### Use as a Library

You can also import and use the agent in your own Python code:

```python
from google_maps_scraper_agent import create_agent
import asyncio

async def scrape_maps():
    agent = create_agent()
    result = await agent.process(
        query="hair salons",
        location="Los Angeles, CA",
        max_results=25,
        enrich_with_website=True,  # Optional: scrape websites for emails
    )
    return result

# Run the scraper
result = asyncio.run(scrape_maps())
print(f"Found {result['total_found']} results")
```

## Output

Results are automatically saved to the `output` folder:

### File Structure

- **`results_{query}_{timestamp}.md`** - Human-readable markdown format with business details
- **`results_{query}_{timestamp}.json`** - Machine-readable JSON format for further processing

### Output Location

- When run as a script: `{script_directory}/output/`
- When run as a module: `{current_working_directory}/output/`

The `output` folder is automatically created if it doesn't exist.

### Markdown Format

```markdown
# Google Maps Search Results

**Search Query:** coffee shops in San Francisco, CA
**Total Results Found:** 20
**Generated at:** 2024-11-30 10:30:00

---

## 1. Blue Bottle Coffee

- **Rating:** 4.5 (1,234 reviews)
- **Category:** Coffee shop
- **Price Level:** $$
- **Address:** 66 Mint St, San Francisco, CA
- **Phone:** +1 415-555-1234
- **Website:** https://www.bluebottlecoffee.com
- **Email:** contact@bluebottlecoffee.com
- **Website Title:** Blue Bottle Coffee - Artisan Coffee Roasters
- **Website Description:** Premium coffee roasters specializing in single-origin beans
- **Website Summary:** Blue Bottle Coffee is a specialty coffee roaster...
- **All Emails Found:** contact@bluebottlecoffee.com, info@bluebottlecoffee.com
- **Google Maps URL:** https://www.google.com/maps/...

---

## 2. Philz Coffee

- **Rating:** 4.6 (890 reviews)
- **Category:** Coffee shop
- **Price Level:** $$
- **Address:** 201 Berry St, San Francisco, CA
- **Phone:** +1 415-555-5678
- **Website:** https://www.philzcoffee.com
- **Google Maps URL:** https://www.google.com/maps/...

---
```

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

## Data Extracted

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

When `enrich_with_website=True`, the agent also:

- **Visits Business Websites**: Scrapes each business website for additional information
- **Finds Contact Pages**: Automatically detects and scrapes Contact/Contact Us pages for emails
- **Finds About Pages**: Automatically detects and scrapes About/About Us pages for better summaries
- **Extracts Website Metadata**:
  - Website title
  - Meta description
  - Website summary (from About page when available)
  - All email addresses found on the website
  - Additional phone numbers from the website

## How It Works

### 1. Playwright Automation

The agent uses Playwright to:
- Launch a headless Chromium browser
- Navigate to Google Maps search URL
- Wait for results to load
- Scroll to load more results
- Extract data using JavaScript evaluation

### 2. Data Extraction

The scraper:
- Finds result items using `div[role="feed"]` selector
- Extracts information from aria-labels and visible text
- Parses ratings, reviews, categories, addresses, phone numbers, and websites from list view
- Clicks on each business to open detail panel and extract additional phone numbers and emails
- Deduplicates results by business name

### 3. Website Enrichment (Optional)

When enabled, the scraper:
- Visits each business website using Playwright
- Automatically finds Contact pages by scanning links for keywords (contact, contact us, get in touch, etc.)
- Automatically finds About pages by scanning links for keywords (about, about us, our story, etc.)
- Extracts emails from Contact pages (more reliable than homepage)
- Extracts website summaries from About pages (better content than homepage)
- Falls back to homepage if Contact/About pages aren't found
- Filters out false positive emails (example.com, test.com, etc.)

### 4. Rate Limiting

Built-in delays prevent:
- IP blocking
- CAPTCHA challenges
- Failed requests
- 1 second delay between website scrapes when enrichment is enabled

## Limitations

- **Rate Limits**: Google may still block excessive requests even with anti-detection (use proxy rotation for scale)
- **CAPTCHA**: May appear if detection is triggered (configure CAPTCHA service for automatic resolution)
- **Data Accuracy**: Extracted data depends on Google Maps HTML structure which may change
- **JavaScript Required**: Must use browser automation; simple HTTP requests won't work
- **No API Features**: Can't access some API-only features (e.g., detailed hours, photos)
- **Proxy Quality**: Anti-detection effectiveness depends on proxy quality and rotation

## Best Practices

1. **Use Delays**: Add delays between searches to avoid rate limiting
2. **Reasonable Limits**: Don't request hundreds of results at once
3. **Handle Errors**: The agent has built-in error handling
4. **Check Output**: Verify data quality in the output files
5. **Respect Terms**: Be aware of Google's Terms of Service
6. **Use Proxies**: For production use, configure proxy rotation to avoid IP blocking
7. **Enable Stealth Mode**: Keep `STEALTH_ENABLED=true` for better success rates

## Anti-Detection Features

### Overview

This scraper includes comprehensive anti-detection features to bypass bot detection and ensure reliable operation:

| Feature | Description | Configuration |
|---------|-------------|---------------|
| Stealth Browser | Evades automation detection | `STEALTH_ENABLED=true` |
| Human Simulation | Random delays, natural scrolling | `HUMAN_SIMULATION_ENABLED=true` |
| Proxy Rotation | Rotate IP addresses | `PROXY_URL`, `PROXY_LIST` |
| User Agent Rotation | Rotate browser fingerprints | Automatic |
| Timezone Spoofing | Match timezone to search location | Automatic |
| Geolocation Spoofing | Match coordinates to search location | Automatic |
| CAPTCHA Solving | Automatic CAPTCHA resolution | `CAPTCHA_SERVICE`, `CAPTCHA_API_KEY` |
| Cookie Consent | Auto-handle cookie popups | Automatic |

### Stealth Browser Configuration

When `STEALTH_ENABLED=true`, the scraper:
- Uses `playwright-stealth` for fingerprint evasion
- Disables automation detection flags
- Spoofs WebGL vendor/renderer
- Overrides navigator properties
- Uses realistic browser plugins

### Human Behavior Simulation

When `HUMAN_SIMULATION_ENABLED=true`, the scraper:
- Uses random delays with normal distribution (not fixed delays)
- Scrolls in increments with slight pauses (mimics human scrolling)
- Adds delays before clicks
- Waits realistically between page loads

### Proxy Configuration

For reliable operation at scale, configure proxy rotation:

```env
# Single proxy
PROXY_URL=http://proxy.example.com:8080
PROXY_USERNAME=user
PROXY_PASSWORD=pass

# Multiple proxies with rotation
PROXY_ROTATION_ENABLED=true
PROXY_LIST=http://proxy1:8080,http://proxy2:8080,http://proxy3:8080
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

### Fallback Methods

The scraper uses a fallback architecture:

1. **Primary**: Stealth Playwright with configured proxy
2. **Secondary**: Browserless service (if configured)

If the primary method fails due to detection, it automatically tries the next method.

### Health Check with Stealth Status

The `/health` endpoint shows the current anti-detection configuration:

```json
{
  "status": "healthy",
  "message": "Google Maps Scraper API is running",
  "version": "1.0.0",
  "stealth_status": {
    "stealth_enabled": true,
    "human_simulation_enabled": true,
    "proxy_configured": true,
    "browserless_configured": false,
    "captcha_service_configured": true
  }
}
```

## Dependencies

The agent requires:

**Core Dependencies:**
- `langgraph` - Graph-based agent orchestration
- `playwright` - Browser automation for JavaScript rendering
- `fastapi` - API framework
- `uvicorn` - ASGI server
- `slowapi` - Rate limiting

**Anti-Detection Dependencies:**
- `playwright-stealth` - Browser fingerprint evasion
- `aiohttp` - HTTP client for fallback methods

**Optional Dependencies:**
- `2captcha-python` - CAPTCHA solving (install if using CAPTCHA service)

All dependencies are listed in `requirements.txt`.

## Logging

The agent provides detailed logging during execution:

- Navigation status
- Scraping progress
- Number of results found
- Error messages
- Workflow completion status

All logs are printed to the console with timestamps.

## Error Handling

The agent includes comprehensive error handling:

- Browser launch failures
- Page load timeouts
- Element not found errors
- Network errors
- File writing errors

Errors are logged and reported clearly for easy debugging.

## Example Output

```
🚀 Starting Google Maps Scraper Agent Workflow
================================================================================

🔍 NODE: scrape_google_maps_node - Starting Google Maps scraping
================================================================================
Navigating to: https://www.google.com/maps/search/coffee+shops+in+San+Francisco%2C+CA
Extracted 10 results so far...
Extracted 15 results so far...
Extracted 20 results so far...
Enriching results with phone numbers and websites...
Enriching 1/20: Blue Bottle Coffee
Enriching 2/20: Philz Coffee
...
✅ Successfully scraped 20 results

📊 NODE: process_results_node - Processing results
================================================================================
✅ Processed 20 results

🌐 NODE: enrich_websites_node - Scraping websites for additional info
================================================================================
Enriching 1/20: Blue Bottle Coffee - https://www.bluebottlecoffee.com
Found contact page: https://www.bluebottlecoffee.com/contact
Found about page: https://www.bluebottlecoffee.com/about
Successfully scraped website: https://www.bluebottlecoffee.com, found 2 emails
...
✅ Enriched 20 results with website information

✅ Workflow completed successfully!
================================================================================

✅ Results saved to: output/results_coffee-shops_20241130_103000.md
   Full path: /path/to/output/results_coffee-shops_20241130_103000.md
✅ JSON results saved to: output/results_coffee-shops_20241130_103000.json
   Full path: /path/to/output/results_coffee-shops_20241130_103000.json
```

## Use Cases

- **Local Business Research**: Find competitors in your area
- **Market Analysis**: Research business density by category
- **Lead Generation**: Extract contact information (phone, email, website) for outreach
- **Email Collection**: Automatically find business emails from websites and Contact pages
- **Data Analysis**: Analyze ratings, reviews, and pricing trends
- **Location Scouting**: Find businesses in specific areas
- **Contact Database Building**: Build comprehensive contact databases with phone, email, and website

## Troubleshooting

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

## Website Enrichment Details

### How It Works

1. **Homepage Scraping**: First scrapes the homepage for basic metadata (title, description)
2. **Contact Page Detection**: Scans all links on the homepage to find Contact/Contact Us pages
3. **Contact Page Scraping**: Extracts emails and phone numbers from Contact pages (more reliable)
4. **About Page Detection**: Scans all links to find About/About Us pages
5. **About Page Scraping**: Extracts content from About pages for better summaries
6. **Fallback Logic**: Uses homepage if Contact/About pages aren't found

### Email Extraction

The agent extracts emails from:
- Contact pages (primary source)
- Homepage (fallback)
- `mailto:` links
- Text content using regex patterns

Emails are filtered to exclude:
- Example/test domains (example.com, test.com)
- Social media emails (@google, @facebook)
- Auto-generated emails (noreply, no-reply)

### Summary Extraction

The agent prioritizes:
1. About page content (best quality)
2. Homepage content (fallback)

This ensures summaries contain meaningful business information rather than code snippets.

## Future Enhancements

Potential improvements:
- Extract photos and business hours
- Support for filtering results
- Export to CSV format
- Parallel scraping for multiple queries
- Support for multiple languages
- Selenium undetected-chromedriver fallback
- Machine learning-based CAPTCHA detection
- Residential proxy pool integration

## License

This is a standalone agent template. Use and modify as needed for your projects.

**Note**: Web scraping may violate Google's Terms of Service. Use responsibly and consider using the official Google Places API for production applications.

# google-maps-scrapper-agent
