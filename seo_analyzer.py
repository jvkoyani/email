#!/usr/bin/env python3
"""
SEO/GEO/AEO Analyzer
Analyzes domains for SEO, GEO, and AEO readiness.
"""

import logging
import requests
from typing import Dict, List
import socket
import ssl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 10

    def analyze_domain(self, domain: str, business_name: str = "", business_category: str = "") -> Dict:
        """Comprehensive SEO/GEO/AEO analysis for a domain"""

        analysis = {
            'domain': domain,
            'business_name': business_name,
            'business_category': business_category,
            'seo_score': 0,
            'geo_score': 0,
            'aeo_score': 0,
            'overall_score': 0,
            'seo_analysis': {},
            'geo_analysis': {},
            'aeo_analysis': {},
            'recommendations': [],
            'critical_issues': [],
            'analysis_timestamp': str(__import__('datetime').datetime.now())
        }

        try:
            # Get page content
            url = f"https://{domain}" if not domain.startswith('http') else domain
            response = self.session.get(url, timeout=self.timeout)
            content = response.text.lower()
            headers = response.headers

            # SEO Analysis
            analysis['seo_analysis'] = self._analyze_seo(domain, response, content, headers)
            analysis['seo_score'] = analysis['seo_analysis'].get('score', 0)

            # GEO Analysis
            analysis['geo_analysis'] = self._analyze_geo(domain, business_name, content)
            analysis['geo_score'] = analysis['geo_analysis'].get('score', 0)

            # AEO Analysis
            analysis['aeo_analysis'] = self._analyze_aeo(domain, content)
            analysis['aeo_score'] = analysis['aeo_analysis'].get('score', 0)

            # Overall score
            analysis['overall_score'] = round((analysis['seo_score'] + analysis['geo_score'] + analysis['aeo_score']) / 3)

            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            analysis['critical_issues'] = self._identify_critical_issues(analysis)

        except Exception as e:
            logger.error(f"Error analyzing {domain}: {e}")
            analysis['error'] = str(e)

        return analysis

    def _analyze_seo(self, domain: str, response, content: str, headers: Dict) -> Dict:
        """Analyze SEO readiness"""
        seo = {
            'checks': {},
            'issues': [],
            'score': 0
        }

        score = 0
        max_score = 10

        # HTTPS Check
        is_https = domain.startswith('https') or response.url.startswith('https')
        seo['checks']['ssl_certificate'] = is_https
        if is_https:
            score += 1
        else:
            seo['issues'].append('Missing SSL/HTTPS certificate')

        # Meta Title
        has_title = '<title>' in content
        seo['checks']['meta_title'] = has_title
        if has_title:
            score += 1
        else:
            seo['issues'].append('Missing meta title tag')

        # Meta Description
        has_meta_desc = 'meta name="description"' in content
        seo['checks']['meta_description'] = has_meta_desc
        if has_meta_desc:
            score += 1
        else:
            seo['issues'].append('Missing meta description')

        # H1 Tags
        h1_count = content.count('<h1')
        seo['checks']['h1_tags'] = h1_count
        if h1_count == 1:
            score += 1
        elif h1_count > 1:
            seo['issues'].append(f'Multiple H1 tags found ({h1_count}) - should have only 1')
        else:
            seo['issues'].append('No H1 tag found')

        # Structured Data (Schema)
        has_schema = 'schema.org' in content or '"@context"' in content
        seo['checks']['structured_data'] = has_schema
        if has_schema:
            score += 1
        else:
            seo['issues'].append('Missing schema markup (structured data)')

        # Mobile Meta Viewport
        has_viewport = 'viewport' in headers.get('content-type', '') or 'viewport' in content
        seo['checks']['mobile_viewport'] = has_viewport
        if has_viewport:
            score += 1
        else:
            seo['issues'].append('Missing mobile viewport meta tag')

        # Robots.txt
        try:
            robots_response = self.session.get(f"https://{domain}/robots.txt", timeout=5)
            seo['checks']['robots_txt'] = robots_response.status_code == 200
            if robots_response.status_code == 200:
                score += 1
        except:
            seo['checks']['robots_txt'] = False
            seo['issues'].append('robots.txt not accessible')

        # Sitemap
        try:
            sitemap_response = self.session.get(f"https://{domain}/sitemap.xml", timeout=5)
            seo['checks']['sitemap'] = sitemap_response.status_code == 200
            if sitemap_response.status_code == 200:
                score += 1
        except:
            seo['checks']['sitemap'] = False
            seo['issues'].append('sitemap.xml not found')

        # Page speed (basic check based on response time)
        seo['checks']['page_speed'] = 'good' if response.elapsed.total_seconds() < 3 else 'slow'
        if response.elapsed.total_seconds() < 3:
            score += 1

        seo['score'] = round((score / max_score) * 100)
        return seo

    def _analyze_geo(self, domain: str, business_name: str, content: str) -> Dict:
        """Analyze GEO readiness"""
        geo = {
            'checks': {},
            'issues': [],
            'score': 0
        }

        score = 0
        max_score = 7

        # Local Schema (LocalBusiness, Organization)
        has_local_schema = ('localbusiness' in content or 'organization' in content or
                           '"address"' in content or '"telephone"' in content)
        geo['checks']['local_schema'] = has_local_schema
        if has_local_schema:
            score += 1
        else:
            geo['issues'].append('Missing LocalBusiness or Organization schema markup')

        # Address Information
        has_address = ('street' in content or 'address' in content or
                      'qld' in content or 'nsw' in content or 'vic' in content or
                      'australia' in content.lower())
        geo['checks']['address_info'] = has_address
        if has_address:
            score += 1
        else:
            geo['issues'].append('No clear address information on website')

        # Phone Number
        has_phone = ('phone' in content or 'tel:' in content or '(' in content and ')' in content)
        geo['checks']['phone_number'] = has_phone
        if has_phone:
            score += 1
        else:
            geo['issues'].append('No phone number found on website')

        # Business Type/Category
        has_category = (business_name.lower() in content or
                       'service' in content or 'business' in content or
                       'company' in content)
        geo['checks']['business_category'] = has_category
        if has_category:
            score += 1
        else:
            geo['issues'].append('Business category not clearly defined')

        # NAP Consistency (Name, Address, Phone)
        geo['checks']['nap_consistency'] = 'needs_verification'
        geo['issues'].append('NAP consistency needs manual verification')

        # Local Citations
        geo['checks']['local_citations'] = 'needs_verification'
        geo['issues'].append('Google Business Profile optimization needs review')

        # Mobile Optimization
        has_mobile = 'mobile' in content or 'responsive' in content
        geo['checks']['mobile_ready'] = has_mobile
        if has_mobile:
            score += 1
        else:
            geo['issues'].append('Website may not be mobile optimized')

        geo['score'] = round((score / max_score) * 100)
        return geo

    def _analyze_aeo(self, domain: str, content: str) -> Dict:
        """Analyze AEO (Answer Engine Optimization) readiness"""
        aeo = {
            'checks': {},
            'issues': [],
            'score': 0
        }

        score = 0
        max_score = 6

        # FAQ Schema
        has_faq = 'faqpage' in content or '"@type":"Question"' in content
        aeo['checks']['faq_schema'] = has_faq
        if has_faq:
            score += 1
        else:
            aeo['issues'].append('No FAQ schema markup (good for featured snippets)')

        # Question-Answer Format
        has_qa_format = ('?</h' in content or 'answer' in content or
                        'how' in content or 'what' in content or 'why' in content)
        aeo['checks']['qa_format'] = has_qa_format
        if has_qa_format:
            score += 1
        else:
            aeo['issues'].append('No clear question-answer format detected')

        # Definition/Description
        has_definitions = ('definition' in content or 'describe' in content or
                          'explanation' in content)
        aeo['checks']['definitions'] = has_definitions
        if has_definitions:
            score += 1
        else:
            aeo['issues'].append('Missing clear definitions and explanations')

        # Lists/Tables
        has_lists = '<ul' in content or '<ol' in content or '<table' in content
        aeo['checks']['structured_lists'] = has_lists
        if has_lists:
            score += 1
        else:
            aeo['issues'].append('No structured lists or tables for easy scanning')

        # Clear Headlines
        has_headlines = '<h2' in content or '<h3' in content
        aeo['checks']['clear_headlines'] = has_headlines
        if has_headlines:
            score += 1
        else:
            aeo['issues'].append('Missing clear section headlines')

        # Short Answers (typical featured snippet is 40-60 words)
        aeo['checks']['featured_snippet_ready'] = 'needs_optimization'
        aeo['issues'].append('Content optimization for featured snippets needed')

        aeo['score'] = round((score / max_score) * 100)
        return aeo

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # SEO Recommendations
        if analysis['seo_score'] < 80:
            seo_issues = analysis['seo_analysis'].get('issues', [])
            for issue in seo_issues[:3]:  # Top 3 issues
                recommendations.append(f"SEO: {issue}")

        # GEO Recommendations
        if analysis['geo_score'] < 80:
            geo_issues = analysis['geo_analysis'].get('issues', [])
            for issue in geo_issues[:2]:
                recommendations.append(f"GEO: {issue}")

        # AEO Recommendations
        if analysis['aeo_score'] < 80:
            aeo_issues = analysis['aeo_analysis'].get('issues', [])
            for issue in aeo_issues[:2]:
                recommendations.append(f"AEO: {issue}")

        return recommendations

    def _identify_critical_issues(self, analysis: Dict) -> List[str]:
        """Identify critical issues that need immediate attention"""
        critical = []

        if not analysis['seo_analysis'].get('checks', {}).get('ssl_certificate'):
            critical.append('⚠️ CRITICAL: No SSL certificate - must add HTTPS')

        if not analysis['seo_analysis'].get('checks', {}).get('meta_title'):
            critical.append('⚠️ CRITICAL: Missing meta title - essential for SEO')

        if analysis['seo_score'] < 50:
            critical.append('⚠️ CRITICAL: SEO score very low - comprehensive optimization needed')

        return critical


