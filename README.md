# Google Maps Business Scraper - Web UI

A professional web-based interface for scraping business data from Google Maps.

## Features

✅ **Easy to Use** - Beautiful web interface, no command line needed  
✅ **Real-time Progress** - See scraping progress live  
✅ **Smart Scraping** - Retry logic, error handling, smart waits  
✅ **Email Extraction** - Automatically extract emails from websites  
✅ **Data Export** - Download results as CSV or JSON  
✅ **Resume Support** - Pick up from where you left off  
✅ **Professional Stats** - View data quality metrics  

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browser
```bash
playwright install chromium
```

## Usage

### Option 1: Web UI (Recommended)
```bash
python app.py
```
Then open **http://localhost:5000** in your browser.

### Option 2: Command Line
```bash
python maps_scraper.py --keyword "restaurant" --city "New York" --headless
```

## Web UI Features

- **🔍 Search**: Enter any business type and location
- **⚙️ Options**:
  - Headless mode (faster, no visible browser)
  - Skip email extraction (faster)
  - Set max results for testing
  - Adjust timeout (5-30 minutes)
- **📊 Real-time Progress**: Watch the scraper work
- **📈 Statistics**: See results count, phone/website/email percentages
- **📥 Download**: Get results as CSV or JSON
- **👀 Preview**: See first 10 results in the UI

## Output Files

After scraping, results are saved in:

```
output/
├── businesses.csv    # Spreadsheet format
└── businesses.json   # JSON format (for APIs)

logs/
└── scraper_*.log     # Detailed logs

checkpoints/
└── keyword_city.json # Resume checkpoint
```

## Configuration

Edit delays in `maps_scraper.py`:

```python
DELAY_BETWEEN_REQUESTS = 1      # seconds
DELAY_BETWEEN_BUSINESS = 2      # seconds
DELAY_BETWEEN_SCROLL = 1.5      # seconds
DELAY_AFTER_EMAIL_EXTRACTION = 1.5
```

## Data Quality

The scraper extracts:

| Field | Description |
|-------|-------------|
| **name** | Business name |
| **address** | Full address |
| **phone** | Phone number |
| **website** | Website URL |
| **emails** | Extracted from website |

## Tips

1. **First Run**: Use `--max-results 10` to test
2. **Large Datasets**: Run with `--headless` flag (faster)
3. **Email Extraction**: Takes longer - use `--no-emails` for speed
4. **Rate Limiting**: Built-in delays prevent IP bans
5. **Resume**: Checkpoints auto-save every 10 businesses

## Troubleshooting

**"Browser not found"?**
```bash
playwright install chromium
```

**Too slow?**
- Use `--headless` mode
- Reduce `--max-results`
- Enable `Skip Emails` in UI

**Getting blocked?**
- Increase delays in config
- Wait a few hours before retrying
- Use a VPN

## Architecture

```
app.py                     # Flask web server
├── maps_scraper.py       # Core scraper (unchanged)
├── templates/
│   └── index.html        # Web UI (responsive)
└── output/
    ├── businesses.csv
    └── businesses.json
```

## License

MIT - Feel free to modify and use!
