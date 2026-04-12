import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
from pathlib import Path
load_dotenv(Path(__file__).parent.parent / '.env')

# Load dataframe
df = pd.read_csv('../db/4.12.bts_sha_lax.csv',
                 encoding='utf-16',
                 sep='\t'
                 )

print("Raw columns:", df.columns.tolist())
print("Shape:", df.shape)
print(df.head(3))

# Clean the data - Keep only what we need
df = df[['Date', "Rate"]].copy()

# Parse the date — strip the time portion
df['observed_date'] = pd.to_datetime(
    df['Date'].str.replace('12:00:00 a.m.', '').str.strip()
).dt.date

# Drop any rows with missing rates
df = df.dropna(subset=['Rate'])
df['rate_usd'] = pd.to_numeric(df['Rate'], errors='coerce')
df = df.dropna(subset=['rate_usd'])

print(f"\nClean rows ready to insert: {len(df)}")
print(df[['observed_date', 'rate_usd']].head(5))

# ── Connect to DB ─────────────────────────────────────
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="meridian_db",
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
cur = conn.cursor()

# ── Insert ────────────────────────────────────────────
inserted = 0
skipped  = 0

for _, row in df.iterrows():
    try:
        cur.execute("""
            INSERT INTO rate_observations
                (lane, observed_date, rate_usd, container_type, rate_type, source)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'SHA-LAX',
            row['observed_date'],
            row['rate_usd'],
            '40ft',
            'spot',
            'BTS'
        ))
        inserted += 1
    except Exception as e:
        print(f"  Skipped {row['observed_date']}: {e}")
        skipped += 1

conn.commit()
cur.close()
conn.close()

print(f"\n✅ Done — {inserted} rows inserted, {skipped} skipped")