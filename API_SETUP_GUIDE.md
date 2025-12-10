# 🚀 Production Setup Guide - Real APIs

## ⚠️ Important: You Need API Keys!

The production server uses **REAL APIs** and requires valid API keys. Follow these steps:

---

## 📋 Step 1: Get Google Maps API Key (Required)

### **A. Create Google Cloud Project**
1. Go to: https://console.cloud.google.com/
2. Click "Create Project" or select existing project
3. Name it (e.g., "Childcare-Location-Intelligence")

### **B. Enable Required APIs**
In the Google Cloud Console, enable these APIs:
1. **Geocoding API** - Convert addresses to coordinates
2. **Places API** - Find childcare centers
3. **Distance Matrix API** - Calculate commute times
4. **Directions API** - Traffic and routing

### **C. Create API Key**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "API Key"
3. Copy the API key
4. (Recommended) Click "Restrict Key" → Select the 4 APIs above

### **D. Enable Billing** (Required for Google Maps)
- Google Maps APIs require a billing account
- You get **$200 free credits per month**
- Typical cost for testing: $5-20/month

---

## 📋 Step 2: Get Census Bureau API Key (Free!)

### **A. Request API Key**
1. Go to: https://api.census.gov/data/key_signup.html
2. Fill out the form:
   - Organization: Your name/company
   - Email: Your email
3. Click "Submit"

### **B. Check Email**
- You'll receive the API key via email instantly
- It's **completely FREE** - no credit card required

---

## 📋 Step 3: Add Keys to .env File

Open `.env` file and replace these lines:

```env
# Replace this:
GOOGLE_MAPS_API_KEY="ADD_YOUR_GOOGLE_MAPS_API_KEY_HERE"

# With your actual key:
GOOGLE_MAPS_API_KEY="AIzaSyD_your_actual_key_here_xxxxxxxxxxxxx"

# Replace this:
CENSUS_API_KEY="ADD_YOUR_CENSUS_API_KEY_HERE"

# With your actual key:
CENSUS_API_KEY="your_census_key_here_xxxxxxxxxxxxx"
```

---

## 📋 Step 4: Run Production Server

```powershell
# Stop the demo server first (if running)
# Then start production server:
cd c:\kamaraj\Prototype\ONDCBuyerApp\childcare-location-intelligence
python production_server.py
```

---

## ✅ Verify Configuration

### **Check API Configuration:**
Visit: http://127.0.0.1:8000/api/check-config

You should see:
```json
{
  "google_maps": {
    "configured": true,
    "key_prefix": "AIzaSyD..."
  },
  "census": {
    "configured": true,
    "key_prefix": "your_cen..."
  }
}
```

### **Test Analysis:**
1. Go to: http://127.0.0.1:8000/
2. Enter address: "1600 Amphitheatre Parkway, Mountain View, CA"
3. Click "Analyze Location"
4. Wait 10-15 seconds (real API calls take time)
5. See REAL data from Google Maps and Census Bureau!

---

## 💰 API Costs Estimate

### **Google Maps** (With $200/month free credit)
- Geocoding: $5 per 1000 requests
- Places: $17 per 1000 requests
- Distance Matrix: $5 per 1000 requests
- **Average cost per analysis:** ~$0.03
- **Free tier allows:** ~6,600 analyses/month

### **Census Bureau**
- **Cost:** FREE ✅
- **No limits** on requests

### **Total Monthly Cost**
- Light usage (100 analyses): ~$3
- Medium usage (500 analyses): ~$15
- Heavy usage (2000 analyses): ~$60

---

## 🔍 What Data You Get (Real vs Mock)

| Category | Mock Data | Real API Data |
|----------|-----------|---------------|
| Demographics | Fixed sample | Live Census data for exact location |
| Competition | 8 generic centers | Actual childcare centers from Google |
| Accessibility | Estimated values | Real commute times with traffic |
| Safety | Generic scores | Proxy indicators from area data |
| Economic | Sample costs | Estimated from real property data |
| Regulatory | Generic rules | Location-specific requirements |

---

## 🆘 Troubleshooting

### **Error: "REQUEST_DENIED"**
- API key is invalid
- APIs not enabled in Google Cloud Console
- **Solution:** Re-check Steps 1B and 1C above

### **Error: "OVER_QUERY_LIMIT"**
- Exceeded free quota
- Billing not enabled
- **Solution:** Enable billing in Google Cloud

### **Error: "INVALID_REQUEST"**
- Address cannot be geocoded
- Try a more specific address
- **Solution:** Add city, state, zip code

### **Slow Response (15-20 seconds)**
- This is normal! Real APIs take time
- Each category makes 2-5 API calls
- **Solution:** This is expected behavior

---

## 🔄 Switch Back to Demo Mode

If you want instant responses with mock data:

```powershell
# Stop production server (Ctrl+C)
# Start demo server:
python fast_server.py
```

---

## 📊 Current Status

- ✅ Production server ready
- ⏸️ Waiting for API keys
- 📝 Edit `.env` file with your keys
- 🚀 Then run `python production_server.py`

---

## 💡 Quick Start (If You Have Keys)

```powershell
# 1. Stop current server
Get-Process python | Stop-Process

# 2. Edit .env file - add your API keys

# 3. Run production server
cd c:\kamaraj\Prototype\ONDCBuyerApp\childcare-location-intelligence
python production_server.py

# 4. Open browser
# http://127.0.0.1:8000/
```

---

**Questions?** Check:
- Google Cloud Console: https://console.cloud.google.com/
- Census API Docs: https://www.census.gov/data/developers/guidance.html
