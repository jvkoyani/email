#!/usr/bin/env python3
"""
LocalSearch.com.au Business Scraper - Selenium Version
For JavaScript-heavy sites. Handles dynamic content loading.
"""

import csv
import json
import time
import logging
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocalSearchSeleniumScraper:
    def __init__(self, headless=True):
        """Initialize Selenium WebDriver"""
        self.base_url = "https://www.localsearch.com.au"
        self.businesses = []
        self.driver = None
        self.headless = headless
        self.wait = None

    def init_driver(self):
        """Initialize Chrome WebDriver"""
        try:
            options = uc.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')

            self.driver = uc.Chrome(options=options, version_main=None)
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing WebDriver: {e}")
            raise

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def search_businesses(self, category: str = "", location: str = "") -> List[Dict]:
        """Search for businesses with filters"""
        businesses = []
        page = 1
        base_search_url = f"{self.base_url}/search"

        while page <= 50:  # Limit pages
            try:
                # Build search URL
                url = base_search_url
                params = []
                if category:
                    params.append(f"category={category}")
                if location:
                    params.append(f"location={location}")
                params.append(f"page={page}")

                if params:
                    url += "?" + "&".join(params)

                logger.info(f"Navigating to: {url}")
                self.driver.get(url)

                # Wait for listings to load
                try:
                    self.wait.until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "listing"))
                    )
                except TimeoutException:
                    logger.warning("Timeout waiting for listings")
                    break

                time.sleep(2)  # Additional wait for dynamic content

                # Scroll to load lazy images
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                # Extract all listings on current page
                listings = self.driver.find_elements(By.CLASS_NAME, "listing")

                if not listings:
                    logger.info(f"No listings found on page {page}")
                    break

                logger.info(f"Found {len(listings)} listings on page {page}")

                for listing in listings:
                    try:
                        business = self.extract_business_from_element(listing, category, location)
                        if business:
                            businesses.append(business)
                    except Exception as e:
                        logger.error(f"Error extracting business: {e}")

                # Check if next page exists
                try:
                    next_button = self.driver.find_element(By.CLASS_NAME, "next-page")
                    if not next_button.is_enabled():
                        break
                except NoSuchElementException:
                    logger.info("No next page button found")
                    break

                page += 1
                time.sleep(2)  # Rate limiting

            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                break

        return businesses

    def extract_business_from_element(self, element, category: str, location: str) -> Dict:
        """Extract business information from Selenium element"""
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

        try:
            # Extract name
            try:
                name_elem = element.find_element(By.CLASS_NAME, "business-name")
                business['name'] = name_elem.text.strip()
            except NoSuchElementException:
                name_elem = element.find_element(By.TAG_NAME, "h2")
                business['name'] = name_elem.text.strip()

            # Extract address
            try:
                address_elem = element.find_element(By.CLASS_NAME, "address")
                business['address'] = address_elem.text.strip()
            except NoSuchElementException:
                pass

            # Extract phone
            try:
                phone_elem = element.find_element(By.CLASS_NAME, "phone")
                business['phone'] = phone_elem.text.strip()
            except NoSuchElementException:
                pass

            # Extract website
            try:
                website_elem = element.find_element(By.CLASS_NAME, "website")
                business['website'] = website_elem.get_attribute('href')
            except NoSuchElementException:
                pass

            # Extract email
            try:
                email_elem = element.find_element(By.CLASS_NAME, "email")
                business['email'] = email_elem.text.strip()
            except NoSuchElementException:
                pass

            # Extract rating
            try:
                rating_elem = element.find_element(By.CLASS_NAME, "rating")
                business['rating'] = rating_elem.text.strip()
            except NoSuchElementException:
                pass

            # Extract reviews
            try:
                reviews_elem = element.find_element(By.CLASS_NAME, "reviews")
                business['reviews'] = reviews_elem.text.strip()
            except NoSuchElementException:
                pass

            # Extract hours
            try:
                hours_elem = element.find_element(By.CLASS_NAME, "hours")
                business['hours'] = hours_elem.text.strip()
            except NoSuchElementException:
                pass

            # Extract description
            try:
                desc_elem = element.find_element(By.CLASS_NAME, "description")
                business['description'] = desc_elem.text.strip()
            except NoSuchElementException:
                pass

            if business['name']:
                return business

        except Exception as e:
            logger.error(f"Error extracting business element: {e}")

        return None

    def get_categories(self) -> List[str]:
        """Fetch all categories from the site"""
        try:
            logger.info("Fetching categories...")
            self.driver.get(self.base_url)
            time.sleep(3)

            categories = []
            try:
                category_elements = self.driver.find_elements(By.CLASS_NAME, "category-link")
                for elem in category_elements:
                    text = elem.text.strip()
                    if text:
                        categories.append(text)
            except:
                logger.warning("Could not find category elements")

            return list(set(categories))  # Remove duplicates
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []

    def get_locations(self) -> List[str]:
        """Fetch all locations from the site"""
        try:
            logger.info("Fetching locations...")
            self.driver.get(f"{self.base_url}/locations")
            time.sleep(3)

            locations = []
            try:
                location_elements = self.driver.find_elements(By.CLASS_NAME, "location-link")
                for elem in location_elements:
                    text = elem.text.strip()
                    if text:
                        locations.append(text)
            except:
                logger.warning("Could not find location elements")

            return list(set(locations))  # Remove duplicates
        except Exception as e:
            logger.error(f"Error fetching locations: {e}")
            return []

    def scrape_all(self):
        """Scrape all businesses from all categories and locations"""
        try:
            self.init_driver()

            # Get categories and locations
            categories = self.get_categories()
            locations = self.get_locations()

            if not categories or not locations:
                # Fallback to popular combinations
                categories = ['Restaurants', 'Cafes', 'Medical', 'Plumbing', 'Automotive']
                locations = ['Sydney', 'Melbourne', 'Brisbane']

            logger.info(f"Found {len(categories)} categories and {len(locations)} locations")

            # Scrape each combination
            total = len(categories) * len(locations)
            count = 0

            for category in categories:
                for location in locations:
                    count += 1
                    logger.info(f"Progress: {count}/{total} - Category: {category}, Location: {location}")

                    businesses = self.search_businesses(category=category, location=location)
                    self.businesses.extend(businesses)
                    time.sleep(2)

        except Exception as e:
            logger.error(f"Error in scrape_all: {e}")
        finally:
            self.close_driver()

    def scrape_specific(self, category: str = "", location: str = ""):
        """Scrape specific category and location"""
        try:
            self.init_driver()
            businesses = self.search_businesses(category=category, location=location)
            self.businesses.extend(businesses)
        except Exception as e:
            logger.error(f"Error scraping: {e}")
        finally:
            self.close_driver()

    def save_to_csv(self, filename: str = 'localsearch_businesses.csv'):
        """Save to CSV"""
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
            logger.error(f"Error saving CSV: {e}")

    def save_to_json(self, filename: str = 'localsearch_businesses.json'):
        """Save to JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(self.businesses, jsonfile, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self.businesses)} businesses to {filename}")
        except Exception as e:
            logger.error(f"Error saving JSON: {e}")


def main():
    """Main execution"""
    scraper = LocalSearchSeleniumScraper(headless=True)

    # Scrape specific category and location
    scraper.scrape_specific(category="Restaurants", location="Sydney")

    # Or scrape all
    # scraper.scrape_all()

    # Save results
    scraper.save_to_csv('localsearch_businesses.csv')
    scraper.save_to_json('localsearch_businesses.json')

    logger.info(f"Total businesses scraped: {len(scraper.businesses)}")


if __name__ == '__main__':
    main()
