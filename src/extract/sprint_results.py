import fastf1
import pandas as pd
from pathlib import Path

RACES_FILE = Path("data/races_clean.csv")
OUTPUT_FILE = Path("data/sprint_results_clean.csv")

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))

races_df = pd.read_csv(RACES_FILE)

all_sprint_results = []

for _, race in races_df.iterrows():

    season = int(race["season"])
    round_number = int(race["round_number"])

    try:
        session = fastf1.get_session(
            season,
            round_number,
            "S"
        )

        session.load(
            laps=False,
            telemetry=False,
            weather=False,
            messages=False
        )

    except Exception:
        print(
            f"No Sprint: {season} Round {round_number}"
        )
        continue

    if session.results.empty:
        print(
            f"No Sprint results: {season} Round {round_number}"
        )
        continue

    print(
        f"Loading Sprint: {season} Round {round_number}"
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
            "Time": "sprint_time",
            "Status": "sprint_status"
        }
    )

    all_sprint_results.append(results)


if not all_sprint_results:
    raise ValueError(
        "No Sprint results were extracted."
    )


sprint_results_df = pd.concat(
    all_sprint_results,
    ignore_index=True
)


sprint_results_df["grid_position"] = (
    sprint_results_df["grid_position"]
    .astype("Int64")
)

sprint_results_df["finish_position"] = (
    sprint_results_df["finish_position"]
    .astype("Int64")
)

sprint_results_df["laps_completed"] = (
    sprint_results_df["laps_completed"]
    .astype("Int64")
)


# Remove completely empty placeholder rows
sprint_results_df["driver_id"] = (
    sprint_results_df["driver_id"]
    .replace(["nan", "", "None"], pd.NA)
)

sprint_results_df["team_id"] = (
    sprint_results_df["team_id"]
    .replace(["nan", "", "None"], pd.NA)
)

empty_rows = (
    sprint_results_df["driver_id"].isna()
    & sprint_results_df["team_id"].isna()
    & sprint_results_df["finish_position"].isna()
)

sprint_results_df = sprint_results_df[
    ~empty_rows
].copy()


# Validate IDs
missing_driver = sprint_results_df[
    sprint_results_df["driver_id"].isna()
]

if not missing_driver.empty:
    print(missing_driver)

    raise ValueError(
        "Sprint rows with missing driver_id found."
    )


# Check duplicates
duplicates = sprint_results_df.duplicated(
    subset=[
        "season",
        "round_number",
        "driver_id"
    ],
    keep=False
)

if duplicates.any():

    print(
        sprint_results_df[
            duplicates
        ]
    )

    raise ValueError(
        "Duplicate Sprint results found."
    )


sprint_results_df = sprint_results_df[
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
        "sprint_time",
        "sprint_status"
    ]
]


sprint_results_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSprint extraction complete.")
print("Total rows:", len(sprint_results_df))
print(f"Saved to {OUTPUT_FILE}")
