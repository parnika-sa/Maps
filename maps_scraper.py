from playwright.sync_api import sync_playwright
import time
import csv
import os
import argparse
import re
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Set
from urllib.parse import urlparse

# ============================================
# CONFIGURATION & CONSTANTS
# ============================================
LOG_DIR = "logs"
CHECKPOINT_DIR = "checkpoints"
OUTPUT_DIR = "output"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Setup logging
log_file = os.path.join(LOG_DIR, f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# CSS Selectors (with fallbacks)
SEARCH_BOX_SELECTORS = [
    "input#searchboxinput",
    "input[aria-label*='Search']",
    "input[placeholder*='Search']"
]
RESULTS_PANEL_SELECTORS = [
    'div[role="feed"]',
    'div[role="list"]',
    'div[data-attrid*="results"]'
]
BUSINESS_NAME_SELECTORS = [
    'h1[class*="DUwDvf"]',
    'h1[class*="fontHeadline"]',
    'h1'
]
BUSINESS_CARD_SELECTOR = 'a[href*="/place/"]'

# Timeouts (in milliseconds)
SEARCH_TIMEOUT = 60000
BUSINESS_LOAD_TIMEOUT = 8000
WEBSITE_LOAD_TIMEOUT = 10000
ELEMENT_WAIT_TIMEOUT = 5000

# Email settings
SKIP_EMAIL_DOMAINS = {
    'facebook.com', 'instagram.com', 'twitter.com', 'youtube.com',
    'tiktok.com', 'linkedin.com', 'pinterest.com', 'google.com',
    'maps.google.com'
}

# Rate limiting
DELAY_BETWEEN_REQUESTS = 1  # seconds
DELAY_BETWEEN_BUSINESS = 2  # seconds
DELAY_BETWEEN_SCROLL = 1.5  # seconds
DELAY_AFTER_EMAIL_EXTRACTION = 1.5  # seconds

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# ============================================
# UTILITY FUNCTIONS
# ============================================

def safe_filename(text: str) -> str:
    """Convert text to safe filename by replacing special chars"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text)

def normalize_phone(phone: str) -> str:
    """Normalize phone number by removing special characters"""
    if phone == "N/A":
        return phone
    return re.sub(r'[^\d+]', '', phone)

def validate_email(email: str) -> bool:
    """Validate email format more strictly"""
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        # Exclude common false positives
        invalid_patterns = ['test@', 'example@', 'temp@', 'placeholder@']
        return not any(email.startswith(p) for p in invalid_patterns)
    return False

def extract_emails_from_text(text: str) -> Set[str]:
    """Extract and validate emails from text"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found = re.findall(pattern, text)
    return {e for e in found if validate_email(e)}

def should_skip_email_extraction(website: str) -> bool:
    """Check if website is in skip list"""
    try:
        domain = urlparse(website).netloc.lower()
        return any(skip in domain for skip in SKIP_EMAIL_DOMAINS)
    except:
        return False

def wait_for_selector(page, selectors: List[str], timeout: int = ELEMENT_WAIT_TIMEOUT) -> bool:
    """Try multiple selectors with fallback"""
    for selector in selectors:
        try:
            page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            continue
    return False

def get_selector(page, selectors: List[str]):
    """Get element using fallback selectors"""
    for selector in selectors:
        try:
            element = page.query_selector(selector)
            if element:
                return element
        except:
            continue
    return None

def retry_action(action, max_retries: int = MAX_RETRIES, delay: float = RETRY_DELAY):
    """Retry an action with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return action()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 1.5

def save_checkpoint(checkpoint_file: str, businesses: List[Dict], index: int):
    """Save progress checkpoint"""
    checkpoint = {
        "timestamp": datetime.now().isoformat(),
        "index": index,
        "businesses_count": len(businesses),
        "businesses": businesses
    }
    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    logger.info(f"Checkpoint saved: {index} businesses processed")

def load_checkpoint(checkpoint_file: str) -> Optional[Dict]:
    """Load progress checkpoint"""
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
            logger.info(f"Checkpoint loaded: {checkpoint['index']} businesses already processed")
            return checkpoint
        except Exception as e:
            logger.warning(f"Could not load checkpoint: {e}")
    return None

def deduplicate_businesses(businesses: List[Dict]) -> List[Dict]:
    """Deduplicate businesses with better matching"""
    seen = {}
    for business in businesses:
        # Create composite key: normalized name + normalized phone
        name_key = business["name"].lower().strip()
        phone_key = normalize_phone(business["phone"])
        key = (name_key, phone_key)
        
        # If key exists, merge emails
        if key in seen:
            existing = seen[key]
            if business["emails"] != "N/A":
                existing_emails = set(existing["emails"].split(", ")) if existing["emails"] != "N/A" else set()
                new_emails = set(business["emails"].split(", "))
                merged_emails = existing_emails | new_emails
                existing["emails"] = ", ".join(sorted(merged_emails)) if merged_emails else "N/A"
        else:
            seen[key] = business
    
    return list(seen.values())

# ============================================
# MAIN SCRAPER
# ============================================

def main():
    # CLI Arguments
    parser = argparse.ArgumentParser(description="Google Maps Business Scraper (Improved)")
    parser.add_argument("--keyword", required=True, help="Business keyword")
    parser.add_argument("--city", required=True, help="City / Area")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--max-results", type=int, default=None, help="Maximum businesses to scrape")
    parser.add_argument("--no-emails", action="store_true", help="Skip email extraction")
    parser.add_argument("--timeout", type=int, default=300, help="Total timeout in seconds")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    KEYWORD = args.keyword
    CITY = args.city
    HEADLESS = args.headless
    MAX_RESULTS = args.max_results
    SKIP_EMAILS = args.no_emails
    TIMEOUT = args.timeout
    RESUME = args.resume
    
    query = f"{KEYWORD} in {CITY}"
    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"{safe_filename(KEYWORD)}_{safe_filename(CITY)}.json")
    
    logger.info(f"Starting scraper for: {query}")
    logger.info(f"Config: headless={HEADLESS}, max_results={MAX_RESULTS}, skip_emails={SKIP_EMAILS}")
    
    start_time = time.time()
    businesses = []
    start_index = 0
    
    # Check for checkpoint
    if RESUME:
        checkpoint = load_checkpoint(checkpoint_file)
        if checkpoint:
            businesses = checkpoint["businesses"]
            start_index = checkpoint["index"]
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS, slow_mo=50)
            page = browser.new_page()
            
            try:
                # Navigate to Google Maps
                logger.info("Loading Google Maps...")
                page.goto("https://www.google.com/maps", timeout=SEARCH_TIMEOUT)
                
                # Search
                logger.info(f"Searching for: {query}")
                search_box = get_selector(page, SEARCH_BOX_SELECTORS)
                if not search_box:
                    raise RuntimeError("Could not find search box")
                
                search_box.fill(query)
                time.sleep(1)
                page.keyboard.press("Enter")
                
                # Wait for results panel with smart wait
                logger.info("Waiting for results...")
                if not wait_for_selector(page, RESULTS_PANEL_SELECTORS, SEARCH_TIMEOUT):
                    raise RuntimeError("Results panel did not load")
                
                results_panel = get_selector(page, RESULTS_PANEL_SELECTORS)
                time.sleep(3)
                
                # Scroll to load all results
                logger.info("Scrolling results panel...")
                prev_height = 0
                scroll_count = 0
                
                for scroll_attempt in range(50):
                    if time.time() - start_time > TIMEOUT:
                        logger.warning(f"Global timeout reached ({TIMEOUT}s)")
                        break
                    
                    try:
                        page.evaluate(
                            "(panel) => panel.scrollBy(0, panel.scrollHeight)",
                            results_panel
                        )
                        time.sleep(DELAY_BETWEEN_SCROLL)
                        
                        curr_height = page.evaluate(
                            "(panel) => panel.scrollHeight",
                            results_panel
                        )
                        
                        if curr_height == prev_height:
                            logger.info("✅ No more new results")
                            break
                        
                        prev_height = curr_height
                        scroll_count += 1
                        
                    except Exception as e:
                        logger.error(f"Scroll error: {e}")
                        break
                
                logger.info(f"✅ Scrolling complete ({scroll_count} scrolls)")
                
                # Collect business cards (get count, not references)
                all_cards = page.query_selector_all(BUSINESS_CARD_SELECTOR)
                cards_count = len(all_cards)
                logger.info(f"📍 Total businesses found: {cards_count}")
                
                if MAX_RESULTS:
                    cards_count = min(cards_count, MAX_RESULTS)
                
                # Process businesses (by index to avoid stale element references)
                for index in range(cards_count):
                    if time.time() - start_time > TIMEOUT:
                        logger.warning("Global timeout reached, saving progress...")
                        break
                    
                    if start_index > 0 and index < start_index:
                        continue
                    
                    try:
                        time.sleep(DELAY_BETWEEN_BUSINESS)
                        
                        # Re-query card to avoid stale element reference
                        card = page.query_selector_all(BUSINESS_CARD_SELECTOR)[index]
                        
                        # Click business card with retry
                        def click_card():
                            card.click()
                        
                        retry_action(click_card)
                        
                        # Wait for details to load
                        if not wait_for_selector(page, BUSINESS_NAME_SELECTORS, BUSINESS_LOAD_TIMEOUT):
                            logger.warning(f"Skipping business {index}: details didn't load")
                            continue
                        
                        time.sleep(1)
                        
                        # Extract data
                        name = "N/A"
                        address = "N/A"
                        phone = "N/A"
                        website = "N/A"
                        emails = set()
                        
                        # Business Name
                        name_el = get_selector(page, BUSINESS_NAME_SELECTORS)
                        if name_el:
                            try:
                                name = name_el.inner_text().strip()
                            except Exception as e:
                                logger.debug(f"Error extracting name: {e}")
                        
                        # Validate name (skip junk/placeholder data)
                        if not name or name.lower() in {"results", "overview", "about", "reviews"}:
                            logger.warning(f"Skipping invalid name at index {index + 1}")
                            continue
                        
                        # Contact info from buttons
                        try:
                            buttons = page.query_selector_all("button")
                            for btn in buttons:
                                try:
                                    aria = btn.get_attribute("aria-label")
                                    if not aria:
                                        continue
                                    
                                    if "Address:" in aria:
                                        address = aria.replace("Address:", "").strip()
                                    elif "Phone:" in aria:
                                        phone = aria.replace("Phone:", "").strip()
                                    elif "Website:" in aria:
                                        website = aria.replace("Website:", "").strip()
                                except:
                                    continue
                        except Exception as e:
                            logger.debug(f"Error extracting contact info: {e}")
                        
                        # Email Extraction
                        if not SKIP_EMAILS and website != "N/A" and not should_skip_email_extraction(website):
                            try:
                                def extract_emails():
                                    page.goto(website, timeout=WEBSITE_LOAD_TIMEOUT)
                                    time.sleep(2)
                                    content = page.content()
                                    found_emails = extract_emails_from_text(content)
                                    return found_emails
                                
                                emails = retry_action(extract_emails)
                                time.sleep(DELAY_AFTER_EMAIL_EXTRACTION)
                                page.go_back()
                                time.sleep(1)
                            
                            except Exception as e:
                                logger.debug(f"Email extraction failed for {name}: {e}")
                                try:
                                    page.go_back()
                                except:
                                    pass
                        
                        business = {
                            "name": name,
                            "address": address,
                            "phone": phone,
                            "website": website,
                            "emails": ", ".join(sorted(emails)) if emails else "N/A"
                        }
                        
                        businesses.append(business)
                        logger.info(f"✅ {index + 1}. {name}")
                        
                        # Save checkpoint every 10 businesses
                        if (index + 1) % 10 == 0:
                            save_checkpoint(checkpoint_file, businesses, index + 1)
                    
                    except Exception as e:
                        logger.error(f"❌ Failed at business {index}: {e}")
                        continue
                
                logger.info(f"Processing complete. Total collected: {len(businesses)}")
            
            finally:
                browser.close()
        
        # Deduplication
        logger.info("Deduplicating businesses...")
        businesses = deduplicate_businesses(businesses)
        logger.info(f"🧹 After deduplication: {len(businesses)} businesses")
        
        # Display sample
        logger.info("\n📌 SAMPLE OUTPUT (first 5):")
        for b in businesses[:5]:
            logger.info(str(b))
        
        # Save CSV
        csv_file = os.path.join(OUTPUT_DIR, "businesses.csv")
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["name", "address", "phone", "website", "emails"]
            )
            writer.writeheader()
            writer.writerows(businesses)
        
        logger.info(f"📁 CSV saved → {csv_file}")
        
        # Save JSON
        json_file = os.path.join(OUTPUT_DIR, "businesses.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(businesses, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 JSON saved → {json_file}")
        
        # Statistics summary
        with_phone = sum(1 for b in businesses if b["phone"] != "N/A")
        with_website = sum(1 for b in businesses if b["website"] != "N/A")
        with_email = sum(1 for b in businesses if b["emails"] != "N/A")
        
        logger.info("\n" + "="*50)
        logger.info("📊 FINAL SUMMARY")
        logger.info("="*50)
        logger.info(f"Total businesses: {len(businesses)}")
        logger.info(f"With phone number: {with_phone} ({100*with_phone//len(businesses) if businesses else 0}%)")
        logger.info(f"With website: {with_website} ({100*with_website//len(businesses) if businesses else 0}%)")
        logger.info(f"With email: {with_email} ({100*with_email//len(businesses) if businesses else 0}%)")
        logger.info("="*50)
    
        # Cleanup checkpoint on success
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            logger.info("Checkpoint cleaned up")
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️  Total time: {elapsed:.1f}s")
        logger.info(f"📊 Log file: {log_file}")
    
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
