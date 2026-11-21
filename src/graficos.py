"""Gráficos para el informe, a partir de resultados/*.csv.

Necesita matplotlib (es lo único que no es de la biblioteca estándar).
Correr antes: python3 src/experimentos.py
Uso: python3 src/graficos.py
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt

from datos import leer_csv

RAIZ = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ / "resultados"
AZUL, NARANJA, GRIS = "#2a78d6", "#eb6834", "#52514e"   # exacto, genético, texto

plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#bbbbbb"})

resumen = leer_csv(RESULTADOS / "resumen.csv")
comparacion = leer_csv(RESULTADOS / "comparacion.csv")
escenarios = [r["escenario"] for r in resumen]


# 1. Tiempo de cálculo (escala logarítmica: los valores van de ms a segundos)
fig, ax = plt.subplots(figsize=(7, 3.8))
y = range(len(escenarios))
exacto = [max(float(r["exacto_segundos"]), 0.001) for r in resumen]
genetico = [float(r["ag_segundos_medio"]) for r in resumen]
ax.barh([i - 0.2 for i in y], exacto, height=0.38, color=AZUL, label="Exacto")
ax.barh([i + 0.2 for i in y], genetico, height=0.38, color=NARANJA, label="Genético (media de 5 semillas)")
ax.set_xscale("log")
ax.set_yticks(list(y), escenarios)
ax.invert_yaxis()
ax.set_xlabel("Tiempo de cálculo (segundos, escala logarítmica)")
ax.set_title("El exacto crece muy rápido; el genético queda por debajo de 1 s", loc="left", pad=28)
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1), ncol=2, borderaxespad=0.2)
for i, (e, g) in enumerate(zip(exacto, genetico)):
    for valor, desplazamiento in [(e, -0.2), (g, 0.2)]:
        texto = "<0.01 s" if valor < 0.01 else f"{valor:.2f} s"
        ax.text(valor * 1.15, i + desplazamiento, texto, va="center", fontsize=8, color=GRIS)
ax.set_xlim(right=60)
fig.tight_layout()
fig.savefig(RESULTADOS / "tiempo_calculo.png", dpi=200)


# 2. Calidad: prioridad del genético como % del óptimo, una marca por semilla
fig, ax = plt.subplots(figsize=(7, 3.8))
optimo = {r["escenario"]: int(r["exacto_prioridad"]) for r in resumen}
ax.axvline(100, color=AZUL, linewidth=2, label="Óptimo (exacto)")
for i, esc in enumerate(escenarios):
    valores = [100 * int(f["prioridad"]) / optimo[esc] for f in comparacion
               if f["escenario"] == esc and f["solucion"] == "genetico"]
    ax.scatter(valores, [i] * len(valores), s=60, color=NARANJA, alpha=0.6,
               edgecolors="white", linewidths=2, label="Genético (cada semilla)" if i == 0 else None)
ax.set_yticks(range(len(escenarios)), escenarios)
ax.invert_yaxis()
ax.set_xlim(90, 101)
ax.set_xlabel("Prioridad obtenida (% del óptimo)")
ax.set_title("El genético llega al óptimo salvo en A_TIEMPO y A_BASE", loc="left")
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig(RESULTADOS / "calidad_genetico.png", dpi=200)


# 3. Recorridos en A_AMPLIO: exacto vs genético (semilla 11) sobre la red
datos_dir = RAIZ / "datos" / "adaptado"
pos = {n["nodo_id"]: (float(n["x"]), float(n["y"])) for n in leer_csv(datos_dir / "nodos.csv")}
tipo = {n["nodo_id"]: n["tipo"] for n in leer_csv(datos_dir / "nodos.csv")}
conexiones = leer_csv(datos_dir / "conexiones.csv")
nodo_pedido = {p["pedido_id"]: p["nodo_id"] for p in leer_csv(datos_dir / "pedidos.csv")}

fig, ejes = plt.subplots(1, 2, figsize=(10, 5))
for ax, solucion, semilla, color in [(ejes[0], "exacto", "", AZUL), (ejes[1], "genetico", "11", NARANJA)]:
    fila = next(f for f in comparacion if f["escenario"] == "A_AMPLIO"
                and f["solucion"] == solucion and f["semilla"] == semilla)
    for c in conexiones:                                    # red de fondo
        (x1, y1), (x2, y2) = pos[c["origen"]], pos[c["destino"]]
        ax.plot([x1, x2], [y1, y2], color="#dddddd", linewidth=1, zorder=1)
    recorrido = fila["recorrido"].split()                   # recorrido del plan
    ax.plot([pos[n][0] for n in recorrido], [pos[n][1] for n in recorrido],
            color=color, linewidth=2.5, zorder=2)
    atendidos = {nodo_pedido[p] for p in fila["pedidos"].split()}
    for n, (x, y) in pos.items():
        if tipo[n] == "deposito":
            ax.scatter(x, y, s=160, marker="s", color="black", zorder=3)
        elif n in atendidos:
            ax.scatter(x, y, s=80, color=color, edgecolors="white", linewidths=2, zorder=3)
        elif tipo[n] == "centro":
            ax.scatter(x, y, s=60, facecolors="white", edgecolors=GRIS, zorder=3)
    nombre = "Exacto" if solucion == "exacto" else "Genético (semilla 11)"
    ax.set_title(f"{nombre}: prioridad {fila['prioridad']}, {fila['total']} min", loc="left")
    ax.set_aspect("equal")
    ax.axis("off")
fig.text(0.01, 0.02, "■ depósito   ● centro atendido   ○ centro no atendido   "
         "Misma prioridad; el genético recorre 13 min más.", fontsize=9, color=GRIS)
fig.tight_layout(rect=(0, 0.05, 1, 0.95))
fig.savefig(RESULTADOS / "recorridos_A_AMPLIO.png", dpi=200)

print("Gráficos guardados en", RESULTADOS)
