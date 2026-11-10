
import sys
import time
from pathlib import Path

import pandas as pd

from extract import extract_shots

FIXTURES_FILE = Path("data/raw/fixtures_mw1_mw10.csv")
OUTPUT_DIR = Path("data/raw")
REQUEST_DELAY = 10


def extract_matchweek(matchweek):
    fixtures = pd.read_csv(FIXTURES_FILE)

    week_fixtures = fixtures[
        fixtures["matchweek"] == matchweek
    ]

    if week_fixtures.empty:
        print(f"No fixtures found for Matchweek {matchweek}.")
        return

    print(f"\nMATCHWEEK {matchweek} EXTRACTION")
    print("=" * 40)
    print("Fixtures found:", len(week_fixtures))

    successful = []
    failed = []
    skipped = []

    for _, match in week_fixtures.iterrows():
        match_id = int(match["match_id"])
        match_url = match["match_url"]

        output_file = OUTPUT_DIR / f"match_{match_id}_shots.csv"

        print(
            f"\nProcessing: {match['home_team']} "
            f"vs {match['away_team']}"
        )
        print("Match ID:", match_id)

        if output_file.exists():
            print("Already extracted. Skipping.")
            skipped.append(match_id)
            continue

        try:
            shot_count = extract_shots(match_id, match_url)

            if shot_count and shot_count > 0:
                successful.append({
                    "match_id": match_id,
                    "shots": shot_count,
                    "status": "success"
                })
            else:
                failed.append({
                    "match_id": match_id,
                    "error": "No shot records returned"
                })

        except Exception as error:
            print("Extraction failed:", error)
            failed.append({
                "match_id": match_id,
                "error": str(error)
            })

        if match_id != int(week_fixtures.iloc[-1]["match_id"]):
            time.sleep(REQUEST_DELAY)

    report = pd.DataFrame(successful)

    report_path = OUTPUT_DIR / f"matchweek_{matchweek}_report.csv"
    report.to_csv(report_path, index=False)

    if failed:
        pd.DataFrame(failed).to_csv(
            OUTPUT_DIR / f"matchweek_{matchweek}_failed.csv",
            index=False
        )

    print("\nMATCHWEEK SUMMARY")
    print("=" * 40)
    print("Successful:", len(successful))
    print("Skipped:", len(skipped))
    print("Failed:", len(failed))
    print("Report:", report_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/extract_matchweek.py MATCHWEEK")
        sys.exit(1)

    matchweek = int(sys.argv[1])
    extract_matchweek(matchweek)
