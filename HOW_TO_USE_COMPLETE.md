# Complete LocalSearch Scraper + WHOIS Enrichment Guide

## 🎯 What You Can Do

This complete package allows you to:

1. **Scrape business listings** from LocalSearch.com.au by category and location
2. **Enrich with WHOIS data** - Get registrant contact information
3. **Export to CSV** - Ready for Excel, Google Sheets, CRM systems
4. **Generate reports** - Analyze and filter the data

## 📋 Complete Workflow

```
┌─────────────────────┐
│   LocalSearch.com   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Scrape Businesses  │ (localsearch_scraper.py)
│   - Name            │
│   - Address         │
│   - Phone           │
│   - Website         │
│   - Rating          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Local CSV File    │
│  (scraped_data.csv) │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  WHOIS Enrichment   │ (whois_enricher.py)
│  - Domain lookup    │
│  - Extract contacts │
│  - Parse emails     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Enriched CSV File  │ ← Ready for analysis & outreach!
│ (with WHOIS data)   │
└─────────────────────┘
```

## 🚀 Quick Start (5 minutes)

### Step 1: Prepare Your System

```bash
# Navigate to project folder
cd /path/to/email/

# Install dependencies (do this once)
pip install -r requirements.txt
```

### Step 2: Configure (Optional)

Edit `config.json` to customize your search:

```json
{
  "scraper": {
    "type": "beautifulsoup"
  },
  "search": {
    "categories": ["Air Conditioning", "Plumbing"],
    "locations": ["Brisbane", "Sydney"]
  },
  "scraping": {
    "delay_between_requests": 1,
    "max_pages_per_search": 50
  }
}
```

### Step 3: Run Full Pipeline

```bash
python full_pipeline.py
```

This will:
1. ✅ Scrape all businesses (using config.json settings)
2. ✅ Enrich with WHOIS contact data
3. ✅ Save two CSV files with timestamps
4. ✅ Display summary statistics

### Step 4: Use Your Data

Check the output folder for timestamped files:
- `step1_scraped_20240914_120000.csv` - Raw scraped data
- `step2_enriched_20240914_120000.csv` - With WHOIS contacts ⭐

---

## 📊 Three Usage Methods

### Method 1: Full Automated Pipeline (RECOMMENDED)

**Best for:** Getting everything in one go

```bash
python full_pipeline.py
```

**What happens:**
- Reads config.json
- Scrapes LocalSearch
- Enriches with WHOIS
- Saves both CSVs
- Shows summary

**Output:**
- `step1_scraped_*.csv` (scraped businesses)
- `step2_enriched_*.csv` (with WHOIS contacts)

**Time:** ~5-10 minutes for 100 businesses

---

### Method 2: Just Enrich Existing CSV

**Best for:** You already have a CSV and just want WHOIS data

```bash
python whois_enricher.py your_existing.csv output.csv
```

**Example:**
```bash
python whois_enricher.py brisbane_air_conditioning_sample.csv enriched_output.csv
```

**What it does:**
1. Reads your CSV
2. Extracts domains from website column
3. Looks up WHOIS for each domain
4. Adds 5 new columns
5. Saves enriched CSV

**Output columns:**
- domain
- registrant_name
- registrant_email
- tech_name
- tech_email

---

### Method 3: Custom Python Script

**Best for:** Advanced users who want full control

```python
from localsearch_scraper import LocalSearchScraper
from whois_enricher import WHOISEnricher

# Step 1: Scrape
scraper = LocalSearchScraper()
businesses = scraper.search_businesses(
    category="Restaurants",
    location="Brisbane"
)
scraper.businesses = businesses
scraper.save_to_csv('restaurants.csv')

# Step 2: Enrich
enricher = WHOISEnricher()
enricher.enrich_csv('restaurants.csv', 'restaurants_enriched.csv')

print("Done!")
```

---

## 📁 File Organization

