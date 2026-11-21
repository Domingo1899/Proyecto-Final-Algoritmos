"""Solución de REFERENCIA: método exacto (Held-Karp con poda).

Es el Held-Karp de la ADI 1 con dos cambios:
  1. No hay que visitar todos los centros: cada estado (S, j) es un
     subconjunto S de pedidos atendidos que termina en el pedido j.
     Al recorrer todos los estados se prueban todas las combinaciones.
  2. Poda: si un estado ya supera la capacidad o no llega a volver a tiempo,
     se descarta. Agregar más pedidos solo suma cajas y minutos, así que de
     ese estado nunca saldría un plan válido (como en ramificación y poda).

Garantía: encuentra el plan óptimo. Límite: la cantidad de estados crece
de forma exponencial con los pedidos que entran en el vehículo.
Uso: python3 src/exacto.py
"""
import time
from grafo import calcular_distancias, recorrido_completo


def resolver_exacto(datos, escenario):
    esc = datos["escenarios"][escenario]
    deposito, capacidad, limite = esc["deposito"], esc["capacidad"], esc["limite"]
    pedidos = datos["pedidos"]
    ids = list(pedidos)                        # el pedido j es el bit j de S
    centro = [pedidos[p]["nodo"] for p in ids]
    dist, padres = calcular_distancias(datos["grafo"], [deposito] + centro)

    # tabla[(S, j)] = (tiempo, anterior, cajas, prioridad)
    #   tiempo = minutos mínimos (viaje + servicio) para atender S terminando en j
    #   anterior = pedido atendido antes de j (para reconstruir el orden)
    tabla = {}

    # Caso base: ir del depósito a un solo pedido.
    capa = {}
    for j, p in enumerate(ids):
        t = dist[deposito][centro[j]] + pedidos[p]["servicio"]
        if pedidos[p]["cajas"] <= capacidad and t + dist[centro[j]][deposito] <= limite:
            capa[(1 << j, j)] = (t, None, pedidos[p]["cajas"], pedidos[p]["prioridad"])

    mejor = (0, 0, None)                       # (prioridad, total, estado); plan vacío
    while capa:
        tabla.update(capa)
        nueva = {}
        for (S, j), (t, _, cajas, prio) in capa.items():
            # Cerrar acá: volver al depósito. ¿Es el mejor plan hasta ahora?
            total = t + dist[centro[j]][deposito]
            if prio > mejor[0] or (prio == mejor[0] and total < mejor[1]):
                mejor = (prio, total, (S, j))

            # Extender: agregar un pedido k que todavía no está en S.
            for k, p in enumerate(ids):
                if S & (1 << k):
                    continue
                nuevas_cajas = cajas + pedidos[p]["cajas"]
                nuevo_t = t + dist[centro[j]][centro[k]] + pedidos[p]["servicio"]
                if nuevas_cajas > capacidad:                     # poda por capacidad
                    continue
                if nuevo_t + dist[centro[k]][deposito] > limite:  # poda por tiempo
                    continue
                estado = (S | (1 << k), k)
                if estado not in nueva or nuevo_t < nueva[estado][0]:
                    nueva[estado] = (nuevo_t, j, nuevas_cajas, prio + pedidos[p]["prioridad"])
        capa = nueva

    # Reconstruir el orden siguiendo los "anterior" desde el mejor estado.
    orden = []
    estado = mejor[2]
    while estado is not None:
        S, j = estado
        orden.append(j)
        anterior = tabla[estado][1]
        estado = None if anterior is None else (S & ~(1 << j), anterior)
    orden.reverse()

    return {"pedidos": [ids[j] for j in orden],
            "recorrido": recorrido_completo(padres, deposito, [centro[j] for j in orden]),
            "estados": len(tabla)}


if __name__ == "__main__":
    from pathlib import Path
    from datos import cargar
    from verificador import evaluar

    raiz = Path(__file__).resolve().parent.parent
    for carpeta in ["original", "adaptado"]:
        datos = cargar(raiz / "datos" / carpeta)
        for escenario in datos["escenarios"]:
            inicio = time.perf_counter()
            plan = resolver_exacto(datos, escenario)
            segundos = time.perf_counter() - inicio
            r = evaluar(datos, escenario, plan)        # control independiente
            print(f"{escenario:12} factible={r['factible']}  prioridad={r['prioridad']:3}  "
                  f"cajas={r['cajas']:2}  viaje={r['viaje']:3}  servicio={r['servicio']:3}  "
                  f"total={r['total']:3}  estados={plan['estados']:8}  {segundos:.2f} s")
            print(f"{'':12} pedidos: {' '.join(plan['pedidos'])}")
