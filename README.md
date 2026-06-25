# Model Training Pipeline

This project is an ML training pipeline for apartment price prediction. It covers data collection, data cleaning, EDA, model training, model evaluation, DVC-based artifact versioning, and model storage in S3.

The project was built as part of an ML engineering workflow. The current model is a reproducible baseline, not a final production-quality model.

## Project Goal

The goal of this project is to build a reproducible ML pipeline that predicts apartment prices based on real estate data.

The main focus of the project is not only model quality, but also the engineering workflow:

* automated data collection with Airflow
* data cleaning and validation
* reproducible model training with DVC
* external storage of large artifacts in S3
* clear separation between source code, configuration, data, and model artifacts

---

## Project Architecture

The project consists of two main parts:
* `part1_airflow` - data collection, data cleaning, and orchestration with Airflow
* `part2_dvc` - DVC pipeline for model training, evaluation, and artifact tracking

High-level workflow:

```text
PostgreSQL source tables
        |
        v
Airflow data collection DAG
        |
        v
Raw PostgreSQL table: mle1_real_estate_dataset
        |
        v
EDA notebook and cleaning logic
        |
        v
Airflow cleaning DAG
        |
        v
Clean PostgreSQL table: mle1_clean_real_estate_dataset
        |
        v
DVC pipeline
        |
        v
Train/test split -> model training -> model evaluation
        |
        v
Model and large artifacts stored in S3 via DVC
```

---

## Repository Structure

```text
.
├── .dvc/
│   ├── config
│   └── .gitignore
├── docs/
├── part1_airflow/
│   ├── dags/
│   │   ├── collect_real_estate_data.py
│   │   └── clean_real_estate_data.py
│   ├── logs/
│   ├── notebooks/
│   │   └── mle1_raw_data_eda.ipynb
│   └── plugins/
│       └── steps/
│           ├── clean_data.py
│           └── messages.py
├── part2_dvc/
│   ├── cv_results/
│   ├── data/
│   ├── models/
│   ├── notebooks/
│   └── scripts/
│       ├── load_data.py
│       ├── split_data.py
│       ├── train_model.py
│       └── evaluate_model.py
├── .dvcignore
├── .env.example
├── .gitignore
├── dvc.lock
├── dvc.yaml
├── params.yaml
├── requirements.txt
└── README.md
```

---

## Large Artifacts and DVC

Large artifacts are tracked with DVC and stored in an S3-compatible remote storage, not committed directly to GitHub.

This includes:
- cleaned dataset
- train/test datasets
- trained model
- evaluation metrics

GitHub stores the source code, configuration files, and DVC metadata, while DVC tracks the data and model artifacts.

The trained model was successfully pushed to the configured DVC remote and verified in S3-compatible storage.

---

## Data Collection with Airflow

The first Airflow DAG collects real estate data from PostgreSQL source tables and creates a raw table for the project.

DAG:
```text
mle1_collect_real_estate_data
```

Output table:
```text
mle1_real_estate_dataset
```

The raw dataset contains:
```text
141362 rows
```

---

## Data Cleaning with Airflow

The second Airflow DAG applies cleaning logic to the raw dataset and saves the cleaned data into a separate PostgreSQL table.

DAG:
```text
mle1_clean_real_estate_data
```

Output table:
```text
mle1_clean_real_estate_dataset
```

Cleaning steps:
* remove full duplicates
* remove duplicates by `flat_id`
* remove invalid prices below 100000
* fix suspicious `ceiling_height` values caused by scale errors

After cleaning:
```text
Raw rows: 141362
Clean rows: 141217
Removed rows: 145
```

Final validation confirmed:
* no missing values
* no full duplicates
* no duplicated `flat_id`
* no invalid prices
* no suspicious ceiling heights above the accepted threshold

---

## EDA

The EDA notebook is stored here:
```text
part1_airflow/notebooks/mle1_raw_data_eda.ipynb
```

The notebook includes:
* dataset shape analysis
* data type checks
* missing value analysis
* duplicate checks
* suspicious value detection
* cleaning strategy definition
* final validation of the cleaned dataset

---

## DVC Pipeline

The DVC pipeline consists of four stages:
```text
load_data -> split_data -> train_model -> evaluate_model
```

DVC configuration files:
```text
dvc.yaml
dvc.lock
params.yaml
```

The file `params.yaml` contains pipeline and model parameters:

```yaml
data:
  target_column: price
  drop_columns:
    - flat_id
    - building_id

split:
  test_size: 0.25
  random_state: 42

model:
  type: RandomForestRegressor
  n_estimators: 50
  max_depth: 20
  random_state: 42
  n_jobs: -1
```

---

## DVC Stages

### 1. load_data

Script:
```text
part2_dvc/scripts/load_data.py
```

Purpose:
* read the cleaned PostgreSQL table
* save the dataset as a CSV file for DVC tracking

