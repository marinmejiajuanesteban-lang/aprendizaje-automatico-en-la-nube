# Sección 1.1 — Problema de negocio, métricas, alcance y timeline

**Proyecto:** Mantenimiento predictivo industrial — AI4I 2020
**Curso:** Aprendizaje Automático en la Nube — Especialización en Ciencia de Datos e Inteligencia Artificial, Universidad de Medellín
**Grupo:** Esteban Marín, Diana Tuberquía, Carolina Tobón

---

## Problema de negocio (hipotético)

Una planta de manufactura opera máquinas industriales que pueden fallar sin previo aviso, generando paradas de producción costosas, retrabajo y reparaciones de emergencia. Hoy el mantenimiento es reactivo (se arregla cuando ya se dañó) o programado por calendario (se revisa cada tanto, sin importar el estado real de la máquina) — ambos desperdician recursos: lo reactivo por el costo de la parada no planeada, lo programado porque a veces cambia piezas que aún servían o no alcanza a detectar una falla que ocurre antes de la revisión programada.

La empresa quiere anticipar, con datos de sensores en tiempo real, cuándo una máquina está a punto de fallar, para intervenir antes de que la falla ocurra (mantenimiento predictivo).

**Pregunta medible:** dado un conjunto de lecturas de sensores (temperatura del aire, temperatura del proceso, velocidad rotacional, torque, desgaste de herramienta, tipo de producto), ¿se puede predecir si la máquina va a fallar?

## Dataset

**AI4I 2020 Predictive Maintenance Dataset** (UCI Machine Learning Repository / Kaggle) — 10.000 observaciones, 14 variables, datos sintéticos diseñados para reflejar patrones reales de fallas industriales.

**Variables predictoras:** temperatura del aire, temperatura del proceso, velocidad rotacional, torque, desgaste de la herramienta, tipo/calidad del producto (L/M/H).

**Variable objetivo (target):** `Machine failure` (binaria: 0/1). El dataset también incluye 5 banderas de tipo de falla (TWF, HDF, PWF, OSF, RNF) que se exploran como extensión del alcance.

## Métricas de éxito

El dataset está desbalanceado (las fallas son una minoría frente a las observaciones normales), por lo que **no se usa accuracy como métrica principal** — sería engañosa, ya que un modelo que siempre prediga "no falla" tendría accuracy alta sin ser útil. Se priorizan:

- **Recall de la clase "falla"** — prioridad principal, ya que no detectar una falla real es el error más costoso para el negocio (parada de producción no planeada).
- **Precision** — para no generar demasiadas falsas alarmas que reduzcan la confianza del equipo de mantenimiento en el sistema.
- **F1-score / AUC-PR** — como métricas de resumen general del desempeño.

**Meta declarada:** Recall ≥ 0.80 en la clase de falla, manteniendo una Precision razonable (a ajustar durante la fase de modelado).

## Alcance del proyecto

| | Incluye |
|---|---|
| **MVP (obligatorio)** | EDA completo · modelo baseline + un modelo más robusto, comparados · clasificación binaria de `Machine failure` · tracking de experimentos con MLflow · pipeline básico con Prefect · API con FastAPI (despliegue en tiempo real / web service) · Dockerfile básico · tests unitarios + linter · propuesta de monitoreo (diseño inicial) |
| **Extra (si el tiempo alcanza)** | Clasificación de los 5 tipos de falla (TWF/HDF/PWF/OSF/RNF) · optimización de la imagen Docker · despliegue real en la nube · CI/CD · reentrenamiento automático |

## Timeline y responsables

| Fecha | Fase | Entregable | Responsable |
|---|---|---|---|
| 25–27 ago | Fase 1 — Planificación y Setup | Problema de negocio, repositorio + entorno | Diana Tuberquía |
| 28–30 ago | Fase 1.3 — EDA y baseline | Notebook de EDA + modelo baseline | Carolina Tobón |
| 31 ago – 3 sept | Fase 2 — Experiment Tracking | MLflow configurado, varios modelos comparados, mejor modelo registrado | Esteban Marín |
| 4–6 sept | Fase 3 — Pipeline | Flows de Prefect (preprocesamiento + entrenamiento) | Carolina Tobón |
| 7–9 sept | Fase 4 — Deployment | Dockerfile + API FastAPI funcionando | Diana Tuberquía |
| 10 sept | Fase 5 — Monitoreo | Diseño de propuesta de monitoreo | Esteban Marín |
| 11 sept | Fase 6 — Testing y documentación | Tests, linter, README final | Diana Tuberquía |
| 12 sept | Buffer / revisión final | Repositorio pulido y entregado | Esteban Marín, Carolina Tobón, Diana Tuberquía |

## Repositorio

[github.com/marinmejiajuanesteban-lang/aprendizaje-automatico-en-la-nube](https://github.com/marinmejiajuanesteban-lang/aprendizaje-automatico-en-la-nube)
