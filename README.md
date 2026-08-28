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