```
email/
├── Core Scrapers
│   ├── localsearch_scraper.py          ← Main scraper
│   ├── localsearch_scraper_selenium.py ← For JS sites
│   └── scraper_runner.py               ← Advanced runner
│
├── WHOIS Enrichment
│   ├── whois_enricher.py               ← WHOIS lookup
│   └── full_pipeline.py                ← Automated workflow
│
├── Configuration
│   ├── config.json                     ← Your settings
│   └── requirements.txt                ← Dependencies
│
├── Documentation
│   ├── QUICKSTART.md                   ← 5-min guide
│   ├── README_SCRAPER.md               ← Full docs
│   ├── WHOIS_ENRICHMENT_GUIDE.md       ← WHOIS guide
│   └── HOW_TO_USE_COMPLETE.md          ← This file
│
└── Sample Data
    ├── brisbane_air_conditioning_sample.csv
    ├── brisbane_air_conditioning_sample.json
    └── SAMPLE_DATA_REPORT.md
```

---

## 💡 Common Tasks

### Task 1: Get All Plumbers in Sydney + Their Contacts

```bash
# 1. Edit config.json:
{
  "search": {
    "categories": ["Plumbing"],
    "locations": ["Sydney"]
  }
}

# 2. Run:
python full_pipeline.py

# 3. Output: step2_enriched_*.csv with all plumbers + WHOIS contacts
```

### Task 2: Combine Multiple Cities

```bash
# 1. Edit config.json:
{
  "search": {
    "categories": ["Restaurants"],
    "locations": ["Brisbane", "Sydney", "Melbourne"]
  }
}

# 2. Run:
python full_pipeline.py

# 3. Filter in Excel by location
```

### Task 3: Build Email Contact List

```bash
# 1. Run full pipeline
python full_pipeline.py

# 2. Open enriched CSV in Excel

# 3. Create new column "email_list"
# Formula: =IF(NOT(ISBLANK(E2)),E2,F2)
# (Use registrant email or tech email)

# 4. Export emails for campaign
```

### Task 4: Analysis & Reports

```bash
# Use Python to analyze:
import pandas as pd

df = pd.read_csv('step2_enriched_*.csv')

# Top rated businesses
top = df.nlargest(10, 'rating')

# Businesses with registrant contacts
with_contacts = df[df['registrant_email'].notna()]

# By category
by_category = df.groupby('category').size()

# With email percentage
pct = 100 * len(with_contacts) / len(df)
print(f"{pct:.1f}% have registrant email")
```

---

## 🎓 Step-by-Step Example: Air Conditioning Brisbane

### Setup (1 time only)

```bash
cd ~/email
pip install -r requirements.txt
```

### Configuration

Edit `config.json`:
```json
{
  "search": {
    "categories": ["Air Conditioning"],
    "locations": ["Brisbane"]
  },
  "scraping": {
    "max_pages_per_search": 10
  }
}
```

### Execution

```bash
python full_pipeline.py
```

### Output

```
Step 1: Scraping 1/1 - Air Conditioning in Brisbane
✓ Found 23 businesses
Saved to: step1_scraped_20240914_143022.csv

Step 2: Enriching with WHOIS
✓ Processed 23 domains
✓ Found 19 registrant emails
✓ Found 16 tech emails
Saved to: step2_enriched_20240914_143022.csv

RESULTS:
- Total: 23 businesses
- With registrant email: 19 (82%)
- With tech email: 16 (70%)
```

### Using the Data

1. **Download the file** `step2_enriched_20240914_143022.csv`

2. **Open in Excel**

3. **Filter/Sort:**
   - Sort by rating (highest first)
   - Filter by registrant_email (not empty)
   - Filter by location (Brisbane CBD, Suburbs, etc.)

4. **Create campaigns:**
   - Export emails for mailshot
   - Call phone numbers for outreach
   - Visit websites to understand services

5. **Analysis:**
   - Which areas have most AC businesses?
   - Average rating by suburb?
   - Contact coverage by suburb?

---

## ⚡ Advanced Features

### Run on Schedule (Automation)

```bash
# Linux/Mac - Add to crontab:
0 0 * * * cd /home/user/email && python full_pipeline.py

# Windows - Use Task Scheduler
# Or use: python send_later.py --delay 24h
```

### Process Multiple Categories

```python
categories = [
    "Plumbing", "Electrical", "Air Conditioning",
    "Heating", "HVAC", "Building Services"
]
locations = ["Brisbane", "Sydney", "Melbourne"]

# Create config for each combination...
```

### Custom Filters

