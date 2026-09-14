#!/usr/bin/env python3
"""
WHOIS Data Enricher
Adds Registrant and Tech Contact information to business CSV from WHOIS lookups.
"""

import csv
import time
import logging
import re
import socket
from urllib.parse import urlparse
from typing import Dict, List, Optional
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WHOISEnricher:
    def __init__(self, whois_server: str = "whois.auda.org.au", port: int = 43):
        """Initialize WHOIS enricher"""
        self.whois_server = whois_server
        self.port = port
        self.whois_cache = {}
        self.rate_limit_delay = 1  # seconds between requests

    def extract_domain_from_url(self, url: str) -> Optional[str]:
        """Extract domain name from URL"""
        if not url or not url.strip():
            return None

        try:
            # Remove protocol if present
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            parsed = urlparse(url)
            domain = parsed.netloc

            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]

            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]

            return domain if domain else None

        except Exception as e:
            logger.error(f"Error extracting domain from URL '{url}': {e}")
            return None

    def query_whois_socket(self, domain: str) -> Optional[str]:
        """Query WHOIS server using socket connection"""
        try:
            logger.info(f"Querying WHOIS for: {domain}")

            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.whois_server, self.port))

            # Send query
            sock.send(f"{domain}\r\n".encode())

            # Receive response
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data

            sock.close()
            return response.decode('utf-8', errors='ignore')

        except socket.timeout:
            logger.error(f"WHOIS query timeout for {domain}")
            return None
        except ConnectionRefusedError:
            logger.error(f"Connection refused for WHOIS server {self.whois_server}")
            return None
        except Exception as e:
            logger.error(f"Error querying WHOIS for {domain}: {e}")
            return None

    def query_whois_http(self, domain: str) -> Optional[str]:
        """Query WHOIS via HTTP API (fallback method)"""
        try:
            # Try WHOIS.com API
            url = f"https://www.whois.com/whois/{domain}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.text

            # Try auda.org.au web interface
            url = f"https://whois.auda.org.au/?domain={domain}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.text

            return None

        except Exception as e:
            logger.error(f"Error in HTTP WHOIS query for {domain}: {e}")
            return None

    def parse_whois_response(self, whois_text: str) -> Dict[str, str]:
        """Parse WHOIS response to extract contact information"""
        data = {
            'registrant_name': '',
            'registrant_email': '',
            'tech_name': '',
            'tech_email': ''
        }

        if not whois_text:
            return data

        lines = whois_text.split('\n')

        current_section = None
        registrant_data = {}
        tech_data = {}

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Identify sections
            if 'registrant' in line.lower() and ':' in line:
                current_section = 'registrant'
            elif 'tech' in line.lower() and ('contact' in line.lower() or 'contact' in lines[lines.index(line) - 1].lower()):
                current_section = 'tech'

            # Parse contact names and emails
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                # Registrant information
                if 'registrant' in key or (current_section == 'registrant' and key):
                    if 'name' in key and not registrant_data.get('name'):
                        registrant_data['name'] = value
                    elif 'email' in key and not registrant_data.get('email'):
                        registrant_data['email'] = value

                # Tech contact information
                elif 'tech' in key or (current_section == 'tech' and key):
                    if 'name' in key and not tech_data.get('name'):
                        tech_data['name'] = value
                    elif 'email' in key and not tech_data.get('email'):
                        tech_data['email'] = value

        # Extract using regex patterns as fallback
        if not registrant_data.get('name'):
            match = re.search(r'Registrant:\s*(.+?)(?:\n|$)', whois_text, re.IGNORECASE)
            if match:
                registrant_data['name'] = match.group(1).strip()

        if not registrant_data.get('email'):
            match = re.search(r'Registrant.*?Email:\s*(.+?)(?:\n|$)', whois_text, re.IGNORECASE)
            if match:
                registrant_data['email'] = match.group(1).strip()

        if not tech_data.get('name'):
            match = re.search(r'Tech.*?Name:\s*(.+?)(?:\n|$)', whois_text, re.IGNORECASE)
            if match:
                tech_data['name'] = match.group(1).strip()

        if not tech_data.get('email'):
            match = re.search(r'Tech.*?Email:\s*(.+?)(?:\n|$)', whois_text, re.IGNORECASE)
            if match:
                tech_data['email'] = match.group(1).strip()

        # Populate return data
        data['registrant_name'] = registrant_data.get('name', '')
        data['registrant_email'] = registrant_data.get('email', '')
        data['tech_name'] = tech_data.get('name', '')
        data['tech_email'] = tech_data.get('email', '')

        return data

    def lookup_domain(self, domain: str) -> Dict[str, str]:
        """Look up a domain in WHOIS"""
        if not domain:
            return {
                'registrant_name': '',
                'registrant_email': '',
                'tech_name': '',
                'tech_email': ''
            }

        # Check cache
        if domain in self.whois_cache:
            logger.info(f"Using cached WHOIS data for {domain}")
            return self.whois_cache[domain]

        # Query WHOIS
        whois_response = self.query_whois_socket(domain)

        # Fallback to HTTP if socket fails
        if not whois_response:
            logger.warning(f"Socket query failed for {domain}, trying HTTP fallback...")
            whois_response = self.query_whois_http(domain)

        # Parse response
        contact_data = self.parse_whois_response(whois_response)

        # Cache result
        self.whois_cache[domain] = contact_data

        # Rate limiting
        time.sleep(self.rate_limit_delay)

        return contact_data

    def enrich_csv(self, input_csv: str, output_csv: str) -> None:
        """Enrich CSV with WHOIS contact information"""
        try:
            # Read input CSV
            businesses = []
            with open(input_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                businesses = list(reader)

            logger.info(f"Loaded {len(businesses)} businesses from {input_csv}")

            # Add WHOIS data to each business
            total = len(businesses)
            for idx, business in enumerate(businesses, 1):
                logger.info(f"Processing {idx}/{total}: {business.get('name', 'Unknown')}")

                # Extract domain
                website = business.get('website', '')
                domain = self.extract_domain_from_url(website)

                if domain:
                    # Lookup WHOIS
                    contact_data = self.lookup_domain(domain)

                    # Add to business record
                    business['domain'] = domain
                    business['registrant_name'] = contact_data.get('registrant_name', '')
                    business['registrant_email'] = contact_data.get('registrant_email', '')
                    business['tech_name'] = contact_data.get('tech_name', '')
                    business['tech_email'] = contact_data.get('tech_email', '')
                else:
                    business['domain'] = ''
                    business['registrant_name'] = ''
                    business['registrant_email'] = ''
                    business['tech_name'] = ''
                    business['tech_email'] = ''

            # Write output CSV
            if businesses:
                fieldnames = list(businesses[0].keys())

                with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(businesses)

                logger.info(f"Enriched data saved to {output_csv}")
                print(f"\n✅ Successfully enriched {len(businesses)} businesses!")
                print(f"📁 Output file: {output_csv}")

        except FileNotFoundError:
            logger.error(f"Input file not found: {input_csv}")
        except Exception as e:
            logger.error(f"Error enriching CSV: {e}")

    def print_sample(self, csv_file: str) -> None:
        """Print sample of enriched data"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                businesses = list(reader)

            if not businesses:
                print("No data found")
                return

            print("\n" + "=" * 150)
            print("SAMPLE: First 3 Enriched Records")
            print("=" * 150 + "\n")

            for i, business in enumerate(businesses[:3], 1):
                print(f"{i}. {business.get('name', 'N/A')}")
                print(f"   Website: {business.get('website', 'N/A')}")
                print(f"   Domain: {business.get('domain', 'N/A')}")
                print(f"   📧 Registrant Name: {business.get('registrant_name', 'N/A')}")
                print(f"   📧 Registrant Email: {business.get('registrant_email', 'N/A')}")
                print(f"   🔧 Tech Name: {business.get('tech_name', 'N/A')}")
                print(f"   🔧 Tech Email: {business.get('tech_email', 'N/A')}")
                print()

        except Exception as e:
            logger.error(f"Error printing sample: {e}")


def main():
    """Main execution"""
    import sys

    # File names
    input_csv = 'brisbane_air_conditioning_sample.csv'
    output_csv = 'brisbane_air_conditioning_with_whois.csv'

    # Check if input file exists
    import os
    if not os.path.exists(input_csv):
        print(f"❌ Input file not found: {input_csv}")
        print("\nUsage:")
        print("  python whois_enricher.py <input_csv> [output_csv]")
        print("\nExample:")
        print("  python whois_enricher.py localsearch_businesses.csv localsearch_with_whois.csv")
        sys.exit(1)

    # Override with command line arguments if provided
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
    if len(sys.argv) > 2:
        output_csv = sys.argv[2]

    print("\n" + "=" * 150)
    print("WHOIS CONTACT INFORMATION ENRICHER")
    print("=" * 150)
    print(f"\nInput CSV:  {input_csv}")
    print(f"Output CSV: {output_csv}")
    print("\nThis will add the following columns:")
    print("  • domain")
    print("  • registrant_name")
    print("  • registrant_email")
    print("  • tech_name")
    print("  • tech_email")
    print("\n⏳ Processing (may take 1-2 minutes per 100 businesses)...\n")

    # Enrich CSV
    enricher = WHOISEnricher()
    enricher.enrich_csv(input_csv, output_csv)

    # Print sample
    enricher.print_sample(output_csv)

    print("=" * 150)
    print("✅ ENRICHMENT COMPLETE!")
    print("=" * 150)


if __name__ == '__main__':
    main()
