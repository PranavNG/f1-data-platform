SELECT
    qualifying_key,
    race_key,
    driver_key,
    team_key,
    qualifying_position,
    q1_time,
    q2_time,
    q3_time,

    EXTRACT(EPOCH FROM q1_time) AS q1_seconds,
    EXTRACT(EPOCH FROM q2_time) AS q2_seconds,
    EXTRACT(EPOCH FROM q3_time) AS q3_seconds

FROM {{ source('f1_warehouse', 'fact_qualifying') }}