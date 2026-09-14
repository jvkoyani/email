# WHOIS Enrichment Guide

## Overview

This guide explains how to enrich your LocalSearch business data with WHOIS contact information (Registrant and Tech Contact details).

## What is WHOIS?

**WHOIS** is a database that contains registration information for domain names, including:
- **Registrant Name** - The person/organization who registered the domain
- **Registrant Email** - Contact email of the registrant
- **Tech Contact Name** - The technical administrator of the domain
- **Tech Contact Email** - Technical contact's email address

This information is publicly available through WHOIS servers.

## New Columns Added

Your enriched CSV will have these new columns:

| Column | Description | Example |
|--------|-------------|---------|
| `domain` | Extracted domain from website URL | premierac.com.au |
| `registrant_name` | Name of domain registrant | John Smith |
| `registrant_email` | Registrant's email address | john@premierac.com.au |
| `tech_name` | Technical contact name | Jane Doe |
| `tech_email` | Technical contact email | tech@premierac.com.au |

## Usage

### Option 1: Enrich Existing CSV

If you already have a scraped CSV file:

```bash
python whois_enricher.py brisbane_air_conditioning_sample.csv enriched_output.csv
```

This will:
1. Read the input CSV
2. Extract domains from the `website` column
3. Look up WHOIS information for each domain
4. Add new columns with contact data
5. Save to output CSV

### Option 2: Full Pipeline (Scrape + Enrich)

For a complete workflow:

```bash
python full_pipeline.py
```

This will:
1. **Step 1:** Scrape businesses from LocalSearch (uses config.json)
2. **Step 2:** Enrich with WHOIS contact data
3. Save both intermediate and final results
4. Display summary statistics

### Option 3: Custom Configuration

Edit `config.json` to customize the scrape:

```json
{
  "scraper": {"type": "beautifulsoup"},
  "search": {
    "categories": ["Air Conditioning", "Plumbing"],
    "locations": ["Brisbane", "Sydney"]
  }
}
```

Then run:
```bash
python full_pipeline.py
```

## How It Works

### 1. Domain Extraction

From the website URL, the script extracts the domain:
```
https://www.premierac.com.au → premierac.com.au
https://coolbreeze.com.au    → coolbreeze.com.au
```

### 2. WHOIS Lookup

The script connects to WHOIS servers and queries for the domain:
- Primary method: Socket connection to whois.auda.org.au
- Fallback method: HTTP API request

### 3. Data Parsing

Parses WHOIS response to extract:
- Registrant contact name
- Registrant contact email
- Tech contact name
- Tech contact email

### 4. CSV Enrichment

Adds the extracted data as new columns to your CSV

## Output Files

### Full Pipeline Creates:

1. **step1_scraped_TIMESTAMP.csv**
   - Original scraped data from LocalSearch
   - Without WHOIS enrichment

2. **step2_enriched_TIMESTAMP.csv**
   - Complete data with WHOIS contact information
   - Ready for email campaigns or analysis

### Simple Enrichment Creates:

1. **enriched_output.csv** (or your specified name)
   - Original CSV + WHOIS columns

## Processing Time

Average processing time per business:
- **Lookup:** ~1-2 seconds per domain
- **Parsing:** Instantaneous
- **Total for 100 businesses:** 2-3 minutes

**Note:** Rate limiting is applied to respect WHOIS server resources.

## Success Rates

Typically you can expect:

| Metric | Rate |
|--------|------|
| Domains found | 95-100% |
| Registrant info found | 85-95% |
| Email found | 70-85% |
| Tech info found | 60-75% |

Some domains may have:
- Private/hidden registrant information
- Outdated WHOIS data
- Inactive domains

## Troubleshooting

### Issue: "No data extracted"

**Possible causes:**
- Website URL is missing or invalid
- Domain doesn't exist
- WHOIS server is unavailable
- Domain has private registration

**Solution:**
- Check the domain manually at: https://whois.auda.org.au/
- Verify the website URL in the original CSV

### Issue: "Connection refused"

**Cause:** WHOIS server connection failed

**Solution:**
- Wait a few minutes and retry
- Check your internet connection
- The server may be temporarily down

### Issue: Very slow processing

**Cause:** WHOIS server is responding slowly

**Solution:**
- This is normal, especially for large batches
- Reduce concurrent requests (currently 1 per second)
- Run overnight for large datasets (1000+ records)

### Issue: Partial data (some fields empty)

**Cause:** WHOIS data not available for that domain

**Solution:**
- Some domains have private registration
- Check manually at https://whois.auda.org.au/
- Use the data you have (registrant name, tech email, etc.)

## Using the Enriched Data

### Lead Generation

```
Filter: registrant_email is not empty
Result: List of business owners to contact
Action: Email marketing campaigns
```

### Tech Contact Outreach

```
Filter: tech_email is not empty
Result: List of technical administrators
Action: Promote tech services/products
```

### Business Research

