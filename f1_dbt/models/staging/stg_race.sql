SELECT
    race_key,
    season,
    round_number,
    official_event_name,
    event_date,
    event_format,
    circuit_key
FROM {{ source('f1_warehouse', 'dim_race') }}