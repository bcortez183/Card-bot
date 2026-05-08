import os
import sys
import time
import datetime
import requests
import schedule
import pytz
import re

sys.stdout.flush()

# CONFIG
MIN_DISCOUNT     = 0.5
SCAN_INTERVAL    = 5
MAX_LISTINGS     = 60

TELEGRAM_TOKEN   = "8641980068:AAGQGSh1ooskkUPmg2DQz84pFjio3aiCh78"
TELEGRAM_CHAT_ID = "8773798653"

SEARCH_QUERIES = [
    # ── BASKETBALL ────────────────────────────────────────────────────────────
    # Luka Doncic
    "Luka Doncic rookie PSA",
    "Luka Doncic rookie raw",
    "Luka Doncic PSA 10",
    "Luka Doncic autograph",
    "Luka Doncic prizm",
    "Luka Doncic optic",
    "Luka Doncic select",
    "Luka Doncic mosaic",
    "Luka Doncic refractor",

    # Ja Morant
    "Ja Morant rookie PSA",
    "Ja Morant rookie raw",
    "Ja Morant PSA 10",
    "Ja Morant autograph",
    "Ja Morant prizm",
    "Ja Morant optic",

    # Victor Wembanyama
    "Victor Wembanyama rookie PSA",
    "Victor Wembanyama rookie raw",
    "Victor Wembanyama PSA 10",
    "Victor Wembanyama autograph",
    "Victor Wembanyama prizm",
    "Victor Wembanyama select",

    # LeBron James
    "LeBron James rookie PSA",
    "LeBron James rookie raw",
    "LeBron James PSA 10",
    "LeBron James autograph",
    "LeBron James prizm",
    "LeBron James refractor",
    "LeBron James mosaic",

    # Kobe Bryant
    "Kobe Bryant rookie PSA",
    "Kobe Bryant rookie raw",
    "Kobe Bryant PSA 10",
    "Kobe Bryant autograph",
    "Kobe Bryant refractor",
    "Kobe Bryant prizm",

    # Michael Jordan
    "Michael Jordan rookie PSA",
    "Michael Jordan PSA 10",
    "Michael Jordan autograph",
    "Michael Jordan refractor",
    "Michael Jordan fleer",

    # Stephen Curry
    "Stephen Curry rookie PSA",
    "Stephen Curry rookie raw",
    "Stephen Curry PSA 10",
    "Stephen Curry autograph",
    "Stephen Curry prizm",
    "Stephen Curry select",

    # Giannis Antetokounmpo
    "Giannis Antetokounmpo rookie PSA",
    "Giannis Antetokounmpo rookie raw",
    "Giannis Antetokounmpo PSA 10",
    "Giannis Antetokounmpo autograph",
    "Giannis Antetokounmpo prizm",

    # Jayson Tatum
    "Jayson Tatum rookie PSA",
    "Jayson Tatum rookie raw",
    "Jayson Tatum PSA 10",
    "Jayson Tatum autograph",
    "Jayson Tatum prizm",

    # Kevin Durant
    "Kevin Durant rookie PSA",
    "Kevin Durant PSA 10",
    "Kevin Durant autograph",
    "Kevin Durant prizm",

    # ── FOOTBALL ──────────────────────────────────────────────────────────────
    # Patrick Mahomes
    "Patrick Mahomes rookie PSA",
    "Patrick Mahomes rookie raw",
    "Patrick Mahomes PSA 10",
    "Patrick Mahomes autograph",
    "Patrick Mahomes prizm",
    "Patrick Mahomes optic",
    "Patrick Mahomes select",
    "Patrick Mahomes mosaic",
    "Patrick Mahomes refractor",

    # Josh Allen
    "Josh Allen rookie PSA",
    "Josh Allen rookie raw",
    "Josh Allen PSA 10",
    "Josh Allen autograph",
    "Josh Allen prizm",
    "Josh Allen optic",

    # Justin Jefferson
    "Justin Jefferson rookie PSA",
    "Justin Jefferson rookie raw",
    "Justin Jefferson PSA 10",
    "Justin Jefferson autograph",
    "Justin Jefferson prizm",

    # Joe Burrow
    "Joe Burrow rookie PSA",
    "Joe Burrow rookie raw",
    "Joe Burrow PSA 10",
    "Joe Burrow autograph",
    "Joe Burrow prizm",

    # Brock Purdy
    "Brock Purdy rookie PSA",
    "Brock Purdy rookie raw",
    "Brock Purdy PSA 10",
    "Brock Purdy autograph",
    "Brock Purdy prizm",

    # CJ Stroud
    "CJ Stroud rookie PSA",
    "CJ Stroud rookie raw",
    "CJ Stroud PSA 10",
    "CJ Stroud autograph",
    "CJ Stroud prizm",

    # Tom Brady
    "Tom Brady rookie PSA",
    "Tom Brady PSA 10",
    "Tom Brady autograph",
    "Tom Brady prizm",
    "Tom Brady refractor",

    # ── BASEBALL ──────────────────────────────────────────────────────────────
    # Aaron Judge
    "Aaron Judge rookie PSA",
    "Aaron Judge rookie raw",
    "Aaron Judge PSA 10",
    "Aaron Judge autograph",
    "Aaron Judge prizm",
    "Aaron Judge refractor",
    "Aaron Judge topps chrome",

    # Shohei Ohtani
    "Shohei Ohtani rookie PSA",
    "Shohei Ohtani rookie raw",
    "Shohei Ohtani PSA 10",
    "Shohei Ohtani autograph",
    "Shohei Ohtani prizm",
    "Shohei Ohtani topps chrome",

    # Ronald Acuna
    "Ronald Acuna rookie PSA",
    "Ronald Acuna rookie raw",
    "Ronald Acuna PSA 10",
    "Ronald Acuna autograph",
    "Ronald Acuna prizm",

    # Juan Soto
    "Juan Soto rookie PSA",
    "Juan Soto rookie raw",
    "Juan Soto PSA 10",
    "Juan Soto autograph",
    "Juan Soto prizm",

    # Fernando Tatis
    "Fernando Tatis rookie PSA",
    "Fernando Tatis rookie raw",
    "Fernando Tatis PSA 10",
    "Fernando Tatis autograph",
    "Fernando Tatis prizm",

    # Mike Trout
    "Mike Trout rookie PSA",
    "Mike Trout PSA 10",
    "Mike Trout autograph",
    "Mike Trout prizm",
    "Mike Trout refractor",

    # Julio Rodriguez
    "Julio Rodriguez rookie PSA",
    "Julio Rodriguez rookie raw",
    "Julio Rodriguez PSA 10",
    "Julio Rodriguez autograph",

    # Mookie Betts
    "Mookie Betts PSA 10",
    "Mookie Betts autograph",
    "Mookie Betts prizm",

    # ── F1 ────────────────────────────────────────────────────────────────────
    # Max Verstappen
    "Max Verstappen PSA 10",
    "Max Verstappen rookie raw",
    "Max Verstappen autograph",
    "Max Verstappen prizm",
    "Max Verstappen topps",
    "Max Verstappen chrome",
    "Max Verstappen refractor",

    # Lewis Hamilton
    "Lewis Hamilton PSA 10",
    "Lewis Hamilton autograph",
    "Lewis Hamilton prizm",
    "Lewis Hamilton topps",
    "Lewis Hamilton chrome",

    # Charles Leclerc
    "Charles Leclerc PSA 10",
    "Charles Leclerc autograph",
    "Charles Leclerc prizm",
    "Charles Leclerc topps",

    # Lando Norris
    "Lando Norris PSA 10",
    "Lando Norris autograph",
    "Lando Norris prizm",
    "Lando Norris topps",
    "Lando Norris trading card",

    # ── SOCCER ────────────────────────────────────────────────────────────────
    # Lamine Yamal
    "Lamine Yamal rookie PSA",
    "Lamine Yamal rookie raw",
    "Lamine Yamal PSA 10",
    "Lamine Yamal autograph",
    "Lamine Yamal prizm",
    "Lamine Yamal topps",

    # Lionel Messi
    "Lionel Messi PSA 10",
    "Lionel Messi autograph",
    "Lionel Messi prizm",
    "Lionel Messi topps",
    "Lionel Messi refractor",
    "Lionel Messi rookie PSA",

    # Cristiano Ronaldo
    "Cristiano Ronaldo PSA 10",
    "Cristiano Ronaldo autograph",
    "Cristiano Ronaldo prizm",
    "Cristiano Ronaldo topps",

    # Kylian Mbappe
    "Kylian Mbappe PSA 10",
    "Kylian Mbappe autograph",
    "Kylian Mbappe prizm",
    "Kylian Mbappe rookie PSA",

    # Erling Haaland
    "Erling Haaland PSA 10",
    "Erling Haaland autograph",
    "Erling Haaland prizm",
    "Erling Haaland rookie PSA",

    # Jude Bellingham
    "Jude Bellingham PSA 10",
    "Jude Bellingham autograph",
    "Jude Bellingham rookie PSA",

    # ── HOCKEY ────────────────────────────────────────────────────────────────
    # Connor McDavid
    "Connor McDavid rookie PSA",
    "Connor McDavid rookie raw",
    "Connor McDavid PSA 10",
    "Connor McDavid autograph",
    "Connor McDavid prizm",
    "Connor McDavid upper deck",

    # Alex Ovechkin
    "Alex Ovechkin rookie PSA",
    "Alex Ovechkin PSA 10",
    "Alex Ovechkin autograph",
    "Alex Ovechkin upper deck",

    # Sidney Crosby
    "Sidney Crosby rookie PSA",
    "Sidney Crosby PSA 10",
    "Sidney Crosby autograph",
    "Sidney Crosby upper deck",

    # Auston Matthews
    "Auston Matthews rookie PSA",
    "Auston Matthews PSA 10",
    "Auston Matthews autograph",

    # ── GOLF ──────────────────────────────────────────────────────────────────
    # Tiger Woods
    "Tiger Woods PSA 10",
    "Tiger Woods autograph",
    "Tiger Woods rookie PSA",
    "Tiger Woods upper deck",
    "Tiger Woods refractor",

    # Scottie Scheffler
    "Scottie Scheffler PSA 10",
    "Scottie Scheffler autograph",
    "Scottie Scheffler rookie",

    # ── TENNIS ────────────────────────────────────────────────────────────────
    "Roger Federer PSA 10",
    "Roger Federer autograph",
    "Rafael Nadal PSA 10",
    "Rafael Nadal autograph",
    "Novak Djokovic PSA 10",
    "Carlos Alcaraz rookie PSA",
    "Carlos Alcaraz autograph",

    # ── BOXING ────────────────────────────────────────────────────────────────
    "Canelo Alvarez PSA 10",
    "Canelo Alvarez autograph",
    "Tyson Fury PSA 10",
    "Ryan Garcia PSA 10",
    "Ryan Garcia autograph",

    # ── WWE ───────────────────────────────────────────────────────────────────
    "John Cena WWE PSA 10",
    "John Cena WWE autograph",
    "Roman Reigns WWE PSA 10",
    "The Rock WWE PSA 10",
    "Stone Cold Steve Austin PSA 10",

    # ── NASCAR ────────────────────────────────────────────────────────────────
    "Jeff Gordon NASCAR PSA 10",
    "Dale Earnhardt NASCAR PSA 10",
    "Chase Elliott NASCAR PSA 10",
    "Chase Elliott NASCAR autograph",

    # ── RUGBY ─────────────────────────────────────────────────────────────────
    "All Blacks rugby card PSA",
    "England rugby card PSA",
    
    # Cooper Flagg
    "Cooper Flagg rookie PSA",
    "Cooper Flagg rookie raw",
    "Cooper Flagg PSA 10",
    "Cooper Flagg autograph",
    "Cooper Flagg prizm",
    "Cooper Flagg select",
    "Cooper Flagg topps",

    # Wembanyama extra variations
    "Wembanyama bowman PSA",
    "Wembanyama bowman raw",
    "Wembanyama autograph",
    "Wembanyama prizm silver",
    "Wembanyama select",
    "Wembanyama mosaic",

    # New Topps Football
    "Topps football chrome PSA 10",
    "Topps football chrome autograph",
    "Topps football chrome refractor",
    "Topps football chrome rookie",

    # New Bowman Basketball
    "Bowman basketball chrome PSA 10",
    "Bowman basketball chrome autograph",
    "Bowman basketball chrome rookie",
    "Bowman University basketball PSA",
]

