import pandas as pd

FILE = "data/raw/fixtures_mw1_mw10.csv"

df = pd.read_csv(FILE)

print("FIXTURE DATA QUALITY REPORT")
print("---------------------------")

print("Total records:", len(df))
print("Unique match IDs:", df["match_id"].nunique())

print("\nDuplicate match IDs:")
print(df["match_id"].duplicated().sum())

print("\nMissing values:")
print(df.isnull().sum())

print("\nMatchweek distribution:")
print(df["matchweek"].value_counts().sort_index())

print("\nSample records:")
print(df[[
    "matchweek",
    "home_team",
    "away_team",
    "score",
    "match_id"
]].head(10).to_string(index=False))