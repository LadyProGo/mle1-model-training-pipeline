"""Evaluate the trained apartment price prediction model."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "part2_dvc" / "data"
MODELS_DIR = PROJECT_DIR / "part2_dvc" / "models"
METRICS_DIR = PROJECT_DIR / "part2_dvc" / "cv_results"

X_TEST_PATH = DATA_DIR / "X_test.csv"
Y_TEST_PATH = DATA_DIR / "y_test.csv"
MODEL_PATH = MODELS_DIR / "random_forest_model.joblib"
METRICS_PATH = METRICS_DIR / "metrics.json"


def evaluate_model() -> None:
    """Evaluate the trained model and save regression metrics."""
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    # load test features and target
    X_test = pd.read_csv(X_TEST_PATH)
    y_test = pd.read_csv(Y_TEST_PATH).squeeze("columns")

    # load the trained model
    model = joblib.load(MODEL_PATH)

    # generate predictions
    y_pred = model.predict(X_test)

    # calculate regression metrics
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # save metrics to JSON
    metrics = {
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    print(f"X_test shape: {X_test.shape}")
    print(f"y_test shape: {y_test.shape}")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAE: {mae:.2f}")
    print(f"R2: {r2:.4f}")
    print(f"Metrics saved to: {METRICS_PATH}")


if __name__ == "__main__":
    evaluate_model()
