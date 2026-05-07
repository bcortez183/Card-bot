"""
Sports Card Deal Finder Bot
============================
Scans eBay for underpriced sports cards by comparing
current listings against recent sold prices.

Sports covered:
- Basketball
- Baseball  
- Football
- F1

Sends Telegram alerts when it finds cards listed
significantly below their market value.

Setup:
  pip install requests schedule pytz

Environment variables:
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID

Usage:
  python sports_card_bot.py
"""

import os
import time
import datetime
import requests
import schedule
import pytz
import re

# ── CONFIG ────────────────────────────────────────────────────────────────────

# Minimum profit margin to trigger an alert (e.g. 0.30 = 30% below market)
MIN_DISCOUNT     = 0.30

# How often to scan in minutes
SCAN_INTERVAL    = 10

# Max listings to check per search
MAX_LISTINGS     = 20

# Telegram
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── SEARCH QUERIES ────────────────────────────────────────────────────────────
# Each entry is a search term the bot will scan on eBay
# Add or remove any players/cards you want

SEARCH_QUERIES = [
    # Basketball
    "Luka Doncic rookie PSA",
    "Ja Morant rookie PSA",
    "Victor Wembanyama rookie",
    "LeBron James rookie PSA",
    "Stephen Curry rookie PSA",
    "Giannis Antetokounmpo PSA 10",
    "Jayson Tatum rookie PSA",

    # Football
    "Patrick Mahomes rookie PSA",
    "Justin Jefferson rookie PSA",
    "Joe Burrow rookie PSA",
    "Josh Allen rookie PSA",
    "CJ Stroud rookie PSA",

    # Baseball
    "Ronald Acuna rookie PSA",
    "Juan Soto rookie PSA",
    "Shohei Ohtani rookie PSA",
    "Fernando Tatis rookie PSA",
    "Julio Rodriguez rookie PSA",

    # F1
    "Max Verstappen card PSA",
    "Lewis Hamilton card PSA",
    "Charles Leclerc card PSA",
    "Lando Norris card PSA",
]

# ── HELPERS ───────────────────────────────────────────────────────────────────

def now_pt():
    return datetime.datetime.now(pytz.timezone("America/Los_Angeles"))

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(message)
        return
    try:
        url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print("Telegram error: " + str(e))

def clean_price(price_str):
    """Extract float price from eBay price string."""
    try:
        cleaned = re.sub(r"[^\d.]", "", str(price_str))
        return float(cleaned)
    except:
        return None

# ── EBAY SEARCH ───────────────────────────────────────────────────────────────

def search_ebay_sold(query):
    """Get recent sold prices for a query from eBay."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        search  = query.replace(" ", "+")
        url     = "https://www.ebay.com/sch/i.html?_nkw=" + search + "&LH_Sold=1&LH_Complete=1&_sop=13"
        r       = requests.get(url, headers=headers, timeout=10)
        
        # Extract prices from sold listings
        prices  = []
        matches = re.findall(r'\$[\d,]+\.?\d*', r.text)
        for m in matches[:20]:
            p = clean_price(m)
            if p and 5 < p < 50000:
                prices.append(p)

        if len(prices) >= 3:
            # Return average of recent sold prices
            return sum(prices[:10]) / len(prices[:10])
        return None

    except Exception as e:
        print("Sold search error: " + str(e))
        return None


def search_ebay_active(query):
    """Get current active listings from eBay."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        search  = query.replace(" ", "+")
        url     = "https://www.ebay.com/sch/i.html?_nkw=" + search + "&_sop=15&LH_BIN=1"
        r       = requests.get(url, headers=headers, timeout=10)

        listings = []
        # Find prices and item URLs
        price_matches = re.findall(r'\$[\d,]+\.?\d*', r.text)
        url_matches   = re.findall(r'href="(https://www\.ebay\.com/itm/[^"]+)"', r.text)

        prices = []
        for m in price_matches[:30]:
            p = clean_price(m)
            if p and 5 < p < 50000:
                prices.append(p)

        for i, price in enumerate(prices[:MAX_LISTINGS]):
            url_link = url_matches[i] if i < len(url_matches) else "https://www.ebay.com/sch/i.html?_nkw=" + search
            listings.append({"price": price, "url": url_link})

        return listings

    except Exception as e:
        print("Active search error: " + str(e))
        return []


# ── DEAL DETECTION ────────────────────────────────────────────────────────────

# Track alerted deals to avoid spam
alerted_deals = set()

def check_for_deals(query):
    """Compare active listings vs sold prices and alert on deals."""
    avg_sold = search_ebay_sold(query)
    if not avg_sold:
        print("  No sold data for: " + query)
        return

    listings = search_ebay_active(query)
    if not listings:
        print("  No listings for: " + query)
        return

    print("  " + query + " | Avg sold: $" + str(round(avg_sold, 2)) + " | Listings: " + str(len(listings)))

    for listing in listings:
        price    = listing["price"]
        url      = listing["url"]
        discount = (avg_sold - price) / avg_sold

        if discount >= MIN_DISCOUNT:
            # Create unique key to avoid duplicate alerts
            deal_key = str(round(price)) + "_" + query[:20]
            if deal_key in alerted_deals:
                continue

            profit_est = avg_sold - price
            deal_msg   = (
                "🔥 CARD DEAL FOUND!\n\n"
                "🃏 " + query + "\n"
                "💰 Listed: $" + str(round(price, 2)) + "\n"
                "📊 Avg sold: $" + str(round(avg_sold, 2)) + "\n"
                "📉 Discount: " + str(round(discount * 100)) + "% below market\n"
                "💵 Est. profit: ~$" + str(round(profit_est, 2)) + "\n"
                "🔗 " + url + "\n"
                "🕐 " + now_pt().strftime("%I:%M %p PT")
            )

            print("\n" + deal_msg)
            send_telegram(deal_msg)
            alerted_deals.add(deal_key)

            # Keep set from growing too large
            if len(alerted_deals) > 500:
                alerted_deals.clear()


# ── MAIN SCAN ─────────────────────────────────────────────────────────────────

def scan():
    print("\n" + "="*55)
    print("  Sports Card Deal Scanner")
    print("  [" + now_pt().strftime("%Y-%m-%d %H:%M") + " PT]")
    print("  Scanning " + str(len(SEARCH_QUERIES)) + " searches...")
    print("="*55)

    for query in SEARCH_QUERIES:
        check_for_deals(query)
        time.sleep(2)  # polite delay between requests

    print("\n  Scan complete. Next scan in " + str(SCAN_INTERVAL) + " minutes.\n")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Sports Card Deal Finder Bot")
    print("Searches: " + str(len(SEARCH_QUERIES)))
    print("Min discount to alert: " + str(int(MIN_DISCOUNT * 100)) + "% below market")
    print("Scan interval: every " + str(SCAN_INTERVAL) + " minutes")
    print("Telegram: " + ("enabled" if TELEGRAM_TOKEN else "disabled"))
    print()

    startup_msg = (
        "🃏 Sports Card Deal Bot started!\n"
        "Scanning " + str(len(SEARCH_QUERIES)) + " searches on eBay\n"
        "Alerting when cards are " + str(int(MIN_DISCOUNT * 100)) + "%+ below market value\n\n"
        "Sports covered:\n"
        "🏀 Basketball | 🏈 Football | ⚾ Baseball | 🏎️ F1"
    )
    send_telegram(startup_msg)

    scan()
    schedule.every(SCAN_INTERVAL).minutes.do(scan)

    while True:
        schedule.run_pending()
        time.sleep(30)
