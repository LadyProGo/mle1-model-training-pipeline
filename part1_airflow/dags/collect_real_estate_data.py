from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator


with DAG(
    dag_id="collect_real_estate_data",
    description="Collect raw real estate data from PostgreSQL source tables.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["real_estate", "data_collection"],
) as dag:
    create_table = EmptyOperator(task_id="create_table")
    extract = EmptyOperator(task_id="extract")
    transform = EmptyOperator(task_id="transform")
    load = EmptyOperator(task_id="load")

    create_table >> extract >> transform >> load
