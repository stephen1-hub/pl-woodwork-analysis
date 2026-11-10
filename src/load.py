
import os
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.dialects.postgresql import insert

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# File location
PROCESSED_FILE = Path("data/processed/shots_cleaned.csv")


def load_shots():

    # Check database configuration
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing. Check your .env file.")

    # Read processed data
    df = pd.read_csv(PROCESSED_FILE)

    # Convert missing values to Python None
    df = df.astype(object).where(pd.notna(df), None)

    # Convert DataFrame to records
    records = df.to_dict(orient="records")

    # Create database connection
    engine = create_engine(DATABASE_URL)

    try:
        # Load existing PostgreSQL table structure
        metadata = MetaData()
        shots_table = Table(
            "shots",
            metadata,
            autoload_with=engine
        )

        # Prepare insert statement
        statement = insert(shots_table).values(records)

        # Skip records that already exist
        statement = statement.on_conflict_do_nothing(
            index_elements=["match_id", "id"]
        )

        # Execute database insertion
        with engine.begin() as connection:
            result = connection.execute(statement)

        # Verify database records
        with engine.connect() as connection:
            total_records = connection.execute(
                text("SELECT COUNT(*) FROM shots")
            ).scalar()

        print("DATABASE LOAD COMPLETE")
        print("-----------------------")
        print("New records inserted:", result.rowcount)
        print("Total database records:", total_records)
        print("Table name: shots")
        print("Database: pl_woodwork_db")

    finally:
        engine.dispose()


if __name__ == "__main__":
    load_shots()
