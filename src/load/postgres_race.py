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

races_clean_df = pd.read_csv(
    "data/races_clean.csv"
)

cursor = conn.cursor()

circuit_lookup_query = """
SELECT circuit_key
FROM dim_circuit
WHERE circuit_name = %s
  AND circuit_location = %s
  AND circuit_country = %s;
"""

insert_query = """
INSERT INTO dim_race (
    season,
    round_number,
    official_event_name,
    event_date,
    event_format,
    circuit_key
)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (season, round_number)
DO UPDATE SET
    official_event_name = EXCLUDED.official_event_name,
    event_date = EXCLUDED.event_date,
    event_format = EXCLUDED.event_format,
    circuit_key = EXCLUDED.circuit_key;
"""

for _, row in races_clean_df.iterrows():

    cursor.execute(
        circuit_lookup_query,
        (
            row["circuit_name"],
            row["circuit_location"],
            row["circuit_country"]
        )
    )

    result = cursor.fetchone()

    if result is None:
        raise ValueError(
            f"No circuit found for "
            f"{row['circuit_name']} - "
            f"{row['circuit_location']}"
        )

    circuit_key = result[0]

    cursor.execute(
        insert_query,
        (
            int(row["season"]),
            int(row["round_number"]),
            row["official_event_name"],
            row["event_date"],
            row["event_format"],
            circuit_key
        )
    )

conn.commit()

print("Race data loaded successfully.")

cursor.close()
conn.close()
