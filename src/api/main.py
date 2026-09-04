"""API FastAPI para servir el modelo de mantenimiento predictivo (Fase 4 — Deployment)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.model_loader import load_champion_model, DECISION_THRESHOLD
from src.api.schemas import SensorReading, PredictionResponse

model_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta una sola vez al arrancar la API — cargar el modelo aquí,
    # no dentro de /predict, para no pagar el costo de carga en cada request.
    model_state["model"] = load_champion_model()
    yield
    model_state.clear()


app = FastAPI(
    title="API de Mantenimiento Predictivo",
    description="Predice si una máquina va a fallar a partir de lecturas de sensores (AI4I 2020).",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": "model" in model_state,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(reading: SensorReading):
    model = model_state["model"]
    df_input = reading.to_model_input()
    probability = float(model.predict_proba(df_input)[:, 1][0])
    predicted = probability >= DECISION_THRESHOLD

    return PredictionResponse(
        failure_probability=probability,
        failure_predicted=predicted,
        decision_threshold=DECISION_THRESHOLD,
    )