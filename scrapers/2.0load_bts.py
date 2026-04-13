import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

file_path = Path(__file__).parent.parent / "db" / "4.13_West_Coast_Shipping_Rates_data.csv"

df = pd.read_csv(
    file_path,
    encoding="utf-16",
    sep="\t"
)

# Clean column names
df.columns = df.columns.str.strip()

print("Raw columns:", df.columns.tolist())
print("Shape:", df.shape)
print(df.head(3))

# Pick the right rate column automatically
rate_col = None
for candidate in ["Value", "Rate", "value", "rate"]:
    if candidate in df.columns:
        rate_col = candidate
        break

if rate_col is None:
    raise ValueError(f"Could not find a rate column. Available columns: {df.columns.tolist()}")

# Keep only needed columns
keep_cols = ["Date", rate_col]
if "Origin" in df.columns:
    keep_cols.append("Origin")

df = df[keep_cols].copy()

# If Origin exists, keep only LA rows
if "Origin" in df.columns:
    df = df[df["Origin"].str.strip() == "U.S. West Coast (Los Angeles)"]

# Parse date
df["observed_date"] = pd.to_datetime(
    df["Date"].astype(str).str.replace("12:00:00 a.m.", "", regex=False).str.strip(),
    errors="coerce"
).dt.date

# Parse rate
df["rate_usd"] = pd.to_numeric(df[rate_col], errors="coerce")

# Drop bad rows
df = df.dropna(subset=["observed_date", "rate_usd"])

# Remove duplicate dates inside the file
df = df.drop_duplicates(subset=["observed_date"]).sort_values("observed_date")

print(f"\nClean rows ready to insert: {len(df)}")
print(df[["observed_date", "rate_usd"]].head())
print(df[["observed_date", "rate_usd"]].tail())

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="meridian_db",
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
cur = conn.cursor()

# Add unique constraint once if not already there
cur.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'uq_rate_observations_lane_date_source'
        ) THEN
            ALTER TABLE rate_observations
            ADD CONSTRAINT uq_rate_observations_lane_date_source
            UNIQUE (lane, observed_date, source);
        END IF;
    END
    $$;
""")

rows = [
    ("SHA-LAX", row.observed_date, float(row.rate_usd), "40ft", "spot", "BTS")
    for row in df.itertuples(index=False)
]

execute_values(
    cur,
    """
    INSERT INTO rate_observations
        (lane, observed_date, rate_usd, container_type, rate_type, source)
    VALUES %s
    ON CONFLICT (lane, observed_date, source)
    DO UPDATE SET
        rate_usd = EXCLUDED.rate_usd,
        container_type = EXCLUDED.container_type,
        rate_type = EXCLUDED.rate_type
    """,
    rows
)

conn.commit()
cur.close()
conn.close()

print(f"\n✅ Done — {len(rows)} rows inserted/updated")