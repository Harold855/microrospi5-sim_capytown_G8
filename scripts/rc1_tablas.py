#!/usr/bin/env python3
"""rc1_tablas — tablas en Markdown de los Experimentos 1, 2 y 3 a partir de la hoja y de los CSV (solo lectura).

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


def corridas3():
    """Filas del Experimento 3 (sim) de la hoja: {(prueba, corrida): fila}."""
    with open(os.path.join(RAIZ, "hoja_resultados.csv"), newline="", encoding="utf-8") as f:
        return {(r["prueba"], r["notas"].split(";")[0].strip()): r for r in csv.DictReader(f)
                if r["planta"] == "sim" and r["prueba"] in ("3A", "3B", "3C")}


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def pred3(texto):
    m = re.search(r"/odom = ([\d.]+) cm; cierre REAL = ([\d.]+) cm", texto or "")
    return (float(m.group(1)), float(m.group(2))) if m else (None, None)


def exp3():
    h = corridas3()
    nom = {"3A": "3A lazo abierto", "3B": "3B PID sobre /odom", "3C": "3C PID + Ki"}
    orden = ("run1", "run2", "run3", "medium")
    out = ["### Experimento 3 — cuadrado de 2 x 2 m en el simulador\n",
           "Cierre «`/odom`» = lo que cree el robot (y lo que imprime el nodo); cierre «real» = distancia a la marca de inicio según "
           "`/sim/pose` (`cierre_real.py`). `\\|e\\|` medio = error lateral medio en las rectas, calculado de `csv/exp3*_sim_*.csv`.\n",
           "| Prueba | Corrida | Ruido | Cierre `/odom` (cm) | Cierre real (cm) | Yaw real (°) | Yaw `/odom` (°) | \\|e\\| medio rectas (cm) | Tiempo (s) |",
           "|---|---|---|---|---|---|---|---|---|"]
    for p in ("3A", "3B", "3C"):
        for c in orden:
            r = h.get((p, c))
            if not r:
                continue
            n = r["notas"]
            e = [abs(float(x["e_line"])) * 100 for x in filas_csv(f"exp{p.lower()}_sim_{c}", "AVANZA")]
            em = f"{sum(e) / len(e):.2f}" if e else "—"
            tm = re.search(r"([\d.]+) s", n.split("FIN nodo:")[-1]) if "FIN nodo:" in n else None
            out.append(f"| {p} | {c} | {r['noise']} | {r['cierre_odom_cm']} | {r['cierre_real_cm']} | {r['yaw_acum_deg']} | "
                       f"{re.search(r'yaw odom ([\d.]+)', n).group(1) if re.search(r'yaw odom ([\d.]+)', n) else '—'} | {em} | {tm.group(1) if tm else '—'} |")
    out.append("")
    out.append("#### Resumen con `noise:=low` (3 corridas) y la corrida `medium`\n")
    out.append("| Prueba | Real low: corridas (cm) | Real low: media | Real low: mín–máx | `/odom` low: media | Real medium (cm) | Corridas low ≤ 40 cm |")
    out.append("|---|---|---|---|---|---|---|")
    for p in ("3A", "3B", "3C"):
        real = [num(h[(p, c)]["cierre_real_cm"]) for c in orden[:3] if (p, c) in h]
        od = [num(h[(p, c)]["cierre_odom_cm"]) for c in orden[:3] if (p, c) in h]
        med = h.get((p, "medium"), {}).get("cierre_real_cm", "—")
        if None in real or not real:
            continue
        ok = sum(1 for x in real if x <= 40)
        out.append(f"| {nom[p]} | {' / '.join(f'{x:g}' for x in real)} | **{sum(real) / len(real):.1f}** | {min(real):g}–{max(real):g} | "
                   f"{sum(od) / len(od):.1f} | {med} | {ok} de {len(real)} |")
    out.append("")
    out.append("#### Predicción contra medición (cierre `/odom` / cierre real, cm)\n")
    out.append("| Prueba | Corrida | Predijeron | Se midió | Diferencia real |")
    out.append("|---|---|---|---|---|")
    for p in ("3A", "3B", "3C"):
        for c in ("run1", "medium"):
            r = h.get((p, c))
            if not r:
                continue
            po, pr = pred3(r["prediccion"])
            if c == "run1":
                c_txt, rr = "low (las 3 corridas)", [num(h[(p, k)]["cierre_real_cm"]) for k in orden[:3]]
                ro = [num(h[(p, k)]["cierre_odom_cm"]) for k in orden[:3]]
                med = f"{min(ro):g}–{max(ro):g} / {min(rr):g}–{max(rr):g}"
                dif = "; ".join(f"{x - pr:+.1f}" for x in rr)
            else:
                c_txt, med = "medium", f"{r['cierre_odom_cm']} / {r['cierre_real_cm']}"
                dif = f"{num(r['cierre_real_cm']) - pr:+.1f}"
            out.append(f"| {p} | {c_txt} | {po:g} / {pr:g} | {med} | {dif} |")
    out.append("")
    out.append("Meta de la rúbrica (E4): 3B o 3C con cierre real ≤ 40 cm. La redacción no aclara si es cada corrida, la media o al menos una; "
               "pendiente de confirmar con el docente.\n")
    out.append("| Lectura de E4 | 3B | 3C |")
    out.append("|---|---|---|")
    for lectura, f in (("Cada corrida low ≤ 40 cm", lambda v: all(x <= 40 for x in v)),
                       ("Media de las 3 low ≤ 40 cm", lambda v: sum(v) / len(v) <= 40),
                       ("Al menos una corrida low ≤ 40 cm", lambda v: any(x <= 40 for x in v))):
        fila = []
        for p in ("3B", "3C"):
            v = [num(h[(p, c)]["cierre_real_cm"]) for c in orden[:3]]
            fila.append("✓" if f(v) else "✗")
        out.append(f"| {lectura} | {fila[0]} | {fila[1]} |")
    return out


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
    out.append("")
    out.extend(exp3())
    print("\n".join(out))


if __name__ == "__main__":
    sys.exit(main())
