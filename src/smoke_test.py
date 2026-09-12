"""Smoke test: verifica rápidamente que el entorno esté listo para entrenar."""

import sys


def check_imports() -> bool:
    """Verifica que las librerías clave estén instaladas."""
    libs = ["pandas", "sklearn", "mlflow", "prefect", "fastapi", "pandera"]
    ok = True
    for lib in libs:
        try:
            __import__(lib)
            print(f"[OK] {lib} instalado")
        except ImportError:
            print(f"[FALLO] {lib} no está instalado")
            ok = False
    return ok


def check_project_modules() -> bool:
    """Verifica que los módulos propios del proyecto se puedan importar."""
    modules = ["src.config"]
    ok = True
    for mod in modules:
        try:
            __import__(mod)
            print(f"[OK] {mod} se importa correctamente")
        except ImportError as e:
            print(f"[FALLO] {mod} no se pudo importar: {e}")
            ok = False
    return ok


def main() -> None:
    print("Corriendo smoke test...\n")
    checks = [check_imports(), check_project_modules()]

    if all(checks):
        print("\nSmoke test superado: el entorno está listo.")
        sys.exit(0)
    else:
        print("\nSmoke test falló: revisa los mensajes de [FALLO] arriba.")
        sys.exit(1)


if __name__ == "__main__":
    main()
    