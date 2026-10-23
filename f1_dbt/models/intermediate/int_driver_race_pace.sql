SELECT
    race_key,
    driver_key,
    team_key,

    COUNT(*) AS clean_lap_count,

    AVG(lap_time_seconds) AS avg_lap_time_seconds,
    MIN(lap_time_seconds) AS fastest_lap_seconds,

    AVG(sector_1_seconds) AS avg_sector_1_seconds,
    AVG(sector_2_seconds) AS avg_sector_2_seconds,
    AVG(sector_3_seconds) AS avg_sector_3_seconds

FROM {{ ref('int_clean_race_laps') }}

GROUP BY
    race_key,
    driver_key,
    team_key