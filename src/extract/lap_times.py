import fastf1
import pandas as pd
from pathlib import Path
from fastf1.exceptions import DataNotLoadedError

RACES_FILE = Path("data/races_clean.csv")

PARTIAL_FILE = Path("data/lap_times_partial.csv")
OUTPUT_FILE = Path("data/lap_times_clean.csv")
CHECKPOINT_FILE = Path("data/lap_times_checkpoint.txt")

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))

races_df = pd.read_csv(RACES_FILE)

completed_races = set()

if CHECKPOINT_FILE.exists():

    with open(CHECKPOINT_FILE, "r") as file:

        for line in file:

            line = line.strip()

            if line:
                completed_races.add(line)


print(
    f"Completed races from checkpoint: "
    f"{len(completed_races)}"
)

for _, race in races_df.iterrows():

    season = int(race["season"])
    round_number = int(race["round_number"])

    race_id = f"{season}-{round_number}"

    if race_id in completed_races:

        print(
            f"Skipping {season} Round {round_number}"
        )

        continue

    print(
        f"\nLoading laps: "
        f"{season} Round {round_number}..."
    )

    session = fastf1.get_session(
        season,
        round_number,
        "R"
    )

    try:
        session.load(
            laps=True,
            telemetry=False,
            weather=False,
            messages=False
        )

        # Force-check that lap data is actually available
        if session.laps.empty:
            print(
                f"No lap data available for "
                f"{season} Round {round_number}. Skipping."
            )
            continue

    except DataNotLoadedError:
        print(
            f"Race data not yet available for "
            f"{season} Round {round_number}. Skipping."
        )
        continue

    driver_mapping = session.results[
        [
            "Abbreviation",
            "DriverId",
            "TeamId"
        ]
    ].copy()

    driver_mapping = driver_mapping.rename(
        columns={
            "Abbreviation": "Driver",
            "DriverId": "driver_id",
            "TeamId": "team_id"
        }
    )

    # --------------------------------------------------
    # Select lap fields
    # --------------------------------------------------
    laps = session.laps[
        [
            "Driver",
            "LapNumber",
            "LapTime",
            "Sector1Time",
            "Sector2Time",
            "Sector3Time",
            "Position",
            "Stint",
            "Compound",
            "TyreLife",
            "FreshTyre",
            "PitInTime",
            "PitOutTime",
            "TrackStatus",
            "Deleted",
            "IsAccurate",
            "IsPersonalBest"
        ]
    ].copy()

    # --------------------------------------------------
    # Map abbreviation → DriverId / TeamId
    # --------------------------------------------------
    laps = laps.merge(
        driver_mapping,
        on="Driver",
        how="left"
    )

    laps["season"] = season
    laps["round_number"] = round_number

    # --------------------------------------------------
    # Rename columns
    # --------------------------------------------------
    laps = laps.rename(
        columns={
            "LapNumber": "lap_number",
            "LapTime": "lap_time",
            "Sector1Time": "sector1_time",
            "Sector2Time": "sector2_time",
            "Sector3Time": "sector3_time",
            "Position": "position",
            "Stint": "stint",
            "Compound": "compound",
            "TyreLife": "tyre_life",
            "FreshTyre": "fresh_tyre",
            "PitInTime": "pit_in_time",
            "PitOutTime": "pit_out_time",
            "TrackStatus": "track_status",
            "Deleted": "deleted",
            "IsAccurate": "is_accurate",
            "IsPersonalBest": "is_personal_best"
        }
    )

    # --------------------------------------------------
    # Clean integer-like fields
    # --------------------------------------------------
    laps["lap_number"] = (
        laps["lap_number"]
        .astype("Int64")
    )

    laps["position"] = (
        laps["position"]
        .astype("Int64")
    )

    laps["stint"] = (
        laps["stint"]
        .astype("Int64")
    )

    # --------------------------------------------------
    # Validate driver mapping
    # --------------------------------------------------
    missing_driver = laps[
        laps["driver_id"].isna()
    ]

    if not missing_driver.empty:

        print(
            missing_driver[
                [
                    "Driver",
                    "season",
                    "round_number",
                    "lap_number"
                ]
            ].head(20)
        )

        raise ValueError(
            f"Missing driver mapping for "
            f"{season} Round {round_number}"
        )

    laps["track_status"] = laps["track_status"].astype("string")

    # --------------------------------------------------
    # Final column order
    # --------------------------------------------------
    laps = laps[
        [
            "season",
            "round_number",
            "driver_id",
            "team_id",
            "lap_number",
            "lap_time",
            "sector1_time",
            "sector2_time",
            "sector3_time",
            "position",
            "stint",
            "compound",
            "tyre_life",
            "fresh_tyre",
            "pit_in_time",
            "pit_out_time",
            "track_status",
            "deleted",
            "is_accurate",
            "is_personal_best"
        ]
    ]

    # --------------------------------------------------
    # Check uniqueness within race
    # --------------------------------------------------
    duplicate_mask = laps.duplicated(
        subset=[
            "season",
            "round_number",
            "driver_id",
            "lap_number"
        ],
        keep=False
    )

    if duplicate_mask.any():

        print(
            laps[
                duplicate_mask
            ][
                [
                    "season",
                    "round_number",
                    "driver_id",
                    "lap_number"
                ]
            ]
        )

        raise ValueError(
            f"Duplicate laps found for "
            f"{season} Round {round_number}"
        )

    # --------------------------------------------------
    # Append race to partial CSV
    # --------------------------------------------------
    write_header = not PARTIAL_FILE.exists()

    laps.to_csv(
        PARTIAL_FILE,
        mode="a",
        header=write_header,
        index=False
    )

    # --------------------------------------------------
    # Save checkpoint only AFTER data was saved
    # --------------------------------------------------
    with open(
        CHECKPOINT_FILE,
        "a"
    ) as file:

        file.write(
            race_id + "\n"
        )

    print(
        f"Saved {len(laps)} laps for "
        f"{season} Round {round_number}"
    )


# --------------------------------------------------
# Finalize dataset
# --------------------------------------------------
if not PARTIAL_FILE.exists():

    raise ValueError(
        "No lap data was extracted."
    )


lap_times_df = pd.read_csv(
    PARTIAL_FILE
)


# Final duplicate check
duplicate_mask = lap_times_df.duplicated(
    subset=[
        "season",
        "round_number",
        "driver_id",
        "lap_number"
    ],
    keep=False
)


if duplicate_mask.any():

    print(
        lap_times_df[
            duplicate_mask
        ].head(50)
    )

    raise ValueError(
        "Duplicate laps found in final dataset."
    )


lap_times_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\nLap extraction complete.")
print("Total lap rows:", len(lap_times_df))
print(f"Saved to {OUTPUT_FILE}")
