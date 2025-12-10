# Manual Testing Guide - Brightspot Locator AI

## Quick Test (5 minutes)

### Test the Dashboard Manually

1. **Open the Dashboard**
   ```
   URL: http://127.0.0.1:9025/
   ```

2. **Test Location 1: Silicon Valley**
   - Address: `1600 Amphitheatre Parkway, Mountain View, CA 94043`
   - Radius: `2.0 miles`
   - Click "Analyze Location"
   - Wait ~15 seconds
   - Expected Score: 70-85/100
   - Check all 6 categories display

3. **Test Location 2: Manhattan**
   - Address: `350 5th Avenue, New York, NY 10118`
   - Radius: `2.0 miles`
   - Click "Analyze Location"
   - Wait ~15 seconds
   - Expected Score: 65-80/100
   - Toggle "Show AI Explanations" in Demographics

4. **Test Location 3: Austin**
   - Address: `500 W 2nd St, Austin, TX 78701`
   - Radius: `2.0 miles`
   - Click "Analyze Location"
   - Wait ~15 seconds
   - Expected Score: 70-85/100
   - Test export to JSON

5. **View Data Sources**
   - Click "Data Sources" in navbar
   - Verify all 6 insight layers display
   - Check status indicators

---

## What to Test

### ✅ Core Functionality
- [ ] Address input accepts valid US addresses
- [ ] Radius selector works (0.5-10 miles)
- [ ] "Analyze Location" button triggers analysis
- [ ] Loading spinner appears during processing
- [ ] Results display after 10-20 seconds

### ✅ Results Display
- [ ] Overall score shows (0-100)
- [ ] Recommendation text appears
- [ ] 6 category cards show scores
- [ ] Performance metrics display (4 boxes)
- [ ] Category tabs are clickable

### ✅ Detailed Data
- [ ] Each category shows data points
- [ ] Values display correctly (numbers, percentages, text)
- [ ] Collection time shown in milliseconds
- [ ] Circular progress indicators work

### ✅ Explainable AI (XAI)
- [ ] "Show/Hide AI Explanations" button works
- [ ] 5W1H details expand/collapse
- [ ] What/How/Why/Where/When sections display
- [ ] Confidence badges show (HIGH/MEDIUM/LOW)
- [ ] Interpretation badges show (EXCELLENT/GOOD/FAIR/POOR)

### ✅ UI/UX
- [ ] Sidebar toggle button works
- [ ] Sidebar slides in/out smoothly
- [ ] Close button (X) works
- [ ] Responsive on different screen sizes
- [ ] No JavaScript errors in console

### ✅ Export
- [ ] "Export JSON" downloads file
- [ ] "Export CSV" downloads file
- [ ] "Print Report" opens print dialog
- [ ] Files contain correct data

### ✅ Navigation
- [ ] "Data Sources" link works
- [ ] API sources page displays
- [ ] Back to Dashboard link works
- [ ] All 6 layer cards display

---

## Expected Results

### Demographics (15 points)
- Children 0-5 count: 2000-10000 (varies by area)
- Children 5-9 count: 2000-10000
- Median household income: $50,000-$150,000
- Unemployment rate: 2-10%
- Population density: 1000-15000 per sq mi
- Score: 60-90/100

### Competition (12 points)
- Existing centers: 5-30 (within 2 miles)
- Market saturation: 20-80%
- Average rating: 3.5-4.5 stars
- Competitive intensity: Low/Medium/High
- Score: 50-85/100

### Accessibility (10 points)
- Transit score: 30-90 (varies by city)
- Transit stations: 0-15
- Average commute: 15-45 minutes
- Parking score: 40-90
- Score: 40-85/100

### Safety (11 points)
- Police stations: 1-5 nearby
- Fire stations: 1-5 nearby
- Hospitals: 1-10 nearby
- Safety score: 50-85
- Score: 50-85/100

### Economic (10 points)
- Real estate cost: $10-$50/sqft
- Startup cost: $50,000-$200,000
- Revenue potential: $200,000-$1,000,000/year
- Break-even: 12-36 months
- Score: 40-80/100

### Regulatory (8 points)
- Licensing complexity: 3-7/10
- Staff ratio requirements: 1:4 to 1:8
- Compliance: State-specific
- Score: 60-85/100

---

## Performance Benchmarks

### Response Times (Expected)
- Total analysis: 10-20 seconds
- Demographics: 3-5 seconds
- Competition: 2-4 seconds
- Accessibility: 3-5 seconds
- Safety: 2-3 seconds
- Economic: 1-2 seconds
- Regulatory: <1 second

### UI Performance
- Page load: <2 seconds
- Sidebar toggle: <0.5 seconds
- Tab switching: Instant
- XAI toggle: <0.3 seconds
- Export: <1 second

---

## Common Issues & Solutions

