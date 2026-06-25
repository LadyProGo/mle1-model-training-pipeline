"""Split the cleaned real estate dataset into train and test datasets."""

from pathlib import Path

import pandas as pd
import yaml
from sklearn.model_selection import train_test_split


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "part2_dvc" / "data"
PARAMS_PATH = PROJECT_DIR / "params.yaml"

INPUT_PATH = DATA_DIR / "clean_real_estate_dataset.csv"

X_TRAIN_PATH = DATA_DIR / "X_train.csv"
X_TEST_PATH = DATA_DIR / "X_test.csv"
Y_TRAIN_PATH = DATA_DIR / "y_train.csv"
Y_TEST_PATH = DATA_DIR / "y_test.csv"


def load_params() -> dict:
    """Load project parameters from params.yaml."""
    with open(PARAMS_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def split_data() -> None:
    """Split the cleaned dataset into features and target train/test datasets."""
    params = load_params()

    target_column = params["data"]["target_column"]
    drop_columns = params["data"]["drop_columns"]
    test_size = params["split"]["test_size"]
    random_state = params["split"]["random_state"]

    data = pd.read_csv(INPUT_PATH)

    # Separate the target variable from the feature matrix.
    y = data[target_column]
    X = data.drop(columns=[target_column] + drop_columns)

    # Split the data into train and test parts.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
    )

    # Save the resulting datasets.
    X_train.to_csv(X_TRAIN_PATH, index=False)
    X_test.to_csv(X_TEST_PATH, index=False)
    y_train.to_csv(Y_TRAIN_PATH, index=False)
    y_test.to_csv(Y_TEST_PATH, index=False)

    print(f"Input dataset shape: {data.shape}")
    print(f"Feature matrix shape: {X.shape}")
    print(f"Target vector shape: {y.shape}")
    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"y_test shape: {y_test.shape}")


if __name__ == "__main__":
    split_data()
