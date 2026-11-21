# Proyecto Final - Algoritmos Avanzados de Búsqueda y Optimización

Trabajo final grupal ALGABO 2026 (UCU). Selección y ruteo de pedidos de libros
con un vehículo de capacidad limitada y tiempo máximo: solución exacta vs.
heurística en Python.

**Integrantes:** Domingo Leiva, Facundo Diaz, Santiago Alba, Marcos Devincenzi

## El problema

Un vehículo sale de un depósito, entrega pedidos de libros en centros y vuelve.
Hay que decidir qué pedidos atender, en qué orden y por qué tramos viajar para
**maximizar la prioridad total**, sin superar la capacidad (cajas) ni el tiempo
límite (viaje + descarga). Si dos planes empatan en prioridad, gana el más corto.

## Requisitos

- Python 3.10 o superior (probado con Python 3.14)
- Biblioteca estándar para todo el análisis
- `matplotlib` solo para los gráficos: `pip install -r requirements.txt`

## Estructura

```
datos/
  original/      dataset entregado por el curso (sin cambios)
  adaptado/      dataset ampliado: 36 nodos, 20 pedidos (ver CAMBIOS.md)
  caso_chico/    caso de 5 nodos y 3 pedidos, comprobable a mano
src/
  datos.py             carga y validación de los CSV
  grafo.py             Dijkstra y armado del recorrido completo
  verificador.py       control independiente de cada plan
  exacto.py            solución de referencia: Held-Karp con poda
  genetico.py          solución propuesta: algoritmo genético + 2-opt
  experimentos.py      corre los dos métodos y guarda las tablas
  graficos.py          genera los gráficos a partir de las tablas
  generar_adaptado.py  genera datos/adaptado (semilla 2026)
tests/
  test_caso_chico.py   compara el código con el caso chico
resultados/
  comparacion.csv      una fila por ejecución (con el recorrido completo)
  resumen.csv          una fila por escenario
  entorno.txt          Python y computadora usada
  *.png                gráficos del informe
```

## Cómo ejecutar

Desde la carpeta del proyecto:

```
python3 src/datos.py datos/original      # valida el dataset original
python3 src/datos.py datos/adaptado      # valida el dataset adaptado
python3 src/generar_adaptado.py          # regenera el dataset adaptado
python3 tests/test_caso_chico.py         # prueba con el caso chico
python3 src/exacto.py                    # resuelve todos los escenarios con el exacto
python3 src/genetico.py                  # resuelve todos los escenarios con el genético
python3 src/experimentos.py              # comparación completa -> resultados/ (~20 s)
python3 src/graficos.py                  # gráficos -> resultados/
```

## Notas

- `src/exacto.py` tarda unos 15 s y usa ~1,2 GB de memoria en el escenario A_AMPLIO.
- Tiempo de cálculo: medido con `time.perf_counter()` (reloj de pared, segundos),
  una ejecución por método, escenario y semilla. Incluye el cálculo de Dijkstra.

## Semillas

- Dataset adaptado: semilla 2026 (`src/generar_adaptado.py`)
- Algoritmo genético: semillas 11, 22, 33, 44 y 55 (`src/genetico.py`)

## Uso de IA

Se usó Claude (Anthropic) como apoyo. El detalle de cada uso está en el informe
y las evidencias en la carpeta `evidencias_IA/`.
