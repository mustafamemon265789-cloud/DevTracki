# DevTrack Railway Deployment Guide

This guide walks you through deploying DevTrack API with PostgreSQL on Railway using the web dashboard.

## Prerequisites

- Railway account (sign up at https://railway.app)
- GitHub account with this repository pushed

## Step 1: Push Code to GitHub

Make sure all changes are committed and pushed to your GitHub repository:

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

## Step 2: Create Railway Project

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your DevTrack repository

## Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Wait for the database to provision

## Step 4: Configure Environment Variables

1. Click on your DevTrack service
2. Go to "Variables" tab
3. Add the following variables:

| Variable | Value | Source |
|----------|-------|--------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Click "Add Reference" → Select your PostgreSQL service |
| `SECRET_KEY` | Generate a random string | Use: `openssl rand -hex 32` or any random string |
| `ALGORITHM` | HS256 | Hardcoded |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Hardcoded |

4. Click "Deploy" to apply changes

## Step 5: Deploy

1. Railway will automatically deploy when you push to main
2. Or click "Deploy" in the dashboard to redeploy
3. Wait for deployment to complete (green checkmark)

## Step 6: Verify Deployment

1. Click on your service → "Settings" → "Public Networking"
2. Generate a domain (Railway will provide a URL)
3. Test the API:
   ```
   curl https://your-app-name.up.railway.app/
   ```

## Troubleshooting

### Issue: Database connection fails
- Check `DATABASE_URL` is correctly set
- Ensure PostgreSQL service is healthy (green)

### Issue: Build fails
- Check logs in Railway dashboard
- Ensure `pyproject.toml` is valid

### Issue: App crashes
- Check all environment variables are set
- Check application logs in Railway

## Project Files for Railway

The following files configure the deployment:

- `railway.json` - Railway deployment configuration
- `nixpacks.toml` - Build configuration
- `pyproject.toml` - Python dependencies
