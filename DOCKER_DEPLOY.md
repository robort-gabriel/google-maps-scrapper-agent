# Docker Deployment Guide for Coolify

This guide explains how to deploy the Google Maps Scraper API using Docker Compose on Coolify.

## Prerequisites

- Coolify installed and configured
- Access to your Coolify dashboard
- GitHub repository with the code

## Deployment Methods

### Method 1: Using Coolify Dashboard (Recommended)

1. **Add New Resource**
   - Go to your Coolify dashboard
   - Click "New Resource" → "Docker Compose"
   - Select your server

2. **Configure Repository**
   - Repository: `https://github.com/your-username/google-maps-scraper`
   - Branch: `main`
   - Docker Compose File: `docker-compose.yml` (default)

3. **Set Environment Variables**
   Go to the "Environment Variables" tab and add:
   ```
   API_KEY=your-secret-api-key-here
   RATE_LIMIT_PER_MINUTE=10
   CORS_ORIGINS=*
   STEALTH_ENABLED=true
   HUMAN_SIMULATION_ENABLED=true
   ```

4. **Optional: Configure Proxy**
   ```
   PROXY_URL=http://proxy-host:port
   PROXY_USERNAME=username
   PROXY_PASSWORD=password
   PROXY_ROTATION_ENABLED=false
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete
   - Check the logs for any errors

### Method 2: Using Docker Compose Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/google-maps-scraper.git
   cd google-maps-scraper
   ```

2. **Create .env file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual values

3. **Build and run**
   ```bash
   docker-compose up -d --build
   ```

4. **Check logs**
   ```bash
   docker-compose logs -f google-maps-scraper
   ```

5. **Stop the service**
   ```bash
   docker-compose down
   ```

## Coolify Configuration

### Port Configuration
- The application runs on port **8000** inside the container
- Coolify will automatically map this to an external port
- You can customize the external port using the `PORT` environment variable

### Resource Limits
The default configuration sets:
- **CPU Limit**: 2 cores
- **Memory Limit**: 2GB
- **CPU Reservation**: 0.5 cores
- **Memory Reservation**: 512MB

Adjust these in `docker-compose.yml` based on your server capacity.

### Volumes
Two volumes are configured:
1. `./output` - Stores scraping results (optional)
2. `playwright-cache` - Caches Playwright browser data

### Health Checks
The container includes a health check that:
- Runs every 30 seconds
- Times out after 10 seconds
- Allows 40 seconds for startup
- Retries 3 times before marking as unhealthy

## Environment Variables

### Required
- `API_KEY` - Your secret API key for authentication

### Optional
- `RATE_LIMIT_PER_MINUTE` - Requests per minute (default: 10)
- `CORS_ORIGINS` - Allowed origins (default: *)
- `STEALTH_ENABLED` - Enable stealth mode (default: true)
- `HUMAN_SIMULATION_ENABLED` - Enable human behavior (default: true)
- `PROXY_URL` - Proxy server URL
- `PROXY_USERNAME` - Proxy username
- `PROXY_PASSWORD` - Proxy password
- `PROXY_LIST` - Comma-separated proxy list
- `PROXY_ROTATION_ENABLED` - Enable proxy rotation (default: false)
- `BROWSERLESS_TOKEN` - Browserless API token
- `BROWSERLESS_BASE_URL` - Browserless endpoint
- `CAPTCHA_SERVICE` - CAPTCHA service (2captcha/anticaptcha)
- `CAPTCHA_API_KEY` - CAPTCHA API key

## Testing the Deployment

1. **Check health endpoint**
   ```bash
   curl http://your-domain.com/health
   ```

2. **Test scraping endpoint**
   ```bash
   curl -X POST http://your-domain.com/scrape \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "restaurants",
       "location": "New York, NY",
       "max_results": 5
     }'
   ```

## Troubleshooting

### Container won't start
- Check logs: `docker-compose logs google-maps-scraper`
- Verify environment variables are set correctly
- Ensure port 8000 is not already in use

### Memory issues
- Increase memory limit in `docker-compose.yml`
- Reduce the number of Gunicorn workers in `Dockerfile`
- Monitor with: `docker stats google-maps-scraper-api`

### Playwright errors
- Ensure Chromium is installed: Check build logs
- Verify system dependencies are present
- Check Playwright cache volume

### Network issues
- Verify network configuration in Coolify
- Check firewall rules
- Test internal network: `docker network inspect google-maps-network`

## Monitoring

### View logs in real-time
```bash
docker-compose logs -f google-maps-scraper
```

### Check container status
```bash
docker-compose ps
```

### Monitor resource usage
```bash
docker stats google-maps-scraper-api
```

## Updating the Application

1. **Pull latest changes**
   ```bash
   git pull origin main
   ```

2. **Rebuild and restart**
   ```bash
   docker-compose up -d --build
   ```

3. **Or use Coolify dashboard**
   - Click "Redeploy" button
   - Coolify will automatically pull and rebuild

## Security Best Practices

1. **Never commit .env file** - It's already in .gitignore
2. **Use strong API keys** - Generate random, long keys
3. **Enable HTTPS** - Use Coolify's built-in SSL/TLS
4. **Rotate API keys regularly** - Update in Coolify dashboard
5. **Monitor rate limits** - Adjust based on usage patterns
6. **Use private proxies** - For production scraping
7. **Keep Docker images updated** - Rebuild regularly

## Support

For issues or questions:
- Check Coolify documentation: https://coolify.io/docs
- Review Docker Compose docs: https://docs.docker.com/compose/
- Check application logs for errors

