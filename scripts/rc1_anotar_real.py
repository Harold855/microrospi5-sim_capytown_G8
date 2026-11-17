#!/usr/bin/env python3
"""rc1_anotar_real — anota (o crea) la fila de UNA corrida del ROBOT REAL en hoja_resultados.csv.

Sirve para E5 (prueba 2), E6 (1D) y E7 (3A, 3B). Identifica la fila por (prueba, planta=real, etiqueta), donde la etiqueta es la
primera palabra de la columna `notas` (exp1, run1, run2, run3, unica, ...). Si la fila no existe, la crea con las ganancias del bloque
`robot_real` de config/rc1_pid.yaml (o las que se pasen). Si existe, actualiza los valores y NO toca la predicción.

Uso:
    python3 scripts/rc1_anotar_real.py <prueba> <etiqueta> clave=valor [clave=valor ...] [--nota "texto"] [--pred "texto"]

Claves con columna propia:  cierre_odom_cm  cierre_real_cm  yaw_acum_deg
Claves de ganancias (si la fila es nueva o se quieren corregir):  kp ki kd kp_yaw ki_yaw kd_yaw
Cualquier otra clave va a `notas` como clave=valor;  (por ejemplo desvio_cm, e_fin_deg, bag, video, cambio)

Ejemplos:
    # E6: tercera corrida oficial de la recta, desvío con cinta 3.5 cm
    python3 scripts/rc1_anotar_real.py 1D run3 desvio_cm=3.5 cierre_odom_cm=200.0 --nota "FIN nodo: 20.9 s"
    # E7: 3B corrida 1, cierre real con cinta 28.0 cm y yaw final 352.0 deg
    python3 scripts/rc1_anotar_real.py 3B run1 cierre_odom_cm=0.6 cierre_real_cm=28.0 yaw_acum_deg=352.0 bag=bags/rc1_real_3b_run1
    # E7: 3A, una sola corrida
    python3 scripts/rc1_anotar_real.py 3A unica cierre_odom_cm=12.0 cierre_real_cm=61.0 yaw_acum_deg=378.0

Los números llevan punto decimal (8.9, no 8,9). Opción --hoja RUTA para trabajar sobre otra copia (pruebas).
Solo biblioteca estándar (PyYAML opcional, para leer las ganancias de una fila nueva).
"""
import csv
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRUEBAS = ("2", "1D", "3A", "3B")
COLUMNAS_PROPIAS = ("cierre_odom_cm", "cierre_real_cm", "yaw_acum_deg")
GANANCIAS = ("kp", "ki", "kd", "kp_yaw", "ki_yaw", "kd_yaw")


def ganancias_yaml():
    try:
        import yaml
        with open(os.path.join(RAIZ, "config", "rc1_pid.yaml"), encoding="utf-8") as f:
            p = yaml.safe_load(f)["robot_real"]["cuadrado_controller"]["ros__parameters"]
        return {k: p[k] for k in GANANCIAS if k in p}
    except Exception:
        return {}


def valor_ok(v):
    if "," in v and v.replace(",", "").replace("-", "").replace(".", "").isdigit():
        sys.exit(f"'{v}': usa punto decimal, no coma.")
    return v


def main(argv):
    hoja = os.path.join(RAIZ, "hoja_resultados.csv")
    nota = pred = ""
    args = []
    it = iter(argv[1:])
    for a in it:
        if a == "--hoja":
            hoja = next(it)
        elif a == "--nota":
            nota = next(it)
        elif a == "--pred":
            pred = next(it)
        else:
            args.append(a)
    if len(args) < 2 or args[0] not in PRUEBAS:
        sys.exit(__doc__)
    prueba, etiqueta, pares = args[0], args[1], args[2:]
    kv = {}
    for p in pares:
        if "=" not in p:
            sys.exit(f"Argumento '{p}' sin '=': usa clave=valor")
        k, v = p.split("=", 1)
        kv[k.strip()] = valor_ok(v.strip())

    with open(hoja, newline="", encoding="utf-8") as f:
        filas = list(csv.reader(f))
    cab = filas[0]
    ix = {c: cab.index(c) for c in cab}
    objetivo = [r for r in filas[1:] if r[ix["prueba"]] == prueba and r[ix["planta"]] == "real"
                and r[ix["notas"]].split(";")[0].strip() == etiqueta]
    if len(objetivo) > 1:
        sys.exit(f"Hay {len(objetivo)} filas de {prueba} real '{etiqueta}'. Revisa hoja_resultados.csv.")
    if objetivo:
        fila, nueva = objetivo[0], False
    else:
        fila, nueva = [""] * len(cab), True
        fila[ix["prueba"]], fila[ix["planta"]] = prueba, "real"
        g = ganancias_yaml()
        for k in GANANCIAS:
            if k in g:
                fila[ix[k]] = repr(float(g[k]))
        fila[ix["prediccion"]] = pred
        fila[ix["notas"]] = etiqueta
        filas.append(fila)

    # ganancias y columnas propias
    for k in GANANCIAS:
        if k in kv:
            fila[ix[k]] = repr(float(kv.pop(k)))
    for k in COLUMNAS_PROPIAS:
        if k in kv:
            fila[ix[k]] = kv[k]
    # notas: la etiqueta, luego clave=valor (se reemplazan las claves repetidas), luego texto libre
    partes = [p.strip() for p in fila[ix["notas"]].split(";") if p.strip()]
    cabeza, resto = (partes[0] if partes else etiqueta), partes[1:]
    claves = {}
    libres = []
    for p in resto:
        if "=" in p and not p.startswith(" "):
            k, v = p.split("=", 1)
            claves[k.strip()] = v.strip()
        else:
            libres.append(p)
    for k in COLUMNAS_PROPIAS:
        if k in kv:
            claves[k] = kv[k]
    for k, v in kv.items():
        if k not in COLUMNAS_PROPIAS:
            claves[k] = v
    if nota:
        libres.append(nota)
    fila[ix["notas"]] = "; ".join([cabeza] + [f"{k}={v}" for k, v in claves.items()] + libres)

    with open(hoja, "w", newline="", encoding="utf-8") as g:
        csv.writer(g, lineterminator="\n").writerows(filas)
    est = "fila NUEVA" if nueva else "fila actualizada"
    print(f"{prueba} real {etiqueta}: {est}  ->  " + "; ".join(f"{k}={v}" for k, v in claves.items()))


if __name__ == "__main__":
    main(sys.argv)
