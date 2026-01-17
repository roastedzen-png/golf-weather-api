# Railway Deployment Guide for Golf Weather API

This guide explains how to deploy the Golf Weather API to Railway with production and staging environments.

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository connected to Railway
- GoDaddy domain: golfphysics.io

## Step 1: Create Railway Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `golf-weather-api` repository
5. Railway will auto-detect the Dockerfile

## Step 2: Add PostgreSQL

1. In your project, click **"+ New"**
2. Select **"Database" → "PostgreSQL"**
3. Railway automatically sets `DATABASE_URL`

## Step 3: Add Redis

1. Click **"+ New"** again
2. Select **"Database" → "Redis"**
3. Railway automatically sets `REDIS_URL`

## Step 4: Set Environment Variables

Click on your API service, go to **"Variables"** tab, and add:

```
ENVIRONMENT=production

# API Keys (generated - see below)
APIKEY_INRANGE_PROD=0aec1cb11c807a5a0c8d3dfe448d11ca5148df402274b36ae4810066892d9853
APIKEY_INRANGE_TEST=56fb641a158597cae861b5a5e96dc48c86f619b013079659642d45b7eccf632b
APIKEY_ADMIN=68829da24d6aaf60ea796b9ff516f001c3aa73c002908d95e9b55a7ce6897a2c
ADMIN_KEY_HASH=68829da24d6aaf60ea796b9ff516f001c3aa73c002908d95e9b55a7ce6897a2c

# Weather API
WEATHER_API_KEY=your_weatherapi_key

# Sentry (optional)
SENTRY_DSN=your_sentry_dsn

# CORS
CORS_ORIGINS=https://app.inrangegolf.com,https://admin.inrangegolf.com

# Logging
LOG_LEVEL=INFO
```

## Step 5: Configure Custom Domain

1. Go to **"Settings" → "Domains"**
2. Click **"+ Custom Domain"**
3. Enter: `api.golfphysics.io`
4. Railway provides DNS records to add

## Step 6: Configure GoDaddy DNS

Add these records in GoDaddy DNS settings:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | api | `<railway-provided-domain>` | 600 |
| CNAME | staging-api | `<staging-railway-domain>` | 600 |

## Step 7: Create Staging Environment

1. In Railway, click **"Environments"** (top right)
2. Click **"+ New Environment"**
3. Name it **"staging"**
4. Staging gets its own PostgreSQL and Redis instances
5. Set staging-specific variables:
   - `ENVIRONMENT=staging`
   - Use the same API keys or generate new ones

## Step 8: Set Staging Domain

1. Switch to staging environment
2. Go to **"Settings" → "Domains"**
3. Add: `staging-api.golfphysics.io`

---

## API Keys Reference

### For Inrange Production
```
API Key: gw_inrange_prod_0d6edafb4e16aeef677f4146976d89f09208ee32a000770f
```

### For Inrange Testing
```
API Key: gw_inrange_test_7938dccb410a07b933a4ec6906dfb86372a1f49e464650c1
```

### For Admin Dashboard
```
API Key: gw_admin_951ce8c1cdbe5e755dee1b7f2e0b8b9bb59893eece727f31
```

---

## Sentry Setup (Error Tracking)

1. Go to https://sentry.io/
2. Create a new project (Python/FastAPI)
3. Copy the DSN
4. Add to Railway variables: `SENTRY_DSN=<your-dsn>`

---

## Testing the Deployment

### Health Check (no auth required)
```bash
curl https://api.golfphysics.io/api/v1/health
```

### Trajectory Calculation (requires auth)
```bash
curl -X POST https://api.golfphysics.io/api/v1/trajectory \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gw_inrange_prod_0d6edafb4e16aeef677f4146976d89f09208ee32a000770f" \
  -d '{
    "shot": {
      "ball_speed_mph": 150,
      "launch_angle_deg": 12,
      "spin_rate_rpm": 2500
    },
    "conditions": {
      "wind_speed_mph": 10,
      "wind_direction_deg": 0,
      "temperature_f": 70,
      "altitude_ft": 500,
      "humidity_pct": 50
    }
  }'
```

### Admin Usage Stats (requires admin key)
```bash
curl https://api.golfphysics.io/api/v1/admin/usage \
  -H "X-Admin-Key: gw_admin_951ce8c1cdbe5e755dee1b7f2e0b8b9bb59893eece727f31"
```

---

## Monitoring

- **Health endpoint**: `/api/v1/health`
- **Readiness endpoint**: `/api/v1/health/ready`
- **Liveness endpoint**: `/api/v1/health/live`

Railway automatically monitors these endpoints.

---

## Rate Limits

| Client | Requests/Minute |
|--------|-----------------|
| inrange_prod | 20,000 |
| inrange_test | 1,000 |
| admin | 10,000 |
| default | 1,000 |

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
