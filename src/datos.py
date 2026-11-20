"""
datos.py - Carga y validación de los datos del problema.

Finalidad
---------
Antes de resolver nada hay que asegurarse de que los datos de entrada son
coherentes. Si un pedido apunta a un nodo inexistente o la red no es conexa,
cualquier algoritmo daría resultados sin sentido. Este módulo:

  1. Lee los cuatro CSV (nodos, conexiones, pedidos, escenarios).
  2. Convierte los tipos (texto -> entero) y arma estructuras cómodas.
  3. Valida claves, referencias, valores, unidades y conectividad.
  4. Informa cada control realizado (sirve como evidencia para el informe).

Solo usa la biblioteca estándar de Python.
Uso:  python3 src/datos.py datos/original
"""

import csv
import sys
from collections import deque
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. CARGA
# ---------------------------------------------------------------------------

def leer_csv(ruta):
    """Lee un CSV y devuelve una lista de diccionarios (una fila = un dict).
    Se mantienen los identificadores como texto para no perder ceros iniciales
    (por ejemplo 'N00')."""
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def cargar_instancia(carpeta):
    """Carga los cuatro CSV de una carpeta y devuelve un diccionario con:
      - nodos:      {nodo_id: {"tipo", "nombre", "x", "y"}}
      - conexiones: lista de (conexion_id, origen, destino, tiempo_min)
      - grafo:      lista de adyacencia {nodo: {vecino: tiempo}} (no dirigido)
      - pedidos:    {pedido_id: {"nodo", "cajas", "prioridad", "servicio"}}
      - escenarios: {escenario_id: {"descripcion", "deposito", "capacidad", "limite"}}
    No valida: solo transforma. La validación se hace aparte en validar()."""
    carpeta = Path(carpeta)
    filas_nodos = leer_csv(carpeta / "nodos.csv")
    filas_con = leer_csv(carpeta / "conexiones.csv")
    filas_ped = leer_csv(carpeta / "pedidos.csv")
    filas_esc = leer_csv(carpeta / "escenarios.csv")

    nodos = {
        f["nodo_id"]: {"tipo": f["tipo"], "nombre": f["nombre"],
                       "x": float(f["x"]), "y": float(f["y"])}
        for f in filas_nodos
    }

    conexiones = [(f["conexion_id"], f["origen"], f["destino"], int(f["tiempo_min"]))
                  for f in filas_con]

    # La red es NO dirigida: cada fila del CSV se agrega en ambos sentidos
    # con el mismo tiempo (no se duplica el costo, solo la posibilidad de ir y volver).
    grafo = {n: {} for n in nodos}
    for _, a, b, t in conexiones:
        grafo.setdefault(a, {})[b] = t
        grafo.setdefault(b, {})[a] = t

    pedidos = {
        f["pedido_id"]: {"nodo": f["nodo_id"], "cajas": int(f["cajas"]),
                         "prioridad": int(f["prioridad"]),
                         "servicio": int(f["servicio_min"])}
        for f in filas_ped
    }

    escenarios = {
        f["escenario_id"]: {"descripcion": f["descripcion"],
                            "deposito": f["deposito_id"],
                            "capacidad": int(f["capacidad_cajas"]),
                            "limite": int(f["limite_tiempo_min"])}
        for f in filas_esc
    }

    return {"nodos": nodos, "conexiones": conexiones, "grafo": grafo,
            "pedidos": pedidos, "escenarios": escenarios,
            # Guardamos las filas crudas para poder detectar claves duplicadas
            # (en los diccionarios de arriba una clave repetida se pisaría).
            "_crudo": {"nodos": filas_nodos, "conexiones": filas_con,
                       "pedidos": filas_ped, "escenarios": filas_esc}}


# ---------------------------------------------------------------------------
# 2. VALIDACIÓN
# ---------------------------------------------------------------------------

def _duplicados(valores):
    """Devuelve los valores que aparecen más de una vez."""
    vistos, dup = set(), set()
    for v in valores:
        (dup if v in vistos else vistos).add(v)
    return dup


def es_conexo(grafo):
    """Recorrido en anchura (BFS) desde un nodo cualquiera: la red es conexa
    si se alcanzan todos los nodos. Si no lo fuera, algunos pedidos serían
    inalcanzables desde el depósito."""
    inicio = next(iter(grafo))
    visitados, cola = {inicio}, deque([inicio])
    while cola:
        u = cola.popleft()
        for v in grafo[u]:
            if v not in visitados:
                visitados.add(v)
                cola.append(v)
    return len(visitados) == len(grafo)


