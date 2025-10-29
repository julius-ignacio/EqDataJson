import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://earthquake.phivolcs.dost.gov.ph/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PHIVOLCS-Scraper/1.0)"}
OUTPUT_FILENAME = "earthquake_data.json"

print("🌋 Fetching latest earthquake data from PHIVOLCS...")
resp = requests.get(URL, headers=HEADERS, verify=False, timeout=15)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

# Find the PHIVOLCS LATEST EARTHQUAKE INFORMATION header
header = soup.find(lambda tag: tag.name in ["b", "strong"] and "LATEST EARTHQUAKE INFORMATION" in tag.get_text())
if not header:
    print("❌ Could not find LATEST EARTHQUAKE INFORMATION header.")
    exit(1)

# Find the first table after the header (month header)
month_table = header.find_next("table")
if not month_table:
    print("❌ Could not find month header table.")
    exit(1)

# Find the actual earthquake data table after the month header table
table = month_table.find_next("table")
if not table:
    print("❌ Could not find earthquake data table.")
    exit(1)

earthquakes = []
rows = table.find_all("tr")[1:]  # skip header

for row in rows[:10]:  # Only the top 10
    cols = row.find_all("td")
    print("Row columns:", [td.get_text(strip=True) for td in cols])
    if len(cols) < 6:
        continue
    time = cols[0].get_text(strip=True)
    magnitude = cols[4].get_text(strip=True)
    location = cols[5].get_text(strip=True)
    earthquakes.append({
        "time": time,
        "magnitude": magnitude,
        "location": location,
    })

if not earthquakes:
    print("⚠️ No data extracted.")
    exit(1)

# Save to JSON
base_path = os.path.join(os.getcwd(), "..", "..", "StreamingAssets")
if not os.path.isdir(base_path):
    base_path = os.path.join(os.getcwd(), "StreamingAssets")
    if not os.path.isdir(base_path):
        base_path = os.getcwd()
output_path = os.path.join(base_path, OUTPUT_FILENAME)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(earthquakes, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(earthquakes)} earthquake records to: {output_path}")