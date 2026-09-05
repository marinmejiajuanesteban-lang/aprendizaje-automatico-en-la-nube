"""Tests para el esquema de validación de datos (Fase 6 — Testing)."""

import pandas as pd
import pytest
from pandera.errors import SchemaErrors

from src.data.load_data import raw_schema


def _fila_valida(**overrides) -> dict:
    fila = {
        "UDI": 1,
        "Product ID": "M14860",
        "Type": "M",
        "Air temperature [K]": 298.1,
        "Process temperature [K]": 308.6,
        "Rotational speed [rpm]": 1551,
        "Torque [Nm]": 42.8,
        "Tool wear [min]": 0,
        "Machine failure": 0,
        "TWF": 0,
        "HDF": 0,
        "PWF": 0,
        "OSF": 0,
        "RNF": 0,
    }
    fila.update(overrides)
    return fila


def test_raw_schema_acepta_datos_validos():
    df = pd.DataFrame([_fila_valida(), _fila_valida(UDI=2)])
    validado = raw_schema.validate(df, lazy=True)
    assert len(validado) == 2


def test_raw_schema_rechaza_type_invalido():
    df = pd.DataFrame([_fila_valida(Type="Z")])
    with pytest.raises(SchemaErrors):
        raw_schema.validate(df, lazy=True)


def test_raw_schema_rechaza_temperatura_fuera_de_rango():
    df = pd.DataFrame([_fila_valida(**{"Air temperature [K]": 1000.0})])
    with pytest.raises(SchemaErrors):
        raw_schema.validate(df, lazy=True)