def main():
    """Test the analyzer"""
    analyzer = SEOAnalyzer()

    # Test domains
    test_domains = [
        ('premierac.com.au', 'Premier AC Service', 'Air Conditioning'),
        ('coolbreeze.com.au', 'Cool Breeze HVAC', 'Air Conditioning'),
    ]

    for domain, name, category in test_domains:
        logger.info(f"\nAnalyzing {domain}...")
        result = analyzer.analyze_domain(domain, name, category)

        print(f"\n{'='*80}")
        print(f"ANALYSIS RESULTS: {domain}")
        print(f"{'='*80}")
        print(f"Business: {name} ({category})")
        print(f"\nSCORES:")
        print(f"  SEO Score:     {result['seo_score']}/100")
        print(f"  GEO Score:     {result['geo_score']}/100")
        print(f"  AEO Score:     {result['aeo_score']}/100")
        print(f"  Overall Score: {result['overall_score']}/100")

        if result['critical_issues']:
            print(f"\nCRITICAL ISSUES:")
            for issue in result['critical_issues']:
                print(f"  {issue}")

        if result['recommendations']:
            print(f"\nRECOMMENDATIONS:")
            for rec in result['recommendations'][:5]:
                print(f"  • {rec}")


if __name__ == '__main__':
    main()
