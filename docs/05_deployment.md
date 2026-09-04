# Fase 4 — Deployment

## Resumen ejecutivo

Esta fase expone el modelo campeón (entrenado y registrado en la Fase 3) como
un servicio HTTP mediante una API REST construida con FastAPI, empaquetada en
una imagen Docker para que pueda ejecutarse en cualquier máquina sin depender
del entorno local de desarrollo.

La API recibe una lectura de sensores de una máquina y devuelve la
probabilidad de falla, aplicando el umbral de decisión de negocio (0.30)
definido en la Fase 2, en lugar del umbral por defecto de scikit-learn (0.5).

## Arquitectura del código

src/api/
├── init.py
├── schemas.py # Esquemas Pydantic de entrada/salida
├── model_loader.py # Carga del modelo campeón
└── main.py # Endpoints FastAPI

src/models/
└── export_champion.py # Exporta una copia portable del modelo campeón

Dockerfile
.dockerignore


### `schemas.py`

Define `SensorReading`, el esquema de entrada, usando `Field(alias=...)` para
poder recibir el JSON con los nombres de columnas originales del dataset
(`"Air temperature [K]"`, con espacios y corchetes) mientras internamente se
usan nombres de atributo válidos en Python (`air_temperature_k`). Incluye
validaciones de rango básicas (`gt`, `ge`) para rechazar valores físicamente
imposibles antes de que lleguen al modelo.

`PredictionResponse` es el esquema de salida: probabilidad de falla,
predicción booleana y el umbral de decisión usado.

### `model_loader.py`

Carga el modelo campeón usando el flavor `sklearn` de MLflow (no el `pyfunc`
genérico) para conservar acceso a `predict_proba()` y poder aplicar el umbral
de decisión personalizado.

### `main.py`

Usa el patrón `lifespan` de FastAPI para cargar el modelo **una sola vez** al
arrancar la aplicación (no en cada request). Expone:

- `GET /health` — verifica que el servicio está arriba y el modelo cargado.
- `POST /predict` — recibe un `SensorReading` y devuelve un `PredictionResponse`.
- `GET /docs` — documentación interactiva (Swagger UI), autogenerada por FastAPI.

## Lección aprendida: portabilidad de MLflow

Durante el despliegue en Docker apareció un error real de MLOps, no un bug de
código:

OSError: No such file or directory: '/c:/Users/.../mlruns/.../artifacts/modelo/.'


El *tracking store* local de MLflow (`file:./mlruns`) guarda, en los metadatos
del experimento, la ruta **absoluta** del sistema de archivos donde se creó
(en este caso, una ruta de Windows generada en la Fase 2 desde `notebooks/`).
Esa ruta no existe dentro del contenedor Docker, que tiene su propio
filesystem Linux — aunque el contenedor tenga una copia completa de
`mlruns/`, MLflow intenta resolver el artefacto usando la ruta original
grabada al crear el experimento.

**Solución:** en vez de cargar el modelo directamente desde el Model Registry
(`models:/mantenimiento-predictivo-hgb@champion`) dentro del contenedor, se
creó `src/models/export_champion.py`, que usa `mlflow.sklearn.save_model()`
para exportar una copia **autocontenida y portable** del modelo a
`models/champion/` (sin dependencias de rutas absolutas). Esta carpeta es la
que se copia a la imagen Docker, y `model_loader.py` carga desde ahí en lugar
de desde el registro.

`models/champion/` es un artefacto regenerable (no se versiona en git) — se
reconstruye cada vez que hay un nuevo modelo campeón corriendo:

```bash
uv run python -m src.models.export_champion
```

## Cómo correr la API localmente

```bash
uv run python -m src.models.export_champion   # solo si no existe models/champion aún
uv run uvicorn src.api.main:app --reload
```

Documentación interactiva en `http://127.0.0.1:8000/docs`.

## Cómo correr la API con Docker

```bash
uv run python -m src.models.export_champion   # genera models/champion/ (prerequisito)
docker build -t mantenimiento-predictivo-api .
docker run -p 8000:8000 mantenimiento-predictivo-api
```

Documentación interactiva en `http://127.0.0.1:8000/docs` (el contenedor
expone el puerto 8000 mapeado al host).

## Ejemplo de uso

Request a `POST /predict`:

```json
{
  "Type": "L",
  "Air temperature [K]": 251,
  "Process temperature [K]": 251,
  "Rotational speed [rpm]": 1,
  "Torque [Nm]": 0,
  "Tool wear [min]": 0
}
```

Response:

```json
{
  "failure_probability": 0.2747229789425598,
  "failure_predicted": false,
  "decision_threshold": 0.3
}
```

## Pendientes para próximas fases

- Fase 5 — Monitoreo: diseño de monitoreo de *data drift* y desempeño del
  modelo en producción con Evidently AI.
- Fase 6 — Testing y buenas prácticas: pruebas automatizadas de la API y del
  pipeline, y revisión final de buenas prácticas de MLOps.