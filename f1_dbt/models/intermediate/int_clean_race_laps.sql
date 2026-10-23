SELECT
    lap_key,
    race_key,
    driver_key,
    team_key,
    lap_number,

    lap_time,
    lap_time_seconds,

    sector_1_time,
    sector_1_seconds,

    sector_2_time,
    sector_2_seconds,

    sector_3_time,
    sector_3_seconds,

    position,
    stint,
    compound,
    tyre_life,
    fresh_tyre,

    pit_in_time,
    pit_out_time,
    is_pit_lap,

    track_status,
    track_status_clean,

    deleted,
    is_accurate,
    is_personal_best

FROM {{ ref('stg_lap_times') }}

WHERE
    lap_time IS NOT NULL
    AND COALESCE(deleted, FALSE) = FALSE
    AND COALESCE(is_accurate, FALSE) = TRUE
    AND is_pit_lap = FALSE