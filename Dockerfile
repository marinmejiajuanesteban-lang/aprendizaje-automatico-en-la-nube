FROM python:3.11-slim

WORKDIR /app

# Instalar uv dentro de la imagen
RUN pip install --no-cache-dir uv

# Copiar primero solo el "recetario" de dependencias — así Docker cachea esta
# capa y solo la vuelve a ejecutar si pyproject.toml/uv.lock cambian, no cada
# vez que se edita el código (builds mucho más rápidos al iterar).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copiar el código y el modelo entrenado (models/champion/ es la copia portable
# y autocontenida del modelo champion — hay que generarla antes de construir la
# imagen con: uv run python -m src.models.export_champion).
COPY src/ ./src/
COPY models/champion ./models/champion

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]