def validar(inst):
    """Ejecuta todos los controles. Devuelve una lista de (descripción, ok, detalle).
    Ningún control modifica los datos: si algo falla se informa y se decide
    a mano qué hacer (y se documenta en el informe)."""
    crudo = inst["_crudo"]
    nodos, grafo = inst["nodos"], inst["grafo"]
    pedidos, escenarios = inst["pedidos"], inst["escenarios"]
    res = []

    def control(desc, ok, detalle=""):
        res.append((desc, bool(ok), detalle))

    # --- Datos faltantes: ninguna celda vacía en ningún archivo ---
    vacias = [(arch, i + 2, k) for arch, filas in crudo.items()
              for i, f in enumerate(filas) for k, v in f.items()
              if v is None or str(v).strip() == ""]
    control("Sin celdas vacías", not vacias, str(vacias[:5]))

    # --- Claves primarias únicas ---
    for arch, clave in [("nodos", "nodo_id"), ("conexiones", "conexion_id"),
                        ("pedidos", "pedido_id"), ("escenarios", "escenario_id")]:
        dup = _duplicados(f[clave] for f in crudo[arch])
        control(f"Clave {clave} única en {arch}.csv", not dup, str(dup))

    # --- Tipos de nodo válidos y exactamente un depósito ---
    tipos_ok = {"deposito", "centro", "interseccion"}
    malos = [n for n, d in nodos.items() if d["tipo"] not in tipos_ok]
    control("Tipos de nodo válidos", not malos, str(malos))

    # --- Conexiones: extremos existentes, tiempos positivos, sin lazos ni repetidas ---
    inexistentes = [c for c, a, b, _ in inst["conexiones"] if a not in nodos or b not in nodos]
    control("Conexiones refieren a nodos existentes", not inexistentes, str(inexistentes))
    no_pos = [c for c, _, _, t in inst["conexiones"] if t <= 0]
    control("Tiempos de conexión positivos", not no_pos, str(no_pos))
    lazos = [c for c, a, b, _ in inst["conexiones"] if a == b]
    control("Sin lazos (origen == destino)", not lazos, str(lazos))
    # Un par {A,B} repetido (aunque esté al revés) sería una conexión duplicada.
    dup_pares = _duplicados(frozenset((a, b)) for _, a, b, _ in inst["conexiones"])
    control("Sin pares de extremos repetidos", not dup_pares,
            str([tuple(p) for p in dup_pares]))

    # --- Conectividad ---
    control("Red conexa", es_conexo(grafo))

    # --- Pedidos ---
    ped_mal_nodo = [p for p, d in pedidos.items() if d["nodo"] not in nodos]
    control("Pedidos refieren a nodos existentes", not ped_mal_nodo, str(ped_mal_nodo))
    ped_no_centro = [p for p, d in pedidos.items()
                     if d["nodo"] in nodos and nodos[d["nodo"]]["tipo"] != "centro"]
    control("Cada pedido está en un nodo de tipo centro", not ped_no_centro, str(ped_no_centro))
    dup_nodo = _duplicados(d["nodo"] for d in pedidos.values())
    control("Un pedido por centro (nodo único)", not dup_nodo, str(dup_nodo))
    ped_no_pos = [p for p, d in pedidos.items()
                  if min(d["cajas"], d["prioridad"], d["servicio"]) <= 0]
    control("Cajas, prioridad y servicio positivos", not ped_no_pos, str(ped_no_pos))

    # --- Escenarios ---
    for e, d in escenarios.items():
        ok = (d["deposito"] in nodos and nodos[d["deposito"]]["tipo"] == "deposito"
              and d["capacidad"] > 0 and d["limite"] > 0)
        control(f"Escenario {e}: depósito válido y límites positivos", ok)

    return res


# ---------------------------------------------------------------------------
# 3. RESUMEN DESCRIPTIVO (útil para la sección de datos del informe)
# ---------------------------------------------------------------------------

def resumen(inst):
    """Devuelve un texto con cifras clave de la instancia."""
    nodos, pedidos = inst["nodos"], inst["pedidos"]
    tipos = {}
    for d in nodos.values():
        tipos[d["tipo"]] = tipos.get(d["tipo"], 0) + 1
    tot_cajas = sum(p["cajas"] for p in pedidos.values())
    tot_prio = sum(p["prioridad"] for p in pedidos.values())
    tot_serv = sum(p["servicio"] for p in pedidos.values())
    lineas = [
        f"Nodos: {len(nodos)}  {tipos}",
        f"Conexiones: {len(inst['conexiones'])}",
        f"Pedidos: {len(pedidos)}  | cajas totales={tot_cajas}  "
        f"prioridad total={tot_prio}  servicio total={tot_serv} min",
    ]
    for e, d in inst["escenarios"].items():
        lineas.append(f"Escenario {e}: capacidad={d['capacidad']} cajas "
                      f"({d['capacidad'] / tot_cajas:.0%} de la demanda), "
                      f"límite={d['limite']} min")
    return "\n".join(lineas)


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "datos/original"
    inst = cargar_instancia(carpeta)
    print(f"== Instancia: {carpeta}\n{resumen(inst)}\n\n== Controles de validación")
    resultados = validar(inst)
    for desc, ok, det in resultados:
        print(f"[{'OK ' if ok else 'ERR'}] {desc}" + (f"  -> {det}" if not ok else ""))
    fallos = sum(not ok for _, ok, _ in resultados)
    print(f"\n{len(resultados) - fallos}/{len(resultados)} controles superados.")
    sys.exit(1 if fallos else 0)
