# Business User Data Validation Guide

## 📊 Data Source Transparency

This guide helps business users understand the accuracy and reliability of each data point in the Brightspot Locator analysis.

---

## 🎯 Data Quality Legend

| Badge | Type | Meaning | Reliability |
|-------|------|---------|-------------|
| ✅ **Real API** | `real_api` | Direct from official government or commercial API | **High** - Verifiable |
| 📐 **Derived** | `derived` | Calculated from real data using formulas | **Medium-High** |
| 📊 **Estimated** | `estimated` | Pattern-based projections | **Medium** - Use as guidance |
| 🔄 **Proxy** | `proxy` | Inferred from related data | **Low-Medium** - Verify independently |

---

## 📋 Category-by-Category Analysis

### 1. Demographics ✅ HIGH RELIABILITY

**Primary Source:** U.S. Census Bureau ACS 5-Year Estimates (2022)

| Metric | Source Type | Verifiable? | How to Verify |
|--------|-------------|-------------|---------------|
| Children 0-5 Count | ✅ Real API | Yes | [data.census.gov](https://data.census.gov) |
| Population Density | ✅ Real API | Yes | Census B01003/ALAND |
| Birth Rate | 📐 Derived | Partial | Calculated from age 0-5 population |
| Age Distribution % | ✅ Real API | Yes | Census B06001 |
| Median Household Income | ✅ Real API | Yes | Census B19013 |
| Income Distribution % | ✅ Real API | Yes | Census B19001 |
| Avg Childcare Spending | 📊 Estimated | No | 10% of median income (industry standard) |
| Income Growth Rate | 📊 Estimated | No | Pattern-based projection |
| Dual Income Rate | ✅ Real API | Yes | Census B23008 |
| Working Mothers Rate | ✅ Real API | Yes | Census B23007 |
| Avg Commute Time | ✅ Real API | Yes | Census B08303 |
| Population Growth Rate | 📊 Estimated | No | Density-based projection |
| Net Migration Rate | 📊 Estimated | No | Pattern-based projection |
| Family Household Rate | ✅ Real API | Yes | Census B11001 |
| Educational Attainment | ✅ Real API | Yes | Census B15003 |

**Verification Steps:**
1. Go to [data.census.gov](https://data.census.gov)
2. Search for your Census tract
3. Look up the specific variable codes (B01001, B19013, etc.)

---

### 2. Competition ⚠️ MIXED RELIABILITY

**Primary Source:** Google Places API

| Metric | Source Type | Verifiable? | How to Verify |
|--------|-------------|-------------|---------------|
| Existing Centers Count | ✅ Real API | Yes | Google Maps search |
| Total Licensed Capacity | 📊 Estimated | No | Derived from review counts |
| Market Saturation Index | 📐 Derived | Partial | Centers ÷ square miles |
| Avg Competitor Rating | ✅ Real API | Yes | Google Maps ratings |
| Premium Facilities Count | ✅ Real API | Yes | Filter by 4.5+ stars |
| Avg Capacity Utilization | 📊 Estimated | No | Derived from rating patterns |
| Waitlist Prevalence | 📊 Estimated | No | Derived from utilization |
| Market Gap Score | 📊 Estimated | No | Demand vs capacity calculation |
| Demand-Supply Ratio | 📊 Estimated | No | Population-based estimate |
| Nearest Competitor Miles | ✅ Real API | Yes | Google coordinates |
| Competitive Intensity | 📐 Derived | Partial | Composite score |
| New Centers Planned | ✅ Real API | Yes | Google Places name search |

**Verification Steps:**
1. Open Google Maps
2. Search "childcare near [address]"
3. Compare center names and ratings

**For Accurate Capacity Data:**
- Contact state licensing board for licensed capacity
- Request enrollment data from individual centers

---

### 3. Accessibility ✅ HIGH RELIABILITY

**Primary Source:** Google Maps Platform

| Metric | Source Type | Verifiable? | How to Verify |
|--------|-------------|-------------|---------------|
| Avg Commute Minutes | ✅ Real API | Yes | Google Maps directions |
| Peak Congestion Factor | ✅ Real API | Yes | Google Maps with traffic |
| Nearest Employer Miles | ✅ Real API | Yes | Google Maps search |
| Employers Within 5mi | ✅ Real API | Yes | Google Places count |
| Transit Score | 📐 Derived | Partial | Transit station count |
| Walk to Transit Minutes | ✅ Real API | Yes | Google walking directions |
| Morning Rush Score | ✅ Real API | Yes | 8 AM departure time |
| Evening Rush Score | ✅ Real API | Yes | 5 PM departure time |
| Highway Access Score | 📐 Derived | Partial | Road type analysis |
| Parking Availability | 🔄 Proxy | No | Parking search results |

**Verification Steps:**
1. Use Google Maps directions from the address
2. Set departure time to 8 AM or 5 PM
3. Compare commute times displayed

---

### 4. Safety ⚠️ LOW-MEDIUM RELIABILITY

**Primary Source:** Google Places API (Proxy Method)

| Metric | Source Type | Actual Source | Real Data Source |
|--------|-------------|---------------|------------------|
| Crime Rate Index | 🔄 Proxy | Nearby place types | FBI Crime Data API |
| Violent Crime Rate | 📊 Estimated | Formula (×0.20) | FBI UCR |
| Property Crime Rate | 📊 Estimated | Formula (×0.80) | FBI UCR |
| Traffic Accident Rate | 🔄 Proxy | Road type analysis | DOT Fatality Analysis |
| Pedestrian Safety | 📐 Derived | Highway density inverse | Local traffic reports |
| Air Quality Index | 🔄 Proxy | Industrial site proximity | EPA AirNow API |
| Superfund Proximity | 🔄 Proxy | Industrial area search | EPA TRI database |
| Industrial Hazards | 🔄 Proxy | Factory search | EPA Envirofacts |
| Flood Risk Score | 🔄 Proxy | Elevation + water bodies | FEMA NFHL |
| Natural Hazard Composite | 📊 Estimated | Regional baseline | FEMA hazard maps |
| Safety Perception | 🔄 Proxy | Business ratings | Community surveys |

**⚠️ IMPORTANT:** Safety data uses proxy methods. **Always verify with:**
- Local police department crime statistics
- [FBI Crime Data Explorer](https://crime-data-explorer.fr.cloud.gov/)
- [EPA AirNow](https://www.airnow.gov/)
- [FEMA Flood Maps](https://msc.fema.gov/portal/home)

---

### 5. Economic ⚠️ LOW-MEDIUM RELIABILITY

**Primary Source:** Google Places API (Proxy Method)

| Metric | Source Type | How Calculated | Better Source |
|--------|-------------|----------------|---------------|
| Real Estate Cost/sqft | 📊 Estimated | Premium amenity density | Zillow/CoStar |
| Property Tax Rate | 📊 Estimated | State averages | County Assessor |
| Construction Cost | 📊 Estimated | Real estate + 40% | Local contractors |
| Commercial Rent/sqft | 📊 Estimated | Derived from property | LoopNet/CoStar |
| Utility Cost Index | 📊 Estimated | State EIA data | Local utilities |
| Local Wage Level | 📊 Estimated | Price level proxy | BLS statistics |
| Worker Availability | 🔄 Proxy | Schools/centers count | Indeed/LinkedIn |
| Childcare Worker Wage | 📊 Estimated | BLS baseline adjusted | BLS OES data |
| Business Incentives | 🔄 Proxy | Gov buildings search | Economic development office |
| Economic Growth | 🔄 Proxy | New business count | Chamber of Commerce |

**For Accurate Economic Data:**
- Contact local commercial real estate agents
- Request quotes from construction companies
- Check [Bureau of Labor Statistics](https://www.bls.gov/)
- Contact local Economic Development Office

---

### 6. Regulatory ⚠️ LOW RELIABILITY - VERIFICATION REQUIRED

**Primary Source:** Pattern-Based Estimates

| Metric | Source Type | Reliability | MUST Verify With |
|--------|-------------|-------------|------------------|
| Zoning Compliance | 📊 Estimated | Low | Local Planning/Zoning Dept |
| Conditional Use Permit | 📊 Estimated | Low | Zoning Board |
| Rezoning Feasibility | 📊 Estimated | Low | City Planning Commission |
| Building Code Complexity | 📊 Estimated | Low | Building Department |
| ADA Compliance Cost | 📊 Estimated | Low | Accessibility consultant |
| Licensing Difficulty | 📊 Estimated | Medium | State Licensing Board |
| Time to License (days) | 📊 Estimated | Medium | State Licensing Board |
| Permit Processing Time | 📊 Estimated | Low | Building Department |

**⚠️ CRITICAL:** Before making any decision, you MUST:

1. **Contact Local Zoning Office**
   - Confirm childcare is permitted use at address
   - Ask about conditional use permit requirements
   - Get actual processing timelines

2. **Contact State Licensing Board**
   - Get current licensing requirements
   - Request timeline estimates
   - Understand inspection requirements

3. **Contact Building Department**
   - Request building code requirements
   - Get occupancy permit process
   - Understand fire safety requirements

4. **Request Fire Marshal Inspection**
   - Verify fire code compliance
   - Understand sprinkler/alarm requirements

---

## 🔍 How to Use This Data

### For Initial Screening ✅
- Use Demographics data confidently (high reliability)
- Use Competition data for general market understanding
- Use Accessibility data for commute analysis

### For Due Diligence ⚠️
- **Verify Safety data** with FBI Crime Data and EPA
- **Verify Economic data** with real estate agents and BLS
- **ALWAYS Verify Regulatory data** with local authorities

### For Final Decision ❌ DO NOT RELY SOLELY
- Never make location decisions based only on this analysis
- Use as one input among many (site visits, local contacts, professional advice)
- Budget for professional feasibility studies

---

## 📞 Recommended Verification Contacts

| Category | Contact | Purpose |
|----------|---------|---------|
| Demographics | Census Bureau | Confirm population data |
| Competition | State Licensing Board | Get actual licensed capacity |
| Safety | Local Police Dept | Crime statistics |
| Safety | EPA Regional Office | Environmental data |
| Economic | Commercial RE Agent | Actual rents/costs |
| Economic | BLS Regional Office | Wage data |
| Regulatory | City Planning Dept | Zoning verification |
| Regulatory | State Licensing Board | Licensing requirements |

---

## 📝 Sample Verification Checklist

Before making a location decision, complete this checklist:

- [ ] Verified Census demographics at data.census.gov
- [ ] Confirmed childcare centers via Google Maps
- [ ] Checked crime statistics with local police
- [ ] Reviewed EPA air quality at airnow.gov
- [ ] Checked FEMA flood maps
- [ ] Contacted local zoning office
- [ ] Contacted state childcare licensing board
- [ ] Got commercial rent quotes
- [ ] Consulted with local childcare operators
- [ ] Conducted physical site visit

---

## 🔄 Data Update Frequency

| Data Source | Update Frequency |
|-------------|------------------|
| Census ACS 5-Year | Annually (September) |
| Google Places | Real-time |
| Crime Statistics | Varies by agency |
| EPA Data | Varies by dataset |
| FEMA Flood Maps | Periodic updates |

---

*Last Updated: December 2025*
*Version: 1.0*
