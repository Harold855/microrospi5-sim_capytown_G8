# RC-1 · Grupo 8 — Estructura de las Partes E y F (robot real, RosCar 4)

Plantilla para llenar durante el laboratorio. Las celdas `[ ]` se completan con lo medido; **no** se llenan antes. Parte E: 90 min con el robot. Parte F: resto de la sesión (evidencia y comparación).
Reglas: un parámetro por prueba, máximo **3 re-sintonías** (cada una anotada), predicción escrita **antes** de cada prueba, el nodo del curso sin modificar, una persona con la mano en Ctrl+C y otra lista para tomar el robot (Anexo C del reto: leerlo antes de encender nada).

## Antes del laboratorio (en casa)

- [ ] Fijar las ganancias del simulador en `config/rc1_pid.yaml` (bloque `simulador`) y marcar el bloque `robot_real` con `linear_speed 0.10` y `max_angular 1.0`.
- [ ] Corregir `wheel_params.yaml` del RC-0 (`r = 0.03145`, `b_eff = 0.2138`).
- [ ] Escribir las predicciones de las pruebas reales (E5, E6, E7) y subirlas con git; no se cambian después.
- [ ] Imprimir o tener a mano: cinta métrica, cinta adhesiva (marca de inicio con cruz y rumbo), transportador, 2 × 2 m libres más 15 cm de margen.
- [ ] Confirmar con el docente: lectura de la meta E4, fecha límite y si se usa `/odom` o `/odom_raw`.

## Parte E — Robot real

### E.0 Puesta en marcha

| Paso | Comando o acción | Resultado |
|---|---|---|
| Encender y esperar ≈ 30 s; entrar por SSH a la Pi5 | `export ROS_DOMAIN_ID=8` | [ ] |
| Bringup | `ros2 launch capytown_esan bringup.launch.py` | [ ] |
| `/odom` llega y cambia al mover el robot a mano | `ros2 topic hz /odom` ; `ros2 topic echo /odom --once` | frecuencia: [ ] Hz |
| ¿Hay EKF? | `ros2 node list \| grep -i ekf` | [ ] (si no hay, usar `/odom` y anotarlo; `-p odom_topic:=/odom_raw` solo si el docente lo pide) |
| Primera prueba con las ruedas en el aire (ω > 0 gira a la izquierda) | – | [ ] |
| Marca de inicio en el piso | cruz y rumbo con cinta | [ ] |

### E.1 Giro de 90° (rúbrica E5, 2 pt; meta: error final ≤ 3° con transportador)

```bash
python3 scripts_pdi/cuadrado_controller.py --ros-args $(python3 scripts/rc1_args.py robot_real experimento=giro90 log_csv=csv/exp2_real_giro90.csv)
```

| Corrida | Ganancias (kp_yaw / ki_yaw / kd_yaw) | `linear_speed` / `max_angular` | Predicción (asentamiento, error final) | Medido: asentamiento (s) | Medido: error final (°, transportador) |
|---|---|---|---|---|---|
| giro90 | [ ] | 0.10 / 1.0 | [ ] | [ ] | [ ] |

Hoja: fila `2`, planta `real`, con `e_fin_deg=` en `notas`.

### E.2 Recta con línea (rúbrica E6, 2 pt; meta: desvío lateral final ≤ 5 cm con cinta en las 3 corridas)

Sin `bias_w`: el robot real ya trae su propio sesgo. Línea a 10 cm.

```bash
python3 scripts_pdi/cuadrado_controller.py --ros-args $(python3 scripts/rc1_args.py robot_real experimento=recta line_offset=0.10 log_csv=csv/exp1d_real_run1.csv)
```

(corridas 2 y 3: cambiar `run1` por `run2` y `run3`)

| Corrida | Ganancias (Kp / Ki / Kd) | Predicción (desvío, cm) | Desvío lateral final (cm, cinta) |
|---|---|---|---|
| run1 | [ ] | [ ] | [ ] |
| run2 | [ ] | [ ] | [ ] |
| run3 | [ ] | [ ] | [ ] |

Hoja: tres filas `1D`, planta `real`, con `desvio_cm=` en `notas`.

### E.3 Cuadrado de 2 × 2 m (rúbrica E7, 4 pt; meta: media de 3B ≤ 25 cm y menor que 3A)

