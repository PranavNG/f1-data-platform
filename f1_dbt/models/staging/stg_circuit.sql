SELECT
    circuit_key,
    circuit_name,
    circuit_location,
    circuit_country,
    circuit_length_km
FROM {{ source('f1_warehouse', 'dim_circuit') }}