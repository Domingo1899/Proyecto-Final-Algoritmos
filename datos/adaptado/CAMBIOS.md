# Dataset adaptado: registro de cambios

Datos **sintéticos**, generados con `src/generar_adaptado.py` (semilla 2026).
No representan bibliotecas, calles ni mediciones reales.

## Pregunta que permite estudiar

¿Qué pasa cuando crece el problema? ¿Hasta dónde el método exacto sigue
siendo rápido y cuánto se aleja la heurística del óptimo?

Con el dataset original (10 pedidos) el método exacto resuelve todo en
milisegundos, así que no se puede ver la diferencia entre los dos métodos.

## Qué se cambió respecto del original

| | Original | Adaptado |
|---|---|---|
| Red | grilla 4x4, 16 nodos, 29 conexiones | grilla 6x6, 36 nodos, 65 conexiones |
| Pedidos | 10 (41 cajas) | 20 (100 cajas) |
| Tiempos de tramo | 5 a 10 min | 5 a 10 min (diagonales 9 a 12) |

Se mantienen las mismas reglas y proporciones: un pedido por centro,
prioridad de unas 3 a 4 veces las cajas, servicio = cajas + 2 a 4 minutos.

## Escenarios

| Escenario | Capacidad | Límite | Qué busca mostrar |
|---|---:|---:|---|
| A_BASE | 30 | 200 | Referencia en la red ampliada |
| A_CAPACIDAD | 18 | 200 | Limita la capacidad |
| A_TIEMPO | 30 | 130 | Limita el tiempo (algunos pedidos lejanos no se pueden atender) |
| A_AMPLIO | 50 | 320 | Muchas combinaciones posibles: costo de cálculo del método exacto |
