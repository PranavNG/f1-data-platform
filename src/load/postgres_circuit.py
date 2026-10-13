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
circuits_clean_df = pd.read_csv("data/circuits_clean.csv")

cursor = conn.cursor()

insert_query = """
INSERT INTO dim_circuit (
    circuit_name,
    circuit_location,
    circuit_country,
    circuit_length_km
)
VALUES (%s, %s, %s, %s)
ON CONFLICT (
    circuit_name,
    circuit_location,
    circuit_country
)
DO UPDATE SET
    circuit_length_km = EXCLUDED.circuit_length_km;
"""
for _, row in circuits_clean_df.iterrows():
    cursor.execute(
        insert_query,
        (
            row["circuit_name"],
            row["circuit_location"],
            row["circuit_country"],
            row["circuit_length_km"]
        )
    )

conn.commit()

print("Circuit data loaded successfully.")

cursor.close()
conn.close()
