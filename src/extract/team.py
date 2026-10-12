import os
from datetime import datetime

import fastf1
import pandas as pd

fastf1.Cache.enable_cache("data/cache")

START_SEASON = 2020
END_SEASON = 2026

CHECKPOINT_FILE = "data/team_checkpoint.txt"
OUTPUT_FILE = "data/teams_partial.csv"

all_team_data = []

if os.path.exists(OUTPUT_FILE):
    previous_df = pd.read_csv(OUTPUT_FILE)
    all_team_data.append(previous_df)

last_season = None
last_round = None

if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        checkpoint = f.read().strip()

        if checkpoint:
            last_season, last_round = map(int, checkpoint.split(","))

for season in range(START_SEASON, END_SEASON + 1):

    schedule = fastf1.get_event_schedule(season)

    for _, event in schedule.iterrows():

        round_number = int(event["RoundNumber"])

        # Skip testing
        if round_number == 0:
            continue

        # Skip future races
        event_date = pd.to_datetime(event["EventDate"])

        if event_date > pd.Timestamp.now(tz=event_date.tz):
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

        race = fastf1.get_session(
            season,
            event["EventName"],
            "R"
        )

        race.load(
            laps=False,
            telemetry=False,
            weather=False,
            messages=False
        )

        team_data = race.results[
            [
                "TeamId",
                "TeamName",
                "TeamColor"
            ]
        ].copy()

        team_data["Season"] = season

        all_team_data.append(team_data)

        # Save checkpoint
        with open(CHECKPOINT_FILE, "w") as f:
            f.write(f"{season},{round_number}")

teams_df = pd.concat(
    all_team_data,
    ignore_index=True
)

teams_df["TeamId"] = teams_df["TeamId"].replace("", pd.NA)

teams_df = teams_df[
    teams_df["TeamId"].notna()
].copy()

# Clean TeamColor
teams_df["TeamColor"] = (
    teams_df["TeamColor"]
    .replace("nan", pd.NA)
    .str.upper()
)


def last_non_empty(series):
    cleaned = series.replace("", pd.NA).dropna()

    if cleaned.empty:
        return pd.NA

    return cleaned.iloc[-1]


teams_df = (
    teams_df
    .groupby(
        ["Season", "TeamId", "TeamName"],
        as_index=False
    )
    .agg({
        "TeamColor": last_non_empty
    })
)

teams_df = teams_df.sort_values(
    by=["Season", "TeamId"]
)

teams_df = teams_df.sort_values(
    by=[
        "Season",
        "TeamId"
    ]
)

teams_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nClean season-level team history:")
print(teams_df.to_string(index=False))

latest_colors = (
    teams_df
    .sort_values("Season")
    .groupby("TeamId")["TeamColor"]
    .apply(last_non_empty)
    .to_dict()
)

validity_rows = []

for team_id, group in teams_df.groupby("TeamId"):

    group = group.sort_values("Season").reset_index(drop=True)

    start_season = group.loc[0, "Season"]
    current_name = group.loc[0, "TeamName"]

    for i in range(1, len(group)):

        season = group.loc[i, "Season"]
        team_name = group.loc[i, "TeamName"]

        # Only create a new version when the team name changes
        if team_name == current_name:
            continue

        validity_rows.append({
            "TeamId": team_id,
            "TeamName": current_name,
            "TeamColor": latest_colors[team_id],
            "valid_from_season": start_season,
            "valid_to_season": group.loc[i - 1, "Season"]
        })

        start_season = season
        current_name = team_name

    # Final/current version
    last_season = group["Season"].max()

    validity_rows.append({
        "TeamId": team_id,
        "TeamName": current_name,
        "TeamColor": latest_colors[team_id],
        "valid_from_season": start_season,
        "valid_to_season": None if last_season == END_SEASON else last_season
    })

teams_clean_df = pd.DataFrame(validity_rows)

teams_clean_df = teams_clean_df.sort_values(
    by=["TeamId", "valid_from_season"]

)
teams_clean_df["valid_from_season"] = (
    teams_clean_df["valid_from_season"].astype("Int64")
)

teams_clean_df["valid_to_season"] = (
    teams_clean_df["valid_to_season"].astype("Int64")
)

teams_clean_df.to_csv(
    "data/teams_clean.csv",
    index=False
)

print("\nFinal dim_team dataset:")
print(teams_clean_df.to_string(index=False))
