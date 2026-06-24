"""Train a baseline model for apartment price prediction."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "part2_dvc" / "data"
MODELS_DIR = PROJECT_DIR / "part2_dvc" / "models"

X_TRAIN_PATH = DATA_DIR / "X_train.csv"
Y_TRAIN_PATH = DATA_DIR / "y_train.csv"

MODEL_PATH = MODELS_DIR / "random_forest_model.joblib"

RANDOM_STATE = 42


def train_model() -> None:
    """Train a compact RandomForestRegressor baseline and save the fitted model."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # load train features and target
    X_train = pd.read_csv(X_TRAIN_PATH)
    y_train = pd.read_csv(Y_TRAIN_PATH).squeeze("columns")

    # initialize a compact baseline model
    model = RandomForestRegressor(
        n_estimators=50,
        max_depth=20,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    # train the model
    model.fit(X_train, y_train)

    # save the trained model
    joblib.dump(model, MODEL_PATH)

    print(f"X_train shape: {X_train.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
