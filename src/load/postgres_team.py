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

teams_clean_df = pd.read_csv("data/teams_clean.csv")
teams_clean_df = teams_clean_df.rename(columns={
    "TeamId": "team_id",
    "TeamName": "team_name",
    "TeamColor": "team_colour",
    "valid_from_season": "valid_from_season",
    "valid_to_season": "valid_to_season"
})

cursor = conn.cursor()

insert_query = """
INSERT INTO dim_team (
    team_id,
    team_name,
    team_colour,
    valid_from_season,
    valid_to_season
)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (team_id, valid_from_season) DO NOTHING;
"""


def sql_value(value):
    return None if pd.isna(value) else value


for _, row in teams_clean_df.iterrows():
    cursor.execute(
        insert_query,
        (
            row["team_id"],
            row["team_name"],
            row["team_colour"],
            int(row["valid_from_season"]),
            sql_value(row["valid_to_season"])
        )
    )

conn.commit()

print("Team data loaded successfully.")

cursor.close()
conn.close()
