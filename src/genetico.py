"""Solución PROPUESTA: algoritmo genético (basado en AG_Mochila.py de clase).

Individuo: una lista de bits, uno por pedido (1 = lo atiendo, 0 = no).
Es la misma idea que la mochila, pero además hay que decidir el ORDEN:
  - el orden se arma con "vecino más cercano" y se mejora con 2-opt
    (búsqueda local: invertir un tramo del orden si acorta el viaje);
  - si el plan no entra en el vehículo o no llega a tiempo, se REPARA
    sacando pedidos (como reparar() en la mochila).

Garantía: siempre devuelve un plan factible, pero NO garantiza el óptimo.
Usa azar, así que se corre con varias semillas.
Uso: python3 src/genetico.py
"""
import random
import time
from grafo import calcular_distancias, tiempo_viaje, recorrido_completo

POBLACION = 40
GENERACIONES = 60
PROB_CRUCE = 0.8
SEMILLAS = [11, 22, 33, 44, 55]


def preparar(datos, escenario):
    """Junta en un diccionario lo que se usa en todo el algoritmo."""
    esc = datos["escenarios"][escenario]
    pedidos = datos["pedidos"]
    ids = list(pedidos)
    centro = [pedidos[p]["nodo"] for p in ids]
    dist, padres = calcular_distancias(datos["grafo"], [esc["deposito"]] + centro)
    return {"ids": ids, "centro": centro, "dist": dist, "padres": padres,
            "deposito": esc["deposito"], "capacidad": esc["capacidad"],
            "limite": esc["limite"], "cajas": [pedidos[p]["cajas"] for p in ids],
            "prioridad": [pedidos[p]["prioridad"] for p in ids],
            "servicio": [pedidos[p]["servicio"] for p in ids]}


def viaje(prob, orden):
    """Minutos de viaje de la gira que atiende los pedidos en ese orden."""
    return tiempo_viaje(prob["dist"], prob["deposito"], [prob["centro"][j] for j in orden])


def armar_orden(prob, elegidos):
    """Vecino más cercano: desde donde estoy, voy al pedido más cercano.
    Después 2-opt: pruebo invertir cada tramo y me quedo si acorta."""
    orden, actual, pendientes = [], prob["deposito"], list(elegidos)
    while pendientes:
        j = min(pendientes, key=lambda k: prob["dist"][actual][prob["centro"][k]])
        orden.append(j)
        pendientes.remove(j)
        actual = prob["centro"][j]

    mejoro = True
    while mejoro:
        mejoro = False
        for a in range(len(orden) - 1):
            for b in range(a + 1, len(orden)):
                nuevo = orden[:a] + orden[a:b + 1][::-1] + orden[b + 1:]
                if viaje(prob, nuevo) < viaje(prob, orden):
                    orden, mejoro = nuevo, True
    return orden


def tiempo_total(prob, orden):
    return viaje(prob, orden) + sum(prob["servicio"][j] for j in orden)


def reparar(prob, individuo):
    """Saca pedidos hasta que el plan sea factible.
    Si sobran cajas: saca el de menor prioridad por caja (como la mochila).
    Si sobra tiempo: saca el de menor prioridad por minuto que se ahorra."""
    elegidos = [j for j, bit in enumerate(individuo) if bit]
    orden = armar_orden(prob, elegidos)
    while True:
        if sum(prob["cajas"][j] for j in elegidos) > prob["capacidad"]:
            quitar = min(elegidos, key=lambda j: prob["prioridad"][j] / prob["cajas"][j])
        elif tiempo_total(prob, orden) > prob["limite"]:
            def prioridad_por_minuto(j):
                sin_j = [k for k in orden if k != j]
                ahorro = tiempo_total(prob, orden) - tiempo_total(prob, sin_j)
                return prob["prioridad"][j] / max(ahorro, 1)
            quitar = min(elegidos, key=prioridad_por_minuto)
        else:
            break
        elegidos.remove(quitar)
        orden = armar_orden(prob, elegidos)
    reparado = [1 if j in elegidos else 0 for j in range(len(individuo))]
    return reparado, orden


def puntuar(prob, orden):
    """Nota para comparar: primero prioridad, después menos tiempo."""
    return (sum(prob["prioridad"][j] for j in orden), -tiempo_total(prob, orden))


def elegir_por_torneo(poblacion, notas, azar):
    a, b = azar.sample(range(len(poblacion)), 2)
    return poblacion[a][:] if notas[a] > notas[b] else poblacion[b][:]


def cruzar(a, b, azar):
    if azar.random() >= PROB_CRUCE:
        return a[:], b[:]
    corte = azar.randrange(1, len(a))
    return a[:corte] + b[corte:], b[:corte] + a[corte:]


def mutar(individuo, azar):
    prob_mutacion = 1 / len(individuo)          # en promedio cambia un bit
    return [1 - bit if azar.random() < prob_mutacion else bit for bit in individuo]


def resolver_genetico(datos, escenario, semilla):
    prob = preparar(datos, escenario)
    azar = random.Random(semilla)
    n = len(prob["ids"])
    guardados = {}                              # para no evaluar dos veces lo mismo

    def evaluar_individuo(individuo):
        clave = tuple(individuo)
        if clave not in guardados:
            reparado, orden = reparar(prob, individuo)
            guardados[clave] = (reparado, orden, puntuar(prob, orden))
        return guardados[clave]

    poblacion, notas, ordenes = [], [], []
    for _ in range(POBLACION):
        reparado, orden, nota = evaluar_individuo([azar.randrange(2) for _ in range(n)])
        poblacion.append(reparado)
        notas.append(nota)
        ordenes.append(orden)

    for _ in range(GENERACIONES):
        elite = max(range(POBLACION), key=lambda i: notas[i])   # el mejor pasa directo
        nueva, nuevas_notas, nuevos_ordenes = [poblacion[elite]], [notas[elite]], [ordenes[elite]]
        while len(nueva) < POBLACION:
            padre = elegir_por_torneo(poblacion, notas, azar)
            madre = elegir_por_torneo(poblacion, notas, azar)
            for hijo in cruzar(padre, madre, azar):
                reparado, orden, nota = evaluar_individuo(mutar(hijo, azar))
                nueva.append(reparado)
                nuevas_notas.append(nota)
                nuevos_ordenes.append(orden)
        poblacion = nueva[:POBLACION]
        notas = nuevas_notas[:POBLACION]
        ordenes = nuevos_ordenes[:POBLACION]

    mejor = max(range(POBLACION), key=lambda i: notas[i])
    orden = ordenes[mejor]
    return {"pedidos": [prob["ids"][j] for j in orden],
            "recorrido": recorrido_completo(prob["padres"], prob["deposito"],
                                            [prob["centro"][j] for j in orden]),
            "evaluaciones": len(guardados)}


if __name__ == "__main__":
    from pathlib import Path
    from datos import cargar
    from verificador import evaluar

    raiz = Path(__file__).resolve().parent.parent
    for carpeta in ["original", "adaptado"]:
        datos = cargar(raiz / "datos" / carpeta)
        for escenario in datos["escenarios"]:
            for semilla in SEMILLAS:
                inicio = time.perf_counter()
                plan = resolver_genetico(datos, escenario, semilla)
                segundos = time.perf_counter() - inicio
                r = evaluar(datos, escenario, plan)    # control independiente
                print(f"{escenario:12} semilla={semilla}  factible={r['factible']}  "
                      f"prioridad={r['prioridad']:3}  total={r['total']:3}  {segundos:.2f} s")
