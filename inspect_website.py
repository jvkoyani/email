#!/usr/bin/env python3
"""
LocalSearch Website Inspector
Helps debug and understand the website structure for custom scraping.
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebsiteInspector:
    def __init__(self):
        self.base_url = "https://www.localsearch.com.au"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def inspect_homepage(self):
        """Inspect homepage structure"""
        logger.info("Inspecting homepage...")

        try:
            response = self.session.get(self.base_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            print("\n" + "="*60)
            print("HOMEPAGE INSPECTION")
            print("="*60)

            # Look for common elements
            self.find_elements(soup, "Categories", [
                ('a', {'class': lambda x: x and 'categor' in x.lower()}),
                ('a', {'class': lambda x: x and 'cat' in x.lower()}),
                ('a', {'class': lambda x: x and 'browse' in x.lower()})
            ])

            self.find_elements(soup, "Locations", [
                ('a', {'class': lambda x: x and 'location' in x.lower()}),
                ('a', {'class': lambda x: x and 'suburb' in x.lower()})
            ])

            self.find_elements(soup, "Search Form", [
                ('form', {}),
                ('input', {'type': 'text'}),
                ('button', {})
            ])

        except Exception as e:
            logger.error(f"Error inspecting homepage: {e}")

    def inspect_search_results(self, category: str = "", location: str = ""):
        """Inspect search results page structure"""
        logger.info(f"Inspecting search results for {category} in {location}...")

        try:
            url = f"{self.base_url}/search"
            params = {}
            if category:
                params['category'] = category
            if location:
                params['location'] = location

            response = self.session.get(url, params=params, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            print("\n" + "="*60)
            print(f"SEARCH RESULTS INSPECTION: {category} in {location}")
            print("="*60)

            # Inspect listings
            self.find_elements(soup, "Business Listings", [
                ('div', {'class': lambda x: x and 'listing' in x.lower()}),
                ('div', {'class': lambda x: x and 'result' in x.lower()}),
                ('article', {})
            ])

            # Inspect business name
            self.find_elements(soup, "Business Name", [
                ('h2', {}),
                ('h3', {}),
                ('span', {'class': lambda x: x and 'name' in x.lower()})
            ])

            # Inspect address
            self.find_elements(soup, "Address", [
                ('address', {}),
                ('div', {'class': lambda x: x and 'address' in x.lower()}),
                ('span', {'class': lambda x: x and 'address' in x.lower()})
            ])

            # Inspect phone
            self.find_elements(soup, "Phone", [
                ('a', {'href': lambda x: x and 'tel:' in x.lower()}),
                ('span', {'class': lambda x: x and 'phone' in x.lower()})
            ])

            # Inspect pagination
            self.find_elements(soup, "Pagination", [
                ('a', {'class': lambda x: x and 'next' in x.lower()}),
                ('a', {'class': lambda x: x and 'page' in x.lower()})
            ])

        except Exception as e:
            logger.error(f"Error inspecting search results: {e}")

    def find_elements(self, soup: BeautifulSoup, section: str, selectors: list):
        """Find and display elements matching selectors"""
        print(f"\n{section}:")
        print("-" * 40)

        found_any = False
        for tag, attrs in selectors:
            try:
                elements = soup.find_all(tag, attrs)
                if elements:
                    found_any = True
                    print(f"  Found {len(elements)} <{tag}> elements")

                    # Show first 3 examples
                    for i, elem in enumerate(elements[:3], 1):
                        class_name = elem.get('class', [])
                        id_name = elem.get('id', '')
                        href = elem.get('href', '')
                        text = elem.get_text(strip=True)[:50]

                        print(f"    [{i}] <{tag}>")
                        if class_name:
                            print(f"        class: {' '.join(class_name)}")
                        if id_name:
                            print(f"        id: {id_name}")
                        if href:
                            print(f"        href: {href}")
                        if text:
                            print(f"        text: {text}")
                        print()

            except Exception as e:
                pass

        if not found_any:
            print(f"  ❌ No elements found")

    def extract_sample_business(self, category: str = "", location: str = "") -> dict:
        """Extract a sample business to show available fields"""
        logger.info("Extracting sample business...")

        try:
            url = f"{self.base_url}/search"
            params = {}
            if category:
                params['category'] = category
            if location:
                params['location'] = location

            response = self.session.get(url, params=params, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            print("\n" + "="*60)
            print("SAMPLE BUSINESS EXTRACTION")
            print("="*60)

            # Find first listing
            listing = soup.find('div', class_=lambda x: x and 'listing' in x.lower())

            if listing:
                business = {}

                # Extract all text content
                business['full_text'] = listing.get_text(strip=True)[:200]

                # Extract all links
                links = listing.find_all('a')
                business['links_found'] = len(links)
                business['link_examples'] = []
                for link in links[:5]:
                    business['link_examples'].append({
                        'text': link.get_text(strip=True)[:50],
                        'href': link.get('href', '')
                    })

                # Extract all classes
                all_classes = set()
                for elem in listing.find_all():
                    classes = elem.get('class', [])
                    all_classes.update(classes)

                business['classes_found'] = sorted(list(all_classes))

                print("\nSample Business Details:")
                print(json.dumps(business, indent=2, default=str))

                return business
            else:
                print("No listings found on page")
                return {}

        except Exception as e:
            logger.error(f"Error extracting sample: {e}")
            return {}

    def generate_css_selector_guide(self):
        """Generate a guide for CSS selectors"""
        print("\n" + "="*60)
        print("CSS SELECTOR GUIDE FOR CUSTOMIZATION")
        print("="*60)

        guide = """
