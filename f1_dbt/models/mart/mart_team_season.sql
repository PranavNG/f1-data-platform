WITH race_results AS (

    SELECT
        r.season,
        rr.team_key,

        COUNT(DISTINCT rr.race_key) AS races_entered,

        SUM(rr.points) AS race_points,

        SUM(
            CASE
                WHEN rr.is_winner THEN 1
                ELSE 0
            END
        ) AS race_wins,

        SUM(
            CASE
                WHEN rr.is_podium THEN 1
                ELSE 0
            END
        ) AS race_podiums,

        AVG(rr.grid_position) AS avg_grid_position,
        AVG(rr.finish_position) AS avg_finish_position,

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
        rr.team_key
),

qualifying AS (

    SELECT
        r.season,
        q.team_key,

        AVG(q.qualifying_position)
            AS avg_qualifying_position

    FROM {{ ref('stg_qualifying') }} q

    JOIN {{ ref('stg_race') }} r
        ON q.race_key = r.race_key

    GROUP BY
        r.season,
        q.team_key
),

sprints AS (

    SELECT
        r.season,
        s.team_key,

        SUM(s.points) AS sprint_points,

        SUM(
            CASE
                WHEN s.is_sprint_winner THEN 1
                ELSE 0
            END
        ) AS sprint_wins

    FROM {{ ref('stg_sprint_results') }} s

    JOIN {{ ref('stg_race') }} r
        ON s.race_key = r.race_key

    GROUP BY
        r.season,
        s.team_key
)

SELECT
    rr.season,
    rr.team_key,

    rr.races_entered,

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

    rr.race_completion_percentage

FROM race_results rr

LEFT JOIN qualifying q
    ON rr.season = q.season
    AND rr.team_key = q.team_key

LEFT JOIN sprints s
    ON rr.season = s.season
    AND rr.team_key = s.team_key