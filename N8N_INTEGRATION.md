# n8n Integration Guide for Google Maps Scraper API

This guide shows you how to use the Google Maps Scraper API in n8n workflows using the HTTP Request node.

## Prerequisites

1. Your API is deployed and accessible (e.g., `https://your-domain.com` or `http://localhost:8000`)
2. You have your API key configured
3. n8n is installed and running

## API Endpoint Details

### Endpoint
- **URL**: `https://your-domain.com/api/v1/scrape` (or your deployed URL)
- **Method**: `POST`
- **Authentication**: API Key via header

### Request Structure

**Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body (JSON):**
```json
{
  "query": "coffee shops",
  "location": "New York, NY",
  "max_results": 20,
  "enrich_with_website": false
}
```

**Field Descriptions:**
- `query` (required): Search query string (1-200 characters)
- `location` (optional): Location string (e.g., "New York, NY")
- `max_results` (optional): Number of results (1-100, default: 20)
- `enrich_with_website` (optional): Boolean to visit business websites (default: false)

### Response Structure

**Success Response (200 OK):**
```json
{
  "status": "success",
  "query": "coffee shops",
  "location": "New York, NY",
  "total_found": 20,
  "processing_status": "completed",
  "results": [
    {
      "rank": 1,
      "name": "Starbucks",
      "rating": "4.5",
      "reviews": "1,234 reviews",
      "category": "Coffee shop",
      "price_level": "$$",
      "address": "123 Main St, New York, NY 10001",
      "phone": "+1 212-555-1234",
      "website": "https://starbucks.com",
      "email": "contact@starbucks.com",
      "url": "https://maps.google.com/...",
      "website_title": null,
      "website_description": null,
      "website_summary": null,
      "website_emails": null
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid API key
- `400 Bad Request`: Invalid request parameters
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: CAPTCHA detected, bot detection, or all methods failed
- `500 Internal Server Error`: Server error

## n8n Configuration Steps

### Step 1: Add HTTP Request Node

1. In your n8n workflow, click the **"+"** button
2. Search for **"HTTP Request"** and add it
3. Connect it to your trigger or previous node

### Step 2: Configure HTTP Request Node

#### Basic Settings

1. **Method**: Select `POST`
2. **URL**: Enter your API endpoint
   ```
   https://your-domain.com/api/v1/scrape
   ```
   Or use an expression:
   ```
   {{ $env.API_BASE_URL }}/api/v1/scrape
   ```

#### Authentication

1. Click **"Add Header"**
2. **Name**: `X-API-Key`
3. **Value**: Your API key (or use expression `{{ $env.API_KEY }}`)

#### Headers

1. Click **"Add Header"**
2. **Name**: `Content-Type`
3. **Value**: `application/json`

#### Request Body

1. **Body Content Type**: Select `JSON`
2. **JSON Body**: Enter your request payload

**Option A: Static JSON**
```json
{
  "query": "coffee shops",
  "location": "New York, NY",
  "max_results": 20,
  "enrich_with_website": false
}
```

**Option B: Dynamic JSON (using expressions)**
```json
{
  "query": "{{ $json.query }}",
  "location": "{{ $json.location }}",
  "max_results": {{ $json.max_results || 20 }},
  "enrich_with_website": {{ $json.enrich_with_website || false }}
}
```

**Option C: Using n8n Expression Editor**
```javascript
{
  "query": $input.item.json.searchQuery,
  "location": $input.item.json.city || "New York, NY",
  "max_results": $input.item.json.limit || 20,
  "enrich_with_website": $input.item.json.enrich || false
}
```

### Step 3: Handle Response

#### Success Response

The HTTP Request node will output the response automatically. You can access:

- **Status Code**: `{{ $json.statusCode }}`
- **Total Found**: `{{ $json.body.total_found }}`
- **Results Array**: `{{ $json.body.results }}`
- **Individual Result**: `{{ $json.body.results[0].name }}`

#### Error Handling

Add an **"IF" node** after HTTP Request to check for errors:

**Condition:**
```
{{ $json.statusCode }} !== 200
```

**True Branch (Error):**
- Add a **"Set" node** to format error message
- Or add **"Stop and Error" node** to stop workflow

**False Branch (Success):**
- Continue processing results

## Example n8n Workflow

### Workflow 1: Simple Search

```
[Manual Trigger] → [HTTP Request] → [Set] → [Output]
```

**HTTP Request Configuration:**
- Method: `POST`
- URL: `https://your-api.com/api/v1/scrape`
- Headers:
  - `X-API-Key`: `your-api-key`
  - `Content-Type`: `application/json`
- Body:
```json
{
  "query": "restaurants",
  "location": "San Francisco, CA",
  "max_results": 10
}
```

### Workflow 2: Dynamic Search with Input

```
[Webhook] → [HTTP Request] → [Split In Batches] → [Process Results]
```

**Webhook Input:**
```json
{
  "query": "coffee shops",
  "location": "Boston, MA",
  "max_results": 50
}
```

**HTTP Request Body (Expression):**
```json
{
  "query": "{{ $json.query }}",
  "location": "{{ $json.location }}",
  "max_results": {{ $json.max_results }},
  "enrich_with_website": true
}
```

