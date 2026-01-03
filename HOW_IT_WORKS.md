# Google Maps Scraper - Complete Guide

## 🎯 **How It Works (Step-by-Step)**

### **Phase 1: Search & Discovery**
1. Opens Google Maps in a browser (Chromium)
2. Enters your search query (e.g., "Restaurants in New York")
3. **Scrolls through results** to load ALL available businesses (not just initial ones)
4. Collects all business links/cards

### **Phase 2: Data Extraction**
For each business found:
1. **Clicks** the business card to open its details panel
2. **Extracts data**:
   - Business name (from heading)
   - Address (from aria-label on button)
   - Phone number (from aria-label on button)
   - Website URL (from aria-label on button)

### **Phase 3: Email Mining** (Optional)
1. If website found and not on skip-list (Facebook, Instagram, etc.)
2. **Navigates to the website**
3. **Extracts all emails** using regex pattern matching
4. Returns to Google Maps (doesn't affect other scraping)
5. *Takes longest due to website loading*

### **Phase 4: Deduplication & Quality**
1. **Removes duplicates** (same name + phone)
2. **Merges emails** if same business found twice
3. **Validates data** (removes fake/junk entries)
4. **Filters out placeholder names** (like "Results", "About")

### **Phase 5: Export**
1. Saves to **businesses.csv** (for Excel/Sheets)
2. Saves to **businesses.json** (for APIs/integrations)
3. Creates logs for debugging

---

## ⚙️ **Timeout Settings Explained**

| Setting | Time | Best For | Speed |
|---------|------|----------|-------|
| **5 min (Fast)** | 300s | Testing, small areas | ⚡ Very Fast |
| **10 min (Recommended)** | 600s | Standard scraping | ✅ Balanced |
| **15 min (Thorough)** | 900s | Large cities | 🐢 Slower |
| **20 min (Very Thorough)** | 1200s | Complete data | 🐌 Very Slow |
| **30 min (Exhaustive)** | 1800s | All possible results | 🐢🐢 Slowest |

**What timeout does:**
- Sets max time the scraper runs
- Doesn't limit results per se, just total time
- If scraping finishes early, returns immediately
- If hits timeout, saves progress and exits gracefully

---

## 🚀 **Usage Tips**

### **For Speed (Best):**
```
- Keyword: "Pizza"
- City: "New York"
- Max Results: 50
- Headless: ✅ ON
- Skip Emails: ✅ ON (unless you need emails)
- Timeout: 5-10 min
```
**Speed**: ~3-5 minutes for 50 businesses

### **For Completeness:**
```
- Keyword: "Restaurant"
- City: "Los Angeles"
- Max Results: (empty for all)
- Headless: ✅ ON
- Skip Emails: ❌ OFF
- Timeout: 20-30 min
```
**Speed**: 20-30 minutes for 100-200 businesses

### **For Testing/Development:**
```
- Max Results: 10
- Skip Emails: ✅ ON
- Headless: ❌ OFF (see browser)
- Timeout: 5 min
```
**Speed**: ~2 minutes

---

## 📊 **Output Explanation**

### **Stats Shown**
- **Total Businesses**: All unique businesses found
- **With Phone**: Percentage that have phone numbers
- **With Website**: Percentage that have websites
- **With Email**: Percentage that have emails (if extraction enabled)

### **Data Quality**
```
If all 100 businesses have:
- Phone: 95% → Only 5 businesses missing phone
- Website: 72% → 72 out of 100 have websites
- Email: 40% → 40 out of 100 have emails
```

---

## 🔧 **Advanced Options**

### **Headless Mode** ✅ (Recommended: ON)
- **ON**: No browser window visible, **2-3x faster**
- **OFF**: See the scraper work in real-time (debugging)
- Default: ON

### **Skip Email Extraction** ✅ (Default: OFF)
- **ON**: 50% faster, no emails extracted
- **OFF**: Slower but gets all emails from websites
- Default: OFF (extracts emails)

### **Max Results**
- Leave empty: Gets all available results (can be 100+)
- Set number (e.g., 50): Stops after 50 businesses found
- **Use this for testing** before running full scrapes

---

## 📥 **Export Formats**

### **CSV (Excel Format)**
```
name,address,phone,website,emails
Starbucks,"123 Main St, NYC","(212) 555-0123","https://starbucks.com","manager@starbucks.com"
```
✅ Open in: Excel, Google Sheets, LibreOffice

### **JSON (API Format)**
```json
[
  {
    "name": "Starbucks",
    "address": "123 Main St, NYC",
    "phone": "(212) 555-0123",
    "website": "https://starbucks.com",
    "emails": "manager@starbucks.com"
  }
]
```
✅ Use for: APIs, webhooks, integrations

---

## ⚠️ **Important Notes**

### **Rate Limiting**
- Built-in delays (1-2 seconds between actions)
- Prevents IP bans
- Mimics human behavior
- May take time but sustainable

### **Email Extraction**
- Only searches visible HTML content
- Skips: Facebook, Instagram, Twitter, LinkedIn, YouTube, etc.
- Validates emails to reduce false positives
- Can be slow (adds 5-10 seconds per business)

### **Proxy/VPN**
- Not required for small datasets (<500 businesses)
- May need for larger/repeated scraping
- Consider using residential proxies for scale

### **Accuracy**
- Data is extracted from Google Maps (user-provided)
- Some businesses may not have emails/phones public
- Deduplication removes accidental duplicates

---

## 📈 **Performance Examples**

### **Example 1: Small City**
```
Keyword: Coffee Shop
City: Portland, OR
Results: ~40 businesses
Time: 4 minutes
```

### **Example 2: Large City**
```
Keyword: Restaurant
City: Los Angeles
Results: 200+ businesses
Time: 25 minutes (with emails)
```

### **Example 3: Specific Service**
```
Keyword: Plumber
City: Chicago
Results: ~80 businesses
Time: 8 minutes (no emails)
```

---

## 🐛 **Troubleshooting**

| Issue | Solution |
|-------|----------|
| No results found | Try simpler keyword, check spelling |
| Very slow | Enable "Skip Emails", reduce timeout |
| Getting blocked | Wait a few hours, use different city |
| Emails not extracted | Some websites don't have emails in HTML |
| Crashes mid-scrape | Use Resume feature to continue |

---

## 💾 **File Structure**

```
output/
├── businesses.csv          # Spreadsheet format
└── businesses.json         # JSON format

logs/
└── scraper_*.log          # Detailed logs

checkpoints/
└── keyword_city.json      # Resume checkpoint (auto-deleted on success)
```

---

## ✨ **Pro Tips**

1. **Start small**: Test with `--max-results 10` first
2. **Use headless**: Always use headless mode for speed
3. **Skip emails initially**: Get all businesses first, then extract emails separately
4. **Batch searches**: Scrape multiple cities, combine results
5. **Monitor logs**: Check `logs/` folder for detailed debugging

---

## 🎯 **When to Use Each Setting**

| Scenario | Settings |
|----------|----------|
| Quick test | 5 min, 10 results, skip emails |
| Small business list | 10 min, 50 results, with emails |
| Full city data | 20-30 min, unlimited, with emails |
| API automation | 10 min, 100 results, skip emails |

---

Good luck scraping! Happy data gathering! 🎉
