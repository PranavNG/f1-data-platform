from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd


load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    host=DB_HOST,
    port=DB_PORT
)


df = pd.read_csv(
    "data/lap_times_clean.csv"
)


cursor = conn.cursor()


# --------------------------------------------------
# Lookups
# --------------------------------------------------
race_lookup_query = """
SELECT race_key
FROM dim_race
WHERE season = %s
  AND round_number = %s;
"""


driver_lookup_query = """
SELECT driver_key
FROM dim_driver
WHERE driver_id = %s;
"""


team_lookup_query = """
SELECT team_key
FROM dim_team
WHERE team_id = %s
  AND valid_from_season <= %s
  AND (
        valid_to_season >= %s
        OR valid_to_season IS NULL
      );
"""


# --------------------------------------------------
# Insert
# --------------------------------------------------
insert_query = """
INSERT INTO fact_lap_times (
    race_key,
    driver_key,
    team_key,
    lap_number,
    lap_time,
    sector_1_time,
    sector_2_time,
    sector_3_time,
    position,
    stint,
    compound,
    tyre_life,
    fresh_tyre,
    pit_in_time,
    pit_out_time,
    track_status,
    deleted,
    is_accurate,
    is_personal_best
)
VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s
)

ON CONFLICT (
    race_key,
    driver_key,
    lap_number
)

DO UPDATE SET
    team_key = EXCLUDED.team_key,
    lap_time = EXCLUDED.lap_time,
    sector_1_time = EXCLUDED.sector_1_time,
    sector_2_time = EXCLUDED.sector_2_time,
    sector_3_time = EXCLUDED.sector_3_time,
    position = EXCLUDED.position,
    stint = EXCLUDED.stint,
    compound = EXCLUDED.compound,
    tyre_life = EXCLUDED.tyre_life,
    fresh_tyre = EXCLUDED.fresh_tyre,
    pit_in_time = EXCLUDED.pit_in_time,
    pit_out_time = EXCLUDED.pit_out_time,
    track_status = EXCLUDED.track_status,
    deleted = EXCLUDED.deleted,
    is_accurate = EXCLUDED.is_accurate,
    is_personal_best = EXCLUDED.is_personal_best;
"""


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def nullable_int(value):
    return None if pd.isna(value) else int(value)


def nullable_float(value):
    return None if pd.isna(value) else float(value)


def nullable_text(value):
    return None if pd.isna(value) else str(value)


def nullable_bool(value):

    if pd.isna(value):
        return None

    if isinstance(value, bool):
        return value

    return str(value).lower() == "true"


def parse_time(value):

    if pd.isna(value):
        return None

    timedelta = pd.to_timedelta(value)

    return timedelta.to_pytimedelta()


# --------------------------------------------------
# Process rows
# --------------------------------------------------
for index, row in df.iterrows():

    season = int(row["season"])
    round_number = int(row["round_number"])

    # ----------------------------------------------
    # Race key
    # ----------------------------------------------
    cursor.execute(
        race_lookup_query,
        (
            season,
            round_number
        )
    )

    race_result = cursor.fetchone()

    if race_result is None:

        raise ValueError(
            f"Race not found: "
            f"{season} Round {round_number}"
        )

    race_key = race_result[0]

    # ----------------------------------------------
    # Driver key
    # ----------------------------------------------
    cursor.execute(
        driver_lookup_query,
        (
            row["driver_id"],
        )
    )

    driver_result = cursor.fetchone()

    if driver_result is None:

        raise ValueError(
            f"Driver not found: "
            f"{row['driver_id']}"
        )

    driver_key = driver_result[0]

    # ----------------------------------------------
    # Team key
    # ----------------------------------------------
    cursor.execute(
        team_lookup_query,
        (
            row["team_id"],
            season,
            season
        )
    )

    team_result = cursor.fetchone()

    if team_result is None:

        raise ValueError(
            f"Team not found: "
            f"{row['team_id']} "
            f"for season {season}"
        )

    team_key = team_result[0]

    # ----------------------------------------------
    # Insert lap
    # ----------------------------------------------
    cursor.execute(
        insert_query,
        (
            race_key,
            driver_key,
            team_key,

            int(row["lap_number"]),

            parse_time(
                row["lap_time"]
            ),

            parse_time(
                row["sector1_time"]
            ),

            parse_time(
                row["sector2_time"]
            ),

            parse_time(
                row["sector3_time"]
            ),

            nullable_int(
                row["position"]
            ),

            nullable_int(
                row["stint"]
            ),

            nullable_text(
                row["compound"]
            ),

            nullable_float(
                row["tyre_life"]
            ),

            nullable_bool(
                row["fresh_tyre"]
            ),

            parse_time(
                row["pit_in_time"]
            ),

            parse_time(
                row["pit_out_time"]
            ),

            nullable_text(
                row["track_status"]
            ),

            nullable_bool(
                row["deleted"]
            ),

            nullable_bool(
                row["is_accurate"]
            ),

            nullable_bool(
                row["is_personal_best"]
            )
        )
    )

    # Optional progress indicator
    if (index + 1) % 5000 == 0:

        print(
            f"Loaded {index + 1} laps..."
        )


conn.commit()


print(
    f"Lap data loaded successfully. "
    f"{len(df)} rows processed."
)


cursor.close()
conn.close()
