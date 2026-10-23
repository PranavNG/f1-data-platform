SELECT
    r.season,
    r.round_number,
    r.race_key,
    r.official_event_name,

    l.driver_key,
    d.full_name,
    d.abbreviation,

    l.team_key,
    t.team_name,

    l.lap_number,
    l.position,

    l.compound,
    l.tyre_life,
    l.stint,

    l.lap_time_seconds,
    l.track_status_clean,

    l.is_pit_lap,
    l.is_accurate

FROM {{ ref('stg_lap_times') }} l

JOIN {{ ref('stg_race') }} r
    ON l.race_key = r.race_key

JOIN {{ ref('stg_driver') }} d
    ON l.driver_key = d.driver_key

JOIN {{ ref('stg_team') }} t
    ON l.team_key = t.team_key

WHERE
    l.position IS NOT NULL