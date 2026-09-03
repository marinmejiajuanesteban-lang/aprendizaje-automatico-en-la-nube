"""Despliegue programado del flow de entrenamiento (Fase 3 — scheduling automático)."""

from src.flows.training_flow import training_flow

if __name__ == "__main__":
    # Deja este proceso corriendo (Ctrl+C para detenerlo) y Prefect dispara
    # training_flow automáticamente según el cron definido — no hace falta
    # dejarlo corriendo para siempre, esto es para demostrar que el
    # reentrenamiento programado es posible.
    training_flow.serve(
        name="reentrenamiento-programado-mantenimiento-predictivo",
        cron="0 2 * * 0",  # cada domingo a las 2:00 am
    )