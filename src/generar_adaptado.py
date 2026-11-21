"""Genera el dataset adaptado: la misma idea del original, pero más grande.

Red en grilla de 6x6 (36 nodos) con 20 pedidos. Usa una semilla fija,
así siempre se generan exactamente los mismos datos.
Uso: python3 src/generar_adaptado.py
"""
import csv
import random
from pathlib import Path

SEMILLA = 2026
LADO = 6              # grilla de LADO x LADO nodos
N_PEDIDOS = 20
CARPETA = Path(__file__).resolve().parent.parent / "datos" / "adaptado"

azar = random.Random(SEMILLA)


def nombre(fila, col):
    """Número de nodo a partir de su posición: (0,0)->N00, (1,2)->N08."""
    return f"N{fila * LADO + col:02d}"


# Nodos: el N00 es el depósito; 20 nodos al azar son centros; el resto, cruces.
todos = [nombre(f, c) for f in range(LADO) for c in range(LADO)]
centros = sorted(azar.sample(todos[1:], N_PEDIDOS))
nodos = []
for f in range(LADO):
    for c in range(LADO):
        n = nombre(f, c)
        tipo = "deposito" if n == "N00" else "centro" if n in centros else "interseccion"
        nodos.append([n, tipo, n, c, f])

# Conexiones: cada nodo con su vecino de la derecha y el de abajo (5 a 10 min).
# Además, algunas diagonales al azar (9 a 12 min), como en el dataset original.
conexiones = []
for f in range(LADO):
    for c in range(LADO):
        if c + 1 < LADO:
            conexiones.append([nombre(f, c), nombre(f, c + 1), azar.randint(5, 10)])
        if f + 1 < LADO:
            conexiones.append([nombre(f, c), nombre(f + 1, c), azar.randint(5, 10)])
        if f + 1 < LADO and c + 1 < LADO and azar.random() < 0.25:
            conexiones.append([nombre(f, c), nombre(f + 1, c + 1), azar.randint(9, 12)])

# Pedidos: con proporciones parecidas al original
# (prioridad de unas 3 a 4 veces las cajas; servicio = cajas + 2 a 4 min).
pedidos = []
for i, centro in enumerate(centros, start=1):
    cajas = azar.randint(2, 7)
    pedidos.append([f"P{i:02d}", centro, cajas,
                    cajas * 3 + azar.randint(0, 8), cajas + azar.randint(2, 4)])

escenarios = [
    ["A_BASE", "Red ampliada - condiciones de referencia", "N00", 30, 200],
    ["A_CAPACIDAD", "Red ampliada - menor capacidad", "N00", 18, 200],
    ["A_TIEMPO", "Red ampliada - menor tiempo", "N00", 30, 130],
    ["A_AMPLIO", "Red ampliada - vehiculo grande y jornada larga", "N00", 50, 320],
]


def guardar(archivo, cabecera, filas):
    with open(CARPETA / archivo, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(cabecera)
        escritor.writerows(filas)


CARPETA.mkdir(parents=True, exist_ok=True)
guardar("nodos.csv", ["nodo_id", "tipo", "nombre", "x", "y"], nodos)
guardar("conexiones.csv", ["conexion_id", "origen", "destino", "tiempo_min"],
        [[f"C{i:02d}"] + c for i, c in enumerate(conexiones, start=1)])
guardar("pedidos.csv", ["pedido_id", "nodo_id", "cajas", "prioridad", "servicio_min"], pedidos)
guardar("escenarios.csv", ["escenario_id", "descripcion", "deposito_id",
                           "capacidad_cajas", "limite_tiempo_min"], escenarios)
print(f"Dataset adaptado guardado en {CARPETA}: {len(nodos)} nodos, "
      f"{len(conexiones)} conexiones, {len(pedidos)} pedidos.")
