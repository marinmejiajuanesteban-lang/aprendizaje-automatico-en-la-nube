"""Flow de Prefect que orquesta el pipeline de entrenamiento completo (Fase 3)."""

from datetime import datetime

import mlflow
from prefect import flow, task
from sklearn.model_selection import train_test_split

from src.data.load_data import load_raw_data
from src.features.preprocessing import get_feature_target_split
from src.models.train import (
    MLFLOW_EXPERIMENT_NAME,
    build_training_pipeline,
    evaluate_model,
    log_run_to_mlflow,
    register_champion_model,
    train_model,
)

RECALL_THRESHOLD_PARA_PROMOCION = 0.80  # meta de la Sección 1.1


@task(name="cargar_y_validar_datos", retries=1)
def cargar_datos_task(data_path: str):
    return load_raw_data(data_path)


@task(name="dividir_datos")
def dividir_datos_task(df):
    X, y = get_feature_target_split(df)
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


@task(name="entrenar_modelo")
def entrenar_modelo_task(X_train, y_train):
    pipeline = build_training_pipeline()
    return train_model(pipeline, X_train, y_train)


@task(name="evaluar_modelo")
def evaluar_modelo_task(pipeline, X_test, y_test):
    return evaluate_model(pipeline, X_test, y_test)


@task(name="registrar_en_mlflow")
def registrar_en_mlflow_task(pipeline, metrics, run_name, input_example):
    run_id = log_run_to_mlflow(pipeline, metrics, run_name=run_name, input_example=input_example)

    if metrics["recall"] >= RECALL_THRESHOLD_PARA_PROMOCION:
        register_champion_model(run_id)
        promovido = True
    else:
        promovido = False

    return run_id, promovido


@flow(name="pipeline-entrenamiento-mantenimiento-predictivo")
def training_flow(data_path: str = "data/raw/ai4i2020.csv"):
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    df = cargar_datos_task(data_path)
    X_train, X_test, y_train, y_test = dividir_datos_task(df)
    pipeline = entrenar_modelo_task(X_train, y_train)
    metrics = evaluar_modelo_task(pipeline, X_test, y_test)

    run_name = f"prefect_flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_id, promovido = registrar_en_mlflow_task(pipeline, metrics, run_name, X_train.head())

    print(f"Run ID: {run_id}")
    print(f"Métricas: {metrics}")
    print(f"Promovido a champion: {promovido}")

    return run_id, metrics, promovido


if __name__ == "__main__":
    training_flow()