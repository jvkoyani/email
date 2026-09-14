# Quick Start Guide - LocalSearch Scraper

Get started scraping LocalSearch.com.au business data in minutes!

## Installation (2 minutes)

```bash
# Install dependencies
pip install -r requirements.txt
```

## Basic Usage (3 ways)

### Method 1: Quick Scrape (Fastest - Recommended)

```bash
python localsearch_scraper.py
```

This will scrape the site using default settings and save to CSV and JSON.

### Method 2: Configuration-Based Scraping

1. **Edit `config.json`** to customize:
```json
{
  "scraper": {"type": "beautifulsoup"},
  "search": {
    "categories": ["Restaurants", "Cafes"],
    "locations": ["Sydney", "Melbourne"]
  }
}
```

2. **Run the scraper:**
```bash
python scraper_runner.py
```

Results will be saved to `results/` directory with timestamp.

### Method 3: Custom Python Script

```python
from localsearch_scraper import LocalSearchScraper

# Create scraper
scraper = LocalSearchScraper()

# Scrape restaurants in Sydney
businesses = scraper.search_businesses(
    category="Restaurants",
    location="Sydney"
)

# Add more searches
more_businesses = scraper.search_businesses(
    category="Cafes",
    location="Melbourne"
)
scraper.businesses.extend(more_businesses)

# Save results
scraper.save_to_csv('my_results.csv')
scraper.save_to_json('my_results.json')

print(f"Found {len(scraper.businesses)} businesses")
```

## Output Files

After running the scraper, you'll get:

- **CSV File:** `localsearch_businesses.csv` - Import into Excel, Google Sheets, etc.
- **JSON File:** `localsearch_businesses.json` - For data processing

### CSV Structure:
```
name,address,phone,website,email,category,location,rating,reviews,hours,description
Joe's Pizza,123 Main St,02 1234 5678,https://...,info@...,Restaurants,Sydney,4.5,127,Mon-Fri 10am-10pm,...
```

## Popular Categories

- Accounting
- Automotive
- Beauty & Personal Care
- Cafes & Coffee Shops
- Construction
- Dental
- Education
- Fitness & Gyms
- Florists
- Hardware
- Health & Medical
- Insurance
- Legal Services
- Plumbing
- Real Estate
- Restaurants
- Retail
- Tradies
- Travel & Tourism

## Popular Locations

- Sydney (and suburbs)
- Melbourne (and suburbs)
- Brisbane (and suburbs)
- Perth (and suburbs)
- Adelaide (and suburbs)
- Gold Coast
- Newcastle
- Canberra
- Hobart
- Darwin

## Tips & Tricks

### Tip 1: Filter Results in Excel/Sheets
```
1. Open CSV in Excel
2. Select header row
3. Data → AutoFilter
4. Filter by category, location, rating, etc.
```

### Tip 2: Process with Python
```python
import pandas as pd

# Load CSV
df = pd.read_csv('localsearch_businesses.csv')

# Filter
restaurants = df[df['category'] == 'Restaurants']
highly_rated = df[df['rating'] >= 4.0]
sydney_only = df[df['location'] == 'Sydney']

# Save filtered
highly_rated.to_csv('highly_rated.csv', index=False)
```

### Tip 3: Scrape Specific Categories
Edit `config.json`:
```json
"categories": ["Plumbing", "Electricians", "Construction"]
```

### Tip 4: Slow Down if Getting Blocked
Edit `config.json`:
```json
"delay_between_requests": 3,
"delay_between_searches": 5
```

## Troubleshooting

### "No businesses found"
- Try a different category/location combination
- Check if the site is accessible in your browser first
- Try the Selenium version: update `config.json` to `"type": "selenium"`

### Script runs but slow
- It's respecting the server delays by design
- Normal speed: 100-200 businesses per minute
- Reduce delays if needed (use with caution)

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Using Selenium (for JavaScript-heavy content)

Update `config.json`:
```json
"scraper": {"type": "selenium"}
```

Then run:
```bash
python scraper_runner.py
```

## Advanced Features

### Parallel Scraping (Multiple processes)
```python
from multiprocessing import Pool
from localsearch_scraper import LocalSearchScraper

def scrape_combo(args):
    category, location = args
    scraper = LocalSearchScraper()
    return scraper.search_businesses(category=category, location=location)

categories = ['Restaurants', 'Cafes', 'Medical']
locations = ['Sydney', 'Melbourne']
combos = [(c, l) for c in categories for l in locations]

with Pool(4) as p:
    results = p.map(scrape_combo, combos)

all_businesses = [b for r in results for b in r]
```

### Export to Different Formats

**Excel:**
```python
import pandas as pd
df = pd.read_csv('localsearch_businesses.csv')
df.to_excel('businesses.xlsx', index=False)
```

**Google Sheets:**
1. Upload CSV to Google Drive
2. Right-click → Open with → Google Sheets
3. Share the sheet

## Common Use Cases

### 1. Find all plumbers in Sydney
```json
"categories": ["Plumbing"],
"locations": ["Sydney"]
```

### 2. Compare different categories
```json
"categories": ["Restaurants", "Cafes", "Bars"],
"locations": ["Sydney", "Melbourne"]
```

### 3. Research competitors
```python
df = pd.read_csv('localsearch_businesses.csv')
competitors = df[
    (df['category'] == 'Restaurants') & 
    (df['location'].str.contains('Inner Sydney'))
]
```

### 4. Build contact list
```python
df = pd.read_csv('localsearch_businesses.csv')
# Keep only businesses with phone/email
contacts = df[df['phone'].notna() | df['email'].notna()]
contacts[['name', 'phone', 'email']].to_csv('contacts.csv', index=False)
```

## Need Help?

1. Check `README_SCRAPER.md` for detailed documentation
2. Read error messages carefully - they usually explain the issue
3. Try with a smaller set first (e.g., one category, one location)
4. Verify the website is working in your browser

## What's Next?

- Analyze the data in Excel or Google Sheets
- Import to CRM (Pipedrive, HubSpot, etc.)
- Create a database with the CSV
- Build visualizations from the data
- Use for market research

---

**Happy scraping!** 🎉

Remember to be respectful to the server - don't reduce delays below 1 second.
