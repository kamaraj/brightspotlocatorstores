"""
Simple API Test - 3 Locations with PDF Report
Tests production API and generates comprehensive report
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Any
import time

# Test 3 diverse locations
TEST_LOCATIONS = [
    {
        "name": "Silicon Valley Tech Hub",
        "address": "1600 Amphitheatre Parkway, Mountain View, CA 94043",
        "city": "Mountain View",
        "state": "California"
    },
    {
        "name": "Manhattan Urban Center",
        "address": "350 5th Avenue, New York, NY 10118",
        "city": "New York",
        "state": "New York"
    },
    {
        "name": "Austin Tech District",
        "address": "500 W 2nd St, Austin, TX 78701",
        "city": "Austin",
        "state": "Texas"
    }
]

API_BASE_URL = "http://127.0.0.1:9025"

# Data Sources Information
DATA_SOURCES = {
    "demographics": {
        "api": "U.S. Census Bureau ACS 5-Year",
        "endpoint": "https://api.census.gov/data/2021/acs/acs5",
        "data_points": ["Children 0-5 count", "Children 5-9 count", "Median household income", 
                       "Unemployment rate", "Population density", "Birth rate estimate",
                       "Employment to population ratio", "Family households", "Education attainment",
                       "Poverty rate", "Housing occupancy", "Labor force participation",
                       "Commute patterns", "Language spoken", "Internet access"],
        "count": 15,
        "status": "✅ Active",
        "confidence": "HIGH"
    },
    "competition": {
        "api": "Google Places API",
        "endpoint": "https://maps.googleapis.com/maps/api/place",
        "data_points": ["Existing centers count", "Market saturation index", "Average competitor rating",
                       "Average competitor reviews", "Top competitor name", "Top competitor rating",
                       "Market gap score", "Estimated market demand", "Estimated current supply",
                       "Centers within 1 mile", "Centers within 2 miles", "Competitive intensity"],
        "count": 12,
        "status": "✅ Active",
        "confidence": "HIGH"
    },
    "accessibility": {
        "api": "Google Distance Matrix + Places",
        "endpoint": "https://maps.googleapis.com/maps/api/distancematrix",
        "data_points": ["Transit score", "Transit stations count", "Closest transit distance",
                       "Average commute minutes", "Parking availability score", "Major highways nearby",
                       "Highway distance miles", "Public transit modes", "Peak traffic multiplier",
                       "Accessibility score"],
        "count": 10,
        "status": "✅ Active",
        "confidence": "HIGH"
    },
    "safety": {
        "api": "Proxy Indicators (awaiting FBI CDE + EPA)",
        "endpoint": "Google Places (temporary)",
        "data_points": ["Crime rate index (estimated)", "Police stations nearby", "Fire stations nearby",
                       "Hospitals nearby", "Emergency response time", "Air quality index (estimated)",
                       "Environmental hazards", "Flood risk indicator", "Safety facilities score",
                       "Neighborhood safety score", "Healthcare access"],
        "count": 11,
        "status": "⚠️ Estimated",
        "confidence": "MEDIUM"
    },
    "economic": {
        "api": "Market Estimates (awaiting HUD User)",
        "endpoint": "Calculated from demographics + competition",
        "data_points": ["Real estate cost per sqft (estimated)", "Startup cost estimate", 
                       "Operating cost estimate", "Revenue potential", "Break-even timeline",
                       "Childcare worker availability score", "Labor cost estimate",
                       "Market growth potential", "Economic viability score", "Profit margin estimate"],
        "count": 10,
        "status": "⚠️ Estimated",
        "confidence": "MEDIUM"
    },
    "regulatory": {
        "api": "State Licensing Databases",
        "endpoint": "State-specific regulations",
        "data_points": ["State requirements", "Licensing complexity score", "Staff ratio requirements",
                       "Background check requirements", "Health and safety standards",
                       "Facility requirements", "Zoning compliance", "Operating hours restrictions"],
        "count": 8,
        "status": "✅ Active",
        "confidence": "HIGH"
    }
}


def analyze_location(location: Dict[str, str]) -> Dict[str, Any]:
    """Analyze a single location"""
    print(f"\nAnalyzing: {location['name']}")
    print(f"Address: {location['address']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/analyze",
            json={
                "address": location["address"],
                "radius_miles": 2.0
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            result["location_metadata"] = location
            print(f"✅ Score: {result.get('overall_score', 0):.1f}/100")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            return {"error": True, "status_code": response.status_code, "location_metadata": location}
            
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - Request exceeded 120 seconds")
        return {"error": True, "timeout": True, "location_metadata": location}
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"error": True, "exception": str(e), "location_metadata": location}


def generate_pdf_report(results: List[Dict[str, Any]]):
    """Generate comprehensive PDF report"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_filename = f"brightspot_analysis_{timestamp}.pdf"
    
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Title Page
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Brightspot Locator AI", title_style))
    story.append(Paragraph("Location Intelligence Analysis Report", styles['Heading2']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph(f"Locations Analyzed: {len([r for r in results if not r.get('error')])}", styles['Normal']))
    story.append(Spacer(1, 1*inch))
    
    # Data Sources Section
    story.append(Paragraph("Data Collection Sources", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("This analysis integrates data from 6 authoritative sources:", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    for category, source in DATA_SOURCES.items():
        story.append(Paragraph(f"<b>{category.title()} ({source['count']} data points)</b>", styles['Heading3']))
        story.append(Paragraph(f"API Source: {source['api']}", styles['Normal']))
        story.append(Paragraph(f"Status: {source['status']} | Confidence: {source['confidence']}", styles['Normal']))
        story.append(Paragraph(f"Endpoint: <font size=8>{source['endpoint']}</font>", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    story.append(PageBreak())
    
    # Summary Table
    story.append(Paragraph("Data Source Summary", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))
    
    summary_data = [['Category', 'API Source', 'Data Points', 'Status', 'Confidence']]
    for category, source in DATA_SOURCES.items():
        summary_data.append([
            category.title(),
            source['api'].split()[0] + '...',
            str(source['count']),
            source['status'],
            source['confidence']
        ])
    
    summary_table = Table(summary_data, colWidths=[1.2*inch, 2*inch, 0.8*inch, 1*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 0.5*inch))
    
    # Total metrics
    total_points = sum(s['count'] for s in DATA_SOURCES.values())
    active_sources = sum(1 for s in DATA_SOURCES.values() if '✅' in s['status'])
    
    story.append(Paragraph(f"<b>Total Data Points Collected:</b> {total_points}", styles['Normal']))
    story.append(Paragraph(f"<b>Active API Sources:</b> {active_sources}/6", styles['Normal']))
    story.append(Paragraph(f"<b>Overall System Confidence:</b> HIGH for active sources", styles['Normal']))
    
    story.append(PageBreak())
    
    # Location Results
    successful = [r for r in results if not r.get('error')]
    
    if successful:
        story.append(Paragraph("Location Analysis Results", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Results table
        results_data = [['Rank', 'Location', 'City, State', 'Overall Score', 'Data Points']]
        
        sorted_results = sorted(successful, key=lambda x: x.get('overall_score', 0), reverse=True)
        
        for i, result in enumerate(sorted_results, 1):
            location = result['location_metadata']
            score = result.get('overall_score', 0)
            data_points = result.get('data_points_collected', 0)
            
            results_data.append([
                str(i),
                location['name'][:25],
                f"{location['city']}, {location['state'][:2]}",
                f"{score:.1f}/100",
                str(data_points)
            ])
        
        results_table = Table(results_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 1*inch, 1*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(results_table)
        story.append(PageBreak())
        
        # Detailed results
        for i, result in enumerate(sorted_results, 1):
            location = result['location_metadata']
            
            story.append(Paragraph(f"{i}. {location['name']}", styles['Heading2']))
            story.append(Paragraph(f"{location['address']}", styles['Normal']))
            story.append(Paragraph(f"Overall Score: <b>{result.get('overall_score', 0):.1f}/100</b>", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Category breakdown
            categories = result.get('categories', {})
            cat_data = [['Category', 'Score', 'Data Points', 'Collection Time']]
            
            for cat_name, cat_info in categories.items():
                cat_data.append([
                    cat_name.title(),
                    f"{cat_info.get('score', 0):.1f}/100",
                    str(len(cat_info.get('data', {}))),
                    f"{cat_info.get('collection_time_ms', 0):.1f}ms"
                ])
            
            cat_table = Table(cat_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.5*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 9)
            ]))
            
            story.append(cat_table)
            
            if i < len(sorted_results):
                story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    
    print(f"\n✅ PDF Generated: {pdf_filename}")
    return pdf_filename


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎯 BRIGHTSPOT LOCATOR AI - SIMPLE TEST (3 Locations)")
    print("="*80)
    print(f"\nStart Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    results = []
    
    for i, location in enumerate(TEST_LOCATIONS, 1):
        print(f"[{i}/{len(TEST_LOCATIONS)}]", end=" ")
        result = analyze_location(location)
        results.append(result)
        
        if i < len(TEST_LOCATIONS):
            print("⏳ Waiting 5 seconds...")
            time.sleep(5)
    
    # Save JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_filename = f"test_results_{timestamp}.json"
    
    with open(json_filename, 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "data_sources": DATA_SOURCES,
            "results": results
        }, f, indent=2)
    
    print(f"\n✅ JSON saved: {json_filename}")
    
    # Generate PDF
    print("\n📄 Generating PDF report...")
    pdf_filename = generate_pdf_report(results)
    
    print(f"\n{'='*80}")
    print("✅ TEST COMPLETE!")
    print(f"{'='*80}")
    print(f"\nFiles generated:")
    print(f"  📊 JSON: {json_filename}")
    print(f"  📄 PDF: {pdf_filename}")
    print(f"\n{'='*80}\n")
