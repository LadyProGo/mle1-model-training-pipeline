import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


POSTGRES_CONN_ID = os.getenv("POSTGRES_CONN_ID", "destination_db")
TARGET_TABLE = "real_estate_dataset"

TMP_DIR = Path(os.getenv("AIRFLOW_TMP_DIR", "/tmp/real_estate_airflow"))
BUILDINGS_PATH = TMP_DIR / "buildings.csv"
FLATS_PATH = TMP_DIR / "flats.csv"


with DAG(
    dag_id="collect_real_estate_data",
    description="Collect raw real estate data from PostgreSQL source tables.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["real_estate", "data_collection"],
) as dag:

    @task(task_id="create_table")
    def create_table() -> None:
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {TARGET_TABLE} (
            flat_id INTEGER,
            building_id INTEGER,
            floor INTEGER,
            kitchen_area FLOAT,
            living_area FLOAT,
            rooms INTEGER,
            is_apartment BOOLEAN,
            studio BOOLEAN,
            total_area FLOAT,
            price BIGINT,
            build_year INTEGER,
            building_type_int INTEGER,
            latitude FLOAT,
            longitude FLOAT,
            ceiling_height FLOAT,
            flats_count INTEGER,
            floors_total INTEGER,
            has_elevator BOOLEAN
        );
        """

        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        postgres_hook.run(create_table_sql)

    @task(task_id="extract")
    def extract() -> None:
        TMP_DIR.mkdir(parents=True, exist_ok=True)

        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        engine = postgres_hook.get_sqlalchemy_engine()

        buildings = pd.read_sql("SELECT * FROM buildings;", engine)
        flats = pd.read_sql("SELECT * FROM flats;", engine)

        buildings.to_csv(BUILDINGS_PATH, index=False)
        flats.to_csv(FLATS_PATH, index=False)

    transform = EmptyOperator(task_id="transform")
    load = EmptyOperator(task_id="load")

    create_table() >> extract() >> transform >> load
