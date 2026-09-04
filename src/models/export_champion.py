"""Exporta una copia autocontenida del modelo campeón para deployment (Fase 4).

MLflow con tracking basado en archivos locales guarda internamente rutas
absolutas del sistema de archivos donde se creó el experimento (ej.
C:\\Users\\...\\mlruns\\...). Esas rutas no existen dentro de un contenedor
Docker (que tiene su propio sistema de archivos Linux), así que la API no
puede apuntar directamente al Model Registry dentro del contenedor. Esta
función exporta una copia portable del modelo que sí se puede copiar completa
a la imagen de Docker.
"""

import shutil
from pathlib import Path

import mlflow

MODEL_URI = "models:/mantenimiento-predictivo-hgb@champion"
EXPORT_PATH = "models/champion"


def export_champion_model():
    mlflow.set_tracking_uri("file:./mlruns")
    model = mlflow.sklearn.load_model(MODEL_URI)

    export_path = Path(EXPORT_PATH)
    if export_path.exists():
        shutil.rmtree(export_path)

    mlflow.sklearn.save_model(model, path=str(export_path))
    print(f"Modelo champion exportado a {export_path.resolve()}")


if __name__ == "__main__":
    export_champion_model()