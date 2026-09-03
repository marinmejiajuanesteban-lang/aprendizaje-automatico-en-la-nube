"""Entrenamiento del modelo campeón y registro en MLflow (Fase 3 — Pipeline de entrenamiento)."""

import mlflow
import mlflow.sklearn
from mlflow import MlflowClient
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import recall_score, precision_score, f1_score, average_precision_score
from sklearn.utils.class_weight import compute_sample_weight

from src.features.preprocessing import build_preprocessor

# Hiperparámetros ganadores del tuning con Optuna (Fase 2, notebook 02_mlflow_tracking.ipynb)
BEST_PARAMS = {
    "max_iter": 223,
    "max_depth": 8,
    "learning_rate": 0.057075747161782854,
    "max_leaf_nodes": 54,
    "l2_regularization": 0.21725275745972278,
}

DECISION_THRESHOLD = 0.30
MLFLOW_EXPERIMENT_NAME = "mantenimiento-predictivo-ai4i2020"
REGISTERED_MODEL_NAME = "mantenimiento-predictivo-hgb"


def build_training_pipeline(params: dict | None = None) -> Pipeline:
    """Arma el pipeline completo: preprocesamiento + Hist Gradient Boosting.

    Usa los hiperparámetros ganadores de Optuna por defecto.
    """
    model_params = params if params is not None else BEST_PARAMS
    classifier = HistGradientBoostingClassifier(random_state=42, **model_params)
    return Pipeline(steps=[
        ("preprocessor", build_preprocessor()),
        ("classifier", classifier),
    ])


def train_model(pipeline: Pipeline, X_train, y_train) -> Pipeline:
    """Entrena el pipeline con sample_weight balanceado (la clase minoritaria pesa más)."""
    sample_weight = compute_sample_weight(class_weight="balanced", y=y_train)
    pipeline.fit(X_train, y_train, classifier__sample_weight=sample_weight)
    return pipeline


def evaluate_model(pipeline: Pipeline, X_test, y_test, threshold: float = DECISION_THRESHOLD) -> dict:
    """Evalúa el modelo con el umbral de decisión elegido en la Fase 2."""
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    return {
        "recall": recall_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "auc_pr": average_precision_score(y_test, y_proba),
    }


def log_run_to_mlflow(
    pipeline: Pipeline,
    metrics: dict,
    run_name: str,
    params: dict | None = None,
    input_example=None,
) -> str:
    """Loguea el run a MLflow (parámetros, métricas y el modelo) y devuelve el run_id."""
    model_params = params if params is not None else BEST_PARAMS
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(model_params)
        mlflow.log_param("decision_threshold", DECISION_THRESHOLD)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(pipeline, artifact_path="modelo", input_example=input_example)
        run_id = run.info.run_id

    return run_id


def register_champion_model(run_id: str, model_name: str = REGISTERED_MODEL_NAME, alias: str = "champion") -> None:
    """Registra el modelo del run dado en el Model Registry con el alias indicado."""
    model_uri = f"runs:/{run_id}/modelo"
    registered_model = mlflow.register_model(model_uri=model_uri, name=model_name)

    client = MlflowClient()
    client.set_registered_model_alias(name=model_name, alias=alias, version=registered_model.version)