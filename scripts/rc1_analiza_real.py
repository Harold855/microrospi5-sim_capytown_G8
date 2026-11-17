#!/usr/bin/env python3
"""rc1_analiza_real — análisis automático de uno o varios CSV de cuadrado_controller.py (simulador o robot real).

Detecta el tipo de prueba por los estados del CSV (giro, recta o cuadrado) y calcula en una pasada las métricas que se usan en E5, E6 y E7:
tiempo hasta FIN, errores de línea, cruces de la línea virtual, permanencia en ±2 cm, inversiones de w, yaw, cierre según /odom, y por
lado / por giro en el cuadrado. Opcionalmente contrasta con los criterios de las predicciones y dibuja una gráfica.

Los datos del CSV salen de /odom: NO sustituyen la medición con cinta ni con transportador. Por eso al final propone el comando de
rc1_anotar_real.py para anotar en la hoja los valores físicos medidos.

Uso:
    python3 scripts/rc1_analiza_real.py csv/exp1d_real_run1.csv
    python3 scripts/rc1_analiza_real.py csv/exp1d_real_run*.csv --criterios e6 --png
    python3 scripts/rc1_analiza_real.py csv/exp3b_real_run1.csv csv/exp3b_real_run2.csv csv/exp3b_real_run3.csv --criterios e7b
    python3 scripts/rc1_analiza_real.py csv/exp3a_real.csv --criterios e7a
    python3 scripts/rc1_analiza_real.py csv/exp2_real_giro90_r3.csv --criterios e5

Opciones:
    --experimento recta|giro90|cuadrado|cuadrado_abierto   fuerza el tipo (por defecto se detecta; exp3a_* se toma como cuadrado_abierto)
    --criterios e5|e6|e7a|e7b    contrasta con los criterios de las predicciones (ver CRITERIOS, editables abajo)
    --png                        guarda plots/<nombre>_analisis.png (necesita matplotlib)
    --json                       imprime las métricas en JSON (para otros scripts)

Solo biblioteca estándar (matplotlib solo para --png).
"""
import csv
import json
import math
import os
import sys

UMBRAL_CRUCE = 0.005        # m: un cruce de la línea cuenta si se pasa de +0.5 cm a -0.5 cm (o al revés)
BANDA = 0.02                # m: banda de ±2 cm
PERMANENCIA = 0.3           # s dentro de la banda para contar «permanencia»
VENTANA_W = 2.0             # s previos a FIN para contar inversiones de w
W_MIN = 0.05                # rad/s: se ignoran órdenes menores al contar inversiones

