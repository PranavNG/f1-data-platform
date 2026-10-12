import os
import pandas as pd
import fastf1

fastf1.Cache.enable_cache("data/cache")

START_SEASON = 2020
END_SEASON = 2026

CHECKPOINT_FILE = "data/driver_checkpoint.txt"
OUTPUT_FILE = "data/drivers_partial.csv"

all_driver_data = []

# Load previously collected driver data if it exists
if os.path.exists(OUTPUT_FILE):
    previous_df = pd.read_csv(OUTPUT_FILE)
    all_driver_data.append(previous_df)

# Read checkpoint if it exists
last_season = None
last_round = None

if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        checkpoint = f.read().strip()

        if checkpoint:
            last_season, last_round = map(int, checkpoint.split(","))


def last_non_empty(series):
    cleaned = series.replace("", pd.NA).dropna()

    if cleaned.empty:
        return pd.NA

    return cleaned.iloc[-1]


for season in range(START_SEASON, END_SEASON + 1):

    schedule = fastf1.get_event_schedule(season)

    for _, event in schedule.iterrows():

        round_number = int(event["RoundNumber"])

        # Skip testing
        if round_number == 0:
            continue

        # Skip races already processed
        if last_season is not None:

            if season < last_season:
                continue

            if season == last_season and round_number <= last_round:
                continue

        print(
            f"Processing {season} "
            f"Round {round_number}: {event['EventName']}"
        )

        try:
            race = fastf1.get_session(
                season,
                event["EventName"],
                "R"
            )

            # Lightweight session load
            race.load(
                laps=False,
                telemetry=False,
                weather=False,
                messages=False
            )

            driver_data = race.results[
                [
                    "DriverId",
                    "DriverNumber",
                    "Abbreviation",
                    "FirstName",
                    "LastName",
                    "FullName",
                    "CountryCode"
                ]
            ].copy()

            all_driver_data.append(driver_data)

            # Combine everything collected so far
            combined_df = pd.concat(
                all_driver_data,
                ignore_index=True
            )

            # Build one row per driver
            combined_df = (
                combined_df
                .groupby("DriverId", as_index=False)
                .agg({
                    "DriverNumber": last_non_empty,
                    "Abbreviation": last_non_empty,
                    "FirstName": last_non_empty,
                    "LastName": last_non_empty,
                    "FullName": last_non_empty,
                    "CountryCode": last_non_empty
                })
            )

            # Save progress
            combined_df.to_csv(
                OUTPUT_FILE,
                index=False
            )

            # Save latest completed race
            with open(CHECKPOINT_FILE, "w") as f:
                f.write(f"{season},{round_number}")

            print(
                f"Saved progress — "
                f"{len(combined_df)} unique drivers"
            )

        except Exception as e:
            print(
                f"Stopped at {season} "
                f"Round {round_number}"
            )
            print(e)
            raise


# Final combined driver table
drivers_df = pd.concat(
    all_driver_data,
    ignore_index=True
)

drivers_df = (
    drivers_df
    .groupby("DriverId", as_index=False)
    .agg({
        "DriverNumber": last_non_empty,
        "Abbreviation": last_non_empty,
        "FirstName": last_non_empty,
        "LastName": last_non_empty,
        "FullName": last_non_empty,
        "CountryCode": last_non_empty
    })
)

country_fallback = {
    "aitken": "GBR",
    "antonelli": "ITA",
    "arvid_lindblad": "GBR",
    "bortoleto": "BRA",
    "giovinazzi": "ITA",
    "grosjean": "FRA",
    "hadjar": "FRA",
    "kubica": "POL",
    "kvyat": "RUS",
    "mazepin": "RUS",
    "pietro_fittipaldi": "BRA",
    "raikkonen": "FIN"
}

drivers_df["CountryCode"] = drivers_df.apply(
    lambda row: country_fallback.get(row["DriverId"], row["CountryCode"])
    if pd.isna(row["CountryCode"])
    else row["CountryCode"],
    axis=1
)

drivers_df.to_csv("data/drivers_clean.csv", index=False)
print("\nExtraction complete")
print(drivers_df.shape)
