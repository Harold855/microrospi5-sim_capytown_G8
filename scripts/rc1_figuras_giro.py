#!/usr/bin/env python3
"""rc1_figuras_giro — figuras del Experimento 2 (giro de 90°) para el informe. Solo lectura de la hoja y los CSV.

Genera dos PNG en plots/:

  prediccion_giro_reconstruida.png
      Croquis de yaw(t) de 2a, 2b y 2c RECONSTRUIDO a partir del texto de las predicciones que el grupo escribió y subió
      el 11-nov-2026 a las 10:31 (hoja de resultados, commit 73be6f9). NO es una predicción nueva. Las cajas amarillas
      (rango de sobreimpulso y de tiempo de asentamiento) son los números escritos por el grupo; la curva punteada es solo un
      esquema ilustrativo dentro de esos rangos y sus parámetros no son valores predichos.

  giro_prediccion_vs_medicion.png
      Las curvas MEDIDAS (csv/exp2*_sim.csv) sobre las mismas cajas de predicción, para las seis pruebas.

Requiere matplotlib y numpy.   Uso:  python3 scripts/rc1_figuras_giro.py
"""
import csv
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLOTS = os.path.join(RAIZ, "plots")

# Rangos ESCRITOS por el grupo en la hoja (sobreimpulso en % de 90°; asentamiento en s). Ver predicciones en hoja_resultados.csv.
#   clave: (rango de sobreimpulso, rango de asentamiento, texto de la prediccion)
PRED = {
    "2a":  ((0.0, 5.0),   (2.0, None), "sobreimpulso < 5 %; asentamiento > 2 s"),
    "2b":  ((10.0, 25.0), (3.0, None), "sobreimpulso 10-25 %; >= 2 cruces; asentamiento > 3 s"),
    "2c":  ((0.0, 5.0),   (0.0, 3.0),  "sobreimpulso < 5 %; asentamiento <= 3 s"),
    "2p1": ((1.0, 3.5),   (1.15, 1.35), "sobreimpulso 1-3.5 %; asentamiento 1.15-1.35 s"),
    "2p2": ((0.0, 1.0),   (1.40, 2.00), "sobreimpulso 0-1 %; asentamiento 1.40-2.00 s"),
    "2p3": ((0.0, 3.0),   (1.60, 2.60), "sobreimpulso 0-3 %; asentamiento 1.60-2.60 s"),
}
GAN = {"2a": "kp 1 / kd 0", "2b": "kp 10 / kd 0", "2c": "kp 10 / kd 1.2",
       "2p1": "kp 10 / kd 0.6", "2p2": "kp 10 / kd 2.0", "2p3": "kp 5 / kd 0"}


def segunda_orden(t, sobre_pct, t_as):
    """Esquema ilustrativo: respuesta de segundo orden con el sobreimpulso y el asentamiento (2 %) dados."""
    so = max(sobre_pct, 0.01) / 100.0
    zeta = -math.log(so) / math.sqrt(math.pi ** 2 + math.log(so) ** 2)
    wn = 4.0 / (zeta * t_as)
    wd = wn * math.sqrt(1 - zeta ** 2)
    return 90.0 * (1 - np.exp(-zeta * wn * t) * (np.cos(wd * t) + zeta / math.sqrt(1 - zeta ** 2) * np.sin(wd * t)))


def cajas(ax, p, tmax):
    (so_lo, so_hi), (t_lo, t_hi) = PRED[p][0], PRED[p][1]
    ax.axhspan(90 * (1 + so_lo / 100), 90 * (1 + so_hi / 100), color="#F4B400", alpha=0.25, label="sobreimpulso predicho")
    ax.axvspan(t_lo, t_hi if t_hi is not None else tmax, color="#0277BD", alpha=0.10, label="asentamiento predicho")
    ax.axhline(90, color="gray", ls="--", lw=1)
    ax.axhspan(88, 92, color="green", alpha=0.07)


def medido(nombre):
    ruta = os.path.join(RAIZ, "csv", f"{nombre}.csv")
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = [r for r in csv.DictReader(f)]
    g = [r for r in filas if r["estado"] == "GIRA"]
    y0 = float(g[0]["yaw"])
    t0 = float(g[0]["t"])
    return ([float(r["t"]) - t0 for r in g], [math.degrees(float(r["yaw"]) - y0) for r in g])


def fig_reconstruida():
    ilustr = {"2a": (2.5, 2.5), "2b": (17.5, 3.5), "2c": (2.5, 2.5)}   # (sobreimpulso %, asentamiento s) dentro del rango escrito
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.9), sharey=True)
    tmax = 5.0
    for ax, p in zip(axs, ("2a", "2b", "2c")):
        cajas(ax, p, tmax)
        t = np.linspace(0, tmax, 400)
        so, ta = ilustr[p]
        if p == "2a":      # P sola, sin sobreimpulso apreciable: exponencial
            ax.plot(t, 90 * (1 - np.exp(-t * math.log(45) / ta)), "k:", lw=2, label="esquema ilustrativo")
        else:
            ax.plot(t, segunda_orden(t, so, ta), "k:", lw=2, label="esquema ilustrativo")
        ax.set_title(f"{p} ({GAN[p]})\n{PRED[p][2]}", fontsize=9)
        ax.set_xlabel("tiempo (s)")
        ax.set_xlim(0, tmax)
        ax.set_ylim(0, 118)
        ax.grid(alpha=0.3)
    axs[0].set_ylabel("yaw (°)")
    axs[0].legend(fontsize=7, loc="lower right")
    fig.suptitle("Predicción de yaw(t) RECONSTRUIDA desde el texto escrito el 11-nov-2026 10:31 (no es una predicción nueva)\n"
                 "cajas = rangos escritos por el grupo; curva punteada = esquema ilustrativo, sus parámetros no son valores predichos",
                 fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(os.path.join(PLOTS, "prediccion_giro_reconstruida.png"), dpi=150)
    plt.close(fig)


def fig_comparacion():
    fig, axs = plt.subplots(2, 3, figsize=(13, 7), sharey=True)
    tmax = 5.0
    for ax, p in zip(axs.flat, ("2a", "2b", "2c", "2p1", "2p2", "2p3")):
        cajas(ax, p, tmax)
        t, y = medido(f"exp{p}_sim")
        ax.plot(t, y, color="#0B7A43", lw=2, label="medido (/odom)")
        ax.set_title(f"{p} ({GAN[p]})\npredicción: {PRED[p][2]}", fontsize=8.5)
        ax.set_xlim(0, tmax)
        ax.set_ylim(0, 118)
        ax.grid(alpha=0.3)
        if p in ("2p1", "2p2", "2p3", "2a", "2b", "2c"):
            ax.set_xlabel("tiempo (s)")
    for ax in axs[:, 0]:
        ax.set_ylabel("yaw (°)")
    axs[0, 0].legend(fontsize=7, loc="lower right")
    fig.suptitle("Experimento 2 — predicción (cajas) frente a lo medido (curva verde). Banda verde clara: ±2° alrededor de 90°", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(PLOTS, "giro_prediccion_vs_medicion.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(PLOTS, exist_ok=True)
    fig_reconstruida()
    fig_comparacion()
    print("plots/prediccion_giro_reconstruida.png")
    print("plots/giro_prediccion_vs_medicion.png")
