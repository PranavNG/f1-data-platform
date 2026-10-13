import fastf1
import pandas as pd
from pathlib import Path

START_SEASON = 2020
END_SEASON = 2026

REFERENCE_FILE = Path("data/reference/circuit_reference.csv")
OUTPUT_FILE = Path("data/circuits_clean.csv")

all_circuits = []

# -----------------------------------
# 1. Extract raw circuit information
# -----------------------------------
for season in range(START_SEASON, END_SEASON + 1):

    schedule = fastf1.get_event_schedule(season)

    # Remove testing / non-race events
    schedule = schedule[
        schedule["RoundNumber"] > 0
    ].copy()

    circuits = schedule[
        ["Location", "Country"]
    ].copy()

    all_circuits.append(circuits)

# Combine all seasons
circuits_df = pd.concat(
    all_circuits,
    ignore_index=True
)

# Keep unique raw FastF1 combinations
circuits_df = (
    circuits_df
    .drop_duplicates()
    .sort_values(["Country", "Location"])
    .reset_index(drop=True)
)

print("Unique raw circuits found:")
print(circuits_df)

print("\nTotal raw combinations:")
print(len(circuits_df))


# -----------------------------------
# 2. Load circuit reference mapping
# -----------------------------------
reference_df = pd.read_csv(
    REFERENCE_FILE
)

print("\nReference mappings loaded:")
print(len(reference_df))


# -----------------------------------
# 3. Merge FastF1 with reference data
# -----------------------------------
circuits_merged = circuits_df.merge(
    reference_df,
    left_on=["Location", "Country"],
    right_on=["raw_location", "raw_country"],
    how="left"
)


# -----------------------------------
# 4. Check for missing mappings
# -----------------------------------
missing = circuits_merged[
    circuits_merged["circuit_name"].isna()
]

print("\nMissing circuit mappings:")

if missing.empty:
    print("None")
else:
    print(
        missing[
            ["Location", "Country"]
        ]
    )


# Stop if mappings are missing
if not missing.empty:
    raise ValueError(
        "Some circuits are missing from circuit_reference.csv"
    )


# -----------------------------------
# 5. Build canonical circuit dataset
# -----------------------------------
circuits_clean_df = circuits_merged[
    [
        "circuit_name",
        "circuit_location",
        "circuit_country",
        "circuit_length_km"
    ]
].copy()

# Different raw labels may point to the same circuit
circuits_clean_df = (
    circuits_clean_df
    .drop_duplicates()
    .sort_values(
        by=[
            "circuit_country",
            "circuit_name"
        ]
    )
    .reset_index(drop=True)
)


# -----------------------------------
# 6. Save clean circuit data
# -----------------------------------
circuits_clean_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# -----------------------------------
# 7. Final check
# -----------------------------------
print("\nClean circuit data:")
print(circuits_clean_df)

print(
    "\nTotal canonical circuits:",
    len(circuits_clean_df)
)

print(
    f"\nSaved to {OUTPUT_FILE}"
)
