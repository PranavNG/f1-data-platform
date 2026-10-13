import fastf1
import pandas as pd
from pathlib import Path

START_SEASON = 2020
END_SEASON = 2026

REFERENCE_FILE = Path("data/reference/circuit_reference.csv")
OUTPUT_FILE = Path("data/races_clean.csv")

all_races = []

# -----------------------------
# 1. Extract race schedules
# -----------------------------
for season in range(START_SEASON, END_SEASON + 1):

    schedule = fastf1.get_event_schedule(season)

    # Keep only actual race rounds
    schedule = schedule[
        schedule["RoundNumber"] > 0
    ].copy()

    # Add season explicitly
    schedule["season"] = season

    # Keep only races that have already happened
    schedule["EventDate"] = pd.to_datetime(
        schedule["EventDate"]
    )

    today = pd.Timestamp.today().normalize()

    schedule = schedule[
        schedule["EventDate"] <= today
    ].copy()

    races = schedule[
        [
            "season",
            "RoundNumber",
            "OfficialEventName",
            "EventDate",
            "EventFormat",
            "Location",
            "Country"
        ]
    ].copy()

    all_races.append(races)

# -----------------------------
# 2. Combine all seasons
# -----------------------------
races_df = pd.concat(
    all_races,
    ignore_index=True
)

# -----------------------------
# 3. Load circuit mapping
# -----------------------------
reference_df = pd.read_csv(
    REFERENCE_FILE
)

# -----------------------------
# 4. Map raw FastF1 location
#    to canonical circuit
# -----------------------------
races_merged = races_df.merge(
    reference_df,
    left_on=["Location", "Country"],
    right_on=["raw_location", "raw_country"],
    how="left"
)

# -----------------------------
# 5. Check for missing mappings
# -----------------------------
missing = races_merged[
    races_merged["circuit_name"].isna()
]

if not missing.empty:
    print("Missing circuit mappings:")
    print(
        missing[
            [
                "season",
                "RoundNumber",
                "Location",
                "Country"
            ]
        ]
    )

    raise ValueError(
        "Some races could not be mapped to a circuit."
    )

# -----------------------------
# 6. Build clean race dataset
# -----------------------------
races_clean_df = races_merged[
    [
        "season",
        "RoundNumber",
        "OfficialEventName",
        "EventDate",
        "EventFormat",
        "circuit_name",
        "circuit_location",
        "circuit_country"
    ]
].copy()

races_clean_df = races_clean_df.rename(
    columns={
        "RoundNumber": "round_number",
        "OfficialEventName": "official_event_name",
        "EventDate": "event_date",
        "EventFormat": "event_format"
    }
)

# Keep only date, not timestamp
races_clean_df["event_date"] = (
    pd.to_datetime(
        races_clean_df["event_date"]
    ).dt.date
)

# -----------------------------
# 7. Sort and validate
# -----------------------------
races_clean_df = (
    races_clean_df
    .sort_values(
        by=["season", "round_number"]
    )
    .reset_index(drop=True)
)

duplicates = races_clean_df.duplicated(
    subset=["season", "round_number"]
)

if duplicates.any():
    raise ValueError(
        "Duplicate season + round_number detected."
    )

# -----------------------------
# 8. Save
# -----------------------------
races_clean_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(races_clean_df)

print(
    "\nTotal races:",
    len(races_clean_df)
)

print(
    f"\nSaved to {OUTPUT_FILE}"
)
