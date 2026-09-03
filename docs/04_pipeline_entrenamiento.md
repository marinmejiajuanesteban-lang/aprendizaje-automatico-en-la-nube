# Fase 3 — Pipeline de Entrenamiento con Prefect

## Resumen ejecutivo

En esta fase se convirtió el flujo de entrenamiento validado en la Fase 2 (Hist Gradient Boosting + hiperparámetros de Optuna + umbral de decisión 0.30) en un pipeline reproducible y automatizado, usando **Prefect** para la orquestación y **Pandera** para la validación de datos. El pipeline carga y valida los datos crudos, los preprocesa, entrena el modelo, lo evalúa contra la meta de negocio (Recall ≥ 0.80) y, si la cumple, lo registra y promueve automáticamente como modelo `champion` en el Model Registry de MLflow. Además, se configuró un despliegue programado (scheduling) con Prefect para permitir reentrenamientos periódicos sin intervención manual.

## Arquitectura del código (`src/`)

El código de esta fase vive en módulos de Python reutilizables, no en un notebook — un flow de Prefect está pensado para ejecutarse como proceso, no en celdas interactivas. Además, esta separación deja el código listo para ser reutilizado por la API de la Fase 4.

| Módulo | Responsabilidad |
|---|---|
| `src/data/load_data.py` | Carga el CSV crudo y lo valida contra un esquema de Pandera (`raw_schema`): tipos, columnas esperadas y rangos razonables por sensor. |
| `src/features/preprocessing.py` | Separa features (`X`) y target (`y`); construye el `ColumnTransformer` (escalado + one-hot) sin ajustar. |
| `src/models/train.py` | Arma el pipeline de entrenamiento con los hiperparámetros ganadores de Optuna, lo entrena con `sample_weight` balanceado, lo evalúa con el umbral 0.30, y lo loguea/registra en MLflow. |
| `src/flows/training_flow.py` | Flow de Prefect (`@flow`) que orquesta las 4 tareas anteriores como `@task`, con un *quality gate*: solo promueve el modelo a `champion` si Recall ≥ 0.80 (la meta de la Sección 1.1). |
| `src/flows/deploy.py` | Define un despliegue programado del flow (cron semanal) usando `training_flow.serve(...)`. |

## Validación de datos (Pandera)

El esquema `raw_schema` define el contrato del dataset AI4I2020: 14 columnas con tipos y rangos esperados (por ejemplo, `Air temperature [K]` entre 290-310K, `Type` solo puede ser `L`/`M`/`H`, las banderas de falla solo 0/1). Se probó explícitamente que el esquema **rechaza** datos inválidos (se inyectó un valor de `Type` fuera de catálogo y Pandera lo detectó correctamente), no solo que acepta los válidos.

## Cómo correr el pipeline

Desde la raíz del proyecto, con el entorno activado:

```powershell
# Corrida única del pipeline completo
uv run python -m src.flows.training_flow

# Registrar el despliegue programado (cron: cada domingo 2:00 am)
uv run python -m src.flows.deploy
```

## Resultados

El pipeline reprodujo exactamente las métricas del modelo final de la Fase 2:

| Métrica | Valor |
|---|---|
| Recall | 0.8235 |
| Precision | 0.6022 |
| F1-score | 0.6957 |
| AUC-PR | 0.8485 |

Como Recall (0.8235) ≥ 0.80, el pipeline promovió automáticamente el modelo a `champion` — versión 3 de `mantenimiento-predictivo-hgb` en el Model Registry (la v1 fue la del notebook de la Fase 2; la v2 y v3 salieron de correr el flow durante el desarrollo de esta fase).

## Scheduling automático

Se configuró un despliegue de Prefect (`src/flows/deploy.py`) con `training_flow.serve(cron="0 2 * * 0")`, que deja el flow programado para correr automáticamente cada domingo a las 2:00 am. Se confirmó que el despliegue se registra correctamente y queda "escuchando" runs programados. No se dejó corriendo de forma permanente, ya que no hay infraestructura de servidor dedicada para este proyecto académico — la demostración cubre el requisito de la Fase 3 sobre scheduling.

## Pendientes para próximas fases

- Fase 4 (Deployment): reutilizar `src/data`, `src/features` y `src/models` desde la API de FastAPI para servir el modelo `champion` cargado desde el Model Registry.
- Fase 5 (Monitoreo): diseñar propuesta de monitoreo/drift sobre las features de entrada (ya se cuenta con Evidently instalado).
- Retraining automático real (disparado por drift o por umbral de rendimiento) queda fuera del alcance del MVP — es "Nice to have" según el enunciado oficial.