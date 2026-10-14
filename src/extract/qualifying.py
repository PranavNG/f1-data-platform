import fastf1
import pandas as pd
from pathlib import Path

RACES_FILE = Path("data/races_clean.csv")
OUTPUT_FILE = Path("data/qualifying_clean.csv")

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))

races_df = pd.read_csv(RACES_FILE)

all_qualifying = []

for _, race in races_df.iterrows():

    season = int(race["season"])
    round_number = int(race["round_number"])

    print(f"Loading qualifying: {season} Round {round_number}...")

    session = fastf1.get_session(
        season,
        round_number,
        "Q"
    )

    session.load(
        laps=False,
        telemetry=False,
        weather=False,
        messages=False
    )

    results = session.results[
        [
            "DriverId",
            "TeamId",
            "Position",
            "Q1",
            "Q2",
            "Q3"
        ]
    ].copy()

    results["season"] = season
    results["round_number"] = round_number

    results = results.rename(
        columns={
            "DriverId": "driver_id",
            "TeamId": "team_id",
            "Position": "qualifying_position",
            "Q1": "q1",
            "Q2": "q2",
            "Q3": "q3"
        }
    )

    all_qualifying.append(results)


qualifying_df = pd.concat(
    all_qualifying,
    ignore_index=True
)


qualifying_df["qualifying_position"] = (
    qualifying_df["qualifying_position"]
    .astype("Int64")
)


qualifying_df = qualifying_df[
    [
        "season",
        "round_number",
        "driver_id",
        "team_id",
        "qualifying_position",
        "q1",
        "q2",
        "q3"
    ]
]

# Convert string versions of missing IDs to real missing values
qualifying_df["driver_id"] = qualifying_df["driver_id"].replace(
    ["nan", "", "None"],
    pd.NA
)

qualifying_df["team_id"] = qualifying_df["team_id"].replace(
    ["nan", "", "None"],
    pd.NA
)
empty_rows = (
    qualifying_df["driver_id"].isna()
    & qualifying_df["team_id"].isna()
    & qualifying_df["qualifying_position"].isna()
    & qualifying_df["q1"].isna()
    & qualifying_df["q2"].isna()
    & qualifying_df["q3"].isna()
)

print("\nEmpty qualifying placeholder rows:")
print(
    qualifying_df[empty_rows][
        ["season", "round_number"]
    ]
)

qualifying_df = qualifying_df[
    ~empty_rows
].copy()

missing_driver = qualifying_df[
    qualifying_df["driver_id"].isna()
]

if not missing_driver.empty:
    print(missing_driver)
    raise ValueError(
        "Qualifying rows with data but missing driver_id found."
    )

# Check duplicates
duplicate_mask = qualifying_df.duplicated(
    subset=[
        "season",
        "round_number",
        "driver_id"
    ],
    keep=False
)

if duplicate_mask.any():

    print("\nDuplicate qualifying rows:")

    print(
        qualifying_df[
            duplicate_mask
        ].sort_values(
            [
                "season",
                "round_number",
                "driver_id"
            ]
        )
    )

    raise ValueError(
        "Duplicate driver qualifying results found."
    )


qualifying_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nQualifying extraction complete.")
print("Total rows:", len(qualifying_df))
print(f"Saved to {OUTPUT_FILE}")
