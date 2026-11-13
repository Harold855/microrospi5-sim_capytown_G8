#!/usr/bin/env python3
"""rc1_verificar — avance estimado de la entrega RC-1 contra la rúbrica (solo lectura).

No ejecuta el simulador ni el robot, no toca nada: lee archivos y dice qué falta.
NO es una nota: mide que existan los archivos y que los números de la hoja cumplan
los umbrales; la calidad del informe y la defensa (2 pts) no se pueden medir aquí.

Uso:   python3 scripts/rc1_verificar.py [--raiz .] [--estricto]
       --estricto  sale con código 1 si el avance medible es < 90 %

Convención de la columna `notas` de hoja_resultados.csv (para los umbrales E2 y E3):
       clave=valor separados por ';'  ->  e_medio_cm=2.6; t_as_s=5.8; e_fin_cm=0.5
       giro: sobre_pct=3.0; t_as_s=1.9; e_fin_deg=0.4   (giro real: e_fin_deg = error medido con transportador)
       recta real: desvio_cm=2.5   (desvio lateral final medido con cinta)
Solo biblioteca estándar.
"""
import argparse
import csv
import os
import re
import sys

COLS = ["prueba", "planta", "noise", "kp", "ki", "kd", "kp_yaw", "ki_yaw", "kd_yaw",
        "prediccion", "cierre_odom_cm", "cierre_real_cm", "yaw_acum_deg", "notas"]
PTS = {"E1": 1, "E2": 1, "E3": 1, "E4": 1, "E5": 2, "E6": 2, "E7": 4, "E8": 1, "INF": 3}   # DEF (2) no se mide
UMBRAL_LISTO = 90.0
RUNS = ["run1", "run2", "run3", "medium"]

# Nombres de archivo esperados (ver docs/rc1_g8/matriz_pruebas.md)
SIM_RECTA = ["exp1a_sim", "exp1b_sim", "exp1c_sim", "exp1d_sim"]
SIM_GIRO = ["exp2a_sim", "exp2b_sim", "exp2c_sim", "exp2p_sim"]
SIM_CUAD = [f"exp3{l}_sim_{r}" for l in "abc" for r in RUNS]
SIM_CINTA = [f"exp3{l}_sim_cinta_{r}" for l in "abc" for r in RUNS]
REAL_GIRO = ["exp2_real_giro90_r1", "exp2_real_giro90_r2", "exp2_real_giro90_r3"]   # serie oficial de E5 (el docente evalua el promedio de las 3)
REAL_RECTA = ["exp1d_real_run1", "exp1d_real_run2", "exp1d_real_run3"]
REAL_CUAD = ["exp3a_real", "exp3b_real_run1", "exp3b_real_run2", "exp3b_real_run3"]
REAL_CSV = REAL_GIRO + REAL_RECTA + REAL_CUAD
REAL_BAGS = ["rc1_real_3a", "rc1_real_3b_run1", "rc1_real_3b_run2", "rc1_real_3b_run3"]


class Item:
    def __init__(self, bloque, desc, hechos, total, nota=""):
        self.bloque, self.desc, self.hechos, self.total, self.nota = bloque, desc, hechos, total, nota

    @property
    def frac(self):
        return self.hechos / self.total if self.total else 0.0

    def estado(self):
        if self.hechos >= self.total:
            return "OK   "
        return "FALTA" if self.hechos == 0 else "PARC "


def ruta(raiz, *p):
    return os.path.join(raiz, *p)


