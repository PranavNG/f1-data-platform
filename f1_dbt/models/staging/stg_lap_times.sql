SELECT
    lap_key,
    race_key,
    driver_key,
    team_key,
    lap_number,

    lap_time,
    sector_1_time,
    sector_2_time,
    sector_3_time,

    EXTRACT(EPOCH FROM lap_time) AS lap_time_seconds,
    EXTRACT(EPOCH FROM sector_1_time) AS sector_1_seconds,
    EXTRACT(EPOCH FROM sector_2_time) AS sector_2_seconds,
    EXTRACT(EPOCH FROM sector_3_time) AS sector_3_seconds,

    position,
    stint,
    compound,
    tyre_life,
    fresh_tyre,

    pit_in_time,
    pit_out_time,

    CASE
        WHEN pit_in_time IS NOT NULL
          OR pit_out_time IS NOT NULL
        THEN TRUE
        ELSE FALSE
    END AS is_pit_lap,

    track_status,

    REPLACE(track_status, '.0', '') AS track_status_clean,

    deleted,
    is_accurate,
    is_personal_best

FROM {{ source('f1_warehouse', 'fact_lap_times') }}