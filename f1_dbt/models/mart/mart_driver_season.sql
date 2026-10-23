WITH race_results AS (

    SELECT
        r.season,
        rr.driver_key,

        COUNT(*) AS races_started,
        SUM(rr.points) AS race_points,

        SUM(CASE WHEN rr.is_winner THEN 1 ELSE 0 END) AS race_wins,
        SUM(CASE WHEN rr.is_podium THEN 1 ELSE 0 END) AS race_podiums,

        AVG(rr.grid_position) AS avg_grid_position,
        AVG(rr.finish_position) AS avg_finish_position,
        AVG(rr.positions_changed) AS avg_positions_changed,

        MIN(rr.finish_position) AS best_finish,

        AVG(
            CASE
                WHEN rr.completed_race THEN 1.0
                ELSE 0.0
            END
        ) * 100 AS race_completion_percentage

    FROM {{ ref('stg_race_results') }} rr

    JOIN {{ ref('stg_race') }} r
        ON rr.race_key = r.race_key

    GROUP BY
        r.season,
        rr.driver_key
),

qualifying AS (

    SELECT
        r.season,
        q.driver_key,
        AVG(q.qualifying_position) AS avg_qualifying_position

    FROM {{ ref('stg_qualifying') }} q

    JOIN {{ ref('stg_race') }} r
        ON q.race_key = r.race_key

    GROUP BY
        r.season,
        q.driver_key
),

sprints AS (

    SELECT
        r.season,
        s.driver_key,

        SUM(s.points) AS sprint_points,

        SUM(
            CASE WHEN s.is_sprint_winner THEN 1 ELSE 0 END
        ) AS sprint_wins

    FROM {{ ref('stg_sprint_results') }} s

    JOIN {{ ref('stg_race') }} r
        ON s.race_key = r.race_key

    GROUP BY
        r.season,
        s.driver_key
)

SELECT
    rr.season,
    rr.driver_key,

    rr.races_started,

    rr.race_points,
    COALESCE(s.sprint_points, 0) AS sprint_points,

    rr.race_points
        + COALESCE(s.sprint_points, 0)
        AS total_points,

    rr.race_wins,
    rr.race_podiums,

    COALESCE(s.sprint_wins, 0)
        AS sprint_wins,

    rr.avg_grid_position,
    q.avg_qualifying_position,
    rr.avg_finish_position,
    rr.avg_positions_changed,

    rr.best_finish,
    rr.race_completion_percentage

FROM race_results rr

LEFT JOIN qualifying q
    ON rr.season = q.season
    AND rr.driver_key = q.driver_key

LEFT JOIN sprints s
    ON rr.season = s.season
    AND rr.driver_key = s.driver_key