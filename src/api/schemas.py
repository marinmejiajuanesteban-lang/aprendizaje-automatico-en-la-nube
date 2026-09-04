"""Esquemas Pydantic de entrada/salida de la API (Fase 4 — Deployment)."""

from typing import Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class SensorReading(BaseModel):
    """Una lectura de sensores de una máquina, lista para predecir."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["L", "M", "H"] = Field(alias="Type")
    air_temperature_k: float = Field(alias="Air temperature [K]", gt=250, lt=350)
    process_temperature_k: float = Field(alias="Process temperature [K]", gt=250, lt=350)
    rotational_speed_rpm: float = Field(alias="Rotational speed [rpm]", gt=0)
    torque_nm: float = Field(alias="Torque [Nm]", ge=0)
    tool_wear_min: float = Field(alias="Tool wear [min]", ge=0)

    def to_model_input(self) -> pd.DataFrame:
        """Convierte la lectura a un DataFrame de una fila con los nombres de
        columna que espera el pipeline entrenado (los mismos del dataset original).
        """
        return pd.DataFrame([self.model_dump(by_alias=True)])


class PredictionResponse(BaseModel):
    """Respuesta de la predicción."""

    failure_probability: float
    failure_predicted: bool
    decision_threshold: float