import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from pathlib import Path

URL = "https://www.fotmob.com/leagues/47/fixtures/premier-league?group=by-round&round=0"

response = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
script = soup.find("script", id="__NEXT_DATA__")

if script is None:
    raise ValueError("FotMob page data not found.")

data = json.loads(script.string)
page_props = data["props"]["pageProps"]

all_matches = page_props["fixtures"]["allMatches"]

# Keep completed matches from Matchweeks 1–10
matches = []

for match in all_matches:
    round_number = int(match["round"])

    if round_number > 10:
        continue

    if not match["status"]["finished"]:
        continue

    home = match["home"]
    away = match["away"]
    status = match["status"]

    matches.append({
        "matchweek": round_number,
        "match_date": status["utcTime"],
        "home_team": home["name"],
        "away_team": away["name"],
        "home_team_id": home["id"],
        "away_team_id": away["id"],
        "score": status.get("scoreStr"),
        "match_id": match["id"],
        "match_url": "https://www.fotmob.com" + match["pageUrl"],
        "status": "completed"
    })

df = pd.DataFrame(matches)

output_path = Path("data/raw/fixtures_mw1_mw10.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)

print("FIXTURE EXTRACTION")
print("------------------")
print("Completed matches:", len(df))
print("Matchweeks:", sorted(df["matchweek"].unique()))
print("\nMatches per matchweek:")
print(df["matchweek"].value_counts().sort_index())
print("\nSaved to:", output_path)