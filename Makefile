.PHONY: help setup eda train test lint format smoke

help:
	@echo "Comandos disponibles:"
	@echo "  make setup   - instala/actualiza las dependencias del proyecto"
	@echo "  make smoke    - verifica rápido que el entorno esté listo"
	@echo "  make eda     - abre Jupyter Lab para trabajar los notebooks"
	@echo "  make train   - entrena el modelo y lo registra en MLflow (pipeline de Prefect)"
	@echo "  make test    - corre los tests unitarios"
	@echo "  make lint    - revisa el estilo del codigo con ruff"
	@echo "  make format  - formatea el codigo automaticamente con ruff"

setup:
	uv sync

smoke:
	uv run python -m src.smoke_test
	
eda:
	uv run jupyter lab

train:
	uv run python -m src.flows.training_flow

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .

format:
	uv run ruff format .