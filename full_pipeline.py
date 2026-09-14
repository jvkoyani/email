#!/usr/bin/env python3
"""
Full Pipeline: LocalSearch Scraper + WHOIS Enrichment
Complete workflow to scrape businesses and enrich with WHOIS contact data.
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FullPipeline:
    def __init__(self, config_file: str = 'config.json'):
        """Initialize the full pipeline"""
        self.config = self.load_config(config_file)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def load_config(self, config_file: str) -> dict:
        """Load configuration file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_file}")
            return self.get_default_config()

    @staticmethod
    def get_default_config() -> dict:
        """Return default configuration"""
        return {
            'scraper': {'type': 'beautifulsoup'},
            'search': {
                'categories': ['Air Conditioning'],
                'locations': ['Brisbane']
            },
            'output': {
                'csv_filename': 'localsearch_businesses.csv',
                'json_filename': 'localsearch_businesses.json'
            }
        }

    def step_1_scrape_businesses(self) -> str:
        """Step 1: Scrape businesses from LocalSearch"""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 1: SCRAPING BUSINESSES FROM LOCALSEARCH")
        logger.info("=" * 80)

        try:
            from localsearch_scraper import LocalSearchScraper

            scraper = LocalSearchScraper()
            categories = self.config['search'].get('categories', [''])
            locations = self.config['search'].get('locations', [''])

            total = len(categories) * len(locations)
            count = 0

            for category in categories:
                for location in locations:
                    count += 1
                    logger.info(f"[{count}/{total}] Scraping {category} in {location}...")

                    businesses = scraper.search_businesses(
                        category=category,
                        location=location
                    )

                    if businesses:
                        scraper.businesses.extend(businesses)
                        logger.info(f"  ✅ Found {len(businesses)} businesses")
                    else:
                        logger.warning(f"  ⚠️  No businesses found")

            # Save scraped data
            output_csv = f"step1_scraped_{self.timestamp}.csv"
            scraper.save_to_csv(output_csv)
            logger.info(f"\n✅ Step 1 Complete: Saved {len(scraper.businesses)} businesses to {output_csv}")

            return output_csv

        except Exception as e:
            logger.error(f"Error in scraping step: {e}")
            return ""

    def step_2_enrich_with_whois(self, input_csv: str) -> str:
        """Step 2: Enrich with WHOIS contact data"""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: ENRICHING WITH WHOIS CONTACT DATA")
        logger.info("=" * 80)

        try:
            from whois_enricher import WHOISEnricher

            output_csv = f"step2_enriched_{self.timestamp}.csv"

            enricher = WHOISEnricher()
            enricher.enrich_csv(input_csv, output_csv)

            logger.info(f"\n✅ Step 2 Complete: Enriched data saved to {output_csv}")

            return output_csv

        except Exception as e:
            logger.error(f"Error in WHOIS enrichment step: {e}")
            return ""

    def print_final_summary(self, final_csv: str) -> None:
        """Print summary of final results"""
        try:
            import csv

            with open(final_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                businesses = list(reader)

            if not businesses:
                logger.warning("No data in final output")
                return

            print("\n" + "=" * 130)
            print("FINAL RESULTS - ENRICHED DATA SAMPLE")
            print("=" * 130 + "\n")

            # Print first 3 records
            for i, business in enumerate(businesses[:3], 1):
                print(f"{i}. {business.get('name', 'N/A')}")
                print(f"   Location: {business.get('location', 'N/A')}")
                print(f"   Category: {business.get('category', 'N/A')}")
                print(f"   Phone: {business.get('phone', 'N/A')}")
                print(f"   Website: {business.get('website', 'N/A')}")
                print(f"   Domain: {business.get('domain', 'N/A')}")
                print(f"   📧 Registrant Name: {business.get('registrant_name', 'N/A')}")
                print(f"   📧 Registrant Email: {business.get('registrant_email', 'N/A')}")
                print(f"   🔧 Tech Name: {business.get('tech_name', 'N/A')}")
                print(f"   🔧 Tech Email: {business.get('tech_email', 'N/A')}")
                print()

            # Statistics
            print("=" * 130)
            print("STATISTICS")
            print("=" * 130 + "\n")

            total = len(businesses)
            with_registrant_email = sum(1 for b in businesses if b.get('registrant_email'))
            with_tech_email = sum(1 for b in businesses if b.get('tech_email'))

            print(f"Total Businesses:          {total}")
            print(f"With Registrant Email:     {with_registrant_email} ({100*with_registrant_email/total:.1f}%)")
            print(f"With Tech Email:           {with_tech_email} ({100*with_tech_email/total:.1f}%)")

        except Exception as e:
            logger.error(f"Error printing summary: {e}")

    def run(self) -> None:
        """Execute full pipeline"""
        print("\n" + "=" * 130)
        print("LOCALSEARCH + WHOIS FULL PIPELINE")
        print("=" * 130)
        print("\nThis pipeline will:")
        print("  1. Scrape businesses from LocalSearch")
        print("  2. Enrich data with WHOIS contact information")
        print("\n⏳ Starting pipeline...\n")

        # Step 1: Scrape
        scraped_csv = self.step_1_scrape_businesses()

        if not scraped_csv or not Path(scraped_csv).exists():
            logger.error("Scraping failed or produced no output. Aborting pipeline.")
            return

        # Step 2: Enrich with WHOIS
        enriched_csv = self.step_2_enrich_with_whois(scraped_csv)

        if not enriched_csv or not Path(enriched_csv).exists():
            logger.error("WHOIS enrichment failed or produced no output.")
            return

        # Summary
        self.print_final_summary(enriched_csv)

        print("\n" + "=" * 130)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 130)
        print(f"\nOutput files:")
        print(f"  📄 Scraped data:     {scraped_csv}")
        print(f"  📊 Enriched data:    {enriched_csv}")
        print("\nYou can now:")
        print("  • Import the CSV into Excel/Google Sheets")
        print("  • Filter by category, location, or rating")
        print("  • Contact registrants using collected email addresses")
        print("  • Analyze business distribution and contacts")
        print("\n" + "=" * 130 + "\n")


def main():
    """Main execution"""
    pipeline = FullPipeline('config.json')
    pipeline.run()


if __name__ == '__main__':
    main()
