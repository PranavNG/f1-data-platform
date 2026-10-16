SELECT
    driver_key,
    driver_id,
    driver_number,
    abbreviation,
    first_name,
    last_name,
    full_name,
    country_code
FROM {{ source('f1_warehouse', 'dim_driver') }}