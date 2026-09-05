# Fase 6 — Testing y Buenas Prácticas

## Resumen ejecutivo

Esta fase no agrega funcionalidad nueva al proyecto: endurece lo que ya existe.
El objetivo fue cerrar brechas típicas de un proyecto que creció rápido durante
las Fases 3-5 (constantes duplicadas, cero tests automatizados, sin
configuración de estilo de código) antes de la entrega final. El trabajo tuvo
tres frentes: centralizar configuración, normalizar el repositorio, y agregar
una primera capa de tests unitarios sobre la lógica más crítica del proyecto.

## 1. Centralización de configuración (`src/config.py`)

Antes de esta fase, constantes como el nombre del modelo registrado, el alias
`champion`, el umbral de decisión (0.30) y la ruta del modelo local exportado
estaban duplicadas de forma independiente en tres archivos distintos:
`src/models/train.py`, `src/models/export_champion.py` y
`src/api/model_loader.py`. Esto es una violación clásica del principio DRY
(*Don't Repeat Yourself*): si en algún momento se necesitara cambiar el umbral
de decisión, habría que recordar actualizarlo en los tres lugares a la vez, y
un olvido produciría un desfase silencioso entre el entrenamiento y el
servicio del modelo.

La solución fue crear `src/config.py` como única fuente de verdad para estas
constantes, y hacer que los demás módulos las importen desde ahí en lugar de
redefinirlas. Se verificó que el cambio no rompiera nada re-ejecutando el
pipeline de entrenamiento completo (`make train`) y el script de exportación
del modelo, confirmando que las métricas y el comportamiento fueran idénticos
a antes del refactor.

## 2. Normalización del repositorio (`.gitattributes`)

Se agregó un archivo `.gitattributes` con la regla `* text=auto eol=lf`, que
le indica a git que normalice los finales de línea a LF (estilo Unix) para
todo archivo de texto, sin importar el sistema operativo desde el que se
edite. Esto evita el problema común de que Windows (CRLF) y Linux/Mac (LF)
generen diffs de git que solo muestran cambios de fin de línea sin cambios
reales de contenido — algo especialmente relevante en este proyecto, que corre
en Windows localmente pero se despliega en un contenedor Docker basado en
Linux.

## 3. Linting con Ruff

Se configuró Ruff (`[tool.ruff]` y `[tool.ruff.lint]` en `pyproject.toml`) con:

- `line-length = 100` y `target-version = "py311"`, acordes al proyecto.
- `select = ["E", "F", "I", "UP"]`: errores de estilo (pycodestyle), errores
  reales como imports sin usar (pyflakes), orden de imports (isort) y
  modernización de sintaxis (pyupgrade).
- `exclude = ["notebooks"]`: decisión deliberada de no lintear los notebooks
  exploratorios ya validados de las Fases 1-2 y 5. Reformatear notebooks
  antiguos que ya cumplieron su propósito no aporta valor proporcional al
  esfuerzo, así que el linting se enfoca en el código de producción
  (`src/`, `tests/`).

Al activar estas reglas se encontraron 33 hallazgos, casi todos de formato en
notebooks (ya excluidos después) y uno real: un import sin usar de
`DECISION_THRESHOLD` en `model_loader.py`, que solo estaba ahí para que
`main.py` lo heredara indirectamente. Se corrigió haciendo que `main.py`
importe `DECISION_THRESHOLD` directamente desde `src.config`, lo cual además
de dejar el lint limpio es mejor diseño: cada módulo declara explícitamente
qué necesita, en lugar de depender de una cadena de reexportaciones. Tras el
fix y unos ajustes menores de formato, `ruff check .` reporta
`All checks passed!`.

## 4. Tests unitarios con pytest

Se agregaron 11 tests unitarios en `tests/unit/`, organizados en tres
archivos según el módulo que cubren:

- **`test_load_data.py`** (3 tests): valida que el esquema de Pandera
  (`raw_schema`) acepte datos correctos y rechace datos inválidos — un tipo
  de máquina (`Type`) fuera de las categorías esperadas, y una temperatura
  fuera del rango físicamente razonable.
- **`test_preprocessing.py`** (3 tests): valida que `get_feature_target_split`
  descarte correctamente las columnas que no deben usarse como predictoras
  (identificadores, fugas de información como `TWF`/`HDF`/`PWF`/`OSF`/`RNF`),
  y que el preprocesador (`ColumnTransformer`) se construya y transforme datos
  sin errores.
- **`test_schemas.py`** (5 tests): valida los esquemas Pydantic de la API
  (`SensorReading`, `PredictionResponse`) — que acepten payloads válidos, que
  rechacen valores inválidos (tipo de máquina inválido, torque negativo), y
  que la reconstrucción de nombres de columnas originales
  (`to_model_input`) sea correcta.

Un detalle técnico relevante: `uv run pytest` (el entry point de consola de
pytest) no agrega automáticamente el directorio actual a `sys.path`, a
diferencia de `python -m pytest`. Sin este ajuste, los `from src...` imports
de los archivos de test habrían fallado con `ModuleNotFoundError`. Se
previno agregando `pythonpath = ["."]` a `[tool.pytest.ini_options]` en
`pyproject.toml` antes de escribir los tests.

Resultado: los 11 tests pasan (`11 passed in 3.67s`), cubriendo la validación
de datos de entrada, la lógica de features, y los contratos de la API.

## Cómo correr

```bash
make lint    # revisa el estilo del código con ruff
make format  # formatea el código automáticamente con ruff
make test    # corre los 11 tests unitarios con pytest
```

## Pendiente para futuras fases

- Tests de integración para los endpoints de la API (ej. con
  `TestClient` de FastAPI), en lugar de solo los esquemas de entrada/salida.
- Integración continua (CI) que corra `make lint` y `make test`
  automáticamente en cada push (ej. GitHub Actions) — quedó fuera de alcance
  de este curso pero sería el siguiente paso natural en un proyecto real.
- Flujo de trabajo con ramas y pull requests, en lugar de commits directos a
  `main`.