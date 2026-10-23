SELECT
    race_key,
    driver_key,
    team_key,
    stint,
    compound,

    MIN(lap_number) AS stint_start_lap,
    MAX(lap_number) AS stint_end_lap,
    COUNT(*) AS stint_lap_count,

    MIN(tyre_life) AS starting_tyre_life,
    MAX(tyre_life) AS ending_tyre_life,

    AVG(lap_time_seconds) AS avg_lap_time_seconds,
    MIN(lap_time_seconds) AS fastest_lap_seconds

FROM {{ ref('int_clean_race_laps') }}

WHERE
    stint IS NOT NULL
    AND compound IS NOT NULL

GROUP BY
    race_key,
    driver_key,
    team_key,
    stint,
    compound