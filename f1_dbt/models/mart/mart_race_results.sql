WITH race_results AS (

    SELECT *
    FROM {{ ref('stg_race_results') }}

),

races AS (

    SELECT
        race_key,
        season,
        round_number,
        official_event_name,
        event_date
    FROM {{ ref('stg_race') }}

),

drivers AS (

    SELECT
        driver_key,
        full_name,
        abbreviation
    FROM {{ ref('stg_driver') }}

),

teams AS (

    SELECT
        team_key,
        team_name
    FROM {{ ref('stg_team') }}

)

SELECT
    r.season,
    r.round_number,
    r.official_event_name,
    r.event_date,
    rr.race_key,

    rr.driver_key,
    d.full_name,
    d.abbreviation,

    rr.team_key,
    t.team_name,

    rr.grid_position,
    rr.finish_position,
    rr.classified_position,
    rr.positions_changed,

    rr.points,
    rr.laps_completed,
    rr.race_time,
    rr.race_status,

    rr.is_winner,
    rr.is_podium,
    rr.completed_race

FROM race_results rr

LEFT JOIN races r
    ON rr.race_key = r.race_key

LEFT JOIN drivers d
    ON rr.driver_key = d.driver_key

LEFT JOIN teams t
    ON rr.team_key = t.team_key