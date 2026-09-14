# LocalSearch.com.au Business Scraper

A comprehensive Python web scraper to extract business information from LocalSearch.com.au organized by location and category. Outputs data to CSV and JSON formats.

## Features

- ✅ Scrape business listings by category and location
- ✅ Extract comprehensive business details:
  - Business name
  - Address
  - Phone number
  - Website URL
  - Email
  - Category
  - Location
  - Rating
  - Number of reviews
  - Trading hours
  - Business description
- ✅ Multiple scraper implementations:
  - **requests + BeautifulSoup** - Fast, lightweight (for static sites)
  - **Selenium** - For JavaScript-heavy dynamic sites
- ✅ Output formats: CSV and JSON
- ✅ Rate limiting to be respectful to server
- ✅ Comprehensive error handling and logging

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the scrapers** to your project directory

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **For Selenium version (if using):**
   - Chrome browser must be installed
   - ChromeDriver will be automatically downloaded by undetected-chromedriver

## Usage

### Option 1: BeautifulSoup Scraper (Recommended)

**Fast and lightweight - best for initial exploration:**

```bash
python localsearch_scraper.py
```

#### Customize in the script:

Edit `main()` function to specify category and location:

```python
# Scrape specific category and location
businesses = scraper.search_businesses(
    category="Restaurants",  # or "" for all
    location="Sydney"        # or "" for all
)

# Or scrape everything
scraper.scrape_all()
```

#### Available categories (examples):
- Accounting
- Automotive
- Beauty
- Cafes
- Construction
- Dental
- Education
- Fitness
- Florists
- Hardware
- Health
- Insurance
- Legal
- Medical
- Plumbing
- Real Estate
- Restaurants
- Retail
- Services
- Travel

#### Available locations (examples):
- Sydney
- Melbourne
- Brisbane
- Perth
- Adelaide
- Gold Coast
- Newcastle
- Canberra
- Hobart
- Darwin

### Option 2: Selenium Scraper (For JavaScript sites)

**For sites with heavy JavaScript and dynamic content:**

```bash
python localsearch_scraper_selenium.py
```

#### Customize:

```python
scraper = LocalSearchSeleniumScraper(headless=True)

# Scrape specific category/location
scraper.scrape_specific(category="Restaurants", location="Sydney")

# Or scrape all
scraper.scrape_all()

# Save results
scraper.save_to_csv('localsearch_businesses.csv')
scraper.save_to_json('localsearch_businesses.json')
```

## Output Files

### CSV Format
**File:** `localsearch_businesses.csv`

Contains columns:
- `name` - Business name
- `address` - Full address
- `phone` - Phone number
- `website` - Website URL
- `email` - Email address
- `category` - Business category
- `location` - Location/suburb
- `rating` - Star rating (if available)
- `reviews` - Number of reviews
- `hours` - Trading hours
- `description` - Business description/snippet

Example:
```csv
name,address,phone,website,email,category,location,rating,reviews,hours,description
Joe's Pizza,123 Main St Sydney NSW 2000,(02) 1234 5678,https://joespizza.com.au,info@joespizza.com,Restaurants,Sydney,4.5,127,Mon-Fri 10am-10pm,Authentic Italian pizza
```

### JSON Format
**File:** `localsearch_businesses.json`

```json
[
  {
    "name": "Joe's Pizza",
    "address": "123 Main St Sydney NSW 2000",
    "phone": "(02) 1234 5678",
    "website": "https://joespizza.com.au",
    "email": "info@joespizza.com",
    "category": "Restaurants",
    "location": "Sydney",
    "rating": "4.5",
    "reviews": "127",
    "hours": "Mon-Fri 10am-10pm",
    "description": "Authentic Italian pizza"
  }
]
```

## Advanced Usage

### Scraping Multiple Categories

```python
from localsearch_scraper import LocalSearchScraper

scraper = LocalSearchScraper()

categories = ['Restaurants', 'Cafes', 'Takeaway']
locations = ['Sydney', 'Melbourne']

for category in categories:
    for location in locations:
        print(f"Scraping {category} in {location}...")
        businesses = scraper.search_businesses(
            category=category,
            location=location
        )
        scraper.businesses.extend(businesses)

scraper.save_to_csv('results.csv')
```

