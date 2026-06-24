"""Airflow DAG for cleaning the raw real estate dataset."""

import os
from datetime import datetime

import pandas as pd
import psycopg2
from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook

from steps.clean_data import clean_data
from steps.messages import send_telegram_failure_message, send_telegram_success_message


POSTGRES_CONN_ID = os.getenv("POSTGRES_CONN_ID", "destination_db")

RAW_TABLE = "mle1_real_estate_dataset"
CLEAN_TABLE = "mle1_clean_real_estate_dataset"

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
    dag_id="mle1_clean_real_estate_data",
    description="Clean the raw real estate dataset and save it to a project-specific PostgreSQL table.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["real_estate", "data_cleaning"],
    on_success_callback=send_telegram_success_message,
    on_failure_callback=send_telegram_failure_message,
) as dag:

    @task()
    def create_table() -> None:
        """Create the cleaned real estate table if it does not exist."""
        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {CLEAN_TABLE} (
            flat_id INTEGER,
            building_id INTEGER,
            floor INTEGER,
            kitchen_area REAL,
            living_area REAL,
            rooms INTEGER,
            is_apartment BOOLEAN,
            studio BOOLEAN,
            total_area REAL,
            price REAL,
            build_year INTEGER,
            building_type_int INTEGER,
            latitude REAL,
            longitude REAL,
            ceiling_height REAL,
            flats_count INTEGER,
            floors_total INTEGER,
            has_elevator BOOLEAN
        );
        """

        postgres_hook.run(create_table_query)

    @task()
    def clean_and_load() -> None:
        """Load raw data, apply cleaning logic, and save cleaned data to PostgreSQL."""
        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        connection = postgres_hook.get_conn()

        df_raw = pd.read_sql(f"SELECT * FROM {RAW_TABLE};", connection)

        df_clean = clean_data(df_raw)
        df_clean = df_clean[TARGET_COLUMNS]
        df_clean = df_clean.astype(object).where(pd.notna(df_clean), None)

        cursor = connection.cursor()
        cursor.execute(f"TRUNCATE TABLE {CLEAN_TABLE};")
        connection.commit()
        cursor.close()
        connection.close()

        postgres_hook.insert_rows(
            table=CLEAN_TABLE,
            rows=df_clean.itertuples(index=False, name=None),
            target_fields=TARGET_COLUMNS,
            commit_every=1000,
        )

    create_table() >> clean_and_load()
