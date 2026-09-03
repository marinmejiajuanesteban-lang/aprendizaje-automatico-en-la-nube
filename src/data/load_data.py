"""Carga y validación del dataset AI4I2020 (Fase 3 — Pipeline de datos)."""

import pandas as pd
from pandera.pandas import Column, Check, DataFrameSchema

# Esquema/contrato del dataset crudo: columnas, tipos y rangos esperados.
# Sirve para detectar temprano si el CSV cambió de forma inesperada
# (columna faltante, tipo raro, sensor fuera de rango, etc.).
raw_schema = DataFrameSchema(
    {
        "UDI": Column(int, Check.gt(0), unique=True),
        "Product ID": Column(str, nullable=False),
        "Type": Column(str, Check.isin(["L", "M", "H"])),
        "Air temperature [K]": Column(float, Check.in_range(290, 310)),
        "Process temperature [K]": Column(float, Check.in_range(300, 320)),
        "Rotational speed [rpm]": Column(int, Check.in_range(1000, 3000)),
        "Torque [Nm]": Column(float, Check.in_range(0, 90)),
        "Tool wear [min]": Column(int, Check.in_range(0, 300)),
        "Machine failure": Column(int, Check.isin([0, 1])),
        "TWF": Column(int, Check.isin([0, 1])),
        "HDF": Column(int, Check.isin([0, 1])),
        "PWF": Column(int, Check.isin([0, 1])),
        "OSF": Column(int, Check.isin([0, 1])),
        "RNF": Column(int, Check.isin([0, 1])),
    },
    strict=True,
    coerce=True,
)


def load_raw_data(path: str = "data/raw/ai4i2020.csv") -> pd.DataFrame:
    """Carga el CSV crudo y lo valida contra `raw_schema`.

    Lanza `pandera.errors.SchemaErrors` si algún dato no cumple el contrato.
    La ruta por defecto asume que se ejecuta desde la raíz del proyecto.
    """
    df = pd.read_csv(path, encoding="utf-8-sig")
    validated_df = raw_schema.validate(df, lazy=True)
    return validated_df