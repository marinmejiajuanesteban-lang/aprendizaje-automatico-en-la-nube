"""Feature engineering y preprocesamiento (Fase 3 — Pipeline de entrenamiento)."""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

TARGET_COLUMN = "Machine failure"

COLUMNS_TO_DROP = [
    "UDI",
    "Product ID",
    "Machine failure",
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF",
]

NUMERIC_FEATURES = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]

CATEGORICAL_FEATURES = ["Type"]


def get_feature_target_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separa el DataFrame validado en features (X) y target (y).

    Descarta el identificador (UDI), el ID de producto y las 5 banderas
    de tipo de falla, que no se usan como predictores del MVP
    (clasificación binaria de Machine failure).
    """
    X = df.drop(columns=COLUMNS_TO_DROP)
    y = df[TARGET_COLUMN]
    return X, y


def build_preprocessor() -> ColumnTransformer:
    """Construye el ColumnTransformer: escalado para numéricas, one-hot para Type.

    Se devuelve sin ajustar (unfitted) — el ajuste ocurre dentro del
    pipeline de entrenamiento, después del split train/test, para
    evitar data leakage.
    """
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(drop="first"), CATEGORICAL_FEATURES),
        ]
    )