### Issue: "Address not found"
**Solution:** Use complete address with city and state
```
✅ Good: "1600 Amphitheatre Parkway, Mountain View, CA 94043"
❌ Bad: "1600 Amphitheatre Parkway"
```

### Issue: "Request timeout"
**Solution:** Normal for production. Real APIs take 10-20 seconds.
- Wait patiently
- Check server logs
- Verify API keys in .env

### Issue: "No results displayed"
**Solution:** 
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify server is running: http://127.0.0.1:9025/health
4. Check network tab for API responses

### Issue: "Sidebar not sliding"
**Solution:**
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Check dashboard.css loaded correctly

### Issue: "XAI not showing"
**Solution:**
1. Click category tab first
2. Then click "Show AI Explanations"
3. Check browser console for errors

---

## Browser Testing

### Recommended Browsers
- ✅ Chrome/Edge (Chromium) - Best performance
- ✅ Firefox - Full support
- ✅ Safari - Full support
- ⚠️ Internet Explorer - Not supported

### Screen Sizes to Test
- Desktop: 1920×1080 (full features)
- Laptop: 1366×768 (full features)
- Tablet: 768×1024 (responsive sidebar)
- Mobile: 375×667 (mobile layout)

---

## API Health Checks

### Before Testing
```powershell
# Check server health
Invoke-WebRequest -Uri "http://127.0.0.1:9025/health"

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0-production",
  "api_mode": "real",
  "google_maps_configured": true,
  "census_configured": true
}
```

### During Testing
- Monitor server console for logs
- Check for API errors
- Verify response times

### After Testing
- Review generated files (JSON, CSV)
- Check data accuracy
- Verify all 66 data points collected

---

## Screenshot Checklist

Capture screenshots of:
1. [ ] Dashboard home page
2. [ ] Address input with loading spinner
3. [ ] Results with overall score
4. [ ] All 6 category cards
5. [ ] Demographics tab with data points
6. [ ] XAI explanations expanded
7. [ ] Timing chart
8. [ ] Data Sources page
9. [ ] Mobile responsive view
10. [ ] Sidebar collapsed/expanded

---

## Test Report Template

```
### Test Date: [DATE]
### Tester: [NAME]

**Environment:**
- Browser: [Chrome/Firefox/Edge/Safari]
- Screen: [Resolution]
- Server: http://127.0.0.1:9025/

**Test Results:**

Location 1: [Address]
- Overall Score: [X/100]
- Response Time: [X seconds]
- All categories displayed: ✅/❌
- XAI working: ✅/❌
- Export successful: ✅/❌

Location 2: [Address]
- Overall Score: [X/100]
- Response Time: [X seconds]
- All categories displayed: ✅/❌
- XAI working: ✅/❌
- Export successful: ✅/❌

Location 3: [Address]
- Overall Score: [X/100]
- Response Time: [X seconds]
- All categories displayed: ✅/❌
- XAI working: ✅/❌
- Export successful: ✅/❌

**Data Sources Page:**
- All 6 layers visible: ✅/❌
- Status indicators correct: ✅/❌

**Issues Found:**
1. [Issue description]
2. [Issue description]

**Overall Rating:** ⭐⭐⭐⭐⭐ (1-5 stars)

**Notes:**
[Additional observations]
```

---

## Quick Copy-Paste Addresses

```
# West Coast
1600 Amphitheatre Parkway, Mountain View, CA 94043
1 Apple Park Way, Cupertino, CA 95014
1 Microsoft Way, Redmond, WA 98052

# East Coast
350 5th Avenue, New York, NY 10118
1 Beacon Street, Boston, MA 02108

# Central US
500 W 2nd St, Austin, TX 78701
875 N Michigan Ave, Chicago, IL 60611

# South
1200 Ocean Drive, Miami Beach, FL 33139
200 E Colfax Ave, Denver, CO 80203

# Southwest
620 N 6th St, Phoenix, AZ 85004
1120 SW 5th Ave, Portland, OR 97204
```

---

## Success Criteria

✅ **Core Functionality**
- 3 different addresses analyzed successfully
- All 66 data points collected for each location
- Overall scores between 40-90/100
- Response times 10-20 seconds

✅ **UI/UX**
- Sidebar toggle works smoothly
- All tabs clickable and responsive
- XAI explanations display correctly
- No JavaScript console errors

✅ **Data Quality**
- Demographics data matches location characteristics
- Competition counts reasonable (5-30 centers)
- Accessibility scores vary by urban/suburban
- All export formats work

✅ **Documentation**
- Data Sources page displays all 6 layers
- Status indicators accurate
- API endpoints visible
- Back navigation works

---

**Estimated Testing Time:** 15-20 minutes  
**Difficulty:** Easy  
**Required:** Running server at http://127.0.0.1:9025/  

---

*Ready to test? Open http://127.0.0.1:9025/ and start analyzing!* 🚀
