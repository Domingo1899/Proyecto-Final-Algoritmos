"""Prueba con un caso chico (datos/caso_chico): 5 nodos y 3 pedidos.

Compara lo que calcula el código con los valores esperados del caso.
Uso: python3 tests/test_caso_chico.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ / "src"))

from datos import cargar, validar
from grafo import calcular_distancias, tiempo_viaje, recorrido_completo
from verificador import evaluar

datos = cargar(RAIZ / "datos" / "caso_chico")

# 1. Los datos pasan la validación
assert all(ok for _, ok in validar(datos))

# 2. Dijkstra da las distancias calculadas a mano
dist, padres = calcular_distancias(datos["grafo"], ["D", "A", "B", "C"])
assert dist["D"]["B"] == 5
assert dist["D"]["C"] == 8
assert dist["A"]["C"] == 8
assert dist["C"]["D"] == 8          # la red es no dirigida: ida = vuelta

# 3. La gira {B,C} cuesta 16 y pasa por todos los nodos intermedios
assert tiempo_viaje(dist, "D", ["B", "C"]) == 16
recorrido_bc = recorrido_completo(padres, "D", ["B", "C"])
assert recorrido_bc == ["D", "X", "B", "C", "B", "X", "D"]

# 4. El verificador da los valores calculados a mano
r = evaluar(datos, "S1", {"pedidos": ["PB", "PC"], "recorrido": recorrido_bc})
assert r["factible"] and r["prioridad"] == 17 and r["total"] == 21

# 5. El verificador rechaza planes inválidos
recorrido_abc = recorrido_completo(padres, "D", ["A", "B", "C"])
todos = {"pedidos": ["PA", "PB", "PC"], "recorrido": recorrido_abc}
assert not evaluar(datos, "S1", todos)["factible"]      # 9 cajas > 7
assert not evaluar(datos, "S2", todos)["factible"]      # 27 min > 25
assert evaluar(datos, "S3", todos)["factible"]          # 27 min = 27 (vale)
assert not evaluar(datos, "S1", {"pedidos": ["PB"], "recorrido": ["D", "B", "D"]})["factible"]   # D-B no existe
assert not evaluar(datos, "S1", {"pedidos": ["PA"], "recorrido": ["D", "X", "D"]})["factible"]   # no pasa por A

# 6. Pasar por B sin atender PB no suma su prioridad
r = evaluar(datos, "S1", {"pedidos": ["PC"], "recorrido": recorrido_bc})
assert r["prioridad"] == 9

print("Caso chico: todos los controles OK.")
