#!/usr/bin/env python3
"""
Personalized Email Generator
Creates personalized emails based on SEO/GEO/AEO analysis with attachments.
"""

import logging
from typing import Dict, List
from datetime import datetime
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailGenerator:
    def __init__(self):
        self.email_templates = {
            'poor': self._template_poor,
            'needs_work': self._template_needs_work,
            'good': self._template_good
        }

    def generate_personalized_email(self, business: Dict, analysis: Dict) -> Dict:
        """Generate a personalized email based on business data and SEO analysis"""

        email = {
            'to': business.get('registrant_email', ''),
            'to_name': business.get('registrant_name', 'Valued Partner'),
            'subject': '',
            'body': '',
            'attachments': [],
            'personalization_data': {}
        }

        # Determine readiness level
        overall_score = analysis.get('overall_score', 0)
        if overall_score >= 75:
            readiness = 'good'
        elif overall_score >= 50:
            readiness = 'needs_work'
        else:
            readiness = 'poor'

        # Generate email
        email['personalization_data'] = {
            'business_name': business.get('name', 'Valued Partner'),
            'registrant_name': business.get('registrant_name', 'Valued Partner'),
            'domain': analysis.get('domain', ''),
            'overall_score': overall_score,
            'seo_score': analysis.get('seo_score', 0),
            'geo_score': analysis.get('geo_score', 0),
            'aeo_score': analysis.get('aeo_score', 0),
            'readiness_level': readiness,
            'critical_issues_count': len(analysis.get('critical_issues', [])),
            'recommendations_count': len(analysis.get('recommendations', []))
        }

        template_func = self.email_templates.get(readiness, self._template_needs_work)
        email['subject'], email['body'] = template_func(email['personalization_data'], analysis)

        # Attachments
        email['attachments'] = [
            {
                'filename': f"seo_report_{analysis.get('domain', 'domain').replace('.', '_')}.pdf",
                'type': 'application/pdf',
                'note': 'Detailed SEO/GEO/AEO Analysis Report'
            }
        ]

        return email

    @staticmethod
    def _template_poor(data: Dict, analysis: Dict) -> tuple:
        """Email template for poor readiness (score < 50)"""

        subject = f"🚀 {data['business_name']}: Unlock Your Online Potential"

        body = f"""Dear {data['registrant_name']},

I hope this message finds you well!

I recently completed a comprehensive SEO/GEO/AEO analysis of {data['business_name']} website ({data['domain']}), and I'm reaching out because I've identified some significant opportunities for improvement.

📊 ANALYSIS RESULTS:
• Overall Online Readiness: {data['overall_score']}/100 (Needs Significant Improvement)
• SEO Readiness: {data['seo_score']}/100
• GEO Readiness: {data['geo_score']}/100
• AEO Readiness: {data['aeo_score']}/100

🚨 KEY FINDINGS:
Your website has {data['critical_issues_count']} critical issues that are preventing you from appearing in local search results, and I've identified {data['recommendations_count']} specific improvements that could dramatically impact your online visibility.

WHY THIS MATTERS:
Right now, potential customers searching for "{data['business_name']}" services in your area may not be finding you online. This is costing you real business opportunities every single day.

✨ THE GOOD NEWS:
These issues are fixable. With the right approach, you could:
✓ Rank higher in local Google searches
✓ Get found by customers actively searching for your services
✓ Increase qualified leads and revenue
✓ Build trust with better online presence

📎 ATTACHED:
I've prepared a detailed SEO/GEO/AEO analysis report showing exactly what needs to be fixed and how to do it.

🤝 NEXT STEPS:
I'd love to discuss how we can help {data['business_name']} improve your online visibility and attract more customers. Would you be open to a brief 15-minute consultation where I can walk you through the specific opportunities I've identified?

Looking forward to helping you succeed online!

Best regards,

[Your Name]
[Your Title]
[Your Company]
[Your Phone]
[Your Email]

P.S. The sooner you address these issues, the sooner you'll start seeing improved search visibility. In the meantime, your competitors may be implementing these strategies."""

        return subject, body

    @staticmethod
    def _template_needs_work(data: Dict, analysis: Dict) -> tuple:
        """Email template for needs work readiness (50-75)"""

        subject = f"Improve {data['business_name']}'s Local Search Visibility by 60%+"

        body = f"""Hello {data['registrant_name']},

I've been analyzing local business websites in your area, and I wanted to reach out personally about {data['business_name']}.

📊 YOUR CURRENT STANDING:
Your online readiness score is {data['overall_score']}/100. You're on the right track, but there are some quick wins that could significantly improve your search visibility:

BREAKDOWN:
✓ SEO: {data['seo_score']}/100
✓ GEO: {data['geo_score']}/100
✓ AEO: {data['aeo_score']}/100

🎯 OPPORTUNITY IDENTIFIED:
With just {data['recommendations_count']} key improvements, you could:
→ Increase search visibility by 40-60%
→ Attract more qualified local customers
→ Improve your competitive position

💡 WHAT STANDS OUT:
While you've done a good job establishing your online presence, there are {data['critical_issues_count']} areas where you're likely losing customers to competitors who've optimized these elements.

📈 THE POTENTIAL:
Imagine consistently appearing in the top 3 local search results when someone searches for your services. That's absolutely achievable for {data['business_name']}.

📎 ATTACHED ANALYSIS:
I've included a detailed report highlighting exactly which areas need attention and the specific steps to improve them.

👉 INVITATION:
I'd like to offer you a complimentary strategy session (15 minutes) where I can:
• Walk through your specific opportunities
• Explain the impact of each recommendation
• Discuss a timeline and approach that works for you

Does next week work for a quick chat?

Looking forward to helping {data['business_name']} grow!

Best regards,

[Your Name]
[Your Title]
[Your Company]
[Your Phone]
[Your Email]"""

        return subject, body

    @staticmethod
    def _template_good(data: Dict, analysis: Dict) -> tuple:
        """Email template for good readiness (score >= 75)"""

        subject = f"Next Steps to Dominate Local Search for {data['business_name']}"

        body = f"""Hi {data['registrant_name']},

Great news about {data['business_name']}!

📊 YOUR ANALYSIS RESULTS:
Your online readiness score is {data['overall_score']}/100 – you're doing very well!

BREAKDOWN:
✓ SEO Readiness: {data['seo_score']}/100
✓ GEO Readiness: {data['geo_score']}/100
✓ AEO Readiness: {data['aeo_score']}/100

🌟 WHAT YOU'RE DOING RIGHT:
You've established a solid online foundation. Your website has many of the key elements needed to rank well in local search results.

🚀 OPPORTUNITY TO STAND OUT:
However, there are still {data['recommendations_count']} specific optimizations that could help you dominate your local market and pull ahead of competitors.

📌 NEXT LEVEL STRATEGIES:
→ Capture more voice search and AI-powered search results (AEO optimization)
→ Improve your Google Business Profile impact
→ Optimize for featured snippets in your industry
→ Enhance local citation quality

📎 INCLUDED:
I've prepared a detailed analysis report with specific recommendations for your next phase of growth.

💼 PARTNERSHIP OPPORTUNITY:
I help businesses like {data['business_name']} go from "good" to "dominating" in their local market. Would you be interested in discussing how we can accelerate your growth?

I'm happy to jump on a quick 15-minute call to explore the best opportunities for {data['business_name']}.

Best regards,

[Your Name]
[Your Title]
[Your Company]
[Your Phone]
[Your Email]

P.S. The businesses who act on these recommendations now will be the market leaders in 3-6 months."""

        return subject, body

    def generate_email_sequence(self, businesses_with_analysis: List[Dict]) -> List[Dict]:
        """Generate complete email sequence for all businesses"""

        email_sequence = []

        for item in businesses_with_analysis:
            business = item['business']
            analysis = item['analysis']

            email = self.generate_personalized_email(business, analysis)
            email['business_name'] = business.get('name', '')
            email['domain'] = analysis.get('domain', '')
            email_sequence.append(email)

        return email_sequence

    def save_email_sequence_csv(self, email_sequence: List[Dict], filename: str = 'email_sequence.csv') -> str:
        """Save email sequence to CSV for email platform import"""

        if not email_sequence:
            logger.warning("No emails to save")
            return ""

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'business_name', 'recipient_name', 'recipient_email', 'domain',
                    'overall_score', 'seo_score', 'geo_score', 'aeo_score',
                    'readiness_level', 'subject', 'body', 'attachments'
                ]

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for email in email_sequence:
                    writer.writerow({
                        'business_name': email.get('business_name', ''),
                        'recipient_name': email.get('to_name', ''),
                        'recipient_email': email.get('to', ''),
                        'domain': email.get('domain', ''),
                        'overall_score': email.get('personalization_data', {}).get('overall_score', ''),
                        'seo_score': email.get('personalization_data', {}).get('seo_score', ''),
                        'geo_score': email.get('personalization_data', {}).get('geo_score', ''),
                        'aeo_score': email.get('personalization_data', {}).get('aeo_score', ''),
                        'readiness_level': email.get('personalization_data', {}).get('readiness_level', ''),
                        'subject': email.get('subject', ''),
                        'body': email.get('body', ''),
                        'attachments': ', '.join([a['filename'] for a in email.get('attachments', [])])
                    })

            logger.info(f"Email sequence saved to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error saving email sequence: {e}")
            return ""

    def save_email_templates(self, email_sequence: List[Dict], output_dir: str = 'email_templates') -> List[str]:
        """Save individual email templates as text files"""

        import os
        os.makedirs(output_dir, exist_ok=True)

        files = []

        for email in email_sequence:
            business_name = email.get('business_name', 'business').replace(' ', '_')
            filename = os.path.join(output_dir, f"{business_name}_email.txt")

            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"TO: {email.get('to_name', '')} <{email.get('to', '')}>\n")
                    f.write(f"SUBJECT: {email.get('subject', '')}\n\n")
                    f.write("="*80 + "\n\n")
                    f.write(email.get('body', ''))
                    f.write("\n\n" + "="*80 + "\n")
                    f.write(f"\nATTACHMENTS:\n")
                    for attachment in email.get('attachments', []):
                        f.write(f"  - {attachment['filename']}\n")

                files.append(filename)
                logger.info(f"Email template saved: {filename}")

            except Exception as e:
                logger.error(f"Error saving email template: {e}")

        return files


def main():
    """Test email generator"""

    sample_business = {
        'name': 'Premier AC Service',
        'registrant_name': 'John Smith',
        'registrant_email': 'john@premierac.com.au'
    }

    sample_analysis = {
        'domain': 'premierac.com.au',
        'overall_score': 65,
        'seo_score': 72,
        'geo_score': 65,
        'aeo_score': 58,
        'critical_issues': ['Missing SSL', 'No sitemap'],
        'recommendations': ['Add schema', 'Create GBP', 'Add FAQ']
    }

    generator = EmailGenerator()
    email = generator.generate_personalized_email(sample_business, sample_analysis)

    print("\n" + "="*80)
    print("GENERATED EMAIL")
    print("="*80 + "\n")
    print(f"TO: {email['to_name']} <{email['to']}>")
    print(f"SUBJECT: {email['subject']}\n")
    print(email['body'])
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