# Criterios tomados de las predicciones escritas (docs/rc1_g8/predicciones_*.md). Edítense si cambian las predicciones.
CRITERIOS = {
    "e5": {"titulo": "E5 giro real, kp_yaw 1.0 (predicciones_E5_kp1.md)",
           "t_fin": (5.0, 7.0), "w_fin_cero": True, "inversiones_max": 2, "sobreimpulso_aprox_grados": 1.0},
    "e6": {"titulo": "E6 recta real, experimental 1 (predicciones_E6_exp1.md)",
           "t_fin": (20.0, 30.0), "w_fin_cero": True, "ultimo_e_mayor_cm": 5.0, "sin_permanencia_2cm": True, "cruces_min": 3},
    "e7a": {"titulo": "E7 3A real (predicciones_E7_3A.md)",
            "t_fin": (88.0, 90.0), "cierre_odom_cm": (30.0, 115.0), "yaw_total": (376.0, 408.0)},
    "e7b": {"titulo": "E7 3B real (predicciones_E7_3B.md, borrador)",
            "t_fin": (100.0, 115.0), "cierre_odom_cm": (0.0, 8.0), "yaw_total": (340.0, 370.0),
            "pico_lado_cm": (1.0, 4.0), "cruces_lado_max": 2},
}


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def leer(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        sys.exit(f"{ruta}: CSV vacío")
    d = {k: [float(r[k]) for r in filas] for k in ("t", "x", "y", "yaw", "v", "w", "e_line", "e_yaw")}
    d["estado"] = [r["estado"] for r in filas]
    return d


def segmentos(estados, hasta):
    """Tramos consecutivos de un mismo estado antes de `hasta`: lista de (estado, i0, i1) con i1 exclusivo."""
    out, i = [], 0
    while i < hasta:
        j = i
        while j < hasta and estados[j] == estados[i]:
            j += 1
        out.append((estados[i], i, j))
        i = j
    return out


def cruces_significativos(e):
    """Cambios de signo con histéresis de ±UMBRAL_CRUCE (ignora el ruido alrededor de cero)."""
    lado, n = 0, 0
    for v in e:
        s = 1 if v > UMBRAL_CRUCE else (-1 if v < -UMBRAL_CRUCE else 0)
        if s == 0:
            continue
        if lado != 0 and s != lado:
            n += 1
        lado = s
    return n


def cruces_simples(e):
    return sum(1 for a, b in zip(e, e[1:]) if a * b < 0)


def permanencia(t, e):
    """Mayor tiempo continuo con |e| <= BANDA (s) y primer instante en que entra en la banda."""
    mejor, ini, primero = 0.0, None, None
    for ti, ei in zip(t, e):
        if abs(ei) <= BANDA:
            if ini is None:
                ini = ti
            if primero is None:
                primero = ti
            mejor = max(mejor, ti - ini)
        else:
            ini = None
    return mejor, primero


def asentamiento(t, e):
    """Primer instante a partir del cual |e| <= BANDA hasta el final del tramo (None si no se asienta)."""
    for i in range(len(e)):
        if all(abs(v) <= BANDA for v in e[i:]):
            return t[i]
    return None


def inversiones_w(t, w, t_fin):
    ws = [wi for ti, wi in zip(t, w) if t_fin - VENTANA_W <= ti < t_fin and abs(wi) >= W_MIN]
    return sum(1 for a, b in zip(ws, ws[1:]) if a * b < 0)


def detectar(d, i_fin, nombre, forzado):
    if forzado:
        return forzado
    segs = segmentos(d["estado"], i_fin)
    n_gira = sum(1 for s in segs if s[0] == "GIRA")
    n_av = sum(1 for s in segs if s[0] == "AVANZA")
    if n_av == 0:
        return "giro90"
    if n_gira == 0:
        return "recta"
    return "cuadrado_abierto" if os.path.basename(nombre).startswith("exp3a") else "cuadrado"


def analizar(ruta, forzado=None):
    d = leer(ruta)
    n = len(d["t"])
    i_fin = next((i for i, e in enumerate(d["estado"]) if e == "FIN"), None)
    terminado = i_fin is not None
    hasta = i_fin if terminado else n
    t0 = d["t"][0]
    exp = detectar(d, hasta, ruta, forzado)
    m = {"archivo": ruta, "experimento": exp, "terminado": terminado, "filas": n}

    t = [v - t0 for v in d["t"]]
    m["t_fin_s"] = t[i_fin] if terminado else None
    m["t_ultimo_s"] = t[hasta - 1] if hasta else 0.0
    if terminado:
        m["v_fin"] = d["v"][i_fin]
        m["w_fin"] = d["w"][i_fin]
    # yaw acumulado (rad) y cierre según /odom (posición en FIN respecto del inicio)
    yaw_acum = 0.0
    for a, b in zip(d["yaw"][:hasta + (1 if terminado else 0)], d["yaw"][1:hasta + (1 if terminado else 0)]):
        yaw_acum += wrap(b - a)
    m["yaw_total_deg"] = math.degrees(yaw_acum)
    i_end = i_fin if terminado else n - 1
    m["cierre_odom_cm"] = 100.0 * math.hypot(d["x"][i_end] - d["x"][0], d["y"][i_end] - d["y"][0])
    m["inversiones_w_2s"] = inversiones_w(t, d["w"], m["t_fin_s"]) if terminado else None

    if exp == "giro90":
        y0 = d["yaw"][0]
        ang = [math.degrees(sum(wrap(b - a) for a, b in zip(d["yaw"][:k], d["yaw"][1:k + 1]))) for k in range(0, hasta)]
        m["pico_deg"] = max(ang) if ang else 0.0
        m["sobreimpulso_pct"] = max(0.0, m["pico_deg"] - 90.0) / 90.0 * 100
        m["yaw_en_fin_deg"] = ang[-1] if ang else None
        m["primer_error_menor_2deg_s"] = next((ti for ti, e in zip(t, d["e_yaw"][:hasta]) if abs(math.degrees(e)) < 2.0), None)
        m["fraccion_dentro_2deg"] = (sum(1 for e in d["e_yaw"][:hasta] if abs(math.degrees(e)) < 2.0) / hasta) if hasta else 0
    else:
        segs = segmentos(d["estado"], hasta)
        lados = []
        for est, i0, i1 in (s for s in segs if s[0] == "AVANZA"):
            e = d["e_line"][i0:i1]
            tt = t[i0:i1]
            if not e:
                continue
            psi = d["yaw"][i0]
            s_rec = (d["x"][i1 - 1] - d["x"][i0]) * math.cos(psi) + (d["y"][i1 - 1] - d["y"][i0]) * math.sin(psi)
            perm, primero = permanencia(tt, e)
            lados.append({
                "t_ini": tt[0], "t_fin": tt[-1], "dur_s": tt[-1] - tt[0], "avance_m": s_rec,
                "e_min_cm": 100 * min(e), "e_max_cm": 100 * max(e), "pico_cm": 100 * max(abs(v) for v in e),
                "e_ultimo_cm": 100 * e[-1], "cruces": cruces_significativos(e), "cruces_simples": cruces_simples(e),
                "perm_max_banda_s": perm, "primer_en_banda_s": (primero - tt[0]) if primero is not None else None,
                "t_asienta_s": (asentamiento(tt, e) - tt[0]) if asentamiento(tt, e) is not None else None,
            })
        m["lados"] = lados
        giros = []
        for est, i0, i1 in (s for s in segs if s[0] == "GIRA"):
            ang = math.degrees(sum(wrap(b - a) for a, b in zip(d["yaw"][i0:i1], d["yaw"][i0 + 1:i1 + 1])))
            ang_inicial = math.degrees(wrap(d["yaw"][min(i1, n - 1)] - d["yaw"][i0]))
            giros.append({"t_ini": t[i0], "dur_s": t[i1 - 1] - t[i0], "giro_odom_deg": ang_inicial,
                          "inversiones_w": sum(1 for a, b in zip(d["w"][i0:i1], d["w"][i0 + 1:i1])
                                                if a * b < 0 and abs(a) >= W_MIN and abs(b) >= W_MIN)})
        m["giros"] = giros
        if exp == "recta" and lados:
            L = lados[0]
            m["e_ultimo_cm"] = abs(L["e_ultimo_cm"])
            m["pico_cm"] = L["pico_cm"]
            m["cruces"] = L["cruces"]
            m["cruces_simples"] = L["cruces_simples"]
            m["perm_max_banda_s"] = L["perm_max_banda_s"]
            m["t_asienta_s"] = L["t_asienta_s"]
            m["avance_m"] = L["avance_m"]
            m["e_min_cm"], m["e_max_cm"] = L["e_min_cm"], L["e_max_cm"]
    return m, d, t, hasta


def f(v, fmt="{:.1f}", vacio="—"):
    return vacio if v is None else fmt.format(v)


def informe(m):
    nombre = os.path.basename(m["archivo"])
    print(f"=== {nombre}  [{m['experimento']}] ===")
    print(f"filas: {m['filas']}   terminado: {'sí (FIN)' if m['terminado'] else 'NO — el CSV no llega a FIN'}")
    if m["terminado"]:
        print(f"tiempo hasta FIN: {m['t_fin_s']:.2f} s   v en FIN = {m['v_fin']:.3f}, w en FIN = {m['w_fin']:.3f}")
    print(f"yaw acumulado según /odom: {m['yaw_total_deg']:.1f}°   cierre según /odom: {m['cierre_odom_cm']:.1f} cm")
    if m["inversiones_w_2s"] is not None:
        print(f"inversiones de w (|w| ≥ {W_MIN}) en los {VENTANA_W:.0f} s previos a FIN: {m['inversiones_w_2s']}")
    if m["experimento"] == "giro90":
        print(f"pico de yaw: {m['pico_deg']:.1f}°  sobreimpulso: {m['sobreimpulso_pct']:.2f} %  yaw al final: {f(m.get('yaw_en_fin_deg'))}°")
        print(f"primer instante con |e_yaw| < 2°: {f(m['primer_error_menor_2deg_s'], '{:.2f}')} s   fracción del tiempo dentro de ±2°: {m['fraccion_dentro_2deg']:.2f}")
    else:
        if m["experimento"] == "recta" and m.get("lados"):
            print(f"AVANCE {m['avance_m']:.2f} m  |  e_line: min {m['e_min_cm']:.1f}, max {m['e_max_cm']:.1f}, pico {m['pico_cm']:.1f} cm, "
                  f"último {m['e_ultimo_cm']:.1f} cm (según /odom, NO es el desvío físico)")
            print(f"cruces significativos (±{UMBRAL_CRUCE*100:.1f} cm): {m['cruces']}  simples: {m['cruces_simples']}   "
                  f"mayor permanencia continua en ±2 cm: {m['perm_max_banda_s']:.2f} s   se asienta en ±2 cm desde: {f(m['t_asienta_s'], '{:.1f}')} s")
        else:
            print("  lado    dur(s) avance(m) pico|e|(cm) cruces perm±2cm(s)   giro siguiente (odom°, dur s, inv w)")
            for i, L in enumerate(m["lados"]):
                g = m["giros"][i] if i < len(m["giros"]) else None
                gt = f"{g['giro_odom_deg']:6.1f}°, {g['dur_s']:4.1f}, {g['inversiones_w']}" if g else "—"
                print(f"  {i+1:>4}  {L['dur_s']:8.1f} {L['avance_m']:9.2f} {L['pico_cm']:12.1f} {L['cruces']:6d} {L['perm_max_banda_s']:11.2f}   {gt}")


def evaluar(m, clave):
    c = CRITERIOS[clave]
    print(f"--- criterios de la predicción: {c['titulo']} ---")
    out = []

    def linea(ok, texto):
        out.append(ok)
        print(f"  [{'cumple ' if ok else 'NO cumple'}] {texto}")

    if "t_fin" in c:
        lo, hi = c["t_fin"]
        t = m["t_fin_s"]
        linea(t is not None and lo <= t <= hi, f"FIN entre {lo:g} y {hi:g} s (medido: {f(t, '{:.1f}')} s)")
    if c.get("w_fin_cero"):
        linea(m["terminado"] and abs(m["w_fin"]) < 1e-9 and abs(m["v_fin"]) < 1e-9, "v = 0.000 y w = 0.000 en la primera fila FIN")
    if "inversiones_max" in c:
        v = m["inversiones_w_2s"]
        linea(v is not None and v <= c["inversiones_max"], f"como máximo {c['inversiones_max']} inversiones de w en los 2 s previos (medido: {v})")
    if "ultimo_e_mayor_cm" in c:
        linea(m.get("e_ultimo_cm", 0) > c["ultimo_e_mayor_cm"], f"último |e_line| > {c['ultimo_e_mayor_cm']:g} cm (medido: {f(m.get('e_ultimo_cm'))} cm)")
    if c.get("sin_permanencia_2cm"):
        linea(m.get("perm_max_banda_s", 0) < PERMANENCIA, f"sin permanencia continua de {PERMANENCIA:g} s en ±2 cm (mayor: {f(m.get('perm_max_banda_s'), '{:.2f}')} s)")
    if "cruces_min" in c:
        linea(m.get("cruces", 0) >= c["cruces_min"], f"al menos {c['cruces_min']} cruces de e_line (medido: {m.get('cruces')})")
    if "cierre_odom_cm" in c:
        lo, hi = c["cierre_odom_cm"]
        linea(lo <= m["cierre_odom_cm"] <= hi, f"cierre según /odom entre {lo:g} y {hi:g} cm (medido: {m['cierre_odom_cm']:.1f} cm)")
    if "yaw_total" in c:
        lo, hi = c["yaw_total"]
        linea(lo <= m["yaw_total_deg"] <= hi, f"yaw acumulado /odom entre {lo:g}° y {hi:g}° (medido: {m['yaw_total_deg']:.1f}°)")
    if "pico_lado_cm" in c and m.get("lados"):
        lo, hi = c["pico_lado_cm"]
        picos = [L["pico_cm"] for L in m["lados"]]
        linea(all(p <= hi for p in picos), f"pico |e_line| por lado ≤ {hi:g} cm (medidos: {', '.join(f'{p:.1f}' for p in picos)})")
    if "cruces_lado_max" in c and m.get("lados"):
        cr = [L["cruces"] for L in m["lados"]]
        linea(all(x <= c["cruces_lado_max"] for x in cr), f"como máximo {c['cruces_lado_max']} cruces por lado (medidos: {cr})")
    if "sobreimpulso_aprox_grados" in c:
        so = m.get("pico_deg", 90.0) - 90.0
        print(f"  [info    ] pico de /odom menos 90°: {so:+.1f}° ({'sin sobreimpulso' if so <= 0 else 'sobreimpulso'}; la predicción decía ≈ +{c['sobreimpulso_aprox_grados']:g}°)")
    return out


def sugerencia(m):
    base = os.path.splitext(os.path.basename(m["archivo"]))[0]
    et = base.split("_")[-1] if base.split("_")[-1] in ("run1", "run2", "run3", "exp1", "exp2", "exp3", "r1", "r2", "r3", "extra") else "unica"
    prueba = {"recta": "1D", "giro90": "2", "cuadrado": "3B", "cuadrado_abierto": "3A"}[m["experimento"]]
    if m["experimento"] == "cuadrado_abierto":
        prueba = "3A"
    if m["experimento"] == "giro90":
        return f"python3 scripts/rc1_anotar_real.py 2 {et} e_fin_deg=<transportador> cierre_odom_cm={m['cierre_odom_cm']:.1f}"
    if m["experimento"] == "recta":
        return f"python3 scripts/rc1_anotar_real.py 1D {et} ki=0.5 desvio_cm=<cinta> cierre_odom_cm={m['cierre_odom_cm']:.1f}   # ajusta ki/kp/kd a las ganancias usadas"
    return (f"python3 scripts/rc1_anotar_real.py {prueba} {et} cierre_odom_cm={m['cierre_odom_cm']:.1f} "
            f"cierre_real_cm=<cinta> yaw_acum_deg=<transportador>")


def grafica(m, d, t, hasta, destino):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x0, y0, th0 = d["x"][0], d["y"][0], d["yaw"][0]
    c, s = math.cos(th0), math.sin(th0)
    xs = [c * (x - x0) + s * (y - y0) for x, y in zip(d["x"][:hasta + 1], d["y"][:hasta + 1])]
    ys = [-s * (x - x0) + c * (y - y0) for x, y in zip(d["x"][:hasta + 1], d["y"][:hasta + 1])]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
    ax[0].plot(xs, ys, c="#0277BD", lw=2)
    ax[0].plot(0, 0, "o", c="#0F9D58")
    if m["experimento"].startswith("cuadrado"):
        ax[0].plot([0, 2, 2, 0, 0], [0, 0, 2, 2, 0], "--", c="gray", lw=1.1)
    ax[0].set_aspect("equal"); ax[0].grid(alpha=.3); ax[0].set_title("Trayectoria según /odom (marco del inicio)")
    ax[0].set_xlabel("x (m)"); ax[0].set_ylabel("y (m)")
    if m["experimento"] == "giro90":
        yaw = [0.0]
        for a, b in zip(d["yaw"][:hasta], d["yaw"][1:hasta + 1]):
            yaw.append(yaw[-1] + math.degrees(wrap(b - a)))
        ax[1].plot(t[:len(yaw)], yaw, c="#0277BD", lw=2)
        ax[1].axhline(90, ls="--", c="gray"); ax[1].axhspan(88, 92, color="green", alpha=.08)
        ax[1].set_ylabel("yaw (°)"); ax[1].set_title("Giro")
    else:
        ax[1].plot(t[:hasta], [100 * v for v in d["e_line"][:hasta]], c="#C49000", lw=1.4)
        ax[1].axhline(0, ls="--", c="gray"); ax[1].axhspan(-2, 2, color="green", alpha=.08)
        ax[1].set_ylabel("e_line (cm)"); ax[1].set_title("Error a la línea virtual (según /odom)")
    ax[1].set_xlabel("t (s)"); ax[1].grid(alpha=.3)
    ax[2].plot(t[:hasta], d["w"][:hasta], c="#D93025", lw=1.2)
    ax[2].set_xlabel("t (s)"); ax[2].set_ylabel("w ordenada (rad/s)"); ax[2].set_title("Orden angular"); ax[2].grid(alpha=.3)
    fig.suptitle(os.path.basename(m["archivo"]), fontsize=10)
    fig.tight_layout()
    fig.savefig(destino, dpi=130)
    plt.close(fig)


def main(argv):
    args = argv[1:]
    forzado = criterios = None
    png = js = False
    archivos = []
    it = iter(args)
    for a in it:
        if a == "--experimento":
            forzado = next(it)
        elif a == "--criterios":
            criterios = next(it)
        elif a == "--png":
            png = True
        elif a == "--json":
            js = True
        elif a in ("-h", "--help"):
            print(__doc__); return 0
        else:
            archivos.append(a)
    if not archivos:
        sys.exit(__doc__)
    if criterios and criterios not in CRITERIOS:
        sys.exit(f"--criterios debe ser uno de {', '.join(CRITERIOS)}")
    resultados = []
    for ruta in archivos:
        m, d, t, hasta = analizar(ruta, forzado)
        resultados.append(m)
        if not js:
            informe(m)
            if criterios:
                evaluar(m, criterios)
            print("anotar en la hoja (con los valores medidos a mano):")
            print("  " + sugerencia(m))
            if png:
                raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                os.makedirs(os.path.join(raiz, "plots"), exist_ok=True)
                dest = os.path.join(raiz, "plots", os.path.splitext(os.path.basename(ruta))[0] + "_analisis.png")
                grafica(m, d, t, hasta, dest)
                print(f"gráfica: {os.path.relpath(dest, raiz)}")
            print()
    if js:
        print(json.dumps(resultados, indent=2, ensure_ascii=False, default=lambda o: None))
    elif len(resultados) > 1:
        print("=== resumen de las corridas ===")
        exp = resultados[0]["experimento"]
        if exp == "recta":
            print("  archivo                          FIN(s)  último|e|(cm)  pico(cm)  cruces  perm±2cm(s)")
            for m in resultados:
                print(f"  {os.path.basename(m['archivo']):<32} {f(m['t_fin_s']):>6} {f(m.get('e_ultimo_cm')):>14} {f(m.get('pico_cm')):>9} {str(m.get('cruces', '—')):>7} {f(m.get('perm_max_banda_s'), '{:.2f}'):>11}")
        elif exp.startswith("cuadrado"):
            print("  archivo                          FIN(s)  yaw(°)  cierre /odom (cm)")
            for m in resultados:
                print(f"  {os.path.basename(m['archivo']):<32} {f(m['t_fin_s']):>6} {m['yaw_total_deg']:>7.1f} {m['cierre_odom_cm']:>17.1f}")
            cs = [m["cierre_odom_cm"] for m in resultados]
            print(f"  media del cierre según /odom: {sum(cs)/len(cs):.1f} cm (el cierre que cuenta en E7 es el medido con cinta)")
        else:
            print("  archivo                          FIN(s)  pico(°)  inv w")
            for m in resultados:
                print(f"  {os.path.basename(m['archivo']):<32} {f(m['t_fin_s']):>6} {m['pico_deg']:>8.1f} {str(m['inversiones_w_2s']):>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
