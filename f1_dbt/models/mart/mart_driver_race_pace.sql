SELECT
    r.season,
    r.round_number,
    r.race_key,
    r.official_event_name,
    r.event_date,
    r.circuit_key,

    p.driver_key,
    d.full_name,
    d.abbreviation,

    p.team_key,
    t.team_name,

    p.clean_lap_count,

    p.avg_lap_time_seconds,
    p.fastest_lap_seconds,

    p.avg_sector_1_seconds,
    p.avg_sector_2_seconds,
    p.avg_sector_3_seconds

FROM {{ ref('int_driver_race_pace') }} p

JOIN {{ ref('stg_race') }} r
    ON p.race_key = r.race_key

JOIN {{ ref('stg_driver') }} d
    ON p.driver_key = d.driver_key

JOIN {{ ref('stg_team') }} t
    ON p.team_key = t.team_key