"""Load the cleaned real estate dataset from PostgreSQL."""

import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "part2_dvc" / "data"
OUTPUT_PATH = DATA_DIR / "clean_real_estate_dataset.csv"

SOURCE_TABLE = "mle1_clean_real_estate_dataset"


def load_data_from_postgres() -> pd.DataFrame:
    """Load the cleaned dataset from the project-specific PostgreSQL table."""
    load_dotenv(PROJECT_DIR / ".env")

    connection = psycopg2.connect(
        host=os.getenv("DB_DESTINATION_HOST"),
        port=os.getenv("DB_DESTINATION_PORT"),
        dbname=os.getenv("DB_DESTINATION_NAME"),
        user=os.getenv("DB_DESTINATION_USER"),
        password=os.getenv("DB_DESTINATION_PASSWORD"),
    )

    query = f"SELECT * FROM {SOURCE_TABLE};"
    data = pd.read_sql(query, connection)

    connection.close()

    return data


def main() -> None:
    """Load data and save it as a local CSV file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    data = load_data_from_postgres()
    data.to_csv(OUTPUT_PATH, index=False)

    print(f"Data loaded from table: {SOURCE_TABLE}")
    print(f"Dataset shape: {data.shape}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