Antes de cada corrida: marca de inicio, robot alineado, y empezar el bag.

```bash
ros2 bag record /odom /cmd_vel /tf -o bags/rc1_real_3a            # 3A: una vez
python3 scripts_pdi/cuadrado_controller.py --ros-args $(python3 scripts/rc1_args.py robot_real experimento=cuadrado_abierto log_csv=csv/exp3a_real.csv)

ros2 bag record /odom /cmd_vel /tf -o bags/rc1_real_3b_run1       # 3B: tres veces (run1, run2, run3)
python3 scripts_pdi/cuadrado_controller.py --ros-args $(python3 scripts/rc1_args.py robot_real experimento=cuadrado log_csv=csv/exp3b_real_run1.csv)
```

| Prueba | Corrida | Predicción: cierre `/odom` / cinta (cm) | Cierre `/odom` (nodo, cm) | Cierre real con cinta (cm) | Ángulo final (°, transportador) | Bag |
|---|---|---|---|---|---|---|
| 3A | única | [ ] | [ ] | [ ] | [ ] | `bags/rc1_real_3a` |
| 3B | run1 | [ ] | [ ] | [ ] | [ ] | `bags/rc1_real_3b_run1` |
| 3B | run2 | [ ] | [ ] | [ ] | [ ] | `bags/rc1_real_3b_run2` |
| 3B | run3 | [ ] | [ ] | [ ] | [ ] | `bags/rc1_real_3b_run3` |
| **Media 3B** | | | | **[ ]** (meta ≤ 25 y < 3A) | | |

Hoja: filas `3A` y `3B`, planta `real`, con `cierre_real_cm` y `yaw_acum_deg`.

### E.4 Re-sintonías (máximo 3, un parámetro por cambio)

| N.º | Prueba | Parámetro | Antes → después | Motivo (lo observado) | Resultado |
|---|---|---|---|---|---|
| 1 | [ ] | [ ] | [ ] | [ ] | [ ] |
| 2 | [ ] | [ ] | [ ] | [ ] | [ ] |
| 3 | [ ] | [ ] | [ ] | [ ] | [ ] |

### Bonus (+2 puntos, opcional)

Demostración frente al docente, sin recalibrar: 3B con cierre ≤ 10 cm, más 3A para comparar. [ ] Hecha  [ ] No se intentó

## Parte F — Evidencia y comparación

| Entregable | Estado |
|---|---|
| `09_plot_csv.py` sobre cada CSV real (un PNG por prueba, en `plots/`) | [ ] |
| `cierre_real.py --png` de las corridas del simulador (24 PNG de `exp3*` ya en `plots/`) | hecho |
| `hoja_resultados.csv` completo (columnas del Anexo E, filas reales incluidas) | [ ] |
| Tabla de transferencia (`docs/rc1_g8/transferencia.md`) | [ ] |
| `informe.pdf` (1 página; `informe.md` ya tiene las celdas `[ ]` del robot real) | [ ] |
| `config/rc1_pid.yaml` con las ganancias finales, en dos bloques | [ ] |
| `bags/rc1_real_3a/` y `bags/rc1_real_3b_run1..3/` | [ ] |
| `sim_log.txt` y captura de `rqt_graph` | hecho |
| `README.md`: integrantes, rol, `ROS_DOMAIN_ID`, nivel de ruido y ganancias finales | [ ] |
| Repositorio `capytown_G<n>` con el tag `v1.0-rc1` (confirmar el nombre con el docente) | [ ] |

### Tabla de transferencia (mismas ganancias, simulador contra robot)

Se completa en `docs/rc1_g8/transferencia.md`: por cada aspecto (motores e inercia, derrape de las 4 ruedas, retardo y frecuencia de `/odom`, sesgo de motores, error de `/odom`), lo esperado, lo observado y por qué.

### Cómo se actualiza el informe después del laboratorio

1. Reemplazar las celdas `[ ]` de `informe.md` con los valores de arriba.
2. Redactar (d) y (e) con la tabla de transferencia.
3. Regenerar el PDF con `scripts/rc1_informe_pdf.sh` (necesita `pandoc` y `playwright`); comprobar que sigue en **una página**.
