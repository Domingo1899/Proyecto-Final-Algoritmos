"""Verificador de planes, independiente de las soluciones.

No usa Dijkstra: recalcula todo con las conexiones del CSV.
Así, si una solución tiene un error, el verificador lo detecta.

Un plan es: {"pedidos": ["P01", ...], "recorrido": ["N00", ..., "N00"]}
"""


def evaluar(datos, escenario, plan):
    """Devuelve los totales del plan y la lista de errores (vacía = factible)."""
    esc = datos["escenarios"][escenario]
    pedidos = datos["pedidos"]
    recorrido = plan["recorrido"]
    elegidos = plan["pedidos"]
    tiempo_tramo = {frozenset((a, b)): t for a, b, t in datos["conexiones"]}
    errores = []

    if recorrido[0] != esc["deposito"] or recorrido[-1] != esc["deposito"]:
        errores.append("No sale y vuelve al depósito")

    viaje = 0
    for a, b in zip(recorrido, recorrido[1:]):
        tramo = frozenset((a, b))
        if tramo in tiempo_tramo:
            viaje += tiempo_tramo[tramo]
        else:
            errores.append(f"No existe la conexión {a}-{b}")

    if len(elegidos) != len(set(elegidos)):
        errores.append("Hay pedidos repetidos")
    for p in elegidos:
        if pedidos[p]["nodo"] not in recorrido:
            errores.append(f"El recorrido no pasa por el centro de {p}")

    cajas = sum(pedidos[p]["cajas"] for p in set(elegidos))
    servicio = sum(pedidos[p]["servicio"] for p in set(elegidos))
    prioridad = sum(pedidos[p]["prioridad"] for p in set(elegidos))
    total = viaje + servicio

    if cajas > esc["capacidad"]:
        errores.append(f"Supera la capacidad: {cajas} > {esc['capacidad']}")
    if total > esc["limite"]:
        errores.append(f"Supera el tiempo: {total} > {esc['limite']}")

    return {"factible": len(errores) == 0, "errores": errores,
            "prioridad": prioridad, "cajas": cajas,
            "viaje": viaje, "servicio": servicio, "total": total}


def es_mejor(a, b):
    """True si el plan evaluado a es mejor que b según la consigna:
    primero factible, después más prioridad, después menos tiempo total."""
    return (a["factible"], a["prioridad"], -a["total"]) > \
           (b["factible"], b["prioridad"], -b["total"])
