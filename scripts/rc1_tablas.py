#!/usr/bin/env python3
"""rc1_tablas — tablas en Markdown de los Experimentos 1 y 2 a partir de la hoja y de los CSV (solo lectura).

Los números salen de `hoja_resultados.csv` (columna `notas`) y, donde conviene, se recalculan de `csv/*.csv`
(cruces de la línea, e mín/máx, yaw máximo). No inventa nada: lo que falta aparece como «—».

Uso:   python3 scripts/rc1_tablas.py            # imprime las tablas
       python3 scripts/rc1_tablas.py > tablas.md
Solo biblioteca estándar.
"""
import csv
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def hoja():
    with open(os.path.join(RAIZ, "hoja_resultados.csv"), newline="", encoding="utf-8") as f:
        return {r["prueba"]: r for r in csv.DictReader(f) if r["planta"] == "sim"}


def clave(notas, k):
    """Valor de `k=...` en las notas (hasta el siguiente ';'), recortado antes de un paréntesis."""
    m = re.search(rf"(?:^|[;\s]){re.escape(k)}\s*=\s*([^;]+)", notas or "")
    if not m:
        return "—"
    v = m.group(1).split("(")[0].strip()
    n = re.match(r"[-+]?\d+(?:\.\d+)?", v)
    return n.group(0) if n else v


def filas_csv(nombre, estado):
    ruta = os.path.join(RAIZ, "csv", f"{nombre}.csv")
    if not os.path.isfile(ruta):
        return []
    with open(ruta, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r["estado"] == estado]


def recta(nombre):
    e = [float(r["e_line"]) * 100 for r in filas_csv(nombre, "AVANZA")]
    if not e:
        return "—", "—", "—"
    cruces = sum(1 for a, b in zip(e, e[1:]) if a * b < 0)
    return str(cruces), f"{min(e):.2f}", f"{max(e):.2f}"


def giro(nombre):
    import math
    f = filas_csv(nombre, "GIRA")
    if not f:
        return "—", "—"
    y0 = float(f[0]["yaw"])
    yaw = [math.degrees(float(r["yaw"]) - y0) for r in f]
    w = max(abs(float(r["w"])) for r in f)
    cruces = sum(1 for a, b in zip(yaw, yaw[1:]) if (a - 90) * (b - 90) < 0)
    return str(cruces), f"{w:.2f}"


def main():
    h = hoja()
    out = []
    out.append("### Experimento 1 — corregir una línea (recta de 2 m, `noise:=low`)\n")
    out.append("| Prueba | Control | Kp / Ki / Kd | \\|e\\| medio (cm) | \\|e\\| máx (cm) | e mín (cm) | Cruces de la línea | Asentamiento ±2 cm | Error final (cm) |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    ctrl = {"1A": "bang-bang", "1B": "solo P", "1C": "P + D", "1D": "PID"}
    for p in ("1A", "1B", "1C", "1D"):
        if p not in h:
            continue
        r, n = h[p], h[p]["notas"]
        cr, emin, emax = recta(f"exp{p.lower()}_sim")
        gan = "—" if r["kp"] in ("", "-") else f"{r['kp']} / {r['ki']} / {r['kd']}"
        ta = clave(n, "t_as_s")
        ta = "no se asienta" if ta.startswith("no se asienta") else (ta + " s" if ta != "—" else ta)
        out.append(f"| {p} | {ctrl[p]} | {gan} | {clave(n, 'e_medio_cm')} | {emax} | {emin} | {cr} | {ta} | {clave(n, 'e_fin_cm')} |")
    out.append("")
    out.append("Notas: en 1A, 1B y 1C el «asentamiento» y el «error final» que calcula el script dependen del último instante de la corrida "
               "(la curva pasa por la banda de ±2 cm justo al terminar) y no son resultados fiables; solo la 1D se asienta de verdad. "
               "Meta de la rúbrica (E2): error final de la 1D ≤ 2 cm.\n")

    out.append("### Experimento 2 — giro de 90° en sitio (`noise:=low`)\n")
    out.append("| Prueba | kp_yaw | ki_yaw | kd_yaw | Sobreimpulso (%) | Asentamiento ±2° (s) | Error final (°) | Cruces de 90° | \\|ω\\| máx (rad/s) |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for p in ("2a", "2b", "2c", "2p1", "2p2", "2p3", "2p"):
        if p not in h:
            continue
        r, n = h[p], h[p]["notas"]
        cr, w = giro(f"exp{p}_sim")
        etiqueta = {"2p": "**2p (elegida = 2p1)**"}.get(p, p)
        out.append(f"| {etiqueta} | {r['kp_yaw']} | {r['ki_yaw']} | {r['kd_yaw']} | {clave(n, 'sobre_pct')} | {clave(n, 't_as_s')} | {clave(n, 'e_fin_deg')} | {cr} | {w} |")
    out.append("")
    out.append("Meta de la rúbrica (E3): una combinación propia con sobreimpulso ≤ 10 % y asentamiento ≤ 3 s.")
    print("\n".join(out))


if __name__ == "__main__":
    sys.exit(main())
