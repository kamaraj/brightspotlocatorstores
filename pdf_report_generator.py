"""
PDF Report Generator for Business User Testing
Creates comprehensive PDF reports with charts and insights
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any


class PersonaPDFReport:
    """Generate PDF report for persona analysis"""
    
    def __init__(self, persona_name: str, results: List[Dict[str, Any]]):
        self.persona_name = persona_name
        self.results = results
        self.df = pd.DataFrame(results)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.filename = f"report_{persona_name.replace(' ', '_')}_{self.timestamp}.pdf"
        
        # Colors
        self.primary_color = HexColor('#FF6B6B')
        self.secondary_color = HexColor('#4ECDC4')
        self.accent_color = HexColor('#FFE66D')
        
    def generate(self):
        """Generate the PDF report"""
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.primary_color,
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            spaceAfter=10,
            spaceBefore=15
        )
        
        # Title page
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("🎯 Childcare Location Intelligence", title_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"<b>Persona Analysis Report</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>{self.persona_name}</b>", styles['Heading3']))
        story.append(Spacer(1, 0.3*inch))
        
        # Report metadata
        if self.results:
            persona_data = self.results[0]
            metadata_data = [
                ['Report Date:', datetime.now().strftime('%B %d, %Y')],
                ['Persona:', persona_data['persona_name']],
                ['Role:', persona_data['persona_role']],
                ['Locations Analyzed:', str(len(self.results))],
                ['State:', 'Minnesota'],
                ['Analysis Type:', 'Comprehensive Site Selection']
            ]
            
            metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
            metadata_table.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (0, -1), self.primary_color),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(metadata_table)
        
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        avg_score = self.df['persona_weighted_score'].mean()
        strong_yes = len(self.df[self.df['persona_recommendation'].str.contains('STRONG YES', case=False)])
        yes_count = len(self.df[self.df['persona_recommendation'].str.contains('YES', case=False)])
        top_location = self.df.loc[self.df['persona_weighted_score'].idxmax()]
        
        summary_text = f"""
        This report presents a comprehensive analysis of {len(self.results)} childcare center locations 
        across Minnesota, evaluated specifically from the perspective of <b>{self.persona_name}</b>.
        <br/><br/>
        <b>Key Findings:</b><br/>
        • Average weighted score: <b>{avg_score:.1f}/100</b><br/>
        • Strong recommendations: <b>{strong_yes}</b> locations<br/>
        • All positive recommendations: <b>{yes_count}</b> locations<br/>
        • Top-rated location: <b>{top_location['city']}</b> (Score: {top_location['persona_weighted_score']:.1f})<br/>
        • Investment fit: <b>{top_location['investment_fit']}</b><br/>
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Top 5 Recommendations
        story.append(Paragraph("Top 5 Recommended Locations", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        top5 = self.df.nlargest(5, 'persona_weighted_score')
        top5_data = [['Rank', 'City', 'Score', 'Type', 'Decision', 'Risk']]
        
        for idx, (_, row) in enumerate(top5.iterrows(), 1):
            top5_data.append([
                str(idx),
                row['city'],
                f"{row['persona_weighted_score']:.1f}",
                row['location_type'],
                row['persona_recommendation'][:20] + '...' if len(row['persona_recommendation']) > 20 else row['persona_recommendation'],
                row['risk_assessment']
            ])
        
        top5_table = Table(top5_data, colWidths=[0.5*inch, 1.5*inch, 0.8*inch, 1.3*inch, 1.7*inch, 0.8*inch])
        top5_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F8F9FA')])
        ]))
        story.append(top5_table)
        story.append(PageBreak())
        
        # Detailed Location Analysis
        story.append(Paragraph("Detailed Location Analysis", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        for _, row in self.df.sort_values('persona_weighted_score', ascending=False).iterrows():
            # Location header
            location_title = f"{row['city']} - {row['location_type']}"
            story.append(Paragraph(location_title, styles['Heading3']))
            story.append(Spacer(1, 0.05*inch))
            
            # Scores table
            scores_data = [
                ['Metric', 'Score'],
                ['Persona-Weighted Score', f"{row['persona_weighted_score']:.1f}/100"],
                ['Standard Score', f"{row['overall_score']:.1f}/100"],
                ['Demographics', f"{row['demographics_score']:.1f}"],
                ['Competition', f"{row['competition_score']:.1f}"],
                ['Economic Viability', f"{row['economic_score']:.1f}"],
                ['Safety', f"{row['safety_score']:.1f}"],
                ['Accessibility', f"{row['accessibility_score']:.1f}"]
            ]
            
            scores_table = Table(scores_data, colWidths=[2.5*inch, 1.5*inch])
            scores_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F8F9FA')])
            ]))
            story.append(scores_table)
            story.append(Spacer(1, 0.1*inch))
            
            # Key metrics
            metrics_data = [
                ['Children (0-5)', f"{int(row['children_0_5']):,}"],
                ['Median Income', f"${int(row['median_income']):,}"],
                ['Existing Centers', str(int(row['existing_centers']))],
                ['Market Saturation', f"{row['market_saturation']:.2f}"],
                ['Startup Cost', f"${int(row['startup_cost']):,}"]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#E0E0E0')),
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FAFAFA'))
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 0.1*inch))
            
            # Recommendation
            rec_text = f"""
            <b>Recommendation:</b> {row['persona_recommendation']}<br/>
            <b>Rationale:</b> {row['persona_rationale']}<br/>
            <b>Risk Level:</b> {row['risk_assessment']}<br/>
            <b>Investment Fit:</b> {row['investment_fit']}
            """
            story.append(Paragraph(rec_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        print(f"📄 Generated PDF: {self.filename}")
        return self.filename


def generate_all_persona_pdfs(results: List[Dict[str, Any]]):
    """Generate PDF for each persona"""
    if not results:
        print("No results to generate PDFs")
        return []
    
    df = pd.DataFrame(results)
    pdf_files = []
    
    print("\n" + "="*80)
    print("📄 Generating PDF Reports...")
    print("="*80 + "\n")
    
    for persona_name in df['persona_name'].unique():
        persona_results = df[df['persona_name'] == persona_name].to_dict('records')
        report = PersonaPDFReport(persona_name, persona_results)
        pdf_file = report.generate()
        pdf_files.append(pdf_file)
    
    print(f"\n✅ Generated {len(pdf_files)} PDF reports")
    return pdf_files


def generate_comparison_pdf(results: List[Dict[str, Any]]):
    """Generate comparison PDF across all personas"""
    if not results:
        return None
    
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"comparison_report_all_personas_{timestamp}.pdf"
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("🎯 Minnesota Childcare Location Analysis", styles['Title']))
    story.append(Paragraph("Multi-Persona Comparison Report", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    
    # Summary statistics
    summary_data = [
        ['Total Locations', str(df['city'].nunique())],
        ['Total Personas', str(df['persona_name'].nunique())],
        ['Total Analyses', str(len(df))],
        ['Avg Overall Score', f"{df['overall_score'].mean():.1f}/100"],
        ['Report Date', datetime.now().strftime('%B %d, %Y')]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Best locations by persona
    story.append(Paragraph("Top Location by Each Persona", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    top_by_persona = []
    for persona in df['persona_name'].unique():
        persona_df = df[df['persona_name'] == persona]
        top = persona_df.loc[persona_df['persona_weighted_score'].idxmax()]
        top_by_persona.append([
            persona,
            top['city'],
            f"{top['persona_weighted_score']:.1f}",
            top['persona_recommendation'][:30]
        ])
    
    top_table = Table([['Persona', 'Top City', 'Score', 'Decision']] + top_by_persona,
                     colWidths=[2*inch, 1.5*inch, 0.8*inch, 2.2*inch])
    top_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#FF6B6B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F8F9FA')])
    ]))
    story.append(top_table)
    story.append(PageBreak())
    
    # City rankings
    story.append(Paragraph("City Rankings (Average Across All Personas)", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    city_avg = df.groupby('city').agg({
        'persona_weighted_score': 'mean',
        'demographics_score': 'mean',
        'competition_score': 'mean',
        'economic_score': 'mean'
    }).round(1).sort_values('persona_weighted_score', ascending=False)
    
    city_data = [['City', 'Avg Score', 'Demographics', 'Competition', 'Economic']]
    for city, row in city_avg.head(10).iterrows():
        city_data.append([
            city,
            str(row['persona_weighted_score']),
            str(row['demographics_score']),
            str(row['competition_score']),
            str(row['economic_score'])
        ])
    
    city_table = Table(city_data, colWidths=[1.8*inch, 1*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    city_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4ECDC4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F8F9FA')])
    ]))
    story.append(city_table)
    
    doc.build(story)
    print(f"📄 Generated comparison PDF: {filename}")
    return filename
