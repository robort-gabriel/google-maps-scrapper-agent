# Google Maps Scraper LangGraph Agent

Standalone LangGraph agent for scraping Google Maps search results without using the official Maps API. This production-ready agent uses Playwright for browser automation to extract business information from Google Maps searches.

## Features

- **Free Solution**: No Google Maps API key required
- **Browser Automation**: Uses Playwright to render JavaScript and extract real data
- **Comprehensive Data Extraction**: Business name, rating, reviews, category, price level, address, phone number, website, email, and Google Maps URL
- **Phone & Email Extraction**: Extracts phone numbers and emails from Google Maps listings
- **Website Enrichment** (Optional): Visit business websites to extract additional information and emails
- **Smart Page Detection**: Automatically finds Contact and About pages for better data extraction
- **Pagination Support**: Automatically scrolls to load more results
- **Structured Output**: Saves results in both Markdown and JSON formats
- **LangGraph Workflow**: Follows the same patterns as your other agents

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

- **Rate Limits**: Google may block excessive requests; use delays between searches
- **CAPTCHA**: May appear if too many requests are made
- **Data Accuracy**: Extracted data depends on Google Maps HTML structure
- **JavaScript Required**: Must use browser automation; simple HTTP requests won't work
- **No API Features**: Can't access some API-only features (e.g., detailed hours, photos)

## Best Practices

1. **Use Delays**: Add delays between searches to avoid rate limiting
2. **Reasonable Limits**: Don't request hundreds of results at once
3. **Handle Errors**: The agent has built-in error handling
4. **Check Output**: Verify data quality in the output files
5. **Respect Terms**: Be aware of Google's Terms of Service

## Dependencies

The agent requires:

- `langgraph` - Graph-based agent orchestration
- `playwright` - Browser automation for JavaScript rendering
- `python-dotenv` - Environment variable loading (optional)

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

### Rate Limiting

If you get blocked:
- Add longer delays between searches
- Reduce `max_results`
- Use different search queries
- Wait before retrying

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
- Proxy support for scaling
- Parallel scraping for multiple queries
- Support for multiple languages

## License

This is a standalone agent template. Use and modify as needed for your projects.

**Note**: Web scraping may violate Google's Terms of Service. Use responsibly and consider using the official Google Places API for production applications.

# google-maps-scrapper-agent
