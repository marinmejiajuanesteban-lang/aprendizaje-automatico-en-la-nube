# Fase 2 — Resultados de Experiment Tracking (MLflow)

## Objetivo de esta fase

Configurar un sistema de tracking de experimentos con MLflow, comparar el desempeño del modelo elegido en la Fase 1.3 (Hist Gradient Boosting) bajo distintas condiciones —validación cruzada, ajuste de umbral, tuning de hiperparámetros y una técnica alternativa de manejo de desbalance (SMOTE)— y registrar el modelo final como candidato a producción.

## Setup de MLflow

- **Tracking URI:** `file:../mlruns` (carpeta `mlruns/` en la raíz del proyecto, no versionada en git — se regenera al correr el notebook, igual que la data).
- **Experimento:** `mantenimiento-predictivo-ai4i2020`.
- **Notebook:** `notebooks/02_mlflow_tracking.ipynb`, con la misma metodología markdown → código → análisis usada en la Fase 1.3.
- Todos los runs reutilizan el mismo split (`random_state=42`, `stratify=y`) y preprocesamiento (`ColumnTransformer`) definidos en la Fase 1.3, para que los resultados sean comparables.

## Runs registrados

| Run | Modelo | Manejo de desbalance | Evaluación | Recall | Precision | F1 | AUC-PR |
|---|---|---|---|---|---|---|---|
| `hist_gradient_boosting_baseline` | Hist Gradient Boosting | `sample_weight` balanceado | Split simple (umbral 0.5) | 0.7941 | 0.7297 | 0.7606 | 0.8343 |
| `hist_gradient_boosting_cv5` | Hist Gradient Boosting | `sample_weight` balanceado | CV 5 folds (umbral 0.5) | 0.7712 ± 0.045 | 0.6710 ± 0.056 | 0.7164 ± 0.043 | — |
| `random_forest_cv5` | Random Forest | `class_weight="balanced"` | CV 5 folds (umbral 0.5) | 0.6643 ± 0.020 | 0.7282 ± 0.062 | 0.6934 ± 0.031 | — |
| `hist_gradient_boosting_umbral_030` | Hist Gradient Boosting | `sample_weight` balanceado | Split simple, umbral 0.30 | 0.8088 | 0.6044 | 0.6918 | 0.8343 |
| `hist_gradient_boosting_optuna_umbral_030` | Hist Gradient Boosting (tuneado) | `sample_weight` balanceado | Split simple, umbral 0.30 | **0.8235** | 0.6022 | 0.6957 | **0.8485** |
| `hist_gradient_boosting_smote_cv5` | Hist Gradient Boosting (tuneado) | SMOTE | CV 5 folds (umbral 0.5) | 0.7935 | 0.5726 | 0.6642 | 0.7894 |

## Hallazgos principales

**1. Cross-validation confirma la elección de la Fase 1.3.** Comparando Hist Gradient Boosting contra Random Forest con CV de 5 folds (misma metodología para ambos), Hist Gradient Boosting mantiene mejor Recall (0.7712 vs. 0.6643) — la métrica prioritaria según la Sección 1.1 — aunque Random Forest tiene mejor Precision. Se confirma con más rigor la elección hecha en la Fase 1.3 con un único split.

**2. El umbral de decisión importa tanto como el modelo.** Con el umbral por defecto (0.5), Hist Gradient Boosting no alcanza la meta de Recall ≥ 0.80 de la Sección 1.1. Bajando el umbral a 0.30, el Recall sube a 0.8088 sin sacrificar demasiada Precision (se mantiene por encima de 0.60). Umbrales más bajos siguen subiendo el Recall, pero la Precision se desploma (a 0.10, Precision cae a 0.44).

**3. El tuning con Optuna aporta una mejora real, aunque modesta.** Usando AUC-PR (una métrica independiente del umbral) como objetivo de la búsqueda —para evitar que el tuning sesgue hacia un modelo degenerado que maximice Recall a costa de casi todo lo demás—, Optuna encontró hiperparámetros (`max_iter=223, max_depth=8, learning_rate≈0.057, max_leaf_nodes=54, l2_regularization≈0.217`) que, combinados con el umbral de 0.30, mejoran tanto el Recall (0.8235) como el AUC-PR (0.8485) frente a los hiperparámetros por defecto, manteniendo la Precision estable.

**4. SMOTE no superó al manejo de desbalance por pesos.** Se probó SMOTE (sobremuestreo sintético de la clase minoritaria) como alternativa a `sample_weight`, aplicado correctamente solo sobre el fold de entrenamiento en cada iteración de cross-validation (usando `imbalanced-learn.Pipeline` para evitar fuga de información hacia el fold de validación). El resultado fue peor en Precision y AUC-PR que `sample_weight` con los mismos hiperparámetros. Para este dataset, el desbalance (3.39% de fallas) no parece ser tan extremo como para que la escasez de ejemplos reales sea el cuello de botella — el modelo ya tiene suficientes casos reales para aprender el patrón sin necesitar datos sintéticos. Se descarta SMOTE como técnica para este proyecto.

## Modelo final y Model Registry

**Modelo candidato final:** Hist Gradient Boosting + hiperparámetros optimizados con Optuna + `sample_weight` balanceado + umbral de decisión = 0.30.

- Recall: **0.8235** (supera la meta de ≥ 0.80 de la Sección 1.1)
- Precision: 0.6022
- F1: 0.6957
- AUC-PR: 0.8485

Registrado en el Model Registry de MLflow como **`mantenimiento-predictivo-hgb`**, versión 1, con el alias **`champion`** — cualquier código futuro (por ejemplo, la API de la Fase 4) puede cargar este modelo con `models:/mantenimiento-predictivo-hgb@champion` sin necesitar el run_id exacto.

## Pendientes para próximas fases

- Fase 3 (Pipeline): automatizar este flujo de entrenamiento + tracking con Prefect.
- Fase 4 (Deployment): cargar el modelo `@champion` desde el registry en la API de FastAPI.
- Si se actualiza el modelo más adelante (nuevos datos, más tuning), registrar como versión 2 y mover el alias `champion` — MLflow deja trazabilidad completa de qué modelo estuvo en producción en cada momento.