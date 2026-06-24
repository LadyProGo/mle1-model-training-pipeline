"""Split the cleaned real estate dataset into train and test datasets."""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "part2_dvc" / "data"

INPUT_PATH = DATA_DIR / "clean_real_estate_dataset.csv"

X_TRAIN_PATH = DATA_DIR / "X_train.csv"
X_TEST_PATH = DATA_DIR / "X_test.csv"
Y_TRAIN_PATH = DATA_DIR / "y_train.csv"
Y_TEST_PATH = DATA_DIR / "y_test.csv"

TARGET_COLUMN = "price"
ID_COLUMNS = ["flat_id", "building_id"]

RANDOM_STATE = 42
TEST_SIZE = 0.25


def split_data() -> None:
    """Split the cleaned dataset into features and target train/test datasets."""
    data = pd.read_csv(INPUT_PATH)

    # separate the target variable from the feature matrix
    y = data[TARGET_COLUMN]
    X = data.drop(columns=[TARGET_COLUMN] + ID_COLUMNS)

    # split the data into train and test parts
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    # save the resulting datasets
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
