import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook


POSTGRES_CONN_ID = os.getenv("POSTGRES_CONN_ID", "destination_db")
TARGET_TABLE = "mle1_real_estate_dataset"

TMP_DIR = Path(os.getenv("AIRFLOW_TMP_DIR", "/tmp/mle1_real_estate_airflow"))
BUILDINGS_PATH = TMP_DIR / "mle1_buildings.csv"
FLATS_PATH = TMP_DIR / "mle1_flats.csv"
DATASET_PATH = TMP_DIR / "mle1_real_estate_dataset.csv"

TARGET_COLUMNS = [
    "flat_id",
    "building_id",
    "floor",
    "kitchen_area",
    "living_area",
    "rooms",
    "is_apartment",
    "studio",
    "total_area",
    "price",
    "build_year",
    "building_type_int",
    "latitude",
    "longitude",
    "ceiling_height",
    "flats_count",
    "floors_total",
    "has_elevator",
]


with DAG(
    dag_id="mle1_collect_real_estate_data",
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

    @task(task_id="transform")
    def transform() -> None:
        buildings = pd.read_csv(BUILDINGS_PATH)
        flats = pd.read_csv(FLATS_PATH)

        dataset = flats.merge(
            buildings,
            left_on="building_id",
            right_on="id",
            how="inner",
            suffixes=("_flat", "_building"),
        )

        dataset = dataset.rename(columns={"id_flat": "flat_id"})
        dataset = dataset.drop(columns=["id_building"])
        dataset = dataset[TARGET_COLUMNS]

        dataset.to_csv(DATASET_PATH, index=False)

    @task(task_id="load")
    def load() -> None:
        dataset = pd.read_csv(DATASET_PATH)

        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        engine = postgres_hook.get_sqlalchemy_engine()

        postgres_hook.run(f"TRUNCATE TABLE {TARGET_TABLE};")

        dataset.to_sql(
            TARGET_TABLE,
            engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi",
        )

    create_table() >> extract() >> transform() >> load()