Output:
```text
part2_dvc/data/clean_real_estate_dataset.csv
```

### 2. split_data

Script:
```text
part2_dvc/scripts/split_data.py
```

Purpose:
* split the cleaned dataset into features and target
* remove technical identifiers
* create train and test datasets

Outputs:
```text
part2_dvc/data/X_train.csv
part2_dvc/data/X_test.csv
part2_dvc/data/y_train.csv
part2_dvc/data/y_test.csv
```

Split parameters:
```text
test_size = 0.25
random_state = 42
```

### 3. train_model

Script:
```text
part2_dvc/scripts/train_model.py
```

Purpose:
* train a baseline RandomForestRegressor model
* save the trained model as a joblib artifact

Output:
```text
part2_dvc/models/random_forest_model.joblib
```

Model parameters:
```text
model = RandomForestRegressor
n_estimators = 50
max_depth = 20
random_state = 42
n_jobs = -1
```

### 4. evaluate_model

Script:
```text
part2_dvc/scripts/evaluate_model.py
```

Purpose:
* load the trained model
* predict apartment prices on the test set
* calculate evaluation metrics
* save metrics as JSON

Output:
```text
part2_dvc/cv_results/metrics.json
```

---

## Baseline Model

The baseline model is:
```text
RandomForestRegressor
```

This model was selected as a simple tree-based baseline. No additional feature scaling was applied because Random Forest is a tree-based model and does not require feature scaling. 
No additional categorical encoding was added at this stage because the current training dataset uses numerical features only.

---

## Baseline Results

The current baseline metrics are:
```text
RMSE: 80345371.65
MAE: 4401428.67
R2: 0.1394
```

These results show that the baseline model is reproducible, but its predictive quality is still weak. This model should be treated as a first technical baseline, not as a final production model.

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/LadyProGo/mle1-model-training-pipeline.git
cd mle1-model-training-pipeline
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example`.

The project requires PostgreSQL and S3 credentials.

Do not commit `.env` to GitHub.

### 5. Run the DVC pipeline

```bash
dvc repro
```

### 6. Check DVC status

```bash
dvc status
```

Expected result:

```text
Data and pipelines are up to date.
```

### 7. Pull artifacts from DVC remote if needed

```bash
dvc pull
```

### 8. Push updated DVC artifacts to remote if needed

```bash
dvc push
```

---

## Airflow Usage

To use Airflow locally, set the project-specific Airflow home:

```bash
export AIRFLOW_HOME=/home/mle-user/mle_projects/mle1-model-training-pipeline/part1_airflow
```

Start the scheduler:

```bash
airflow scheduler
```

Main DAGs:

```text
mle1_collect_real_estate_data
mle1_clean_real_estate_data
```

---

## Telegram Notifications

The project includes Telegram callbacks for Airflow DAG success and failure notifications.

The notification logic is implemented in:

```text
part1_airflow/plugins/steps/messages.py
```

In the current VM environment, actual Telegram delivery may be unavailable because external network access to the Telegram API can be restricted. The callback is implemented, errors are logged safely, and DAG execution is not interrupted by notification delivery issues.

---

## Limitations and Future Improvements

The current version of the project should be treated as a reproducible baseline training pipeline, not as a final production solution.

Current limitations:
- the model is a baseline RandomForestRegressor
- model quality is still weak and requires improvement
- feature engineering is minimal
- no advanced model comparison has been performed yet
- no hyperparameter tuning has been added yet
- no inference API is implemented yet
- the trained model is stored in S3 via DVC, but the project does not yet expose a prediction service

Future improvements:
- improve feature engineering and outlier handling
- add categorical feature processing if needed
- compare stronger models such as CatBoost, LightGBM, and XGBoost
- add hyperparameter tuning and cross-validation
- add model explainability
- add experiment tracking and model registry logic
- build an inference service with FastAPI
- containerize the service with Docker
- add CI/CD checks and automated model quality validation

---

## Project Status

The technical training pipeline is complete.

Completed:
* Airflow raw data collection DAG
* Airflow data cleaning DAG
* EDA notebook
* cleaning logic
* DVC pipeline
* `params.yaml`
* baseline model training
* baseline model evaluation
* S3/DVC remote configuration
* trained model stored in S3
* GitHub repository synchronized

---

## Tech Stack

- Python
- Pandas
- Scikit-learn
- RandomForestRegressor
- Joblib
- PostgreSQL
- Apache Airflow
- DVC
- YAML
- boto3
- S3/Yandex Object Storage
- Git/GitHub
- dotenv

---

## Author

Tatiana Pletneva Chavand

Data Science & Machine Learning

**Keywords:** Machine Learning, DVC, Airflow, PostgreSQL, S3, Model Training Pipeline, Scikit-learn, RandomForestRegressor