# HELPERS

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
    try:
        cleaned = re.sub(r"[^\d.]", "", str(price_str))
        return float(cleaned)
    except:
        return None

# EBAY SEARCH

def search_ebay_sold(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        search  = query.replace(" ", "+")
        url     = "https://www.ebay.com/sch/i.html?_nkw=" + search + "&LH_Sold=1&LH_Complete=1&_sop=13"
        r       = requests.get(url, headers=headers, timeout=10)
        prices  = []
        matches = re.findall(r'\$[\d,]+\.?\d*', r.text)
        for m in matches[:20]:
            p = clean_price(m)
            if p and 5 < p < 50000:
                prices.append(p)
        if len(prices) >= 3:
            return sum(prices[:10]) / len(prices[:10])
        return None
    except Exception as e:
        print("Sold search error: " + str(e))
        return None

def search_ebay_active(query):
    try:
        headers  = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        search   = query.replace(" ", "+")
        url      = "https://www.ebay.com/sch/i.html?_nkw=" + search + "&_sop=15&LH_BIN=1"
        r        = requests.get(url, headers=headers, timeout=10)
        listings = []
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

# DEAL DETECTION

alerted_deals = set()

def check_for_deals(query):
    sys.stdout.flush()
    avg_sold = search_ebay_sold(query)
    if not avg_sold:
        print("  No sold data: " + query)
        return

    listings = search_ebay_active(query)
    if not listings:
        print("  No listings: " + query)
        return

    print("  " + query + " | Avg: $" + str(round(avg_sold, 2)) + " | Listings: " + str(len(listings)))

    for listing in listings:
        price    = listing["price"]
        url      = listing["url"]
        discount = (avg_sold - price) / avg_sold

        if discount >= MIN_DISCOUNT:
            deal_key = str(round(price)) + "_" + query[:20]
            if deal_key in alerted_deals:
                continue

            profit_est = avg_sold - price
            deal_msg   = (
                "CARD DEAL FOUND!\n\n"
                "Card: " + query + "\n"
                "Listed: $" + str(round(price, 2)) + "\n"
                "Avg sold: $" + str(round(avg_sold, 2)) + "\n"
                "Discount: " + str(round(discount * 100)) + "% below market\n"
                "Est. profit: ~$" + str(round(profit_est, 2)) + "\n"
                "Link: " + url + "\n"
                "Time: " + now_pt().strftime("%I:%M %p PT")
            )

            print("\n" + deal_msg)
            send_telegram(deal_msg)
            alerted_deals.add(deal_key)

            if len(alerted_deals) > 500:
                alerted_deals.clear()

# MAIN SCAN

def scan():
    sys.stdout.flush()
    print("\n" + "="*55)
    print("  Sports Card Deal Scanner")
    print("  [" + now_pt().strftime("%Y-%m-%d %H:%M") + " PT]")
    print("  Scanning " + str(len(SEARCH_QUERIES)) + " searches...")
    print("="*55)

    for query in SEARCH_QUERIES:
        check_for_deals(query)
        time.sleep(2)

    print("\n  Scan complete. Next scan in " + str(SCAN_INTERVAL) + " minutes.\n")
    sys.stdout.flush()

# ENTRY POINT

if __name__ == "__main__":
    print("Sports Card Deal Finder Bot - All Variations Edition")
    print("Searches: " + str(len(SEARCH_QUERIES)))
    print("Min discount: " + str(int(MIN_DISCOUNT * 100)) + "% below market")
    print("Scan interval: every " + str(SCAN_INTERVAL) + " minutes")
    print("Telegram: " + ("enabled" if TELEGRAM_TOKEN else "disabled"))
    print()

    startup_msg = (
        "Sports Card Deal Bot started - All Variations Edition!\n"
        "Scanning " + str(len(SEARCH_QUERIES)) + " searches on eBay\n"
        "Cards: PSA, raw, autograph, prizm, refractor, optic, select, mosaic, chrome and more\n"
        "Sports: Basketball, Football, Baseball, F1, Soccer, Hockey, Golf, Tennis, Boxing, WWE, NASCAR, Rugby\n"
        "Alerting when cards are " + str(int(MIN_DISCOUNT * 100)) + "% below market value"
    )
    send_telegram(startup_msg)

    scan()
    schedule.every(SCAN_INTERVAL).minutes.do(scan)

    while True:
        schedule.run_pending()
        time.sleep(30)
