"""Experimentos: compara el exacto y el genético en todos los escenarios.

- Mismos datos, restricciones y criterio para los dos métodos.
- Cada plan se controla con el verificador independiente.
- Tiempo de cálculo: reloj de pared con time.perf_counter(), en segundos,
  una ejecución por método, escenario y semilla (incluye Dijkstra).

Guarda en resultados/:
  comparacion.csv  una fila por ejecución (con el recorrido completo)
  resumen.csv      una fila por escenario (genético: media, mínimo y máximo)
  entorno.txt      versión de Python y computadora usada
Uso: python3 src/experimentos.py
"""
import csv
import platform
import statistics
import time
from pathlib import Path

from datos import cargar
from exacto import resolver_exacto
from genetico import resolver_genetico, SEMILLAS
from verificador import evaluar

RAIZ = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ / "resultados"


def correr(datos, escenario, solucion, semilla=""):
    """Ejecuta un método, mide el tiempo y verifica el plan."""
    inicio = time.perf_counter()
    if solucion == "exacto":
        plan = resolver_exacto(datos, escenario)
    else:
        plan = resolver_genetico(datos, escenario, semilla)
    segundos = time.perf_counter() - inicio
    r = evaluar(datos, escenario, plan)
    return {"escenario": escenario, "solucion": solucion, "semilla": semilla,
            "factible": r["factible"], "n_pedidos": len(plan["pedidos"]),
            "prioridad": r["prioridad"], "cajas": r["cajas"], "viaje": r["viaje"],
            "servicio": r["servicio"], "total": r["total"],
            "segundos": round(segundos, 4),
            "pedidos": " ".join(plan["pedidos"]),
            "recorrido": " ".join(plan["recorrido"])}


def guardar_csv(ruta, filas):
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def main():
    RESULTADOS.mkdir(exist_ok=True)
    filas, resumen = [], []

    for carpeta in ["original", "adaptado"]:
        datos = cargar(RAIZ / "datos" / carpeta)
        for escenario, esc in datos["escenarios"].items():
            print(f"Resolviendo {escenario}...")
            ex = correr(datos, escenario, "exacto")
            ags = [correr(datos, escenario, "genetico", s) for s in SEMILLAS]
            filas += [ex] + ags

            prios = [a["prioridad"] for a in ags]
            resumen.append({
                "escenario": escenario, "capacidad": esc["capacidad"], "limite": esc["limite"],
                "exacto_prioridad": ex["prioridad"], "exacto_total": ex["total"],
                "exacto_segundos": ex["segundos"],
                "ag_prioridad_media": round(statistics.mean(prios), 1),
                "ag_prioridad_min": min(prios), "ag_prioridad_max": max(prios),
                "ag_total_medio": round(statistics.mean(a["total"] for a in ags), 1),
                "ag_segundos_medio": round(statistics.mean(a["segundos"] for a in ags), 4),
                "ag_semillas_optimas": sum(a["prioridad"] == ex["prioridad"]
                                           and a["total"] == ex["total"] for a in ags),
                "todos_factibles": ex["factible"] and all(a["factible"] for a in ags),
            })

    guardar_csv(RESULTADOS / "comparacion.csv", filas)
    guardar_csv(RESULTADOS / "resumen.csv", resumen)
    with open(RESULTADOS / "entorno.txt", "w", encoding="utf-8") as f:
        f.write(f"Python {platform.python_version()}\n{platform.platform()}\n"
                f"Procesador: {platform.processor() or platform.machine()}\n"
                f"Fecha: {time.strftime('%Y-%m-%d %H:%M')}\n")

    print(f"\n{'Escenario':12} {'Exacto':>14} {'Genético (media / mín-máx)':>30} "
          f"{'s exacto':>9} {'s AG':>7}  óptimas")
    for r in resumen:
        print(f"{r['escenario']:12} {r['exacto_prioridad']:>6} ({r['exacto_total']:>3} min)"
              f" {r['ag_prioridad_media']:>12} / {r['ag_prioridad_min']}-{r['ag_prioridad_max']}"
              f" ({r['ag_total_medio']:>5} min) {r['exacto_segundos']:>9.2f} "
              f"{r['ag_segundos_medio']:>7.2f}  {r['ag_semillas_optimas']}/{len(SEMILLAS)}")
    print(f"\nResultados guardados en {RESULTADOS}")


if __name__ == "__main__":
    main()
