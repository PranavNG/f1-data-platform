SELECT
    team_key,
    team_id,
    team_name,
    team_colour,
    valid_from_season,
    valid_to_season
FROM {{ source('f1_warehouse', 'dim_team') }}