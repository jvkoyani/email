#!/usr/bin/env python3
"""
LocalSearch Scraper Runner
Main entry point with configuration file support and advanced features.
"""

import json
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Import scrapers
from localsearch_scraper import LocalSearchScraper
from localsearch_scraper_selenium import LocalSearchSeleniumScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScraperRunner:
    def __init__(self, config_file: str = 'config.json'):
        """Initialize runner with configuration"""
        self.config = self.load_config(config_file)
        self.scraper = None
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        self.stats = {
            'total_businesses': 0,
            'start_time': None,
            'end_time': None,
            'errors': []
        }

    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_file}")
            logger.info("Using default configuration")
            return self.get_default_config()
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file: {config_file}")
            return self.get_default_config()

    @staticmethod
    def get_default_config() -> Dict:
        """Return default configuration"""
        return {
            'scraper': {'type': 'beautifulsoup'},
            'search': {'categories': [], 'locations': []},
            'output': {
                'csv_filename': 'localsearch_businesses.csv',
                'json_filename': 'localsearch_businesses.json',
                'save_both_formats': True
            },
            'scraping': {
                'max_pages_per_search': 100,
                'delay_between_requests': 1,
                'delay_between_searches': 2,
                'timeout_seconds': 10,
                'retries': 3
            },
            'selenium': {'headless': True, 'wait_timeout': 20},
            'logging': {'level': 'INFO'}
        }

    def initialize_scraper(self):
        """Initialize appropriate scraper based on configuration"""
        scraper_type = self.config['scraper']['type'].lower()

        if scraper_type == 'selenium':
            logger.info("Initializing Selenium scraper...")
            self.scraper = LocalSearchSeleniumScraper(
                headless=self.config['selenium'].get('headless', True)
            )
        else:
            logger.info("Initializing BeautifulSoup scraper...")
            self.scraper = LocalSearchScraper()

    def get_search_combinations(self) -> List[Dict]:
        """Get category-location combinations to scrape"""
        categories = self.config['search'].get('categories', [])
        locations = self.config['search'].get('locations', [])

        if not categories or not locations:
            # Fallback to popular combinations
            categories = categories or [
                'Accounting', 'Automotive', 'Beauty', 'Cafes', 'Construction',
                'Dental', 'Education', 'Fitness', 'Health', 'Plumbing'
            ]
            locations = locations or [
                'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'
            ]

        combinations = []
        for category in categories:
            for location in locations:
                combinations.append({
                    'category': category,
                    'location': location
                })

        logger.info(f"Will scrape {len(combinations)} category-location combinations")
        return combinations

    def run_scrape(self):
        """Execute scraping"""
        self.stats['start_time'] = datetime.now()

        try:
            self.initialize_scraper()

            # Get combinations
            combinations = self.get_search_combinations()

            # Scrape each combination
            total = len(combinations)
            for idx, combo in enumerate(combinations, 1):
                logger.info(f"[{idx}/{total}] Scraping {combo['category']} in {combo['location']}...")

                try:
                    if isinstance(self.scraper, LocalSearchSeleniumScraper):
                        businesses = self.scraper.search_businesses(
                            category=combo['category'],
                            location=combo['location']
                        )
                    else:
                        businesses = self.scraper.search_businesses(
                            category=combo['category'],
                            location=combo['location']
                        )

                    if businesses:
                        self.scraper.businesses.extend(businesses)
                        logger.info(f"Found {len(businesses)} businesses")
                    else:
                        logger.warning("No businesses found for this combination")

                except Exception as e:
                    logger.error(f"Error scraping {combo['category']}/{combo['location']}: {e}")
                    self.stats['errors'].append({
                        'combination': combo,
                        'error': str(e)
                    })

            # Close Selenium driver if used
            if isinstance(self.scraper, LocalSearchSeleniumScraper):
                self.scraper.close_driver()

            self.stats['total_businesses'] = len(self.scraper.businesses)

        except Exception as e:
            logger.error(f"Fatal error during scraping: {e}")
            self.stats['errors'].append({'error': str(e)})

        self.stats['end_time'] = datetime.now()

    def save_results(self):
        """Save scraping results"""
        if not self.scraper or not self.scraper.businesses:
            logger.warning("No businesses to save")
            return

        # Generate timestamp for filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:
            # Save CSV
            csv_path = self.results_dir / f"{self.config['output']['csv_filename'].replace('.csv', '')}_{timestamp}.csv"
            self.scraper.save_to_csv(str(csv_path))

            # Save JSON
            if self.config['output'].get('save_both_formats', True):
                json_path = self.results_dir / f"{self.config['output']['json_filename'].replace('.json', '')}_{timestamp}.json"
                self.scraper.save_to_json(str(json_path))

            # Save stats
            self.save_stats(timestamp)

        except Exception as e:
            logger.error(f"Error saving results: {e}")

    def save_stats(self, timestamp: str):
        """Save scraping statistics"""
        stats_path = self.results_dir / f"stats_{timestamp}.json"

        stats = {
            'timestamp': timestamp,
            'total_businesses': self.stats['total_businesses'],
            'start_time': str(self.stats['start_time']),
            'end_time': str(self.stats['end_time']),
            'duration_seconds': (self.stats['end_time'] - self.stats['start_time']).total_seconds() if self.stats['end_time'] and self.stats['start_time'] else None,
            'errors_count': len(self.stats['errors']),
            'errors': self.stats['errors'],
            'config_used': {
                'scraper_type': self.config['scraper']['type'],
                'categories': self.config['search'].get('categories'),
                'locations': self.config['search'].get('locations')
            }
        }

        try:
            with open(stats_path, 'w') as f:
                json.dump(stats, f, indent=2)
            logger.info(f"Statistics saved to {stats_path}")
        except Exception as e:
            logger.error(f"Error saving statistics: {e}")

    def print_summary(self):
        """Print scraping summary"""
        logger.info("=" * 60)
        logger.info("SCRAPING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total businesses found: {self.stats['total_businesses']}")
        logger.info(f"Start time: {self.stats['start_time']}")
        logger.info(f"End time: {self.stats['end_time']}")

        if self.stats['end_time'] and self.stats['start_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            logger.info(f"Duration: {duration:.2f} seconds")

        if self.stats['errors']:
            logger.warning(f"Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                logger.warning(f"  - {error}")

        logger.info(f"Results saved to: {self.results_dir}")
        logger.info("=" * 60)

    def run(self):
        """Main execution"""
        logger.info("Starting LocalSearch Scraper...")
        self.run_scrape()
        self.save_results()
        self.print_summary()


def main():
    """Entry point"""
    runner = ScraperRunner('config.json')
    runner.run()


if __name__ == '__main__':
    main()