For customizing the scraper, you need to find the right CSS selectors:

1. USING BROWSER INSPECTOR:
   - Press F12 (or Ctrl+Shift+I) to open Developer Tools
   - Use the Inspector/Elements tab
   - Click the element selector button
   - Click on the element you want to scrape
   - Look at the HTML to find the class or id

2. COMMON SELECTOR PATTERNS:

   By Class: 'listing', 'business-item', 'result'
   By ID: 'business-123', 'item-456'
   By Tag: 'h2', 'address', 'span'

3. UPDATING THE SCRAPER:

   In localsearch_scraper.py, find extract_business_info() method:

   # Change this:
   listings = soup.find_all('div', class_=['listing', 'business-item'])

   # To match your findings:
   listings = soup.find_all('div', class_='your-class-name')

4. COMMON FIELDS TO EXTRACT:

   Business Name:
   - Usually in <h2>, <h3>, or <span class="name">
   - Update: name_elem = listing.find('h2')

   Address:
   - Usually in <address> or <div class="address">
   - Update: address_elem = listing.find('address')

   Phone:
   - Usually in <a href="tel:..."> or <span class="phone">
   - Update: phone_elem = listing.find('a', href=lambda x: x and 'tel:' in x)

   Website:
   - Usually in <a class="website"> or similar
   - Update: website_elem = listing.find('a', class_='website')

5. TESTING SELECTORS:

   >>> from bs4 import BeautifulSoup
   >>> soup = BeautifulSoup(html_content, 'html.parser')
   >>> elem = soup.find('div', class_='listing')
   >>> print(elem.get_text())  # See if it found the right element

6. COMMON ISSUES:

   Problem: Can't find listings
   Solution: Check if site uses JavaScript (try Selenium scraper)

   Problem: Found listings but can't extract fields
   Solution: Classes might be different, use inspector to find exact ones

   Problem: Getting None values
   Solution: Element selector might be wrong, check browser inspector
        """

        print(guide)

    def debug_mode(self):
        """Interactive debug mode"""
        print("\n" + "="*60)
        print("WEBSITE INSPECTOR - INTERACTIVE MODE")
        print("="*60)

        while True:
            print("\nOptions:")
            print("1. Inspect homepage")
            print("2. Inspect search results")
            print("3. Extract sample business")
            print("4. Show CSS selector guide")
            print("5. Exit")

            choice = input("\nSelect option (1-5): ").strip()

            if choice == '1':
                self.inspect_homepage()
            elif choice == '2':
                category = input("Category (or press Enter to skip): ").strip()
                location = input("Location (or press Enter to skip): ").strip()
                self.inspect_search_results(category, location)
            elif choice == '3':
                category = input("Category (or press Enter to skip): ").strip()
                location = input("Location (or press Enter to skip): ").strip()
                self.extract_sample_business(category, location)
            elif choice == '4':
                self.generate_css_selector_guide()
            elif choice == '5':
                print("Exiting...")
                break
            else:
                print("Invalid option")


def main():
    """Main execution"""
    inspector = WebsiteInspector()

    print("LocalSearch Website Inspector")
    print("=" * 60)
    print("\nThis tool helps you understand the website structure")
    print("to customize the scraper if needed.\n")

    # Run automated inspection
    inspector.inspect_homepage()
    inspector.inspect_search_results("Restaurants", "Sydney")
    inspector.extract_sample_business("Restaurants", "Sydney")
    inspector.generate_css_selector_guide()

    # Ask if user wants interactive mode
    response = input("\nRun interactive mode? (y/n): ").strip().lower()
    if response == 'y':
        inspector.debug_mode()


if __name__ == '__main__':
    main()
