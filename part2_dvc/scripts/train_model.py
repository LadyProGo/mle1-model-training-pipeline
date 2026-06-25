"""Train a baseline model for apartment price prediction."""

from pathlib import Path

import joblib
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestRegressor


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "part2_dvc" / "data"
MODELS_DIR = PROJECT_DIR / "part2_dvc" / "models"
PARAMS_PATH = PROJECT_DIR / "params.yaml"

X_TRAIN_PATH = DATA_DIR / "X_train.csv"
Y_TRAIN_PATH = DATA_DIR / "y_train.csv"

MODEL_PATH = MODELS_DIR / "random_forest_model.joblib"


def load_params() -> dict:
    """Load project parameters from params.yaml."""
    with open(PARAMS_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def train_model() -> None:
    """Train a compact RandomForestRegressor baseline and save the fitted model."""
    params = load_params()
    model_params = params["model"]

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Load train features and target.
    X_train = pd.read_csv(X_TRAIN_PATH)
    y_train = pd.read_csv(Y_TRAIN_PATH).squeeze("columns")

    # Initialize a compact baseline model.
    model = RandomForestRegressor(
        n_estimators=model_params["n_estimators"],
        max_depth=model_params["max_depth"],
        random_state=model_params["random_state"],
        n_jobs=model_params["n_jobs"],
    )

    # Train the model.
    model.fit(X_train, y_train)

    # Save the trained model.
    joblib.dump(model, MODEL_PATH)

    print(f"X_train shape: {X_train.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
