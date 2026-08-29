# aprendizaje-automatico-en-la-nube
Proyecto final MLOps — mantenimiento predictivo industrial (AI4I 2020)


## Requisitos

- Python 3.11+ y [uv](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias.
- (Opcional) `make`, para usar los comandos estandarizados del `Makefile`.

## Setup

```bash
uv sync
```

## Comandos disponibles (Makefile)

| Comando | Qué hace |
|---|---|
| `make setup` | Instala/actualiza las dependencias |
| `make eda` | Abre Jupyter Lab |
| `make train` | Entrena el modelo (pendiente hasta Fase 2/3) |
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

## Estado del proyecto

- ✅ **Fase 1.1 — Problema de negocio:** ver [`docs/01_problema_negocio.md`](docs/01_problema_negocio.md).
- ✅ **Fase 1.2 — Setup del entorno:** este mismo repo (`uv`, estructura de carpetas, Makefile).
- ✅ **Fase 1.3 — EDA y modelo baseline:** ver [`notebooks/01_eda_baseline.ipynb`](notebooks/01_eda_baseline.ipynb)
  para el análisis completo, y [`docs/02_resultados_eda.md`](docs/02_resultados_eda.md)
  para el resumen ejecutivo de resultados.
- ⏳ **Fase 2 — Experiment Tracking (MLflow):** en curso.