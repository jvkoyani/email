#!/usr/bin/env python3
"""
PDF Report Generator
Creates professional SEO/GEO/AEO analysis reports in PDF format.
"""

import logging
from datetime import datetime
from typing import Dict
import json

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("reportlab not installed. Install with: pip install reportlab")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFReportGenerator:
    def __init__(self):
        self.available = REPORTLAB_AVAILABLE
        if not self.available:
            logger.warning("PDF generation disabled - reportlab not installed")

    def generate_report(self, analysis: Dict, output_path: str = None) -> str:
        """Generate a professional PDF report from analysis data"""

        if not self.available:
            logger.warning("PDF generation skipped - reportlab not installed")
            return self._generate_fallback_report(analysis)

        if not output_path:
            domain = analysis.get('domain', 'domain').replace('.', '_')
            output_path = f"seo_report_{domain}.pdf"

        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=HexColor('#2c3e50'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )

            # Title
            story.append(Paragraph(f"SEO/GEO/AEO Analysis Report", title_style))
            story.append(Spacer(1, 0.2*inch))

            # Domain Info
            domain_table = Table([
                ['Domain:', analysis.get('domain', 'N/A')],
                ['Business:', analysis.get('business_name', 'N/A')],
                ['Category:', analysis.get('business_category', 'N/A')],
                ['Date:', analysis.get('analysis_timestamp', 'N/A')[:10]]
            ])
            domain_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdc3c7'))
            ]))
            story.append(domain_table)
            story.append(Spacer(1, 0.3*inch))

            # Overall Scores
            story.append(Paragraph("Overall Readiness Scores", heading_style))

            seo_score = analysis.get('seo_score', 0)
            geo_score = analysis.get('geo_score', 0)
            aeo_score = analysis.get('aeo_score', 0)
            overall_score = analysis.get('overall_score', 0)

            score_table = Table([
                ['Metric', 'Score', 'Status'],
                ['SEO Readiness', f'{seo_score}/100', self._get_status(seo_score)],
                ['GEO Readiness', f'{geo_score}/100', self._get_status(geo_score)],
                ['AEO Readiness', f'{aeo_score}/100', self._get_status(aeo_score)],
                ['OVERALL SCORE', f'{overall_score}/100', self._get_status(overall_score)]
            ])

            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdc3c7')),
                ('BACKGROUND', (0, 4), (-1, 4), HexColor('#e8f4f8'))
            ]))
            story.append(score_table)
            story.append(Spacer(1, 0.3*inch))

            # Critical Issues
            critical_issues = analysis.get('critical_issues', [])
            if critical_issues:
                story.append(Paragraph("⚠️ Critical Issues", heading_style))
                for issue in critical_issues:
                    story.append(Paragraph(f"• {issue}", styles['BodyText']))
                story.append(Spacer(1, 0.2*inch))

            # Detailed Analysis Sections
            for section_name, section_key in [('SEO Analysis', 'seo_analysis'),
                                              ('GEO Analysis', 'geo_analysis'),
                                              ('AEO Analysis', 'aeo_analysis')]:
                story.append(PageBreak())
                story.append(Paragraph(section_name, heading_style))

                section_data = analysis.get(section_key, {})
                issues = section_data.get('issues', [])

                if issues:
                    story.append(Paragraph("Areas for Improvement:", styles['Heading3']))
                    for issue in issues:
                        story.append(Paragraph(f"• {issue}", styles['BodyText']))
                else:
                    story.append(Paragraph("✓ No issues detected in this area", styles['BodyText']))

                story.append(Spacer(1, 0.2*inch))

            # Recommendations
            story.append(PageBreak())
            story.append(Paragraph("Recommendations for Improvement", heading_style))

            recommendations = analysis.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    story.append(Paragraph(f"{i}. {rec}", styles['BodyText']))
            else:
                story.append(Paragraph("No specific recommendations at this time", styles['BodyText']))

            story.append(Spacer(1, 0.3*inch))

            # Next Steps
            story.append(Paragraph("Suggested Next Steps", heading_style))
            next_steps = [
                "1. Address critical issues first (marked with ⚠️)",
                "2. Implement quick wins from recommendations",
                "3. Schedule comprehensive SEO audit",
                "4. Set up Google Business Profile optimization",
                "5. Create content strategy for featured snippets",
                "6. Monitor rankings and traffic improvements"
            ]
            for step in next_steps:
                story.append(Paragraph(step, styles['BodyText']))

            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return self._generate_fallback_report(analysis)

    def _generate_fallback_report(self, analysis: Dict) -> str:
        """Generate a text-based report if PDF generation fails"""
        domain = analysis.get('domain', 'domain').replace('.', '_')
        filename = f"seo_report_{domain}.txt"

        with open(filename, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write(f"SEO/GEO/AEO ANALYSIS REPORT\n")
            f.write(f"{'='*80}\n\n")

            f.write(f"Domain: {analysis.get('domain', 'N/A')}\n")
            f.write(f"Business: {analysis.get('business_name', 'N/A')}\n")
            f.write(f"Category: {analysis.get('business_category', 'N/A')}\n")
            f.write(f"Date: {analysis.get('analysis_timestamp', 'N/A')}\n\n")

            f.write(f"{'='*80}\n")
            f.write(f"OVERALL READINESS SCORES\n")
            f.write(f"{'='*80}\n\n")

            f.write(f"SEO Score:     {analysis.get('seo_score', 0)}/100  {self._get_status(analysis.get('seo_score', 0))}\n")
            f.write(f"GEO Score:     {analysis.get('geo_score', 0)}/100  {self._get_status(analysis.get('geo_score', 0))}\n")
            f.write(f"AEO Score:     {analysis.get('aeo_score', 0)}/100  {self._get_status(analysis.get('aeo_score', 0))}\n")
            f.write(f"OVERALL SCORE: {analysis.get('overall_score', 0)}/100  {self._get_status(analysis.get('overall_score', 0))}\n\n")

            # Critical Issues
            critical = analysis.get('critical_issues', [])
            if critical:
                f.write(f"{'='*80}\n")
                f.write(f"CRITICAL ISSUES\n")
                f.write(f"{'='*80}\n\n")
                for issue in critical:
                    f.write(f"{issue}\n")
                f.write("\n")

            # Recommendations
            f.write(f"{'='*80}\n")
            f.write(f"RECOMMENDATIONS\n")
            f.write(f"{'='*80}\n\n")

            recommendations = analysis.get('recommendations', [])
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")

        logger.info(f"Text report generated: {filename}")
        return filename

    @staticmethod
    def _get_status(score: int) -> str:
        """Get status badge based on score"""
        if score >= 80:
            return "✓ Good"
        elif score >= 60:
            return "⚠️ Needs Work"
        elif score >= 40:
            return "✗ Poor"
        else:
            return "✗ Critical"


def main():
    """Test the report generator"""
    # Sample analysis data
    sample_analysis = {
        'domain': 'premierac.com.au',
        'business_name': 'Premier AC Service',
        'business_category': 'Air Conditioning',
        'seo_score': 72,
        'geo_score': 65,
        'aeo_score': 58,
        'overall_score': 65,
        'seo_analysis': {
            'score': 72,
            'issues': [
                'Missing schema markup',
                'No sitemap.xml found'
            ]
        },
        'geo_analysis': {
            'score': 65,
            'issues': [
                'No LocalBusiness schema',
                'NAP consistency needs verification'
            ]
        },
        'aeo_analysis': {
            'score': 58,
            'issues': [
                'No FAQ schema markup',
                'Missing question-answer format'
            ]
        },
        'critical_issues': [
            '⚠️ CRITICAL: No SSL certificate'
        ],
        'recommendations': [
            'SEO: Add schema.org markup for LocalBusiness',
            'GEO: Create Google Business Profile',
            'AEO: Add FAQ section with schema markup'
        ],
        'analysis_timestamp': datetime.now().isoformat()
    }

    generator = PDFReportGenerator()
    report_path = generator.generate_report(sample_analysis)
    print(f"Report generated: {report_path}")


if __name__ == '__main__':
    main()