def leer_texto(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def contar(raiz, rels):
    return sum(1 for r in rels if os.path.isfile(ruta(raiz, *r.split("/"))))


def png_de(raiz, stem):
    return any(os.path.isfile(ruta(raiz, d, stem + ".png")) for d in ("plots", "csv"))


def leer_hoja(raiz):
    p = ruta(raiz, "hoja_resultados.csv")
    if not os.path.isfile(p):
        return None, []
    with open(p, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        cols = r.fieldnames or []
        filas = [x for x in r if any((v or "").strip() for v in x.values())]
    return cols, filas


def num(v):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


def kv(notas):
    return {k: float(v) for k, v in re.findall(r"(\w+)\s*=\s*([-+]?\d+(?:\.\d+)?)", notas or "")}


def filas(hoja, prueba, planta, noise=None):
    out = [f for f in hoja if (f.get("prueba") or "").strip().lower() == prueba.lower()
           and (f.get("planta") or "").strip().lower() == planta.lower()]
    if noise:
        out = [f for f in out if (f.get("noise") or "").strip().lower() == noise]
    return out


def pendiente(path):
    t = leer_texto(path)
    return t is None or "[COMPLETAR" in t or "PENDIENTE" in t


def paginas_pdf(path):
    try:
        with open(path, "rb") as f:
            return len(re.findall(rb"/Type\s*/Page(?![s\w])", f.read()))
    except OSError:
        return None


def evaluar(raiz):
    it = []
    cols, hoja = leer_hoja(raiz)

    # ---- E1: simulador en marcha, sim_log.txt, rqt_graph
    log = leer_texto(ruta(raiz, "sim_log.txt"))
    it.append(Item("E1", "sim_log.txt con contenido", int(bool(log and log.strip())), 1))
    it.append(Item("E1", "sim_log.txt incluye `ros2 topic hz /odom` (average rate)",
                   int(bool(log and "average rate" in log)), 1))
    it.append(Item("E1", "captura de rqt_graph (plots/rqt_graph*.png)",
                   int(any(f.lower().startswith("rqt_graph") and f.endswith(".png")
                           for f in os.listdir(ruta(raiz, "plots")))) if os.path.isdir(ruta(raiz, "plots")) else 0, 1))

    # ---- E2: experimento 1
    it.append(Item("E2", "CSV 1A-1D (csv/)", contar(raiz, [f"csv/{s}.csv" for s in SIM_RECTA]), 4))
    it.append(Item("E2", "PNG 1A-1D", sum(png_de(raiz, s) for s in SIM_RECTA), 4))
    it.append(Item("E2", "filas en la hoja 1A-1D (sim)",
                   sum(1 for p in ("1A", "1B", "1C", "1D") if filas(hoja, p, "sim")), 4))
    f1d = filas(hoja, "1D", "sim")
    e_fin = kv(f1d[0].get("notas")).get("e_fin_cm") if f1d else None
    it.append(Item("E2", "regla: 1D error final <= 2 cm (notas: e_fin_cm=)",
                   int(e_fin is not None and e_fin <= 2.0), 1,
                   "sin dato" if e_fin is None else f"e_fin_cm={e_fin}"))

    # ---- E3: experimento 2
    it.append(Item("E3", "CSV 2a, 2b, 2c y combinación propia", contar(raiz, [f"csv/{s}.csv" for s in SIM_GIRO]), 4))
    it.append(Item("E3", "PNG de los giros", sum(png_de(raiz, s) for s in SIM_GIRO), 4))
    it.append(Item("E3", "filas en la hoja (2a, 2b, 2c, 2p)",
                   sum(1 for p in ("2a", "2b", "2c", "2p") if filas(hoja, p, "sim")), 4))
    f2p = filas(hoja, "2p", "sim")
    m = kv(f2p[0].get("notas")) if f2p else {}
    ok = "sobre_pct" in m and "t_as_s" in m and m["sobre_pct"] <= 10.0 and m["t_as_s"] <= 3.0
    it.append(Item("E3", "regla: combinación propia sobreimpulso <= 10 % y asentamiento <= 3 s", int(ok), 1,
                   "sin dato" if not m else f"sobre_pct={m.get('sobre_pct')} t_as_s={m.get('t_as_s')}"))

    # ---- E4: experimento 3 en el simulador (3 low + 1 medium por prueba)
    it.append(Item("E4", "CSV del nodo, 3A/3B/3C x (3 low + 1 medium)", contar(raiz, [f"csv/{s}.csv" for s in SIM_CUAD]), 12))
    it.append(Item("E4", "CSV de cierre_real.py (cinta virtual)", contar(raiz, [f"csv/{s}.csv" for s in SIM_CINTA]), 12))
    it.append(Item("E4", "PNG odom vs. real (cierre_real.py --png)", sum(png_de(raiz, s) for s in SIM_CINTA), 12))
    it.append(Item("E4", "filas en la hoja (sim, 4 por prueba)",
                   sum(min(4, len(filas(hoja, p, "sim"))) for p in ("3A", "3B", "3C")), 12))
    cumple = []
    for p in ("3B", "3C"):
        low = filas(hoja, p, "sim", "low")
        vals = [num(f.get("cierre_real_cm")) for f in low]
        if len(vals) >= 3 and all(v is not None for v in vals) and all(v <= 40.0 for v in vals):
            cumple.append(p)
    it.append(Item("E4", "regla: 3B o 3C con cierre REAL <= 40 cm en las 3 corridas low", int(bool(cumple)), 1,
                   "cumple " + "/".join(cumple) if cumple else "sin dato o no cumple"))

    # ---- E5: robot real, arranque y giro de 90 grados
    it.append(Item("E5", "CSV del giro90 real, serie oficial (csv/exp2_real_giro90_r1..r3.csv)", contar(raiz, [f"csv/{s}.csv" for s in REAL_GIRO]), len(REAL_GIRO)))
    fg = filas(hoja, "2", "real")
    it.append(Item("E5", "fila de la hoja (prueba 2, planta real)", int(bool(fg)), 1))
    eg = kv(fg[-1].get("notas")).get("e_fin_deg") if fg else None   # la ultima fila es la vigente (las anteriores son configuraciones previas)
    it.append(Item("E5", "regla: error final del giro real <= 3 grados, con transportador (notas: e_fin_deg=; la catedra puede ajustar)",
                   int(eg is not None and eg <= 3.0), 1, "sin dato" if eg is None else f"e_fin_deg={eg}"))

    # ---- E6: robot real, recta (1D), 3 corridas
    it.append(Item("E6", "CSV de las 3 rectas reales", contar(raiz, [f"csv/{s}.csv" for s in REAL_RECTA]), 3))
    f1r = filas(hoja, "1D", "real")
    it.append(Item("E6", "filas de la hoja (1D real, 3 corridas)", min(3, len(f1r)), 3))
    desv = [kv(f.get("notas")).get("desvio_cm") for f in f1r]
    desv = [d for d in desv if d is not None]
    it.append(Item("E6", "regla: desvio lateral final con cinta <= 5 cm en las 3 corridas (notas: desvio_cm=; la catedra puede ajustar)",
                   int(len(desv) >= 3 and max(desv) <= 5.0), 1,
                   "sin 3 datos" if len(desv) < 3 else f"max={max(desv)} cm"))

    # ---- E7: robot real, cuadrado de 2 x 2 m (3A una vez, 3B tres veces)
    it.append(Item("E7", "CSV del cuadrado real (3A x1, 3B x3)", contar(raiz, [f"csv/{s}.csv" for s in REAL_CUAD]), 4))
    it.append(Item("E7", "bags ROS 2 (carpeta con metadata.yaml)",
                   sum(1 for b_ in REAL_BAGS if os.path.isfile(ruta(raiz, "bags", b_, "metadata.yaml"))), 4))
    n_real = min(1, len(filas(hoja, "3A", "real"))) + min(3, len(filas(hoja, "3B", "real")))
    it.append(Item("E7", "filas de la hoja con planta=real (3A x1, 3B x3)", n_real, 4))
    r3b = [num(f.get("cierre_real_cm")) for f in filas(hoja, "3B", "real")]
    r3b = [v for v in r3b if v is not None]
    media = sum(r3b) / len(r3b) if len(r3b) >= 3 else None
    r3a = [num(f.get("cierre_real_cm")) for f in filas(hoja, "3A", "real")]
    r3a = [v for v in r3a if v is not None]
    it.append(Item("E7", "regla: cierre real medio de 3B <= 25 cm (3 corridas; la catedra puede ajustar)",
                   int(media is not None and media <= 25.0), 1,
                   "sin 3 corridas" if media is None else f"media={media:.1f} cm"))
    it.append(Item("E7", "regla: el cierre medio de 3B es menor que el de 3A",
                   int(media is not None and bool(r3a) and media < r3a[0]), 1,
                   "sin datos" if media is None or not r3a else f"3B={media:.1f} cm, 3A={r3a[0]:.1f} cm"))

    # ---- E8: evidencia y transferencia
    it.append(Item("E8", "hoja_resultados.csv con las columnas del Anexo E", int(cols == COLS), 1,
                   "" if cols == COLS else f"columnas: {cols}"))
    it.append(Item("E8", "PNG de las corridas reales", sum(png_de(raiz, s) for s in REAL_CSV), len(REAL_CSV)))
    it.append(Item("E8", "tabla de transferencia simulador->robot completa (docs/rc1_g8/transferencia.md)",
                   int(not pendiente(ruta(raiz, "docs", "rc1_g8", "transferencia.md"))), 1))

    # ---- INF: informe
    pdf = ruta(raiz, "informe.pdf")
    pag = paginas_pdf(pdf) if os.path.isfile(pdf) else None
    it.append(Item("INF", "informe.pdf existe", int(pag is not None), 1))
    it.append(Item("INF", "informe.pdf de 1 página", int(pag == 1), 1, "" if pag is None else f"{pag} pág."))
    it.append(Item("INF", "predicciones escritas (docs/rc1_g8/predicciones_rc1.md sin [COMPLETAR])",
                   int(not pendiente(ruta(raiz, "docs", "rc1_g8", "predicciones_rc1.md"))), 1))

    # ---- Pendientes de texto que no suman puntos pero bloquean la entrega
    extra = []
    readme = leer_texto(ruta(raiz, "README.md")) or ""
    if "[COMPLETAR" in readme:
        extra.append("README.md tiene [COMPLETAR] (integrantes, roles, ganancias finales)")
    cfg = leer_texto(ruta(raiz, "config", "rc1_pid.yaml")) or ""
    if "PENDIENTE" in cfg:
        extra.append("config/rc1_pid.yaml sigue PENDIENTE (ganancias finales sin fijar)")
    if cfg == "":
        extra.append("falta config/rc1_pid.yaml")
    bonus = [num(f.get("cierre_real_cm")) for f in filas(hoja, "3B", "real")]
    bonus = [v for v in bonus if v is not None]
    return it, extra, (min(bonus) if bonus else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--estricto", action="store_true")
    a = ap.parse_args()

    items, extra, mejor3b = evaluar(a.raiz)
    total = 0.0
    print("RC-1 · avance estimado de la entrega (no es la nota)\n")
    for b in PTS:
        its = [i for i in items if i.bloque == b]
        frac = sum(i.frac for i in its) / len(its)
        total += PTS[b] * frac
        print(f"== {b}  ({PTS[b]} pt)  {frac * 100:5.1f} %")
        for i in its:
            n = f" — {i.nota}" if i.nota else ""
            print(f"   [{i.estado()}] {i.desc} ({i.hechos}/{i.total}){n}")
    medible = sum(PTS.values())
    pct = 100.0 * total / medible
    print(f"\nAvance medible: {total:.1f} / {medible} pt = {pct:.1f} %   (DEF, 2 pt, depende de la defensa)")
    if mejor3b is not None:
        print(f"Bonus (3B real, cierre <= 10 cm sin recalibrar): mejor corrida = {mejor3b:.1f} cm "
              f"-> {'candidato' if mejor3b <= 10 else 'no alcanza'}")
    for e in extra:
        print("PENDIENTE:", e)
    listo = pct >= UMBRAL_LISTO and not extra
    print("\nEstado:", "supera el 90 % y no quedan pendientes de texto" if listo
          else f"todavía no: falta llegar a {UMBRAL_LISTO:.0f} % y cerrar los pendientes")
    reglas = [i for i in items if i.desc.startswith("regla") and i.hechos == 0]
    if listo and reglas:
        print(f"OJO: {len(reglas)} regla(s) de umbral de la rúbrica siguen en FALTA (ver arriba): el % no las pondera por separado.")
    if a.estricto and not listo:
        sys.exit(1)


if __name__ == "__main__":
    main()
