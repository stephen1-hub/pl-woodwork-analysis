
import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.dialects.postgresql import insert

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
FILE = "data/raw/fixtures_mw1_mw10.csv"


def load_fixtures():

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing. Check your .env file.")

    # Read fixture data
    df = pd.read_csv(FILE)

    df["match_date"] = pd.to_datetime(
        df["match_date"], utc=True
    )

    columns = [
        "match_id",
        "matchweek",
        "match_date",
        "home_team",
        "away_team",
        "home_team_id",
        "away_team_id",
        "score",
        "status"
    ]

    df = df[columns]

    records = df.to_dict(orient="records")

    engine = create_engine(DATABASE_URL)

    try:
        metadata = MetaData()

        matches_table = Table(
            "matches",
            metadata,
            autoload_with=engine
        )

        # Insert fixtures, skipping existing match IDs
        statement = insert(matches_table).values(records)

        statement = statement.on_conflict_do_nothing(
            index_elements=["match_id"]
        )

        with engine.begin() as connection:
            result = connection.execute(statement)

            total = connection.execute(
                text("SELECT COUNT(*) FROM matches")
            ).scalar()

        print("FIXTURE DATABASE LOAD COMPLETE")
        print("--------------------------------")
        print("New fixtures inserted:", result.rowcount)
        print("Total fixtures in database:", total)

    finally:
        engine.dispose()


if __name__ == "__main__":
    load_fixtures()
