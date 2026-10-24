from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import sys

from airflow.sdk import DAG, task


# f1-data-platform/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DBT_PROJECT_DIR = PROJECT_ROOT / "f1_dbt"
DBT_EXECUTABLE = PROJECT_ROOT / "venv" / "bin" / "dbt"


with DAG(
    dag_id="f1_data_pipeline",
    description="End-to-end Formula 1 data engineering pipeline",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule=None,
    catchup=False,
    tags=["f1", "data-engineering"],
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
):

    @task
    def run_python_script(script: str):
        script_path = PROJECT_ROOT / script

        print(f"Running: {script_path}")

        subprocess.run(
            [sys.executable, str(script_path)],
            cwd=PROJECT_ROOT,
            check=True,
        )

    @task
    def run_dbt_build():
        print("Running dbt build")

        subprocess.run(
            [str(DBT_EXECUTABLE), "build"],
            cwd=DBT_PROJECT_DIR,
            check=True,
        )

    @task
    def pipeline_complete():
        print("F1 data pipeline completed successfully.")

    # -------------------------
    # Extraction
    # -------------------------

    extract_driver = run_python_script.override(
        task_id="extract_driver"
    )("src/extract/driver.py")

    extract_team = run_python_script.override(
        task_id="extract_team"
    )("src/extract/team.py")

    extract_circuit = run_python_script.override(
        task_id="extract_circuit"
    )("src/extract/circuit.py")

    extract_race = run_python_script.override(
        task_id="extract_race"
    )("src/extract/race.py")

    extract_race_results = run_python_script.override(
        task_id="extract_race_results"
    )("src/extract/race_results.py")

    extract_qualifying = run_python_script.override(
        task_id="extract_qualifying"
    )("src/extract/qualifying.py")

    extract_lap_times = run_python_script.override(
        task_id="extract_lap_times"
    )("src/extract/lap_times.py")

    extract_sprint_results = run_python_script.override(
        task_id="extract_sprint_results"
    )("src/extract/sprint_results.py")

    # -------------------------
    # PostgreSQL loading
    # -------------------------

    load_driver = run_python_script.override(
        task_id="load_driver"
    )("src/load/postgres_driver.py")

    load_team = run_python_script.override(
        task_id="load_team"
    )("src/load/postgres_team.py")

    load_circuit = run_python_script.override(
        task_id="load_circuit"
    )("src/load/postgres_circuit.py")

    load_race = run_python_script.override(
        task_id="load_race"
    )("src/load/postgres_race.py")

    load_race_results = run_python_script.override(
        task_id="load_race_results"
    )("src/load/postgres_race_results.py")

    load_qualifying = run_python_script.override(
        task_id="load_qualifying"
    )("src/load/postgres_qualifying.py")

    load_lap_times = run_python_script.override(
        task_id="load_lap_times"
    )("src/load/postgres_lap_times.py")

    load_sprint_results = run_python_script.override(
        task_id="load_sprint_results"
    )("src/load/postgres_sprint_results.py")

    dbt_build = run_dbt_build()
    complete = pipeline_complete()

    # -------------------------
    # Dependencies
    # -------------------------

    (
        extract_driver
        >> extract_team
        >> extract_circuit
        >> extract_race
        >> extract_race_results
        >> extract_qualifying
        >> extract_lap_times
        >> extract_sprint_results
        >> load_driver
        >> load_team
        >> load_circuit
        >> load_race
        >> load_race_results
        >> load_qualifying
        >> load_lap_times
        >> load_sprint_results
        >> dbt_build
        >> complete
    )
