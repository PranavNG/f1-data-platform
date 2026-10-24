from datetime import datetime

from airflow.sdk import DAG, task


with DAG(
    dag_id="test_f1_dag",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["f1", "test"],
):

    @task
    def start():
        print("F1 pipeline started")

    @task
    def finish():
        print("F1 pipeline finished")

    start() >> finish()
