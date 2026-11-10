
import sys
import json
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


def extract_shots(match_id, match_url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        match_url,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")

    if script is None:
        raise ValueError("FotMob match data was not found.")

    data = json.loads(script.string)

    content = data["props"]["pageProps"]["content"]

    # Diagnose shotmap availability
    print("Content keys:", list(content.keys()))
    print("Shotmap available:", content.get("shotmap") is not None)

    shotmap = content.get("shotmap")

    if shotmap is None:
        print("No shotmap data available.")
        return

    print("Shotmap keys:", list(shotmap.keys()))

    shots = shotmap.get("shots", [])

    print("Shot records:", len(shots))


    print("\nMATCH STATISTICS AVAILABLE:")

    stats = content.get("stats", {})

    print("Stats type:", type(stats).__name__)
    print("Stats keys:", list(stats.keys()) if isinstance(stats, dict) else "Not a dictionary")

    print("\nPLAYER STATISTICS AVAILABLE:")
    player_stats = content.get("playerStats", {})
    print("Player stats type:", type(player_stats).__name__)
    print("Player stats keys:", list(player_stats.keys()) if isinstance(player_stats, dict) else "Not a dictionary")


    shots_df = pd.DataFrame(shots)

    if shots_df.empty:
        print(f"No shot records returned for match {match_id}.")
        return

    shots_df["match_id"] = int(match_id)

    shots_df["is_woodwork"] = (
        shots_df["eventType"] == "Post"
    )

    output_path = Path(
        f"data/raw/match_{match_id}_shots.csv"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    shots_df.to_csv(output_path, index=False)

    print("\nPREMIER LEAGUE SHOT EXTRACTION")
    print("--------------------------------")
    print("Match ID:", match_id)
    print("Total shots:", len(shots_df))
    print("Woodwork events:", shots_df["is_woodwork"].sum())
    print("Saved to:", output_path)

    return len(shots_df)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(
            "Usage: python src/extract.py MATCH_ID MATCH_URL"
        )
        sys.exit(1)

    extract_shots(sys.argv[1], sys.argv[2])
