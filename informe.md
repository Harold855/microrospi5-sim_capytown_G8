# RC-1 — Control PID: del simulador al robot real

**Grupo 8 · S-003** · Integrantes: [COMPLETAR] · RosCar 4 · `ROS_DOMAIN_ID=8` · ganancias finales: `config/rc1_pid.yaml` · evidencia: `csv/`, `plots/`, `bags/`, `hoja_resultados.csv` y `docs/rc1_g8/`

## (a) Predicción frente a medición

| Prueba | Predijimos | Medimos | ¿Se cumplió? |
|---|---|---|---|
| Recta en el simulador, solo P | Cruza la línea varias veces; Kd amortigua | 2 cruces; con Kd, 0; con Ki, error final 0.3 cm | Sí |
| Cuadrado PID en el simulador | Cierre `/odom` 5 cm, real 20 cm | `/odom` 0.3–1 cm, real 37–89 cm | Dirección sí; el real fue peor |
| Giro en el robot real con las ganancias del simulador | Más lento (motores, `/odom` a 11 Hz) | Oscila ±15–20°; con `kp_yaw` 1.0 llega a `FIN` en 5–9 s | Sí |
| E6: recta real | Oscila, ≈ 13 cm | Oscila (≈ 30 cm); con las ganancias finales, 0.5–1.5 cm | Sí |
| E7-3A: lazo abierto | ≈ 75 cm | 107.9 cm | Parcial |
| E7-3B: PID sobre `/odom` | Media ≈ 27 cm (18–38) | **17.7 cm** (ver nota) | Parcial: cumple ≤ 25 cm; una corrida bajo el rango |

## (b) Hoja de resultados (`hoja_resultados.csv`)

| Prueba | Simulador | Robot real |
|---|---|---|
| Recta, PID | Kp 3, Ki 0.5, Kd 4: error final **0.30 cm** | Kp 1.0, Ki 0.1, Kd 8.0: desvío con cinta **0.6 / 1.5 / 0.5 cm** (meta ≤ 5) |
| Giro de 90° | `kp_yaw` 10, `kd_yaw` 0.6: sobreimpulso 0 %, 1.01 s | `kp_yaw` 1.0: error físico **1°** (meta ≤ 3°) |

## (c) Cierre `/odom` frente a real: cuadrado de 2 × 2 m (cm)

| Prueba | Sim `/odom` | Sim real | Robot `/odom` | Robot cinta |
|---|---|---|---|---|
| 3A lazo abierto | 4.6 | 16.1 | 97.4 | **107.9** |
| 3B PID sobre `/odom` | 0.5 | 58.7 | 1.9 | **17.7** |
| 3C PID + Ki | 0.4 | 30.1 | – | – |

<img class="fig" src="plots/exp3c_sim_cinta_run2.png" alt="Odometría frente a pose real, 3C run 2">

**Nota sobre 3B.** El 19-nov se hicieron 10 intentos: 1 cortada, 6 sobre baldosas de caucho con uniones que actuaban como baches (34–100 cm; una con interferencia de otro robot) y 3 sobre el piso del laboratorio, con un cuadrado de 2 × 2 m como referencia (10.0 / 16.0 / 27.0 cm). Las 3 del laboratorio son las **oficiales** (`run1`–`run3`), porque la demostración en vivo será en ese piso; las del caucho se catalogan como error por tipo de suelo y se conservan en `csv/` y la hoja. Antes hubo 5 exploratorias en el laboratorio (19–36 cm); las 7 medidas sobre cerámica promedian 24.4 cm.

## (d) Por qué cambió el comportamiento al pasar al robot

- **Motores y retardo:** con `kp_yaw` 10 el giro oscila ±15–20° (T ≈ 2.6 s). El retardo efectivo de motores y `/odom` es de ≈ 0.5–0.65 s y el simulador no lo modela. Con `kp_yaw` 1.0 el giro llega a `FIN` en 5.0–8.7 s, frente a 1.01 s en el simulador. `/odom` llega a ≈ 11 Hz, no a 50.
- **Derivada:** el nodo controla a 30 Hz sobre una pose que cambia cada ≈ 0.09 s y `kd_yaw` da picos en cada muestra nueva: 74 muestras con ω < −0.2 rad/s con 0.6 y 7 con 0.3. Por eso 3B usa 0.3 y E5 se acreditó con 0.6.
- **Recta:** con Kp 3 / Ki 0.5 oscila (≈ 30 cm; con retardo ≈ 0.7 s un Ki alto desestabiliza); con Kp 1.0 / Ki 0.1 / Kd 8.0, el desvío fue de 0.5–1.5 cm.
- **`/odom` no ve el derrape** (la calibración `r` 0.03145 y `b_eff` 0.2138 no dejó sesgo: 88.1° ± 3.5°): su cierre es de ≈ 2 cm y el real, de decenas. En 3A la primera esquina giró ≈ 115° en lugar de 90°, y en 3B el giro físico se pasaba 10–15° en varias esquinas mientras `/odom` marcaba ≈ 90°. El nodo vuelve a anclar cada lado en la posición de `/odom` (`core_cuadrado.py`, línea 213), sin referencia física del cuadrado.
- **El piso importa:** sobre caucho con uniones el cierre fue de 34–100 cm (las uniones atascaban las ruedas); sobre la cerámica del laboratorio, de 10–36 cm.
- **Seguridad:** el robot conserva la última orden si el nodo muere; se usa `timeout --foreground`.
- **Transparencia:** las ganancias finales cambian cinco parámetros (máximo tres; consulta pendiente al docente) y se guardaron todas las exploratorias.
- **RC-2:** giroscopio (`/imu`) para el giro y referencia física para el cuadrado.
