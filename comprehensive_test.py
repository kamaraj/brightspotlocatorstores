"""
Comprehensive Testing Script - 10 US Cities
Tests Brightspot Locator AI with diverse locations and generates PDF report
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Any
import time

# Test locations across different US regions
TEST_LOCATIONS = [
    {
        "name": "Silicon Valley Tech Hub",
        "address": "1600 Amphitheatre Parkway, Mountain View, CA 94043",
        "city": "Mountain View",
        "state": "California",
        "region": "West Coast"
    },
    {
        "name": "Manhattan Urban Center",
        "address": "350 5th Avenue, New York, NY 10118",
        "city": "New York",
        "state": "New York",
        "region": "Northeast"
    },
    {
        "name": "Austin Tech District",
        "address": "500 W 2nd St, Austin, TX 78701",
        "city": "Austin",
        "state": "Texas",
        "region": "South"
    },
    {
        "name": "Seattle Waterfront",
        "address": "1301 Alaskan Way, Seattle, WA 98101",
        "city": "Seattle",
        "state": "Washington",
        "region": "Pacific Northwest"
    },
    {
        "name": "Chicago Downtown",
        "address": "233 S Wacker Dr, Chicago, IL 60606",
        "city": "Chicago",
        "state": "Illinois",
        "region": "Midwest"
    },
    {
        "name": "Miami Beach Resort",
        "address": "1200 Ocean Dr, Miami Beach, FL 33139",
        "city": "Miami Beach",
        "state": "Florida",
        "region": "Southeast"
    },
    {
        "name": "Denver Downtown",
        "address": "1801 California St, Denver, CO 80202",
        "city": "Denver",
        "state": "Colorado",
        "region": "Mountain West"
    },
    {
        "name": "Boston Historic District",
        "address": "1 Beacon St, Boston, MA 02108",
        "city": "Boston",
        "state": "Massachusetts",
        "region": "New England"
    },
    {
        "name": "Phoenix Suburban",
        "address": "2 N Central Ave, Phoenix, AZ 85004",
        "city": "Phoenix",
        "state": "Arizona",
        "region": "Southwest"
    },
    {
        "name": "Portland Downtown",
        "address": "1000 SW Broadway, Portland, OR 97205",
        "city": "Portland",
        "state": "Oregon",
        "region": "Pacific Northwest"
    }
]

API_BASE_URL = "http://127.0.0.1:9025"


def analyze_location(location: Dict[str, str]) -> Dict[str, Any]:
    """Analyze a single location"""
    print(f"\n{'='*80}")
    print(f"Analyzing: {location['name']}")
    print(f"Address: {location['address']}")
    print(f"Region: {location['region']}")
    print(f"{'='*80}")
    
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
            
            # Add location metadata
            result["location_metadata"] = location
            result["analysis_timestamp"] = datetime.now().isoformat()
            
            print(f"✅ SUCCESS - Overall Score: {result.get('overall_score', 'N/A'):.1f}")
            print(f"   Data Points: {result.get('data_points_collected', 0)}")
            print(f"   Analysis Time: {result.get('total_analysis_time_ms', 0):.2f}ms")
            
            return result
        else:
            print(f"❌ ERROR - Status Code: {response.status_code}")
            return {
                "error": True,
                "status_code": response.status_code,
                "location_metadata": location
            }
            
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - Request exceeded 120 seconds")
        print(f"   Note: Real APIs can take 10-20 seconds per location")
        return {
            "error": True,
            "exception": "Request timeout after 120 seconds",
            "location_metadata": location
        }
    except Exception as e:
        print(f"❌ EXCEPTION - {str(e)}")
        return {
            "error": True,
            "exception": str(e),
            "location_metadata": location
        }


def run_comprehensive_test():
    """Run test on all 10 locations"""
    print("\n" + "="*80)
    print("🚀 BRIGHTSPOT LOCATOR AI - COMPREHENSIVE TEST")
    print("="*80)
    print(f"Testing {len(TEST_LOCATIONS)} diverse US locations")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = []
    
    for i, location in enumerate(TEST_LOCATIONS, 1):
        print(f"\n[{i}/{len(TEST_LOCATIONS)}] Processing...")
        
        result = analyze_location(location)
        results.append(result)
        
        # Wait between requests to avoid rate limits
        if i < len(TEST_LOCATIONS):
            print("\n⏳ Waiting 5 seconds before next request...")
            time.sleep(5)
    
    # Save results to JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_filename = f"test_results_{timestamp}.json"
    
    with open(json_filename, 'w') as f:
        json.dump({
            "test_metadata": {
                "total_locations": len(TEST_LOCATIONS),
                "test_date": datetime.now().isoformat(),
                "api_base_url": API_BASE_URL
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ TEST COMPLETE")
    print(f"{'='*80}")
    print(f"Results saved to: {json_filename}")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Generate summary
    generate_summary(results)
    
    return results, json_filename


def generate_summary(results: List[Dict[str, Any]]):
    """Generate test summary"""
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}\n")
    
    successful = [r for r in results if not r.get('error', False)]
    failed = [r for r in results if r.get('error', False)]
    
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {len(successful)} ✅")
    print(f"Failed: {len(failed)} ❌")
    
    if successful:
        print(f"\n{'='*80}")
        print("🏆 TOP 5 LOCATIONS (by Overall Score)")
        print(f"{'='*80}\n")
        
        sorted_results = sorted(successful, key=lambda x: x.get('overall_score', 0), reverse=True)
        
        for i, result in enumerate(sorted_results[:5], 1):
            location = result['location_metadata']
            score = result.get('overall_score', 0)
            print(f"{i}. {location['name']} ({location['city']}, {location['state']})")
            print(f"   Score: {score:.1f}/100")
            print(f"   Region: {location['region']}")
            print()
        
        print(f"{'='*80}")
        print("📈 AVERAGE METRICS")
        print(f"{'='*80}\n")
        
        avg_score = sum(r.get('overall_score', 0) for r in successful) / len(successful)
        avg_time = sum(r.get('total_analysis_time_ms', 0) for r in successful) / len(successful)
        avg_datapoints = sum(r.get('data_points_collected', 0) for r in successful) / len(successful)
        
        print(f"Average Overall Score: {avg_score:.2f}/100")
        print(f"Average Analysis Time: {avg_time:.2f}ms")
        print(f"Average Data Points: {avg_datapoints:.1f}")


def generate_pdf_report(results: List[Dict[str, Any]], json_filename: str):
    """Generate PDF report using reportlab"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"brightspot_test_report_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("Brightspot Locator AI", title_style))
        story.append(Paragraph("Comprehensive Location Analysis Report", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Test metadata
        story.append(Paragraph(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Total Locations Tested: {len(results)}", styles['Normal']))
        story.append(Paragraph(f"Data File: {json_filename}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        # Data sources
        story.append(Paragraph("Data Sources", styles['Heading2']))
        sources_data = [
            ['Category', 'API Source', 'Data Points', 'Status'],
            ['Demographics', 'U.S. Census Bureau ACS', '15 metrics', '✅ Active'],
            ['Competition', 'Google Places API', '12 metrics', '✅ Active'],
            ['Accessibility', 'Google Distance Matrix', '10 metrics', '✅ Active'],
            ['Safety', 'Proxy Indicators', '11 metrics', '⚠️ Estimated'],
            ['Economic', 'Market Estimates', '10 metrics', '⚠️ Estimated'],
            ['Regulatory', 'State Databases', '8 metrics', '✅ Active'],
        ]
        
        sources_table = Table(sources_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1*inch])
        sources_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(sources_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Results summary
        successful = [r for r in results if not r.get('error', False)]
        
        if successful:
            story.append(Paragraph("Location Analysis Results", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))
            
            # Results table
            results_data = [['Rank', 'Location', 'City, State', 'Score', 'Time (ms)']]
            
            sorted_results = sorted(successful, key=lambda x: x.get('overall_score', 0), reverse=True)
            
            for i, result in enumerate(sorted_results, 1):
                location = result['location_metadata']
                score = result.get('overall_score', 0)
                time_ms = result.get('total_analysis_time_ms', 0)
                
                results_data.append([
                    str(i),
                    location['name'][:30],
                    f"{location['city']}, {location['state'][:2]}",
                    f"{score:.1f}",
                    f"{time_ms:.0f}"
                ])
            
            results_table = Table(results_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 0.8*inch, 1*inch])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(results_table)
            story.append(PageBreak())
            
            # Detailed results for each location
            for i, result in enumerate(sorted_results, 1):
                location = result['location_metadata']
                
                story.append(Paragraph(f"{i}. {location['name']}", styles['Heading2']))
                story.append(Paragraph(f"{location['address']}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
                
                # Category scores
                categories = result.get('categories', {})
                cat_data = [['Category', 'Score', 'Data Points', 'Time (ms)']]
                
                for cat_name, cat_info in categories.items():
                    cat_data.append([
                        cat_name.title(),
                        f"{cat_info.get('score', 0):.1f}",
                        str(len(cat_info.get('data', {}))),
                        f"{cat_info.get('collection_time_ms', 0):.1f}"
                    ])
                
                cat_table = Table(cat_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
                cat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(cat_table)
                story.append(Spacer(1, 0.3*inch))
                
                if i < len(sorted_results):
                    story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        print(f"\n{'='*80}")
        print(f"📄 PDF Report Generated: {pdf_filename}")
        print(f"{'='*80}\n")
        
        return pdf_filename
        
    except ImportError:
        print(f"\n{'='*80}")
        print("⚠️  ReportLab not installed. Installing now...")
        print(f"{'='*80}\n")
        import subprocess
        subprocess.check_call(['pip', 'install', 'reportlab'])
        print("\n✅ ReportLab installed! Please run the script again.")
        return None


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎯 BRIGHTSPOT LOCATOR AI - COMPREHENSIVE TESTING")
    print("="*80)
    print("\nThis script will:")
    print("1. Test 10 diverse US locations")
    print("2. Collect data from all 6 categories")
    print("3. Generate JSON results file")
    print("4. Generate PDF report with data sources")
    print("\n" + "="*80 + "\n")
    
    input("Press Enter to start testing...")
    
    # Run tests
    results, json_filename = run_comprehensive_test()
    
    # Generate PDF
    print("\n📄 Generating PDF report...")
    pdf_filename = generate_pdf_report(results, json_filename)
    
    if pdf_filename:
        print(f"\n{'='*80}")
        print("✅ ALL COMPLETE!")
        print(f"{'='*80}")
        print(f"\nFiles generated:")
        print(f"  📊 JSON: {json_filename}")
        print(f"  📄 PDF: {pdf_filename}")
        print(f"\n{'='*80}\n")