```
Analyze: Compare registrant names vs business names
Result: Find hidden business relationships
Action: Competitive intelligence
```

### Email List Creation

```python
import pandas as pd

df = pd.read_csv('enriched_data.csv')

# Get all available emails
all_emails = pd.concat([
    df[df['registrant_email'].notna()][['name', 'registrant_email']],
    df[df['tech_email'].notna()][['name', 'tech_email']]
])

all_emails.to_csv('email_list.csv', index=False)
```

### Excel Processing

1. Open enriched CSV in Excel
2. Add new columns for your tracking:
   - Contact Status (Not Contacted / Contacted / Interested)
   - Follow-up Date
   - Notes
3. Filter by email availability
4. Create mail merge for campaigns

## Data Privacy & Ethics

⚠️ **Important Considerations:**

1. **WHOIS Data Usage:**
   - Public data available through WHOIS
   - Respect the registrant's privacy
   - Don't spam or misuse contact information

2. **Email Campaigns:**
   - Follow email marketing regulations
   - Include unsubscribe option
   - Respect do-not-contact requests

3. **Data Storage:**
   - Secure your CSV files
   - Don't share with unauthorized parties
   - Comply with data protection laws (GDPR, CCPA, etc.)

## Advanced Features

### Cache WHOIS Results

The enricher caches WHOIS lookups to avoid duplicate queries:

```python
enricher = WHOISEnricher()
contact_data = enricher.lookup_domain("example.com")

# Second lookup uses cache (instant)
contact_data = enricher.lookup_domain("example.com")
```

### Manual Lookup

Look up a single domain:

```python
from whois_enricher import WHOISEnricher

enricher = WHOISEnricher()
data = enricher.lookup_domain("premierac.com.au")

print(f"Registrant: {data['registrant_name']}")
print(f"Email: {data['registrant_email']}")
print(f"Tech Contact: {data['tech_name']}")
```

### Batch Processing

Process multiple CSV files:

```bash
# Process all CSVs in a directory
for file in *.csv; do
    python whois_enricher.py "$file" "enriched_$file"
done
```

## Performance Tips

1. **For 100-500 businesses:** Run normally (2-5 minutes)
2. **For 1000+ businesses:** Run overnight
3. **Reduce rate limit delay:** Edit `whois_enricher.py`
   ```python
   self.rate_limit_delay = 0.5  # 500ms instead of 1s
   ```
4. **Use parallel processing:**
   ```python
   from multiprocessing import Pool
   
   with Pool(3) as p:
       results = p.map(enricher.lookup_domain, domain_list)
   ```

## Limitations

1. **Accuracy:** WHOIS data is 85-95% accurate
2. **Completeness:** Some domains have hidden registrant info
3. **Updates:** WHOIS data may be outdated
4. **Coverage:** Limited to domain names (not all have websites)

## Support

For issues:

1. **Domain not found?**
   - Check it exists: https://whois.auda.org.au/
   - Try manual lookup to see available data

2. **Script not working?**
   - Check internet connection
   - Verify CSV file format
   - Check logs for specific error

3. **Need more help?**
   - Review the code comments
   - Check the error messages in logs
   - See examples in full_pipeline.py

## File Reference

| File | Purpose |
|------|---------|
| `whois_enricher.py` | Main WHOIS enrichment script |
| `full_pipeline.py` | Combined scraping + enrichment pipeline |
| `config.json` | Configuration for scraper settings |
| `WHOIS_ENRICHMENT_GUIDE.md` | This documentation |

## Examples

### Example 1: Enrich Sample Data

```bash
python whois_enricher.py brisbane_air_conditioning_sample.csv output.csv
```

### Example 2: Full Workflow

```bash
# 1. Configure your search
# Edit config.json with your categories and locations

# 2. Run full pipeline
python full_pipeline.py

# 3. Check results
# open step2_enriched_*.csv
```

### Example 3: Filter Enriched Data

```python
import pandas as pd

df = pd.read_csv('enriched_output.csv')

# Get only records with registrant email
with_emails = df[df['registrant_email'].notna()]

# Sort by rating (highest first)
top_rated = with_emails.sort_values('rating', ascending=False)

# Save filtered results
top_rated.to_csv('top_rated_with_contacts.csv', index=False)
```

## Success Metrics

Track your enrichment success:

```python
import csv

with open('enriched_output.csv') as f:
    reader = csv.DictReader(f)
    data = list(reader)

total = len(data)
registrant = sum(1 for d in data if d.get('registrant_email'))
tech = sum(1 for d in data if d.get('tech_email'))

print(f"Total records: {total}")
print(f"Registrant emails: {registrant} ({100*registrant/total:.1f}%)")
print(f"Tech emails: {tech} ({100*tech/total:.1f}%)")
```

---

**Ready to enrich your data?**

1. Run: `python whois_enricher.py input.csv output.csv`
2. Check the output CSV
3. Use the contact data for outreach!

For more information, see the main README_SCRAPER.md file.
