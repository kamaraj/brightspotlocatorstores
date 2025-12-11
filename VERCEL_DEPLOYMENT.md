# Vercel Deployment Guide for BrightSpot Locator

## Prerequisites

1. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository** - Already set up at https://github.com/kamaraj/brighspotlocator
3. **API Keys** - OpenAI and Google Maps API keys

## Deployment Steps

### Step 1: Connect to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New" → "Project"
3. Import your GitHub repository: `kamaraj/brighspotlocator`
4. Select the `childcare-location-intelligence` folder as the root directory

### Step 2: Configure Environment Variables

In Vercel project settings, add these environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ Yes |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | ✅ Yes |
| `CENSUS_API_KEY` | Census Bureau API key | Optional |

### Step 3: Deploy

1. Click "Deploy"
2. Wait for the build to complete (usually 1-2 minutes)
3. Your app will be available at `https://your-project.vercel.app`

## Project Structure for Vercel

```
childcare-location-intelligence/
├── api/
│   ├── index.py          # Serverless entry point
│   └── requirements.txt  # Dependencies
├── app/
│   ├── static/           # Static files (JS, CSS, images)
│   └── templates/        # HTML templates
└── vercel.json           # Vercel configuration
```

## How It Works

- **Serverless Function**: `api/index.py` is the main entry point
- **SQLite Database**: Stored in `/tmp/childcare.db` (ephemeral in serverless)
- **Static Files**: Served from `app/static/`
- **Templates**: Rendered from `app/templates/`

## Important Notes

### SQLite in Serverless
- SQLite database is stored in `/tmp` which is ephemeral
- Data will be reset on cold starts
- For persistent storage, consider upgrading to a managed database

### API Rate Limits
- OpenAI: Depends on your plan tier
- Google Maps: 100,000 requests/month on free tier
- Census Bureau: 500 requests/day without key, higher with key

### Timeout Limits
- Function timeout: 60 seconds (configured in vercel.json)
- May need to optimize for complex analyses

## Testing Your Deployment

1. Open your Vercel URL
2. Enter an address (e.g., "123 Main Street, Minneapolis, MN")
3. Click "Analyze Location"
4. Check "Show AI Explanations" to test OpenAI integration

## Troubleshooting

### "OpenAI API key not configured"
- Check that `OPENAI_API_KEY` is set in Vercel environment variables
- Redeploy after adding the variable

### "Google Maps geocoding failed"
- Verify `GOOGLE_MAPS_API_KEY` is valid
- Ensure the key has Geocoding API enabled

### Slow Response Times
- First request may be slow (cold start)
- Subsequent requests will be faster

## Local Testing

Before deploying, test locally:

```bash
cd childcare-location-intelligence

# Set environment variables
$env:OPENAI_API_KEY = "your-key"
$env:GOOGLE_MAPS_API_KEY = "your-key"

# Run locally
python -m uvicorn api.index:app --reload --port 8000
```

## Need Help?

- Check Vercel logs in the dashboard
- Review `api/index.py` for error handling
- Contact support with specific error messages
