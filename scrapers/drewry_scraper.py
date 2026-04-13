import requests
import re
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
from datetime import date
import os

load_dotenv(Path(__file__).parent.parent / '.env')

def scrape_drewry():
    url = "https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text
    except Exception as e:
        print(f"❌ Failed to fetch Drewry: {e}")
        return

    # ── Extract SHA-LAX rate ──────────────────────────
    # Looks for "Los Angeles rose/fell X% to $X,XXX"
    # or "Los Angeles increased/decreased X% to $X,XXX"
    pattern = r'Los Angeles[^$]*\$([0-9,]+)'
    match = re.search(pattern, html)

    if not match:
        print("❌ Could not find SHA-LAX rate in page")
        print("Page snippet:", html[html.find('Los Angeles')-100:html.find('Los Angeles')+200])
        return

    rate_str = match.group(1).replace(',', '')
    rate = float(rate_str)
    today = date.today()

    print(f"✅ SHA-LAX rate found: ${rate:,.0f} as of {today}")

    # ── Insert into DB ────────────────────────────────
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="meridian_db",
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO rate_observations
            (lane, observed_date, rate_usd, container_type, rate_type, source)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (
        'SHA-LAX',
        today,
        rate,
        '40ft',
        'spot',
        'Drewry'
    ))

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ Inserted into DB")

if __name__ == "__main__":
    scrape_drewry()