import fastf1
import pandas as pd
from pathlib import Path

RACES_FILE = Path("data/races_clean.csv")
OUTPUT_FILE = Path("data/race_results_clean.csv")

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))

races_df = pd.read_csv(RACES_FILE)

all_results = []

for _, race in races_df.iterrows():

    season = int(race["season"])
    round_number = int(race["round_number"])

    print(f"Loading {season} Round {round_number}...")

    session = fastf1.get_session(
        season,
        round_number,
        "R"
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
            "GridPosition",
            "Position",
            "ClassifiedPosition",
            "Points",
            "Laps",
            "Time",
            "Status"
        ]
    ].copy()

    results["season"] = season
    results["round_number"] = round_number

    results = results.rename(
        columns={
            "DriverId": "driver_id",
            "TeamId": "team_id",
            "GridPosition": "grid_position",
            "Position": "finish_position",
            "ClassifiedPosition": "classified_position",
            "Points": "points",
            "Laps": "laps_completed",
            "Time": "race_time",
            "Status": "race_status"
        }
    )

    all_results.append(results)


# Combine all races
race_results_df = pd.concat(
    all_results,
    ignore_index=True
)


# Convert position/lap columns to nullable integers
race_results_df["grid_position"] = (
    race_results_df["grid_position"]
    .astype("Int64")
)

race_results_df["finish_position"] = (
    race_results_df["finish_position"]
    .astype("Int64")
)

race_results_df["laps_completed"] = (
    race_results_df["laps_completed"]
    .astype("Int64")
)


# Reorder columns
race_results_df = race_results_df[
    [
        "season",
        "round_number",
        "driver_id",
        "team_id",
        "grid_position",
        "finish_position",
        "classified_position",
        "points",
        "laps_completed",
        "race_time",
        "race_status"
    ]
]


# Check uniqueness
# duplicates = race_results_df.duplicated(
#    subset=[
#        "season",
#        "round_number",
#        "driver_id"
#    ]
# )
print("\nMissing driver IDs:")
print(
    race_results_df[
        race_results_df["driver_id"].isna()
        | (race_results_df["driver_id"] == "")
    ][
        [
            "season",
            "round_number",
            "driver_id",
            "team_id"
        ]
    ]
)

duplicate_mask = race_results_df.duplicated(
    subset=[
        "season",
        "round_number",
        "driver_id"
    ],
    keep=False
)

duplicate_rows = race_results_df[
    duplicate_mask
].sort_values(
    [
        "season",
        "round_number",
        "driver_id"
    ]
)

print("\nDuplicate rows:")
print(
    duplicate_rows[
        [
            "season",
            "round_number",
            "driver_id",
            "team_id",
            "grid_position",
            "finish_position",
            "race_status"
        ]
    ]
)

if duplicate_mask.any():
    raise ValueError(
        "Duplicate driver results found for a race."
    )

# if duplicates.any():
#    raise ValueError(
#        "Duplicate driver results found for a race."
#    )


race_results_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nRace results extraction complete.")
print("Total rows:", len(race_results_df))
print(f"Saved to {OUTPUT_FILE}")
