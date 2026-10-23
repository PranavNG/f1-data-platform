SELECT
    rr.race_key,
    rr.driver_key,
    rr.team_key,

    rr.grid_position,
    rr.finish_position,
    rr.classified_position,
    rr.positions_changed,

    rr.is_winner,
    rr.is_podium,
    rr.completed_race,

    CASE
        WHEN rr.positions_changed > 0 THEN 'Gained'
        WHEN rr.positions_changed < 0 THEN 'Lost'
        ELSE 'No Change'
    END AS movement_direction,

    ABS(rr.positions_changed) AS absolute_movement

FROM {{ ref('stg_race_results') }} rr