### Workflow 3: Batch Processing with Error Handling

```
[Manual Trigger] → [Code] → [HTTP Request] → [IF] → [Success Path] / [Error Path]
```

**Code Node (Generate Queries):**
```javascript
const queries = [
  { query: "restaurants", location: "New York, NY" },
  { query: "hotels", location: "Los Angeles, CA" },
  { query: "gyms", location: "Chicago, IL" }
];

return queries.map(q => ({ json: q }));
```

**HTTP Request (Same as above)**

**IF Node:**
- Condition: `{{ $json.statusCode }} === 200`

**Success Path:**
- Extract results
- Save to database
- Send notification

**Error Path:**
- Log error
- Send alert
- Retry logic

## Advanced n8n Expressions

### Extract Business Names
```javascript
{{ $json.body.results.map(r => r.name).join(', ') }}
```

### Filter by Rating
```javascript
{{ $json.body.results.filter(r => parseFloat(r.rating) >= 4.0) }}
```

### Extract All Emails
```javascript
{{ $json.body.results
  .filter(r => r.email && r.email !== 'N/A')
  .map(r => r.email)
}}
```

### Format Results for Database
```javascript
{{ $json.body.results.map(r => ({
  name: r.name,
  rating: parseFloat(r.rating),
  address: r.address,
  phone: r.phone,
  website: r.website,
  email: r.email
})) }}
```

## Rate Limiting

The API has rate limiting (default: 10 requests/minute per IP).

**Handle Rate Limits in n8n:**

1. Add **"Wait" node** between requests
2. Use **"Schedule Trigger"** to space out requests
3. Implement retry logic with exponential backoff

**Example Wait Configuration:**
- Wait for: `7 seconds` (to stay under 10/min limit)

## Testing in n8n

### Test with Manual Trigger

1. Add **"Manual Trigger"** node
2. Add **"Set" node** with test data:
   ```json
   {
     "query": "test query",
     "location": "test location"
   }
   ```
3. Add **"HTTP Request"** node (configured as above)
4. Add **"Output"** node to see results
5. Click **"Execute Workflow"**

### Test with Webhook

1. Add **"Webhook"** node
2. Set method to `POST`
3. Add **"HTTP Request"** node
4. Use webhook URL to send test requests

## Environment Variables in n8n

For production, use n8n environment variables:

1. Go to **Settings** → **Environment Variables**
2. Add:
   - `API_BASE_URL`: `https://your-api.com`
   - `API_KEY`: `your-secret-api-key`

3. Use in HTTP Request:
   - URL: `{{ $env.API_BASE_URL }}/api/v1/scrape`
   - Header Value: `{{ $env.API_KEY }}`

## Complete n8n Node Configuration Example

### HTTP Request Node JSON Export

```json
{
  "parameters": {
    "method": "POST",
    "url": "https://your-api.com/api/v1/scrape",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "X-API-Key",
          "value": "={{ $env.API_KEY }}"
        },
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ]
    },
    "sendBody": true,
    "bodyParameters": {
      "parameters": []
    },
    "specifyBody": "json",
    "jsonBody": "={\n  \"query\": \"{{ $json.query }}\",\n  \"location\": \"{{ $json.location }}\",\n  \"max_results\": {{ $json.max_results || 20 }},\n  \"enrich_with_website\": {{ $json.enrich_with_website || false }}\n}",
    "options": {}
  }
}
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check API key is correct
   - Verify header name is `X-API-Key` (case-sensitive)

2. **400 Bad Request**
   - Validate JSON structure
   - Check required fields (query)
   - Verify field types (max_results is number, not string)

3. **429 Too Many Requests**
   - Add delays between requests
   - Reduce request frequency

4. **503 Service Unavailable**
   - CAPTCHA detected: Configure CAPTCHA service
   - Bot detection: Use proxy rotation
   - Wait and retry

5. **Connection Errors**
   - Verify API URL is correct
   - Check network connectivity
   - Verify API is running

## Best Practices

1. **Use Environment Variables** for API keys and URLs
2. **Add Error Handling** with IF nodes
3. **Implement Retry Logic** for transient failures
4. **Respect Rate Limits** with wait nodes
5. **Log Responses** for debugging
6. **Validate Input** before sending requests
7. **Use Expressions** for dynamic data
8. **Test Workflows** before production use

## Example: Complete Workflow

```
[Webhook Trigger]
    ↓
[Set Node: Validate Input]
    ↓
[IF Node: Check Required Fields]
    ↓ (True)
[HTTP Request: Scrape API]
    ↓
[IF Node: Check Status Code]
    ↓ (200)
[Code Node: Process Results]
    ↓
[Set Node: Format Output]
    ↓
[HTTP Request: Save to Database]
    ↓
[Output Node]
```

This workflow:
1. Receives webhook with query data
2. Validates input
3. Calls scraping API
4. Checks for success
5. Processes and formats results
6. Saves to database
7. Returns output

## Support

For API issues, check:
- API logs in Coolify
- Health endpoint: `GET /health`
- API documentation: `GET /docs` (Swagger UI)

