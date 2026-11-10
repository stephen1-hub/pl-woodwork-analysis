
from pathlib import Path
import pandas as pd

FIXTURES_FILE = Path("data/raw/fixtures_mw1_mw10.csv")
RAW_DIR = Path("data/raw")

matchweek = 10

fixtures = pd.read_csv(FIXTURES_FILE)
mw_fixtures = fixtures[
    fixtures["matchweek"] == matchweek
]

successful = []
failed = []

for _, match in mw_fixtures.iterrows():

    match_id = int(match["match_id"])
    file_path = RAW_DIR / f"match_{match_id}_shots.csv"

    if not file_path.exists():
        failed.append({
            "match_id": match_id,
            "error": "Shot file missing"
        })
        continue

    df = pd.read_csv(file_path)

    if df.empty:
        failed.append({
            "match_id": match_id,
            "error": "Shot file is empty"
        })
        continue

    if not df["match_id"].eq(match_id).all():
        failed.append({
            "match_id": match_id,
            "error": "Match ID mismatch"
        })
        continue

    successful.append({
        "match_id": match_id,
        "shots": len(df),
        "woodwork": (df["eventType"] == "Post").sum(),
        "status": "success"
    })

report = pd.DataFrame(successful)

report_path = RAW_DIR / "matchweek_2_report.csv"
report.to_csv(report_path, index=False)

print("\nMATCHWEEK 2 VALIDATED REPORT")
print("=" * 50)
print(report.to_string(index=False))

print("\nSUMMARY")
print("=" * 50)
print("Fixtures:", len(mw_fixtures))
print("Successful:", len(successful))
print("Failed:", len(failed))
print("Total shots:", report["shots"].sum())
print("Woodwork events:", report["woodwork"].sum())

if failed:
    print("\nFAILED MATCHES:")
    print(pd.DataFrame(failed).to_string(index=False))