```python
import pandas as pd

df = pd.read_csv('enriched.csv')

# Only highly rated
top_rated = df[df['rating'] >= 4.5]

# Only with emails
with_emails = df[df['registrant_email'].notna()]

# Export filtered
top_rated[with_emails].to_csv('leads.csv', index=False)
```

---

## 🐛 Troubleshooting

### "No businesses found"

**Check:**
1. Is LocalSearch accessible in your browser? (Try manually)
2. Did you use correct category/location names?
3. Is the website blocked by your proxy?

**Solution:**
- Try with well-known category like "Restaurants"
- Use Selenium scraper: change `config.json` to `"type": "selenium"`

### "WHOIS lookup failed"

**Check:**
1. Is the domain valid?
2. Is your internet connection working?
3. Is the WHOIS server down?

**Solution:**
- Check domain manually at https://whois.auda.org.au/
- Try again later (server may be temporarily down)
- Skip domains with private registration

### "Script is very slow"

**Normal:** 1-2 seconds per domain (respecting server)

**To speed up:**
- Reduce delay: Edit `whois_enricher.py`, change `rate_limit_delay = 0.5`
- Run during off-peak hours
- Use fewer categories/locations first

### "CSV file not found"

**Check:**
1. Is the file in the same folder as the script?
2. Correct filename spelling?
3. File exists?

**Solution:**
```bash
# Check what files you have:
ls -la *.csv

# Use full path:
python whois_enricher.py /full/path/to/file.csv output.csv
```

---

## 📈 Performance Expectations

| Task | Time | Notes |
|------|------|-------|
| Scrape 100 businesses | 5-10 min | With delays |
| WHOIS 100 businesses | 2-3 min | ~1-2s each |
| Full pipeline 100 | 7-13 min | Total |
| Scrape 1000 businesses | 1-2 hours | Run overnight |
| WHOIS 1000 businesses | 20-30 min | Parallel possible |

---

## 🎯 Next Steps

1. **Install** - `pip install -r requirements.txt` ✅
2. **Configure** - Edit `config.json` for your needs ✅
3. **Run** - `python full_pipeline.py` ✅
4. **Analyze** - Open CSV in Excel ✅
5. **Export** - Use for outreach/analysis ✅

---

## 📞 Support

### Need Help?

1. **Read the guides:**
   - QUICKSTART.md (5-minute intro)
   - README_SCRAPER.md (detailed)
   - WHOIS_ENRICHMENT_GUIDE.md (WHOIS specific)

2. **Check the logs:**
   - Error messages often explain the issue
   - Look for "ERROR" in output

3. **Test manually:**
   - Try a smaller search first (1 category, 1 location)
   - Verify website/domain manually

4. **Inspect the code:**
   - Comments in scripts explain how they work
   - Functions are well-documented

### Common Success Patterns

✅ **Works best:**
- Brisbane, Sydney, Melbourne (major cities)
- Restaurants, Medical, Plumbing (common categories)
- Running during off-peak hours

✅ **Works okay:**
- Smaller cities (Newcastle, Gold Coast)
- Less common categories
- Daytime running (may be slower)

⚠️ **May have issues:**
- Very small suburbs (few businesses)
- Private WHOIS registrations (hidden emails)
- During high-load periods on servers

---

## 🎉 You're Ready!

**Everything you need is set up:**
- ✅ Scraper built and tested
- ✅ WHOIS enricher ready
- ✅ Automation pipeline ready
- ✅ Documentation complete
- ✅ Sample data provided

**Just run:**
```bash
python full_pipeline.py
```

**And you'll get:**
- Business listings with all details
- Contact information from WHOIS
- Ready-to-use CSV files
- Summary statistics

**Happy scraping! 🚀**

---

## Version History

- **v1.0** - Initial release with full pipeline
  - LocalSearch scraper (BeautifulSoup + Selenium)
  - WHOIS enrichment
  - Automated pipeline
  - Complete documentation

---

## Quick Reference Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run full pipeline
python full_pipeline.py

# Enrich single CSV
python whois_enricher.py input.csv output.csv

# Run with Python directly
python localsearch_scraper.py

# Run advanced runner
python scraper_runner.py

# Inspect website structure (for debugging)
python inspect_website.py
```

---

Created with ❤️ for LocalSearch data extraction and analysis.
