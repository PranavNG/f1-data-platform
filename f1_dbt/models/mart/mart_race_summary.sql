WITH race_results AS (

    SELECT
        rr.race_key,

        MAX(
            CASE
                WHEN rr.is_winner THEN rr.driver_key
            END
        ) AS winner_driver_key,

        MAX(
            CASE
                WHEN rr.is_winner THEN rr.team_key
            END
        ) AS winning_team_key,

        COUNT(*) AS starters,

        SUM(
            CASE
                WHEN rr.completed_race THEN 1
                ELSE 0
            END
        ) AS completed_drivers,

        SUM(
            CASE
                WHEN rr.completed_race THEN 0
                ELSE 1
            END
        ) AS non_completed_drivers,

        AVG(rr.positions_changed) AS avg_positions_changed,

        AVG(
            ABS(rr.positions_changed)
        ) AS avg_absolute_movement

    FROM {{ ref('stg_race_results') }} rr

    GROUP BY
        rr.race_key
),

qualifying AS (

    SELECT
        q.race_key,

        MAX(
            CASE
                WHEN q.qualifying_position = 1
                THEN q.driver_key
            END
        ) AS pole_driver_key

    FROM {{ ref('stg_qualifying') }} q

    GROUP BY
        q.race_key
)

SELECT
    r.race_key,
    r.season,
    r.round_number,
    r.official_event_name,
    r.event_date,
    r.event_format,
    r.circuit_key,

    rr.winner_driver_key,
    rr.winning_team_key,
    q.pole_driver_key,

    rr.starters,
    rr.completed_drivers,
    rr.non_completed_drivers,

    rr.avg_positions_changed,
    rr.avg_absolute_movement

FROM {{ ref('stg_race') }} r

LEFT JOIN race_results rr
    ON r.race_key = rr.race_key

LEFT JOIN qualifying q
    ON r.race_key = q.race_key
    