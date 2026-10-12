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

drivers_df = pd.read_csv("data/drivers_clean.csv")
drivers_df = drivers_df.rename(columns={
    "DriverId": "driver_id",
    "DriverNumber": "driver_number",
    "Abbreviation": "abbreviation",
    "FirstName": "first_name",
    "LastName": "last_name",
    "FullName": "full_name",
    "CountryCode": "country_code"
})
cursor = conn.cursor()

insert_query = """
INSERT INTO dim_driver (
    driver_id,
    driver_number,
    abbreviation,
    first_name,
    last_name,
    full_name,
    country_code
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (driver_id) DO NOTHING;
"""

for _, row in drivers_df.iterrows():
    cursor.execute(
        insert_query,
        (
            row["driver_id"],
            row["driver_number"],
            row["abbreviation"],
            row["first_name"],
            row["last_name"],
            row["full_name"],
            row["country_code"]
        )
    )

conn.commit()

print("Driver data loaded successfully.")

cursor.close()
conn.close()
