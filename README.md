# aprendizaje-automatico-en-la-nube
Proyecto final MLOps — mantenimiento predictivo industrial (AI4I 2020)


## Requisitos

- Python 3.11+ y [uv](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias.
- (Opcional) `make`, para usar los comandos estandarizados del `Makefile`.
- Docker Desktop, para construir y correr la API en contenedor (ver sección "API de Predicciones" más abajo).

## Setup

```bash
uv sync
```

## Comandos disponibles (Makefile)

| Comando | Qué hace |
|---|---|
| `make setup` | Instala/actualiza las dependencias |
| `make eda` | Abre Jupyter Lab |
| `make train` | Entrena el modelo y lo registra en MLflow (`uv run python -m src.flows.training_flow`) |
| `make test` | Corre los tests unitarios |
| `make lint` | Revisa el estilo del código con ruff |
| `make format` | Formatea el código con ruff |

**En Windows:** `make` no viene instalado por defecto. Instálalo con `winget install GnuWin32.Make`. Si tu terminal sigue sin reconocerlo, usa el wrapper incluido en el repo: `.\make.ps1 <comando>` (ej. `.\make.ps1 eda`).


## Dataset

Este proyecto usa el **AI4I 2020 Predictive Maintenance Dataset** (UCI Machine
Learning Repository / Kaggle). El archivo **no está versionado en git** (ver
`.gitignore`), así que cada quien debe descargarlo:

1. Descárgalo desde [UCI](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)
   o [Kaggle](https://www.kaggle.com/datasets/stephanmatzka/predictive-maintenance-dataset-ai4i-2020).
2. Guarda el archivo como `data/raw/ai4i2020.csv` (crea la carpeta `raw` si no existe).

## Experiment Tracking (MLflow)

Los experimentos de entrenamiento se trackean con MLflow. Los runs se guardan
localmente en `mlruns/` (no versionado en git — se regenera al correr el
notebook, igual que la data), así que para verlos:

1. Corre [`notebooks/02_mlflow_tracking.ipynb`](notebooks/02_mlflow_tracking.ipynb)
   de principio a fin (esto genera los runs en tu máquina).
2. Levanta la interfaz visual:
```bash
   uv run mlflow ui --backend-store-uri file:./mlruns
```
3. Abre `http://127.0.0.1:5000` en tu navegador.

El modelo candidato final está registrado en el Model Registry de MLflow como
`mantenimiento-predictivo-hgb`, con el alias `champion`.

## Pipeline de Entrenamiento (Prefect)

El entrenamiento está automatizado con un flow de Prefect que encapsula carga y
validación de datos (con Pandera), preprocesamiento, entrenamiento y registro en
MLflow — con un *quality gate* que solo promueve el modelo a `champion` si
supera la meta de Recall ≥ 0.80. Código en `src/data`, `src/features`,
`src/models` y `src/flows`.

Para correr el pipeline completo (una sola vez):
```bash
uv run python -m src.flows.training_flow
```

Para registrar un despliegue programado (reentrenamiento automático semanal,
cada domingo 2:00 am):
```bash
uv run python -m src.flows.deploy
```

Detalle completo en [`docs/04_pipeline_entrenamiento.md`](docs/04_pipeline_entrenamiento.md).

## API de Predicciones (FastAPI + Docker)

El modelo campeón se expone como una API REST con FastAPI, empaquetada en una
imagen Docker. Antes de correrla (local o en Docker), hay que exportar una
copia portable y autocontenida del modelo campeón:

```bash
uv run python -m src.models.export_champion
```

Este paso es necesario porque MLflow guarda rutas absolutas del sistema de
archivos en su tracking store local, que no son portables entre máquinas ni
dentro de un contenedor Docker (ver detalle en
[`docs/05_deployment.md`](docs/05_deployment.md)).

**Correr localmente:**
```bash
uv run uvicorn src.api.main:app --reload
```

**Correr con Docker:**
```bash
docker build -t mantenimiento-predictivo-api .
docker run -p 8000:8000 mantenimiento-predictivo-api
```

En ambos casos, la documentación interactiva (Swagger UI) queda disponible en
`http://127.0.0.1:8000/docs`.

Detalle completo en [`docs/05_deployment.md`](docs/05_deployment.md).

## Monitoreo (Evidently AI)

Se propone (y se valida con una demostración real) un esquema de monitoreo de
*data drift* sobre las features de entrada del modelo, usando Evidently AI. La
demostración compara los datos de entrenamiento contra un lote simulado con un
cambio operativo realista, y confirma que Evidently detecta el drift a nivel de
columna individual.

Ver el notebook de demostración en
[`notebooks/03_monitoreo_evidently.ipynb`](notebooks/03_monitoreo_evidently.ipynb)
(los reportes HTML generados quedan en
[`docs/monitoring_reports/`](docs/monitoring_reports/)), y la propuesta completa
de diseño (qué monitorear, con qué frecuencia, y qué dispararía un
reentrenamiento) en [`docs/06_propuesta_monitoreo.md`](docs/06_propuesta_monitoreo.md).

## Testing y Buenas Prácticas

El proyecto centraliza su configuración (nombre del modelo, umbral de
decisión, rutas) en [`src/config.py`](src/config.py), normaliza los finales
de línea con `.gitattributes`, y cuenta con linting (Ruff) y una suite de 11
tests unitarios (pytest) sobre la validación de datos, el preprocesamiento y
los esquemas de la API.

```bash
make lint    # revisa el estilo del código
make format  # formatea el código automáticamente
make test    # corre los tests unitarios
```

Ver el detalle completo en
[`docs/07_testing_buenas_practicas.md`](docs/07_testing_buenas_practicas.md).

## Estado del proyecto

- **Fase 1.1 — Problema de negocio:** ver [`docs/01_problema_negocio.md`](docs/01_problema_negocio.md).
- **Fase 1.2 — Setup del entorno:** este mismo repo (`uv`, estructura de carpetas, Makefile).
- **Fase 1.3 — EDA y modelo baseline:** ver [`notebooks/01_eda_baseline.ipynb`](notebooks/01_eda_baseline.ipynb)
  para el análisis completo, y [`docs/02_resultados_eda.md`](docs/02_resultados_eda.md)
  para el resumen ejecutivo de resultados.
- **Fase 2 — Experiment Tracking (MLflow):** ver [`notebooks/02_mlflow_tracking.ipynb`](notebooks/02_mlflow_tracking.ipynb)
  para el tracking completo, y [`docs/03_resultados_experiment_tracking.md`](docs/03_resultados_experiment_tracking.md)
  para el resumen ejecutivo de resultados.
- **Fase 3 — Pipeline de Entrenamiento (Prefect):** ver [`src/flows/training_flow.py`](src/flows/training_flow.py)
  para el pipeline completo, y [`docs/04_pipeline_entrenamiento.md`](docs/04_pipeline_entrenamiento.md)
  para el resumen ejecutivo de resultados.
- **Fase 4 — Deployment (FastAPI + Docker):** ver [`src/api/main.py`](src/api/main.py)
  para la API completa, y [`docs/05_deployment.md`](docs/05_deployment.md)
  para el resumen ejecutivo de resultados.
- **Fase 5 — Monitoreo (propuesta de diseño):** ver [`notebooks/03_monitoreo_evidently.ipynb`](notebooks/03_monitoreo_evidently.ipynb)
  para la demostración con Evidently AI, y [`docs/06_propuesta_monitoreo.md`](docs/06_propuesta_monitoreo.md)
  para la propuesta completa.