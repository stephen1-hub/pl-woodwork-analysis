
import sys
import pandas as pd
from pathlib import Path

FIXTURES_FILE = Path("data/raw/fixtures_mw1_mw10.csv")
RAW_DIR = Path("data/raw")
PROCESSED_FILE = Path("data/processed/shots_cleaned.csv")


def transform_shots(matchweek):

    fixtures = pd.read_csv(FIXTURES_FILE)

    week_fixtures = fixtures[
        fixtures["matchweek"] == matchweek
    ]

    if week_fixtures.empty:
        raise ValueError(f"No fixtures found for Matchweek {matchweek}")

    all_shots = []
    missing_matches = []

    for _, match in week_fixtures.iterrows():

        match_id = int(match["match_id"])
        raw_file = RAW_DIR / f"match_{match_id}_shots.csv"

        if not raw_file.exists():
            missing_matches.append({
                "match_id": match_id,
                "fixture": f"{match['home_team']} vs {match['away_team']}",
                "reason": "Shot file missing"
            })
            continue

        df_match = pd.read_csv(raw_file)

        if df_match.empty:
            missing_matches.append({
                "match_id": match_id,
                "fixture": f"{match['home_team']} vs {match['away_team']}",
                "reason": "Shot file is empty"
            })
            continue

        if not df_match["match_id"].eq(match_id).all():
            missing_matches.append({
                "match_id": match_id,
                "fixture": f"{match['home_team']} vs {match['away_team']}",
                "reason": "Match ID mismatch"
            })
            continue

        all_shots.append(df_match)

    if not all_shots:
        raise ValueError("No valid shot files available for transformation.")

    df = pd.concat(all_shots, ignore_index=True)

    df["playerName"] = (
        df["playerName"].astype("string").str.strip()
    )

    df["is_woodwork"] = df["eventType"].eq("Post")

    outcome_mapping = {
        "Goal": "Goal",
        "AttemptSaved": "Saved",
        "Miss": "Missed",
        "Post": "Woodwork"
    }

    df["shot_outcome"] = (
        df["eventType"].map(outcome_mapping).fillna("Other")
    )

    df = df.drop_duplicates(subset=["match_id", "id"])

    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_FILE, index=False)

    print(f"\nMATCHWEEK {matchweek} TRANSFORMATION")
    print("=" * 45)
    print("Expected fixtures:", len(week_fixtures))
    print("Matches processed:", df["match_id"].nunique())
    print("Processed shots:", len(df))
    print("Woodwork events:", int(df["is_woodwork"].sum()))
    print("Duplicate records:", df.duplicated(["match_id", "id"]).sum())
    print("Missing/unverified matches:", len(missing_matches))
    print("Saved to:", PROCESSED_FILE)

    if missing_matches:
        print("\nMATCHES REQUIRING ATTENTION")
        print("=" * 45)
        print(pd.DataFrame(missing_matches).to_string(index=False))


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python src/transform.py MATCHWEEK")
        sys.exit(1)

    transform_shots(int(sys.argv[1]))
