
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def export_query(engine, query, filename):
    df = pd.read_sql(query, engine)

    output_path = OUTPUT_DIR / filename
    df.to_csv(output_path, index=False)

    print(f"Exported: {filename} ({len(df)} rows)")


def main():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing. Check your .env file.")

    engine = create_engine(DATABASE_URL)

    queries = {
        "match_summary.csv": """
            SELECT
                match_id,
                matchweek,
                match_date,
                home_team,
                away_team,
                score,
                COUNT(*) AS total_shots,
                COUNT(*) FILTER (
                    WHERE is_on_target = TRUE
                ) AS shots_on_target,
                COUNT(*) FILTER (
                    WHERE is_blocked = TRUE
                ) AS blocked_shots,
                COUNT(*) FILTER (
                    WHERE event_type = 'Goal'
                ) AS goals,
                COUNT(*) FILTER (
                    WHERE is_woodwork = TRUE
                ) AS woodwork_events,
                ROUND(SUM(expected_goals)::numeric, 3) AS total_xg
            FROM shot_analysis
            GROUP BY
                match_id, matchweek, match_date,
                home_team, away_team, score
        """,

        "team_shooting_summary.csv": """
            SELECT
                match_id,
                CASE
                    WHEN team_id = home_team_id THEN home_team
                    WHEN team_id = away_team_id THEN away_team
                    ELSE 'Unknown'
                END AS team_name,
                COUNT(*) AS total_shots,
                COUNT(*) FILTER (
                    WHERE is_on_target = TRUE
                ) AS shots_on_target,
                COUNT(*) FILTER (
                    WHERE is_blocked = TRUE
                ) AS blocked_shots,
                COUNT(*) FILTER (
                    WHERE event_type = 'Goal'
                ) AS goals,
                COUNT(*) FILTER (
                    WHERE is_woodwork = TRUE
                ) AS woodwork_events,
                ROUND(SUM(expected_goals)::numeric, 3) AS total_xg
            FROM shot_analysis
            GROUP BY match_id, team_name
        """,

        "player_woodwork_summary.csv": """
            SELECT
                player_name,
                COUNT(*) AS total_shots,
                COUNT(*) FILTER (
                    WHERE is_woodwork = TRUE
                ) AS woodwork_events,
                COUNT(DISTINCT match_id) FILTER (
                    WHERE is_woodwork = TRUE
                ) AS matches_with_woodwork,
                ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE is_woodwork = TRUE
                    ) / NULLIF(COUNT(*), 0),
                    2
                ) AS woodwork_per_100_shots
            FROM shot_analysis
            WHERE player_name IS NOT NULL
            GROUP BY player_name
            ORDER BY woodwork_events DESC,
                     woodwork_per_100_shots DESC
        """,

        "team_woodwork_summary.csv": """
            SELECT
                CASE
                    WHEN team_id = home_team_id THEN home_team
                    WHEN team_id = away_team_id THEN away_team
                    ELSE 'Unknown'
                END AS team_name,
                COUNT(*) AS total_shots,
                COUNT(*) FILTER (
                    WHERE is_woodwork = TRUE
                ) AS woodwork_events,
                ROUND(
                    100.0 * COUNT(*) FILTER (
                        WHERE is_woodwork = TRUE
                    ) / NULLIF(COUNT(*), 0),
                    2
                ) AS woodwork_per_100_shots
            FROM shot_analysis
            GROUP BY team_name
            ORDER BY woodwork_events DESC,
                     woodwork_per_100_shots DESC
        """
    }

    try:
        print("\nANALYSIS EXPORT")
        print("----------------")

        for filename, query in queries.items():
            export_query(engine, query, filename)

        print("\nAll analysis files exported successfully.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
