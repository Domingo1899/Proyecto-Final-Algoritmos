"""Carga y validación de los datos.

Lee los cuatro CSV y revisa que no tengan errores antes de resolver.
Uso: python3 src/datos.py datos/original
"""
import csv
import sys
from pathlib import Path


def leer_csv(ruta):
    """Devuelve una lista de filas; cada fila es un diccionario."""
    with open(ruta, encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def cargar(carpeta):
    """Lee los CSV de una carpeta y devuelve un diccionario con los datos."""
    carpeta = Path(carpeta)
    nodos = {f["nodo_id"]: f["tipo"] for f in leer_csv(carpeta / "nodos.csv")}

    conexiones = []
    grafo = {n: [] for n in nodos}           # grafo[a] = [(b, minutos), ...]
    for f in leer_csv(carpeta / "conexiones.csv"):
        a, b, t = f["origen"], f["destino"], int(f["tiempo_min"])
        conexiones.append((a, b, t))
        grafo[a].append((b, t))              # la red es no dirigida:
        grafo[b].append((a, t))              # se agrega en los dos sentidos

    pedidos = {}
    for f in leer_csv(carpeta / "pedidos.csv"):
        pedidos[f["pedido_id"]] = {"nodo": f["nodo_id"], "cajas": int(f["cajas"]),
                                   "prioridad": int(f["prioridad"]),
                                   "servicio": int(f["servicio_min"])}

    escenarios = {}
    for f in leer_csv(carpeta / "escenarios.csv"):
        escenarios[f["escenario_id"]] = {"deposito": f["deposito_id"],
                                         "capacidad": int(f["capacidad_cajas"]),
                                         "limite": int(f["limite_tiempo_min"])}

    return {"nodos": nodos, "grafo": grafo, "conexiones": conexiones,
            "pedidos": pedidos, "escenarios": escenarios}


def es_conexo(grafo):
    """BFS desde un nodo: la red es conexa si se llega a todos."""
    inicio = next(iter(grafo))
    visitados = {inicio}
    cola = [inicio]
    while cola:
        u = cola.pop(0)
        for v, _ in grafo[u]:
            if v not in visitados:
                visitados.add(v)
                cola.append(v)
    return len(visitados) == len(grafo)


def validar(datos):
    """Hace los controles y devuelve una lista de (control, ok)."""
    nodos, pedidos = datos["nodos"], datos["pedidos"]
    pares = [frozenset((a, b)) for a, b, _ in datos["conexiones"]]
    nodos_pedidos = [p["nodo"] for p in pedidos.values()]
    return [
        ("Conexiones entre nodos existentes",
         all(a in nodos and b in nodos for a, b, _ in datos["conexiones"])),
        ("Tiempos de viaje positivos", all(t > 0 for _, _, t in datos["conexiones"])),
        ("Sin conexiones repetidas", len(pares) == len(set(pares))),
        ("Red conexa", es_conexo(datos["grafo"])),
        ("Cada pedido está en un centro",
         all(nodos.get(n) == "centro" for n in nodos_pedidos)),
        ("Un solo pedido por centro", len(nodos_pedidos) == len(set(nodos_pedidos))),
        ("Cajas, prioridad y servicio positivos",
         all(min(p["cajas"], p["prioridad"], p["servicio"]) > 0 for p in pedidos.values())),
        ("Depósito válido en cada escenario",
         all(nodos.get(e["deposito"]) == "deposito" for e in datos["escenarios"].values())),
    ]


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "datos/original"
    datos = cargar(carpeta)
    cajas = sum(p["cajas"] for p in datos["pedidos"].values())
    print(f"{len(datos['nodos'])} nodos, {len(datos['conexiones'])} conexiones, "
          f"{len(datos['pedidos'])} pedidos ({cajas} cajas en total)")
    for control, ok in validar(datos):
        print("OK " if ok else "ERROR", control)
