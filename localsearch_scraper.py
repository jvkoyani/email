#!/usr/bin/env python3
"""
LocalSearch.com.au Business Scraper
Extracts business information organized by location and category.
Outputs to CSV format.
"""

import requests
import csv
import json
import time
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from typing import List, Dict, Set
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocalSearchScraper:
    def __init__(self):
        self.base_url = "https://www.localsearch.com.au"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.businesses = []
        self.scraped_urls = set()

    def get_categories(self) -> List[str]:
        """Fetch all business categories from LocalSearch"""
        logger.info("Fetching categories...")
        categories = []

        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for category links - adjust selectors based on actual HTML structure
            category_links = soup.find_all('a', class_=['category', 'cat-link', 'browse-category'])

            for link in category_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if href and text:
                    categories.append({
                        'name': text,
                        'url': urljoin(self.base_url, href)
                    })

            logger.info(f"Found {len(categories)} categories")
            return categories
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []

    def get_locations(self) -> List[str]:
        """Fetch all locations from LocalSearch"""
        logger.info("Fetching locations...")
        locations = []

        try:
            response = self.session.get(f"{self.base_url}/locations", timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for location links
            location_links = soup.find_all('a', class_=['location', 'loc-link', 'suburb'])

            for link in location_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if href and text:
                    locations.append({
                        'name': text,
                        'url': urljoin(self.base_url, href)
                    })

            logger.info(f"Found {len(locations)} locations")
            return locations
        except Exception as e:
            logger.error(f"Error fetching locations: {e}")
            return []

    def search_businesses(self, query: str = "", category: str = "", location: str = "") -> List[Dict]:
        """Search for businesses with optional filters"""
        params = {}
        if query:
            params['q'] = query
        if category:
            params['category'] = category
        if location:
            params['location'] = location

        url = f"{self.base_url}/search"
        businesses = []
        page = 1

        while page <= 100:  # Max 100 pages
            try:
                params['page'] = page
                logger.info(f"Scraping page {page} - Category: {category}, Location: {location}")

                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract business listings
                listings = soup.find_all('div', class_=['listing', 'business-item', 'result'])

                if not listings:
                    logger.info(f"No more listings found on page {page}")
                    break

                for listing in listings:
                    business = self.extract_business_info(listing, category, location)
                    if business:
                        businesses.append(business)

                # Check for next page
                next_button = soup.find('a', class_=['next', 'next-page'])
                if not next_button:
                    logger.info("No next page found")
                    break

                page += 1
                time.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                break

        return businesses

    def extract_business_info(self, listing, category: str, location: str) -> Dict:
        """Extract business information from a listing element"""
        try:
            business = {
                'name': '',
                'address': '',
                'phone': '',
                'website': '',
                'email': '',
                'category': category,
                'location': location,
                'rating': '',
                'reviews': '',
                'hours': '',
                'description': ''
            }

            # Extract name
            name_elem = listing.find('h2', class_=['business-name', 'title'])
            if name_elem:
                business['name'] = name_elem.get_text(strip=True)

            # Extract address
            address_elem = listing.find('address')
            if address_elem:
                business['address'] = address_elem.get_text(strip=True)
            else:
                addr = listing.find('span', class_=['address', 'location-address'])
                if addr:
                    business['address'] = addr.get_text(strip=True)

            # Extract phone
            phone_elem = listing.find('a', class_=['phone', 'tel']) or \
                        listing.find('span', class_=['phone', 'telephone'])
            if phone_elem:
                business['phone'] = phone_elem.get_text(strip=True)

            # Extract website/URL
            website_elem = listing.find('a', class_=['website', 'url', 'business-url'])
            if website_elem:
                business['website'] = website_elem.get('href', '')

            # Extract email
            email_elem = listing.find('a', class_=['email']) or \
                        listing.find('span', class_=['email'])
            if email_elem:
                business['email'] = email_elem.get_text(strip=True)

            # Extract rating
            rating_elem = listing.find('span', class_=['rating', 'stars'])
            if rating_elem:
                business['rating'] = rating_elem.get_text(strip=True)

            # Extract review count
            reviews_elem = listing.find('span', class_=['reviews', 'review-count'])
            if reviews_elem:
                business['reviews'] = reviews_elem.get_text(strip=True)

            # Extract hours
            hours_elem = listing.find('div', class_=['hours', 'trading-hours'])
            if hours_elem:
                business['hours'] = hours_elem.get_text(strip=True)

            # Extract description
            desc_elem = listing.find('p', class_=['description', 'snippet'])
            if desc_elem:
                business['description'] = desc_elem.get_text(strip=True)

            # Only add if we have at least a name
            if business['name']:
                return business

        except Exception as e:
            logger.error(f"Error extracting business info: {e}")

        return None

    def scrape_all(self):
        """Scrape all businesses from all categories and locations"""
        logger.info("Starting comprehensive scrape...")

        # Get all categories
        categories = self.get_categories()
        locations = self.get_locations()

        if not categories or not locations:
            # Fallback: scrape by popular combinations
            logger.info("Using fallback: scraping by popular categories and locations")
            self.scrape_fallback()
            return

        # Scrape each category-location combination
        total = len(categories) * len(locations)
        count = 0

        for category in categories:
            for location in locations:
                count += 1
                logger.info(f"Progress: {count}/{total}")

                businesses = self.search_businesses(
                    category=category['name'],
                    location=location['name']
                )
                self.businesses.extend(businesses)
                time.sleep(1)

    def scrape_fallback(self):
        """Fallback scraping method using direct search"""
        popular_categories = [
            'Accounting', 'Automotive', 'Beauty', 'Cafes', 'Construction',
            'Dental', 'Education', 'Fitness', 'Florists', 'Hardware',
            'Health', 'Insurance', 'Legal', 'Medical', 'Plumbing',
            'Real Estate', 'Restaurants', 'Retail', 'Services', 'Travel'
        ]

        popular_locations = [
            'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide',
            'Gold Coast', 'Newcastle', 'Canberra', 'Hobart', 'Darwin'
        ]

        total = len(popular_categories) * len(popular_locations)
        count = 0

        for category in popular_categories:
            for location in popular_locations:
                count += 1
                logger.info(f"Progress: {count}/{total}")

                businesses = self.search_businesses(
                    category=category,
                    location=location
                )
                self.businesses.extend(businesses)
                time.sleep(1)

    def save_to_csv(self, filename: str = 'localsearch_businesses.csv'):
        """Save scraped businesses to CSV file"""
        if not self.businesses:
            logger.warning("No businesses to save")
            return

        try:
            fieldnames = [
                'name', 'address', 'phone', 'website', 'email',
                'category', 'location', 'rating', 'reviews', 'hours', 'description'
            ]

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.businesses)

            logger.info(f"Saved {len(self.businesses)} businesses to {filename}")

        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")

    def save_to_json(self, filename: str = 'localsearch_businesses.json'):
        """Save scraped businesses to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(self.businesses, jsonfile, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self.businesses)} businesses to {filename}")

        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")


def main():
    """Main execution"""
    scraper = LocalSearchScraper()

    # Option 1: Scrape all businesses
    # scraper.scrape_all()

    # Option 2: Scrape specific category and location
    logger.info("Scraping LocalSearch businesses...")
    businesses = scraper.search_businesses(
        category="",  # Leave empty to get all, or specify like "Restaurants"
        location=""   # Leave empty to get all, or specify like "Sydney"
    )
    scraper.businesses.extend(businesses)

    # Save results
    scraper.save_to_csv('localsearch_businesses.csv')
    scraper.save_to_json('localsearch_businesses.json')

    logger.info(f"Scraping complete! Found {len(scraper.businesses)} businesses")


if __name__ == '__main__':
    main()
