"""Tests para los esquemas Pydantic de la API (Fase 6 — Testing)."""

import pytest
from pydantic import ValidationError

from src.api.schemas import PredictionResponse, SensorReading


def _lectura_valida(**overrides) -> dict:
    payload = {
        "Type": "L",
        "Air temperature [K]": 298.1,
        "Process temperature [K]": 308.6,
        "Rotational speed [rpm]": 1551,
        "Torque [Nm]": 42.8,
        "Tool wear [min]": 0,
    }
    payload.update(overrides)
    return payload


def test_sensor_reading_acepta_payload_valido():
    reading = SensorReading(**_lectura_valida())
    assert reading.type == "L"
    assert reading.air_temperature_k == 298.1


def test_sensor_reading_rechaza_type_invalido():
    with pytest.raises(ValidationError):
        SensorReading(**_lectura_valida(Type="Z"))


def test_sensor_reading_rechaza_torque_negativo():
    with pytest.raises(ValidationError):
        SensorReading(**{**_lectura_valida(), "Torque [Nm]": -5})


def test_to_model_input_reconstruye_nombres_originales():
    reading = SensorReading(**_lectura_valida())
    df = reading.to_model_input()

    assert list(df.columns) == [
        "Type",
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]",
    ]
    assert df.iloc[0]["Type"] == "L"


def test_prediction_response_serializa_campos_esperados():
    response = PredictionResponse(
        failure_probability=0.27,
        failure_predicted=False,
        decision_threshold=0.30,
    )
    assert response.model_dump() == {
        "failure_probability": 0.27,
        "failure_predicted": False,
        "decision_threshold": 0.30,
    }