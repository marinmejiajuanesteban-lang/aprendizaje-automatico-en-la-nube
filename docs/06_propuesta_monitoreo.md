# Fase 5 — Propuesta de Monitoreo

## Resumen ejecutivo

Esta fase no implementa un sistema de monitoreo en producción (no es exigido por
el checklist del curso), sino que **propone su diseño** y lo valida con una
demostración real usando Evidently AI: [`notebooks/03_monitoreo_evidently.ipynb`](../notebooks/03_monitoreo_evidently.ipynb).
Los reportes generados quedan como evidencia en [`docs/monitoring_reports/`](monitoring_reports/).

## Qué monitorear y por qué

Una vez el modelo está sirviendo predicciones (la API de la Fase 4), hay tres
señales de monitoreo, con distinta disponibilidad en el tiempo:

1. **Data drift en las features de entrada** — ¿las lecturas de sensores que le
   llegan al modelo se siguen pareciendo a los datos con los que se entrenó?
   Disponible **de inmediato**, no requiere esperar ningún resultado.
2. **Drift en las predicciones** — ¿la distribución de probabilidades que
   produce el modelo se mantiene estable, o empieza a predecir "falla" con
   mucha más o mucha menos frecuencia que antes? También disponible de
   inmediato (no requiere el resultado real, solo lo que el modelo predijo).
3. **Desempeño real** (Recall, Precision, F1) — solo se puede calcular cuando se
   confirma si la máquina realmente falló o no, lo cual llega **con retraso**
   (después de una revisión de mantenimiento o de que ocurra la falla). Es la
   señal más confiable, pero la más lenta.

La propuesta se apoya principalmente en la señal 1 (data drift) como alerta
temprana, complementada con una revisión periódica de la señal 3 cuando haya
suficientes casos confirmados.

## Herramienta: Evidently AI

Se usa `Report` + `DataDriftPreset` de Evidently (ya instalado desde la Fase 1.2)
para comparar un lote de datos de referencia (los datos de entrenamiento) contra
un lote "actual" (lo que le está llegando al modelo en producción). Evidently
calcula, por columna, una prueba estadística de distancia entre distribuciones
(Wasserstein para numéricas, Jensen-Shannon para categóricas) y marca cada
columna como "con drift" o no según un umbral.

## Demostración (evidencia en el notebook)

Se generaron dos reportes:

| Reporte | Comparación | Resultado |
|---|---|---|
| Caso sano | `X_train` vs. `X_test` (misma distribución) | 0 de 6 columnas con drift — control correcto |
| Caso con drift simulado | `X_train` vs. un lote con `Type` forzado a "L" y `Air temperature [K]` corrida +6K | 2 de 6 columnas con drift detectado (`Air temperature [K]`, `Type`) |

**Hallazgo importante:** en el caso simulado, el veredicto agregado de "Dataset
Drift" de Evidently siguió diciendo "NOT detected", porque por defecto solo
marca el dataset completo como "con drift" si más del 50% de las columnas lo
muestran (`drift_share`), y aquí solo fue el 33% (2 de 6) — a pesar de que una
de esas dos columnas (`Air temperature [K]`) es una de las features más
influyentes del modelo. Esta es la razón por la que la propuesta de abajo
recomienda no confiar solo en el veredicto agregado.

## Propuesta de implementación (diseño, no implementado)

1. **Frecuencia:** correr el chequeo de data drift con la misma cadencia del
   reentrenamiento programado ya existente (`src/flows/deploy.py`, semanal,
   domingos 2am) — comparando la ventana de datos de la semana entrante contra
   `X_train` de referencia.
2. **Qué revisar:** el detalle por columna, no solo el resumen agregado (ver
   hallazgo arriba). Alertar si cualquiera de las features numéricas o
   categóricas usadas por el modelo (`NUMERIC_FEATURES` / `CATEGORICAL_FEATURES`
   en `src/features/preprocessing.py`) muestra drift individualmente.
3. **Integración con Prefect:** agregar un nuevo `@task` (ej. `verificar_drift_task`)
   al flow existente en `src/flows/training_flow.py`, que corra el reporte de
   Evidently antes del entrenamiento y registre el resultado (como parámetro o
   artefacto en MLflow, aprovechando el tracking que ya existe).
4. **Trigger de reentrenamiento:** el flow ya tiene un *quality gate* que solo
   promueve un modelo a `champion` si Recall ≥ 0.80 (ver Fase 3). Se propone
   complementarlo con un segundo gate: si se detecta drift en una feature
   importante **y** el Recall de la última evaluación cae cerca del umbral,
   disparar un reentrenamiento inmediato (fuera del schedule semanal) en vez de
   esperar al domingo.
5. **Desempeño real diferido:** proponer una tarea separada (batch semanal o
   mensual) que recalcule Recall/Precision/F1 sobre los casos de la ventana
   anterior donde ya se confirmó el resultado real (`Machine failure`), y los
   compare contra la meta de la Sección 1.1 (Recall ≥ 0.80).

## Pendiente para futuras fases

- Implementación real del `@task` de drift dentro del flow de Prefect.
- Dashboard o alertas automáticas (Slack/email) cuando se detecte drift o caída
  de desempeño — fuera del alcance de este curso, mencionado como extensión
  natural.