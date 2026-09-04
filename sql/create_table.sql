CREATE TABLE dim_driver(
    driver_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    driver_id VARCHAR UNIQUE NOT NULL,
    driver_number INT,
    abbreviation VARCHAR(3),
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    country_code VARCHAR(3)
);

CREATE TABLE dim_team(
    team_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_id VARCHAR NOT NULL,
    team_name VARCHAR NOT NULL,
    team_colour VARCHAR(6),
    valid_from_season SMALLINT NOT NULL,
    valid_to_season SMALLINT,
    CONSTRAINT unq_team UNIQUE (team_id, valid_from_season)
);

CREATE TABLE dim_circuit(
    circuit_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    circuit_name VARCHAR NOT NULL,
    circuit_location VARCHAR NOT NULL,
    circuit_country VARCHAR NOT NULL,
    circuit_length_km NUMERIC(6,3),
    CONSTRAINT unq_cir UNIQUE (circuit_name, circuit_location, circuit_country)
);

CREATE TABLE dim_race(
    race_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    season SMALLINT NOT NULL,
    round_number SMALLINT NOT NULL,
    official_event_name VARCHAR NOT NULL,
    event_date DATE NOT NULL,
    event_format VARCHAR NOT NULL,
    circuit_key INT NOT NULL,
    FOREIGN KEY (circuit_key) 
    REFERENCES dim_circuit(circuit_key),
    CONSTRAINT unq_race UNIQUE (season,round_number)
);

CREATE TABLE fact_race_results(
    race_result_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    race_key INT NOT NULL,
    driver_key INT NOT NULL,
    team_key INT NOT NULL,
    grid_position SMALLINT,
    finish_position SMALLINT,
    classified_position VARCHAR,
    points NUMERIC(5,2) NOT NULL,
    laps_completed SMALLINT NOT NULL,
    race_time INTERVAL,
    race_status VARCHAR NOT NULL,
    FOREIGN KEY (race_key)
    REFERENCES dim_race(race_key),
    FOREIGN KEY (driver_key)
    REFERENCES dim_driver(driver_key),
    FOREIGN KEY (team_key)
    REFERENCES dim_team(team_key),  
    CONSTRAINT unq_race_result UNIQUE (race_key, driver_key)
);

CREATE TABLE fact_qualifying(
    qualifying_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    race_key INT NOT NULL,
    driver_key INT NOT NULL,
    team_key INT NOT NULL,
    qualifying_position SMALLINT,
    q1_time INTERVAL,
    q2_time INTERVAL,
    q3_time INTERVAL,
    FOREIGN KEY (race_key)
    REFERENCES dim_race(race_key),
    FOREIGN KEY (driver_key)
    REFERENCES dim_driver(driver_key),
    FOREIGN KEY (team_key)
    REFERENCES dim_team(team_key),
    CONSTRAINT unq_qualifying UNIQUE (race_key, driver_key)
);

CREATE TABLE fact_lap_times(
    lap_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    race_key INT NOT NULL,
    driver_key INT NOT NULL,
    team_key INT NOT NULL,
    lap_number SMALLINT NOT NULL,
    lap_time INTERVAL,
    sector_1_time INTERVAL,
    sector_2_time INTERVAL,
    sector_3_time INTERVAL,
    position SMALLINT,
    stint SMALLINT,
    compound VARCHAR,
    tyre_life NUMERIC(6,1),
    fresh_tyre BOOLEAN,
    pit_in_time INTERVAL,
    pit_out_time INTERVAL,
    track_status VARCHAR,
    deleted BOOLEAN,
    is_accurate BOOLEAN,
    is_personal_best BOOLEAN,
    FOREIGN KEY (race_key)
    REFERENCES dim_race(race_key),
    FOREIGN KEY (driver_key)
    REFERENCES dim_driver(driver_key),
    FOREIGN KEY (team_key)
    REFERENCES dim_team(team_key),
    CONSTRAINT unq_lap_time UNIQUE (race_key, driver_key, lap_number)
);
