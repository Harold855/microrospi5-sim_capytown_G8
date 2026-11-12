#!/usr/bin/env python3
"""rc1_anotar — anota el resultado de UNA corrida del Experimento 3 en hoja_resultados.csv.

Busca la fila (prueba, planta=sim, corrida) y rellena cierre_odom_cm, cierre_real_cm y yaw_acum_deg. No toca la predicción
ni las demás filas. La corrida se identifica por la etiqueta que va al principio de la columna `notas` (run1, run2, run3, medium).

Uso:
    python3 scripts/rc1_anotar.py <3A|3B|3C> <run1|run2|run3|medium> <cierre_odom_cm> <cierre_real_cm> <yaw_real_deg> ["nota"]

Ejemplo:
    python3 scripts/rc1_anotar.py 3A run1 8.9 10.8 360.5 "FIN nodo: 8.9 cm, yaw 357.5, 47.9 s"

Los tres números salen de las salidas de la corrida:
    cierre_odom_cm : el que imprime cierre_real.py como «cierre según /odom» (coincide con el `FIN` del nodo)
    cierre_real_cm : «cierre REAL» de cierre_real.py
    yaw_real_deg   : «yaw acumulado» de la línea REAL de cierre_real.py
Solo biblioteca estándar.
"""
import csv
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOJA = os.path.join(RAIZ, "hoja_resultados.csv")
CORRIDAS = ("run1", "run2", "run3", "medium")


def main(argv):
    if len(argv) < 6 or argv[1] not in ("3A", "3B", "3C") or argv[2] not in CORRIDAS:
        sys.exit(__doc__)
    prueba, corrida = argv[1], argv[2]
    try:
        odom, real, yaw = (float(x) for x in argv[3:6])
    except ValueError:
        sys.exit("Los tres valores numericos deben llevar punto decimal (8.9, no 8,9).")
    nota = argv[6] if len(argv) > 6 else ""

    with open(HOJA, newline="", encoding="utf-8") as f:
        filas = list(csv.reader(f))
    cab = filas[0]
    i_odom, i_real, i_yaw, i_notas = (cab.index(c) for c in ("cierre_odom_cm", "cierre_real_cm", "yaw_acum_deg", "notas"))
    objetivo = [f for f in filas[1:] if f[0] == prueba and f[1] == "sim" and f[i_notas].split(";")[0].strip() == corrida]
    if len(objetivo) != 1:
        sys.exit(f"Esperaba 1 fila de {prueba} {corrida} y encontre {len(objetivo)}. Revisa hoja_resultados.csv.")
    f = objetivo[0]
    f[i_odom], f[i_real], f[i_yaw] = f"{odom:g}", f"{real:g}", f"{yaw:g}"
    f[i_notas] = f"{corrida}; cierre_odom_cm={odom:g}; cierre_real_cm={real:g}; yaw_real_deg={yaw:g}" + (f"; {nota}" if nota else "")
    with open(HOJA, "w", newline="", encoding="utf-8") as g:
        csv.writer(g).writerows(filas)
    print(f"{prueba} {corrida}: odom {odom:g} cm | real {real:g} cm | yaw real {yaw:g} deg  (fila actualizada)")


if __name__ == "__main__":
    main(sys.argv)
