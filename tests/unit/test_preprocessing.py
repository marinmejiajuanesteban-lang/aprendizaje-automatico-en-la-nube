"""Tests para feature engineering y preprocesamiento (Fase 6 — Testing)."""

import pandas as pd
from sklearn.compose import ColumnTransformer

from src.features.preprocessing import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    build_preprocessor,
    get_feature_target_split,
)


def _df_de_ejemplo() -> pd.DataFrame:
    return pd.DataFrame({
        "UDI": [1, 2],
        "Product ID": ["M1", "M2"],
        "Type": ["M", "L"],
        "Air temperature [K]": [298.1, 298.5],
        "Process temperature [K]": [308.6, 309.0],
        "Rotational speed [rpm]": [1551, 1408],
        "Torque [Nm]": [42.8, 46.3],
        "Tool wear [min]": [0, 3],
        "Machine failure": [0, 1],
        "TWF": [0, 0],
        "HDF": [0, 0],
        "PWF": [0, 0],
        "OSF": [0, 1],
        "RNF": [0, 0],
    })


def test_get_feature_target_split_descarta_columnas_no_predictoras():
    df = _df_de_ejemplo()
    X, y = get_feature_target_split(df)

    columnas_prohibidas = {"UDI", "Product ID", "TWF", "HDF", "PWF", "OSF", "RNF", TARGET_COLUMN}
    assert not columnas_prohibidas & set(X.columns)
    assert set(X.columns) == set(NUMERIC_FEATURES) | set(CATEGORICAL_FEATURES)
    assert list(y) == [0, 1]


def test_build_preprocessor_devuelve_column_transformer():
    preprocessor = build_preprocessor()
    assert isinstance(preprocessor, ColumnTransformer)


def test_build_preprocessor_transforma_sin_error():
    df = _df_de_ejemplo()
    X, _ = get_feature_target_split(df)
    preprocessor = build_preprocessor()

    X_transformado = preprocessor.fit_transform(X)

    assert X_transformado.shape[0] == len(X)