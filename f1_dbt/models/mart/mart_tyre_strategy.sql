SELECT
    r.season,
    r.round_number,
    r.race_key,
    r.official_event_name,

    s.driver_key,
    d.full_name,
    d.abbreviation,

    s.team_key,
    t.team_name,

    s.stint,
    s.compound,

    s.stint_start_lap,
    s.stint_end_lap,
    s.stint_lap_count,

    s.starting_tyre_life,
    s.ending_tyre_life,

    s.avg_lap_time_seconds,
    s.fastest_lap_seconds

FROM {{ ref('int_tyre_stints') }} s

JOIN {{ ref('stg_race') }} r
    ON s.race_key = r.race_key

JOIN {{ ref('stg_driver') }} d
    ON s.driver_key = d.driver_key

JOIN {{ ref('stg_team') }} t
    ON s.team_key = t.team_key