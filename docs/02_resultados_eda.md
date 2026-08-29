# Resultados del EDA y modelo baseline (Fase 1.3)

**Notebook completo:** [`notebooks/01_eda_baseline.ipynb`](../notebooks/01_eda_baseline.ipynb)

## Resumen del dataset

El dataset AI4I 2020 (10.000 filas, 14 columnas) está completamente limpio: 0
valores nulos y 0 filas duplicadas. La variable objetivo (`Machine failure`) está
fuertemente desbalanceada — solo el **3.39%** de las observaciones son fallas
(339 de 10.000). Esto confirma la decisión, tomada desde la Sección 1.1, de no
usar accuracy como métrica y priorizar Recall, Precision, F1 y AUC-PR.

## Hallazgos principales del EDA

- **Torque**, **Tool wear** y **Rotational speed** son las variables más
  predictivas: se ve separación visible entre máquinas que fallan y las que no
  al compararlas por clase (boxplots), aunque su correlación lineal individual
  con el target es baja — los mecanismos de falla del dataset son condicionales
  (ej. desgaste × torque superando un umbral), no relaciones lineales simples.
- **`Type`** (calidad del producto) también aporta señal: a menor calidad, mayor
  tasa de falla (L: 3.92%, M: 2.77%, H: 2.09%).
- **Air temperature** y **Process temperature** están muy correlacionadas entre sí
  (0.88), igual que **Rotational speed** y **Torque** (-0.88) — redundancia
  esperada por el diseño del dataset.
- Los 5 mecanismos de falla (TWF, HDF, PWF, OSF, RNF) se superponen entre sí
  (una falla puede tener más de una bandera activa), lo que confirma que el MVP
  debe enfocarse en clasificación binaria de `Machine failure`.

## Comparación de modelos

Se entrenaron 10 algoritmos de clasificación con el mismo preprocesamiento
(escalado + one-hot encoding) y el mismo trato asimétrico del error: un falso
negativo (no detectar una falla real) es más costoso para el negocio que un falso
positivo, así que se le da más peso a la clase minoritaria durante el
entrenamiento (`class_weight="balanced"` o `sample_weight`, según lo que soporte
cada algoritmo).

| Modelo | Recall (falla) | Precision (falla) | F1 | AUC-PR |
|---|---|---|---|---|
| SVM | 0.897 | 0.272 | 0.418 | 0.616 |
| Gradient Boosting | 0.868 | 0.322 | 0.470 | 0.662 |
| AdaBoost | 0.853 | 0.262 | 0.401 | 0.491 |
| Regresión Logística | 0.824 | 0.142 | 0.242 | 0.382 |
| Naive Bayes | 0.794 | 0.152 | 0.255 | 0.263 |
| **Hist Gradient Boosting** | **0.794** | **0.730** | **0.761** | **0.834** |
| Random Forest | 0.691 | 0.734 | 0.712 | 0.781 |
| Árbol de Decisión | 0.618 | 0.700 | 0.656 | 0.445 |
| K-Nearest Neighbors | 0.279 | 0.826 | 0.418 | 0.465 |
| Extra Trees | 0.279 | 1.000 | 0.437 | 0.715 |

## Modelo elegido: Hist Gradient Boosting

Aunque SVM, Gradient Boosting, AdaBoost y Regresión Logística logran un Recall
más alto, lo hacen sacrificando la Precision de forma poco práctica (hasta 7-9 de
cada 10 alarmas serían falsas). **Hist Gradient Boosting** ofrece el mejor
balance: Recall (0.794) casi igual a la meta declarada en la Sección 1.1 (≥0.80),
la mejor Precision entre los modelos con Recall competitivo (0.730), el mejor F1
(0.761) y el mejor AUC-PR (0.834) de los 10 modelos evaluados.

**Matriz de confusión (set de prueba, 2.000 casos):** de 68 fallas reales, el
modelo detectó 54 (14 se le escaparon) y generó solo 20 falsas alarmas sobre
1.932 casos sin falla.

## Pendiente para la Fase 2

- Ajustar el umbral de decisión de Hist Gradient Boosting (su AUC-PR alto sugiere
  que hay margen para subir el Recall a ≥0.80 sin perder mucha Precision).
- Tracking formal de experimentos con MLflow.
- Probar SMOTE (ya instalado vía `imbalanced-learn`) como alternativa al
  `sample_weight`.
- Tuning de hiperparámetros con Optuna.
- Validación cruzada, en vez de un solo split train/test.