# Riesgos del proyecto

Estos son los riesgos que identificamos en el proyecto, cómo nos daríamos
cuenta si pasan, y qué haríamos en cada caso.

## 1. Que el modelo deje de detectar fallas bien

El modelo se entrenó con muy pocas fallas reales (solo el 3.39% de los
datos). Si en producción esa proporción cambia — por ejemplo si entran
máquinas nuevas — el modelo puede empezar a fallar sin que nadie se dé
cuenta a simple vista.

**Cómo lo notaríamos:** revisando cada semana si la proporción de fallas
reales se aleja mucho del 3.39% que vimos en el entrenamiento.

**Qué haríamos:** volver a medir el Recall cuando tengamos suficientes
casos confirmados, y reentrenar si baja de 0.80.

## 2. Que el resumen de drift esconda un problema real

En la Fase 5 nos dimos cuenta de algo importante: Evidently puede decir
"todo bien" en el resumen general, aunque una columna clave (como la
temperatura del aire) sí tenga un cambio importante. Esto pasa porque el
resumen solo alerta si más de la mitad de las columnas cambian, y en
nuestro caso de prueba solo cambiaron 2 de 6.

**Cómo lo notaríamos:** revisando siempre el detalle por columna, no solo
el resumen general — sobre todo en las variables que más le importan al
modelo (Torque, desgaste de herramienta, velocidad).

**Qué haríamos:** poner alertas separadas para esas columnas clave, en
vez de confiar solo en el veredicto general.

## 3. Que se repita el problema de las rutas de MLflow

En la Fase 4 tuvimos un problema real: MLflow guarda la ruta exacta del
computador donde se entrenó el modelo, y esa ruta no sirve dentro de
Docker. Si alguien más del equipo reentrenca desde su propio computador,
el mismo error puede volver a pasar.

**Cómo lo notaríamos:** es fácil de notar — el sistema tira un error
claro (`OSError`) al intentar cargar el modelo.

**Qué haríamos:** siempre correr el paso de exportar el modelo
(`export_champion.py`) antes de meterlo a Docker, como ya lo dejamos
documentado.

## 4. Que el umbral de decisión (0.30) deje de servir

Elegimos 0.30 como el punto justo entre detectar fallas y no generar
demasiadas falsas alarmas, pero eso se calculó con los datos que tenemos
ahora. Si las máquinas o los sensores cambian con el tiempo, ese número
puede dejar de ser el correcto.

**Cómo lo notaríamos:** revisando de vez en cuando si el balance entre
Recall y Precision sigue siendo bueno con datos nuevos.

**Qué haríamos:** recalcular el umbral cada vez que se reentrenca el
modelo, en vez de dejarlo fijo para siempre.

## 5. Que los tests no cubran si la API realmente funciona bien

Ahora mismo los tests solo revisan que los datos que entran y salen de la
API tengan el formato correcto — no revisan si el endpoint `/predict`
realmente responde bien con un caso real.

**Cómo lo notaríamos:** si alguien cambia algo por dentro sin querer
romper la API, los tests actuales no lo detectarían.

**Qué haríamos:** agregar pruebas que sí manden una petición real a
`/predict` y revisen que la respuesta sea la esperada.