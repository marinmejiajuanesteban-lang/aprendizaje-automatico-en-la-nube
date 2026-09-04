"""Carga del modelo campeón para servirlo en la API (Fase 4 — Deployment)."""

import mlflow

LOCAL_MODEL_PATH = "models/champion"
DECISION_THRESHOLD = 0.30


def load_champion_model():
    """Carga la copia local autocontenida del modelo champion (ver export_champion.py).

    No se carga directamente desde el Model Registry de MLflow porque el
    tracking store basado en archivos locales guarda rutas absolutas del
    sistema de archivos donde se creó el experimento, y esas rutas no
    existen dentro de un contenedor Docker (que tiene su propio filesystem).
    Por eso servimos la copia portable exportada con mlflow.sklearn.save_model().
    """
    return mlflow.sklearn.load_model(LOCAL_MODEL_PATH)