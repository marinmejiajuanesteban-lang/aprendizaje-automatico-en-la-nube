"""Configuración centralizada del proyecto (Fase 6 — Testing y Buenas Prácticas).

Antes estas constantes estaban duplicadas por separado en varios módulos
(src/models/train.py, src/models/export_champion.py, src/api/model_loader.py),
lo que generaba el riesgo real de que un cambio (ej. el umbral de decisión)
se actualizara en un archivo y se olvidara en otro.
"""

MLFLOW_EXPERIMENT_NAME = "mantenimiento-predictivo-ai4i2020"
REGISTERED_MODEL_NAME = "mantenimiento-predictivo-hgb"
MODEL_ALIAS = "champion"
MODEL_URI = f"models:/{REGISTERED_MODEL_NAME}@{MODEL_ALIAS}"

LOCAL_MODEL_PATH = "models/champion"
DECISION_THRESHOLD = 0.30