### Filtering Results

```python
# Load and filter CSV
import pandas as pd

df = pd.read_csv('localsearch_businesses.csv')

# Filter by category
restaurants = df[df['category'] == 'Restaurants']

# Filter by rating (if available)
highly_rated = df[df['rating'] >= 4.0]

# Filter by location
sydney_businesses = df[df['location'] == 'Sydney']

# Save filtered results
restaurants.to_csv('restaurants_only.csv', index=False)
```

## Troubleshooting

### Issue: "No listings found"

**Solution:** 
- The site structure may have changed. You may need to inspect the HTML and update the CSS selectors in the scraper
- Check the website directly to ensure listings are available for your search

### Issue: Selenium scraper is slow

**Solution:**
- The site may have JavaScript that's slow to load
- Increase wait times in the code: `WebDriverWait(self.driver, 30)` (increase from 20)
- Run with `headless=True` (already default)

### Issue: Getting blocked/429 errors

**Solution:**
- Reduce scraping speed by increasing `time.sleep()` delays
- Add delays between requests:
  ```python
  time.sleep(2)  # Sleep 2 seconds between requests
  ```

### Issue: SSL certificate errors

**Solution:**
- This is an environment issue. Try:
  ```bash
  pip install --upgrade certifi
  ```

### Issue: Chrome/ChromeDriver issues

**Solution:**
- Undetected ChromeDriver should handle most issues
- If it fails, manually install ChromeDriver matching your Chrome version
- Or switch to the BeautifulSoup version

## Performance Tips

1. **For large scrapes:** Use the BeautifulSoup scraper (faster)
2. **Add delays:** Increase `time.sleep()` values to be respectful to the server
3. **Use filters:** Scrape specific categories/locations instead of everything
4. **Parallel scraping:** Use multiprocessing for multiple category/location combinations:

```python
from multiprocessing import Pool

def scrape_combination(args):
    category, location = args
    scraper = LocalSearchScraper()
    return scraper.search_businesses(category=category, location=location)

categories = ['Restaurants', 'Cafes']
locations = ['Sydney', 'Melbourne']
combinations = [(c, l) for c in categories for l in locations]

with Pool(4) as p:
    results = p.map(scrape_combination, combinations)

all_businesses = [item for sublist in results for item in sublist]
```

## Legal & Ethical Considerations

⚠️ **Important:** Before scraping:

1. **Check the website's robots.txt:** https://www.localsearch.com.au/robots.txt
2. **Check Terms of Service:** Ensure scraping is allowed
3. **Rate limiting:** Don't hammer the server with requests
4. **Respect resources:** Include delays between requests
5. **User-Agent:** The scrapers identify themselves appropriately

## Customization Guide

### Update CSS Selectors

If the site structure changes, update the selectors in the scraper:

```python
# In extract_business_info() method:

# Find the correct selector by inspecting the website
# Update class names, IDs, or tag selectors

name_elem = listing.find('h2', class_=['business-name', 'title', 'new-class-name'])
```

### Add More Fields

To extract additional information:

```python
# Add new field to business dict
business = {
    'name': '',
    'address': '',
    # ... existing fields ...
    'new_field': ''  # Add here
}

# Extract the new field
new_elem = listing.find('span', class_=['new-field-class'])
if new_elem:
    business['new_field'] = new_elem.get_text(strip=True)
```

## File Structure

```
.
├── localsearch_scraper.py              # Main BeautifulSoup scraper
├── localsearch_scraper_selenium.py     # Selenium scraper for JS sites
├── requirements.txt                     # Python dependencies
├── README_SCRAPER.md                   # This file
└── output/
    ├── localsearch_businesses.csv      # CSV output
    └── localsearch_businesses.json     # JSON output
```

## Contributing

If you improve the scraper, consider:
- Adding support for more fields
- Improving error handling
- Adding proxy support
- Implementing caching

## Support

For issues:
1. Check the Troubleshooting section above
2. Verify the website structure hasn't changed
3. Check logs for specific error messages
4. Try with a specific category/location first

## License

This scraper is provided as-is for learning and legitimate business intelligence purposes.

---

**Last Updated:** 2024
**Python Version:** 3.8+
