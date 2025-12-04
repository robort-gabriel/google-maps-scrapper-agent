# Proxy Configuration Guide

## Quick Fix for Proxy Connection Errors

If you're getting `net::ERR_PROXY_CONNECTION_FAILED` errors, you can disable the proxy to run without it.

## Enable/Disable Proxy

### Option 1: Disable Proxy (Recommended if you don't have a working proxy)

Set the environment variable:
```bash
PROXY_ENABLED=false
```

**In Coolify:**
1. Go to your deployment settings
2. Navigate to "Environment Variables"
3. Add or update: `PROXY_ENABLED=false`
4. Redeploy

**In docker-compose.yml:**
```yaml
environment:
  - PROXY_ENABLED=false
```

**In .env file:**
```env
PROXY_ENABLED=false
```

### Option 2: Enable Proxy (When you have a working proxy)

Set the environment variable:
```bash
PROXY_ENABLED=true
PROXY_URL=http://your-proxy-host:port
PROXY_USERNAME=your-username  # Optional
PROXY_PASSWORD=your-password  # Optional
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROXY_ENABLED` | `false` | Master switch to enable/disable proxy usage |
| `PROXY_URL` | - | Single proxy URL (e.g., `http://proxy.example.com:8080`) |
| `PROXY_USERNAME` | - | Proxy authentication username (optional) |
| `PROXY_PASSWORD` | - | Proxy authentication password (optional) |
| `PROXY_LIST` | - | Comma-separated list of proxies for rotation |
| `PROXY_ROTATION_ENABLED` | `false` | Enable proxy rotation when using PROXY_LIST |

## Examples

### Disable Proxy (Run Direct)
```env
PROXY_ENABLED=false
```

### Enable Single Proxy
```env
PROXY_ENABLED=true
PROXY_URL=http://proxy.example.com:8080
PROXY_USERNAME=user
PROXY_PASSWORD=pass
```

### Enable Proxy Rotation
```env
PROXY_ENABLED=true
PROXY_ROTATION_ENABLED=true
PROXY_LIST=http://proxy1:8080,http://proxy2:8080,http://proxy3:8080
```

## Current Error Fix

**To fix your current error immediately:**

1. **In Coolify Dashboard:**
   - Go to your deployment
   - Click "Environment Variables"
   - Add: `PROXY_ENABLED=false`
   - Save and redeploy

2. **Or update docker-compose.yml:**
   ```yaml
   environment:
     - PROXY_ENABLED=false
   ```
   Then redeploy.

## How It Works

- When `PROXY_ENABLED=false`: The scraper runs **without any proxy**, even if `PROXY_URL` is set
- When `PROXY_ENABLED=true`: The scraper uses the proxy configuration if `PROXY_URL` or `PROXY_LIST` is set
- If `PROXY_ENABLED=true` but no proxy is configured, it runs without proxy

## Troubleshooting

### Error: `net::ERR_PROXY_CONNECTION_FAILED`
**Solution:** Set `PROXY_ENABLED=false` to disable proxy usage

### Error: Proxy authentication failed
**Solution:** 
- Check `PROXY_USERNAME` and `PROXY_PASSWORD` are correct
- Verify proxy URL format: `http://host:port` or `https://host:port`

### Error: All proxies failed
**Solution:**
- Check proxy URLs are valid and accessible
- Verify proxy credentials
- Consider disabling proxy: `PROXY_ENABLED=false`

## Testing

After changing proxy settings, test with:
```bash
curl -X POST http://your-api/health
```

Check the response for `proxy_configured: false` when proxy is disabled.

