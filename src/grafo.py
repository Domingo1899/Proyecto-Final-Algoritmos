"""Caminos más cortos con Dijkstra (igual al código de clase de heaps).

Idea: las soluciones solo deciden el ORDEN de los centros a visitar.
Entre dos centros seguidos siempre conviene ir por el camino más corto,
así que se calcula una vez con Dijkstra y después se reutiliza.
"""
import heapq


def dijkstra(grafo, origen):
    """Devuelve dist (minutos desde origen) y padre (para armar el camino)."""
    dist = {u: float("inf") for u in grafo}
    padre = {u: None for u in grafo}
    dist[origen] = 0
    heap = [(0, origen)]
    while heap:
        d, u = heapq.heappop(heap)
        if d != dist[u]:                 # entrada vieja del heap
            continue
        for v, w in grafo[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                padre[v] = u
                heapq.heappush(heap, (d + w, v))
    return dist, padre


def armar_camino(padre, destino):
    """Sigue los padres hacia atrás desde destino hasta el origen."""
    camino = []
    while destino is not None:
        camino.append(destino)
        destino = padre[destino]
    return camino[::-1]


def calcular_distancias(grafo, nodos):
    """Corre Dijkstra desde cada nodo de la lista.
    dist[a][b] = minutos de a a b; padres[a] sirve para armar caminos."""
    dist, padres = {}, {}
    for a in nodos:
        dist[a], padres[a] = dijkstra(grafo, a)
    return dist, padres


def tiempo_viaje(dist, deposito, orden):
    """Minutos de ir depósito -> orden[0] -> ... -> orden[-1] -> depósito."""
    paradas = [deposito] + list(orden) + [deposito]
    return sum(dist[a][b] for a, b in zip(paradas, paradas[1:]))


def recorrido_completo(padres, deposito, orden):
    """Pasa de la lista de paradas a la lista de TODOS los nodos recorridos."""
    paradas = [deposito] + list(orden) + [deposito]
    recorrido = [deposito]
    for a, b in zip(paradas, paradas[1:]):
        recorrido += armar_camino(padres[a], b)[1:]   # [1:] para no repetir a
    return recorrido
