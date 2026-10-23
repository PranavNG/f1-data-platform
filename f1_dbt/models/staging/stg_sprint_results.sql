SELECT
    sprint_result_key,
    race_key,
    driver_key,
    team_key,

    grid_position,
    finish_position,
    classified_position,

    points,
    laps_completed,

    sprint_time,
    sprint_status,

    CASE
        WHEN finish_position = 1 THEN TRUE
        ELSE FALSE
    END AS is_sprint_winner,

    CASE
        WHEN finish_position BETWEEN 1 AND 3 THEN TRUE
        ELSE FALSE
    END AS is_sprint_podium

FROM {{ source('f1_warehouse', 'fact_sprint_results') }}