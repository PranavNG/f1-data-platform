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
    "data/qualifying_clean.csv"
)

cursor = conn.cursor()


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


insert_query = """
INSERT INTO fact_qualifying (
    race_key,
    driver_key,
    team_key,
    qualifying_position,
    q1_time,
    q2_time,
    q3_time
)
VALUES (%s, %s, %s, %s, %s, %s, %s)

ON CONFLICT (race_key, driver_key)

DO UPDATE SET
    team_key = EXCLUDED.team_key,
    qualifying_position = EXCLUDED.qualifying_position,
    q1_time = EXCLUDED.q1_time,
    q2_time = EXCLUDED.q2_time,
    q3_time = EXCLUDED.q3_time;
"""


def nullable_int(value):
    return None if pd.isna(value) else int(value)


def parse_time(value):

    if pd.isna(value):
        return None

    timedelta = pd.to_timedelta(value)

    return timedelta.to_pytimedelta()


for _, row in df.iterrows():

    season = int(row["season"])
    round_number = int(row["round_number"])

    # -----------------------------
    # Race key
    # -----------------------------
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

    # -----------------------------
    # Driver key
    # -----------------------------
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

    # -----------------------------
    # Team key
    # -----------------------------
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

    # -----------------------------
    # Insert
    # -----------------------------
    cursor.execute(
        insert_query,
        (
            race_key,
            driver_key,
            team_key,
            nullable_int(
                row["qualifying_position"]
            ),
            parse_time(
                row["q1"]
            ),
            parse_time(
                row["q2"]
            ),
            parse_time(
                row["q3"]
            )
        )
    )


conn.commit()

print(
    "Qualifying data loaded successfully."
)

cursor.close()
conn.close()
