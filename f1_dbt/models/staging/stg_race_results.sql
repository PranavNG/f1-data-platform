SELECT
    race_result_key,
    race_key,
    driver_key,
    team_key,
    grid_position,
    finish_position,
    classified_position,
    points,
    laps_completed,
    race_time,
    race_status,

    CASE
        WHEN grid_position IS NOT NULL
         AND finish_position IS NOT NULL
        THEN grid_position - finish_position
    END AS positions_changed,

    CASE
        WHEN finish_position = 1 THEN TRUE
        ELSE FALSE
    END AS is_winner,

    CASE
        WHEN finish_position BETWEEN 1 AND 3 THEN TRUE
        ELSE FALSE
    END AS is_podium,

    CASE
        WHEN race_status IN ('Finished', 'Lapped') THEN TRUE
        ELSE FALSE
    END AS completed_race

FROM {{ source('f1_warehouse', 'fact_race_results') }}