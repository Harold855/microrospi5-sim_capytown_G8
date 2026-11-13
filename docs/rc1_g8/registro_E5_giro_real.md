# RC-1 · Grupo 8 — Registro de las pruebas del giro de 90° en el robot real (E5)

Fecha: 12-nov-2026 (laboratorio, RosCar 4, `ROS_DOMAIN_ID=8`, hora de Perú). Este archivo es un registro **transcrito de la terminal** porque la mayoría de los CSV se sobrescribieron (ver «Datos perdidos»). Lo marcado `[por confirmar]` no estaba claro en lo que reportó el grupo.

## Estado de la sesión
- El reloj del Pi marcaba julio-2026; se corrigió con `timedatectl` (hora de Lima). Tras un corte de batería y reinicio, la hora se conservó.
- Calibración cargada en `odom_corrector` con `wheel_params:=/root/wheel_params_g8.yaml` (`wheel_radius` 0.03145, `wheel_separation` 0.2138; firmware 0.0325 / 0.24). Log de arranque: `r=0.0314 b_eff=0.2138 k_lin=0.9677 k_ang=1.0863`. `/odom` a ≈ 11.1 Hz (períodos 0.07–0.148 s). Batería 82 % antes de las corridas.
- El nodo del curso se modificó dentro del contenedor y se restauró: el hash de `cuadrado_controller.py` coincide con el del zip (`d618e717…`). Ninguna corrida registrada abajo se hizo con el nodo modificado.
- Descubierto: con `timeout -s INT` o Ctrl+C antes de `FIN`, el nodo no logra publicar la orden de frenado (`publisher's context is invalid`) y el robot real **conserva la última orden** (sigue girando). Se agregó `ros2 topic pub -r 10 -t 30 /cmd_vel ... "{}"` al final de cada comando.
- Las predicciones del 12-nov en `predicciones_E5.md` eran para `kp_yaw` 10, `kd_yaw` 0.6, `max_angular` 1.0. Para `kp_yaw` 1.0 **no hay predicción registrada aún**; las corridas con `kp_yaw` 1.0 son exploratorias.

## Corridas

| # | Condición | `kp_yaw` | Resultado | Archivo |
|---|---|---|---|---|
| A | Ruedas en el aire (sin carga) | 10 | No terminó (93.4 s, estado `GIRA`). Primer pico 105.1°; 106 cambios de signo de `e_yaw`; 7 % del tiempo dentro de ±2° | `csv/exp2_real_giro90_aire.csv` |
| B | Suelo, cinta de rumbo | 10 | No terminó (9.6 s, cortada). Primer pico 109.9° (+19.9°, 22 %); oscilación de ±15–20°, período ≈ 2.6 s; solo 4 % del tiempo dentro de ±2°. Al cortar `/odom` marcaba 72.4° y el robot siguió girando por la orden pegada | `csv/exp2_real_giro90_run1.csv` |
| C | Suelo, cinta de rumbo | 1.0 | `FIN`: yaw `/odom` 88.5°, 5.4 s. Físico ≈ 75° (el grupo reporta que las ruedas delanteras hicieron resistencia con el piso) | `csv/exp2_real_giro90_run2.csv` |

### Serie con `kp_yaw` 1.0 (mismo comando; todos con `FIN`)
Todas escribieron en el mismo archivo (`exp2_real_giro90_cal1.csv`); solo se conserva el de la última. Datos de la terminal:

| Corrida | Yaw `/odom` (°) | Tiempo (s) | Error de cierre (cm) |
|---|---|---|---|
| 1 | 89.2 | 6.7 | 0.3 |
| 2 | 88.1 | 6.1 | 0.3 |
| 3 | 89.6 | 6.6 | 0.5 |
| 4 | 88.6 | 7.0 | 0.2 |
| 5 | 88.5 | 6.1 | 0.3 |
| 6 | 88.6 | 6.3 | 0.4 |
| 7 | 88.2 | 8.7 | 0.3 |
| 8 | 88.6 | 5.0 | 0.1 |
| 9 | 89.4 | 5.2 | 0.1 |

Resumen de `/odom` en las 10 corridas con `kp_yaw` 1.0 (incluye la C): 88.1° a 89.6°, tiempo 5.0 a 8.7 s.

### Medidas con transportador (reportadas)
- Corrida C: ≈ 75°.
- Serie: una corrida dio 80° y «la última» 95° `[por confirmar a qué corrida corresponde cada una]`.
- Método usado: transportador sobre el robot, con dudas sobre la posición del centro. Dispersión observada: 75° a 95° con `/odom` ≈ constante (88–89°), mayor que la tolerancia de 3° de E5.
- Observaciones del grupo: las corridas sobre la cinta de rumbo parecían costarle girar (posible resistencia de la cinta en el círculo de las ruedas). En tres posiciones de suelo limpio, sin cinta, el robot giró «a simple vista» 90° (no medido). Las dos últimas corridas (5.0 y 5.2 s) fueron más rápidas que las anteriores (6.1–8.7 s).

## Datos perdidos / por hacer
- Se perdieron los CSV de las corridas 1 a 8 de la serie (sobrescritos). Quedan los `FIN` de la terminal.
- Falta una medida física fiable. Método propuesto: líneas de rumbo largas (≥ 40 cm) con regla, a ≥ 25 cm del centro del robot (fuera del círculo de las ruedas), ángulo medido en el cruce de las líneas por dos personas; o foto cenital. CSV de cada corrida con nombre distinto (`cal$N`).
- Con la media y la dispersión de ≥ 5 corridas se decide: calibrar `wheel_separation` con `b_nuevo = b_actual × θ_odom / θ_real` (si la dispersión es ≤ 3°), o buscar otra causa (patinaje no repetible).
- Predicciones nuevas para `kp_yaw` 1.0, antes de la corrida oficial de E5.

