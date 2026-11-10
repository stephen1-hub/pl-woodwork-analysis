
from pathlib import Path
import pandas as pd

FIXTURES_FILE = Path("data/raw/fixtures_mw1_mw10.csv")
DATA_DIR = Path("data/raw")

fixtures = pd.read_csv(FIXTURES_FILE)
mw1 = fixtures[fixtures["matchweek"] == 1]

results = []

for _, match in mw1.iterrows():
    match_id = int(match["match_id"])
    file_path = DATA_DIR / f"match_{match_id}_shots.csv"

    if not file_path.exists():
        results.append({
            "match_id": match_id,
            "match": f"{match['home_team']} vs {match['away_team']}",
            "shots": 0,
            "woodwork": 0,
            "duplicates": None,
            "status": "MISSING FILE"
        })
        continue

    df = pd.read_csv(file_path)

    results.append({
        "match_id": match_id,
        "match": f"{match['home_team']} vs {match['away_team']}",
        "shots": len(df),
        "woodwork": (df["eventType"] == "Post").sum(),
        "duplicates": df["id"].duplicated().sum(),
        "status": "OK"
    })

report = pd.DataFrame(results)

print("\nMATCHWEEK 1 DATA VALIDATION")
print("=" * 65)
print(report.to_string(index=False))

print("\nFINAL SUMMARY")
print("=" * 65)
print("Fixtures:", len(report))
print("Files found:", (report["status"] == "OK").sum())
print("Total shots:", report["shots"].sum())
print("Total woodwork:", report["woodwork"].sum())
print("Duplicate shot IDs:", report["duplicates"].fillna(0).sum())
print("Missing files:", (report["status"] == "MISSING FILE").sum())

report.to_csv(
    "data/processed/matchweek_1_validation.csv",
    index=False
)
