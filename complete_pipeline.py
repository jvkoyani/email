#!/usr/bin/env python3
"""
Complete Pipeline: LocalSearch + WHOIS + SEO Analysis + Email Generation
Full workflow: Scrape → Enrich → Analyze → Report → Email
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompletePipeline:
    def __init__(self, config_file: str = 'config.json'):
        self.config = self.load_config(config_file)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)

    def load_config(self, config_file: str) -> dict:
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_file}")
            return self.get_default_config()

    @staticmethod
    def get_default_config() -> dict:
        return {
            'scraper': {'type': 'beautifulsoup'},
            'search': {'categories': ['Air Conditioning'], 'locations': ['Brisbane']},
            'output': {'csv_filename': 'localsearch_businesses.csv'},
            'seo_analysis': {'enabled': True}
        }

    def step_1_scrape_businesses(self) -> str:
        logger.info("\n" + "="*80)
        logger.info("STEP 1: SCRAPING BUSINESSES FROM LOCALSEARCH")
        logger.info("="*80)

        try:
            from localsearch_scraper import LocalSearchScraper

            scraper = LocalSearchScraper()
            categories = self.config['search'].get('categories', [''])
            locations = self.config['search'].get('locations', [''])

            for category in categories:
                for location in locations:
                    logger.info(f"Scraping {category} in {location}...")
                    businesses = scraper.search_businesses(category=category, location=location)
                    if businesses:
                        scraper.businesses.extend(businesses)
                        logger.info(f"✅ Found {len(businesses)} businesses")

            output_csv = f"step1_scraped_{self.timestamp}.csv"
            scraper.save_to_csv(output_csv)
            logger.info(f"✅ Step 1 Complete: {len(scraper.businesses)} businesses")
            return output_csv

        except Exception as e:
            logger.error(f"Error in scraping step: {e}")
            return ""

    def step_2_enrich_with_whois(self, input_csv: str) -> str:
        logger.info("\n" + "="*80)
        logger.info("STEP 2: ENRICHING WITH WHOIS CONTACT DATA")
        logger.info("="*80)

        try:
            from whois_enricher import WHOISEnricher

            output_csv = f"step2_enriched_{self.timestamp}.csv"
            enricher = WHOISEnricher()
            enricher.enrich_csv(input_csv, output_csv)

            logger.info(f"✅ Step 2 Complete: Enriched {len(enricher.businesses)} businesses")
            return output_csv

        except Exception as e:
            logger.error(f"Error in WHOIS enrichment step: {e}")
            return ""

    def step_3_seo_analysis(self, input_csv: str) -> str:
        logger.info("\n" + "="*80)
        logger.info("STEP 3: SEO/GEO/AEO ANALYSIS")
        logger.info("="*80)

        try:
            from seo_analyzer import SEOAnalyzer
            import csv

            analyzer = SEOAnalyzer()
            analysis_results = []

            # Read enriched CSV
            with open(input_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                businesses = list(reader)

            total = len(businesses)
            logger.info(f"Analyzing {total} businesses for SEO/GEO/AEO readiness...")

            for idx, business in enumerate(businesses, 1):
                website = business.get('website', '')
                business_name = business.get('name', '')
                category = business.get('category', '')

                if website:
                    logger.info(f"[{idx}/{total}] Analyzing {business_name}...")
                    analysis = analyzer.analyze_domain(website, business_name, category)
                    analysis['business_data'] = business
                    analysis_results.append(analysis)

            # Save analysis results
            output_file = f"step3_seo_analysis_{self.timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, default=str)

            logger.info(f"✅ Step 3 Complete: Analyzed {len(analysis_results)} businesses")
            return output_file

        except Exception as e:
            logger.error(f"Error in SEO analysis step: {e}")
            return ""

    def step_4_generate_reports(self, analysis_file: str) -> list:
        logger.info("\n" + "="*80)
        logger.info("STEP 4: GENERATING PDF REPORTS")
        logger.info("="*80)

        try:
            from pdf_report_generator import PDFReportGenerator

            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_results = json.load(f)

            generator = PDFReportGenerator()
            report_files = []

            logger.info(f"Generating {len(analysis_results)} PDF reports...")

            for idx, analysis in enumerate(analysis_results, 1):
                business_name = analysis.get('business_name', 'business').replace(' ', '_')
                output_path = self.results_dir / f"report_{business_name}_{self.timestamp}.pdf"

                logger.info(f"[{idx}] Generating report for {analysis.get('business_name')}...")
                report_file = generator.generate_report(analysis, str(output_path))
                report_files.append(report_file)

            logger.info(f"✅ Step 4 Complete: Generated {len(report_files)} reports")
            return report_files

        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            return []

    def step_5_generate_emails(self, enriched_csv: str, analysis_file: str) -> str:
        logger.info("\n" + "="*80)
        logger.info("STEP 5: GENERATING PERSONALIZED EMAILS")
        logger.info("="*80)

        try:
            from email_generator import EmailGenerator
            import csv

            # Read enriched CSV
            with open(enriched_csv, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                businesses = {b['domain']: b for b in csv_reader}

            # Read analysis results
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_list = json.load(f)

            # Generate emails
            generator = EmailGenerator()
            email_sequence = []

            logger.info(f"Generating personalized emails...")

            for analysis in analysis_list:
                domain = analysis.get('domain', '')
                business = businesses.get(domain, {})

                if business:
                    email = generator.generate_personalized_email(business, analysis)
                    email['business_name'] = business.get('name', '')
                    email['domain'] = domain
                    email_sequence.append(email)

            # Save email sequence
            csv_output = self.results_dir / f"email_sequence_{self.timestamp}.csv"
            generator.save_email_sequence_csv(email_sequence, str(csv_output))

            # Save individual templates
            templates_dir = self.results_dir / f"email_templates_{self.timestamp}"
            template_files = generator.save_email_templates(email_sequence, str(templates_dir))

            logger.info(f"✅ Step 5 Complete: Generated {len(email_sequence)} personalized emails")
            return str(csv_output)

        except Exception as e:
            logger.error(f"Error generating emails: {e}")
            return ""

    def print_final_summary(self):
        logger.info("\n" + "="*80)
        logger.info("✅ COMPLETE PIPELINE FINISHED")
        logger.info("="*80 + "\n")

        logger.info("📁 Results saved in 'results/' directory\n")

        logger.info("📊 OUTPUT FILES:")
        logger.info(f"  1. Scraped businesses CSV (step 1)")
        logger.info(f"  2. Enriched with WHOIS data (step 2)")
        logger.info(f"  3. SEO/GEO/AEO analysis JSON (step 3)")
        logger.info(f"  4. PDF reports for each business (step 4)")
        logger.info(f"  5. Email sequence CSV (step 5)")
        logger.info(f"  6. Individual email templates (step 5)\n")

        logger.info("🚀 NEXT STEPS:")
        logger.info("  1. Review PDF reports in results/")
        logger.info("  2. Import email_sequence.csv to your email platform")
        logger.info("  3. Upload PDF reports as attachments")
        logger.info("  4. Set up email sequences with appropriate delays")
        logger.info("  5. Monitor open rates and engagement")
        logger.info("  6. Follow up with interested prospects\n")

        logger.info("💡 EMAIL SEQUENCE TIPS:")
        logger.info("  • Poor readiness (< 50): Send immediate follow-up (1-2 days)")
        logger.info("  • Needs work (50-75): Send within 3-5 days")
        logger.info("  • Good (75+): Send for premium services\n")

        logger.info("="*80 + "\n")

    def run(self):
        logger.info("\n" + "="*80)
        logger.info("🚀 COMPLETE LOCALSEARCH PIPELINE")
        logger.info("Scrape → Enrich → Analyze → Report → Email")
        logger.info("="*80 + "\n")

        # Step 1: Scrape
        scraped_csv = self.step_1_scrape_businesses()
        if not scraped_csv or not Path(scraped_csv).exists():
            logger.error("Scraping failed. Aborting pipeline.")
            return

        # Step 2: Enrich with WHOIS
        enriched_csv = self.step_2_enrich_with_whois(scraped_csv)
        if not enriched_csv or not Path(enriched_csv).exists():
            logger.error("WHOIS enrichment failed. Aborting pipeline.")
            return

        # Step 3: SEO Analysis
        analysis_file = self.step_3_seo_analysis(enriched_csv)
        if not analysis_file or not Path(analysis_file).exists():
            logger.error("SEO analysis failed. Aborting pipeline.")
            return

        # Step 4: Generate Reports
        report_files = self.step_4_generate_reports(analysis_file)
        if not report_files:
            logger.warning("No PDF reports generated")

        # Step 5: Generate Emails
        email_csv = self.step_5_generate_emails(enriched_csv, analysis_file)
        if not email_csv:
            logger.error("Email generation failed")

        # Print summary
        self.print_final_summary()


def main():
    pipeline = CompletePipeline('config.json')
    pipeline.run()


if __name__ == '__main__':
    main()