## 13-nov-2026 — serie con transportador circular (`kp_yaw` 1.0, mismas ganancias)
Tres corridas hechas **después** de subir las predicciones de `predicciones_E5_kp1.md` (commit `f9c8336`). Método: transportador circular con el robot colocado en el centro de un cuadrante del piso, ángulo leído al detenerse. Las tres escribieron en el mismo `csv/exp2_real_giro90_cal2.csv` (no se cambió `N`), así que solo se conserva el CSV de la tercera.

| Corrida | Yaw `/odom` (°) | Tiempo (s) | Error de cierre (cm) | Ángulo físico medido (°) | Error físico (°) |
|---|---|---|---|---|---|
| 1 | 88.5 | 6.1 | 0.4 | 85 | 5 |
| 2 | 89.2 | 5.8 | 0.2 | 90 | 0 |
| 3 | 88.5 | 6.3 | 0.2 | 87 | 3 |

Resumen: físico medio 87.3°, desviación estándar muestral ≈ 2.5° (error estándar de la media ≈ 1.5°). Cociente θ_odom/θ_real por corrida: 1.041, 0.991, 1.017 (media 1.016). Con esa dispersión la diferencia de la media respecto de 90° (≈ 2.7°) no es estadísticamente distinguible de cero con 3 corridas, y recalcular `wheel_separation` movería el valor solo ≈ 1.6 % (0.2138 → ≈ 0.217). Observación del grupo: el robot «se acomodó» solo hasta ajustarse a ≈ 90°.
Pendiente: decidir con el docente si E5 se evalúa por una corrida o por el promedio, y registrar las corridas oficiales con un CSV distinto por corrida.

## 13-nov-2026 — serie oficial de E5 (`kp_yaw` 1.0, `r1`, `r2`, `r3`) y contraste con las predicciones
CSV: `csv/exp2_real_giro90_r1.csv`, `_r2.csv`, `_r3.csv` (la corrida 1 se guardó primero como `cal2.csv` por un `N` olvidado y se copió a `r1`). Gráficas: `plots/exp2_real_giro90_r1.png`, `_r2.png`, `_r3.png`. Ángulo físico reportado por el grupo con transportador circular; la corrida 1 se anotó como «mal posicionado».

| Corrida | `FIN` (s) | Yaw `/odom` en `FIN` (°) | Pico de `/odom` (°) | Físico (°) | Error físico (°) |
|---|---|---|---|---|---|
| 1 | 6.10 | 89.0 | 89.0 | 83 (mal posicionado) | 7 |
| 2 | 6.50 | 88.2 | 88.2 | 93 | 3 |
| 3 | 5.60 | 88.5 | 88.5 | 91 | 1 |

Primer instante con `|e_yaw|` < 2°: 5.83, 6.23 y 5.33 s.

### Predicciones frente a lo medido (CSV)
1. **Asentamiento ≈ 6 s:** `FIN` a 6.10, 6.50 y 5.60 s. Se cumple.
2. **Sobreimpulso ≈ 1° (91° según `/odom`):** el máximo de `/odom` fue 89.0°, 88.2° y 88.5°; **no hay sobreimpulso** (la predicción de +1° no se cumple; el robot termina antes de 90°, en la banda de ±2° del nodo).
3. **Ángulo físico 75°–95°; E5 si 87°–93°:** las tres medidas caen en el rango (83°, 93°, 91°). Cumplen el criterio de ±3° la corrida 2 (93°, en el límite) y la 3 (91°); la 1 (83°) no.
4. **Comportamiento final:** `w` = 0.000 en `FIN` en las tres (se cumple). El criterio de «como máximo 2 inversiones de signo de `w` (|w| ≥ 0.05) en los 2 s previos a `FIN`» **no se cumple**: 5, 5 y 16 inversiones. Magnitud: la cola de la respuesta tiene órdenes pequeñas (|w| ≲ 0.25 rad/s; en r1 el robot queda ≈ 1 s con `e` ≈ 2.3° y `w` ≈ 0.04 rad/s, probablemente por debajo de la zona muerta de los motores) y el `FIN` ocurre a 1–2° del objetivo, en el borde de la tolerancia. Es el efecto de la derivada con `/odom` a ≈ 11 Hz.
Lectura de E5 pendiente de la respuesta del docente (una corrida, promedio o al menos una).

## 13-nov-2026 — criterio de E5 confirmado por el docente
El docente respondió que **las tres corridas deben cumplir** el error físico ≤ 3°. Con las dos series hechas con transportador: serie 1 (85°, 90°, 87°; errores 5°, 0°, 3°) y serie oficial (83°, 93°, 91°; errores 7°, 3°, 1°), **ninguna cumple**: en ambas hay una corrida fuera de ±3° (la 1 de la serie oficial fue anotada como «mal posicionado»; no se descarta). En la hoja queda `e_fin_deg=7` (la peor de las tres) en la fila vigente.
Con la desviación observada (≈ 3.8° en las seis corridas, media 88.2°) y bajo una aproximación normal, la probabilidad de que tres corridas consecutivas queden dentro de ±3° es del orden del 15 % por serie [estimación aproximada]. Para mejorar las probabilidades hay que reducir la dispersión (posicionamiento y lectura del ángulo con un montaje fijo) y el desvío medio (≈ −1.8°), no solo repetir.
