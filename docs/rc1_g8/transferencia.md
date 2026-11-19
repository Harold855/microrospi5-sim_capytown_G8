# RC-1 — Tabla de transferencia: simulador → robot real

Con las **mismas ganancias**: ¿qué dio el simulador y qué dio el robot? ¿Qué cambió y por qué? (Anexo A.3 del reto.)
La columna «Esperábamos» se escribió antes de la sesión de laboratorio (ver `informe.md`, apartado (d)); «Observado» y «Por qué» salen de los CSV y de las medidas con cinta y transportador.
Mientras exista el texto «[COMPLETAR]», `scripts/rc1_verificar.py` marca la tabla como pendiente: solo queda en las celdas de 3B del robot real, que se llenan con las tres corridas oficiales.

| Aspecto | Simulador | Robot real | Esperábamos | Observado | Por qué |
|---|---|---|---|---|---|
| Motores e inercia | solo límites de aceleración (`accel_lin`, `accel_ang`) | respuesta de motores e inercia | Un giro más lento y con retardo; las ganancias del simulador oscilarían | `kp_yaw` 10 oscila ±15–20° (T ≈ 2.6 s); con `kp_yaw` 1.0, `FIN` en 5.0–8.7 s frente a 1.01 s del simulador | Retardo efectivo ≈ 0.5–0.65 s de motores y `/odom` (estimado del período de la oscilación); el simulador no lo modela |
| Derrape de las 4 ruedas (χ) | no existe | `b_eff = χ·b` | Giros reales distintos de los que dice `/odom` | 3A: primera esquina ≈ 115° en lugar de 90°. En 3B, el giro físico se pasaba 10–15° en varias esquinas mientras `/odom` marcaba ≈ 90° | El derrape no lo ve `/odom`, que integra las velocidades de las ruedas; el lazo del giro cierra sobre esa medida |
| Retardo de `/odom` | ≈ 0 | hay retardo; además ≈ 11 Hz medidos en el RC-0 frente a 50 Hz del simulador | Vibración de ω por la derivada (chatter) | ω con dientes de sierra al final de los giros: 74 muestras con ω < −0.2 con `kd_yaw` 0.6 frente a 7 con 0.3 | El nodo controla a 30 Hz sobre una pose que cambia cada ≈ 0.09 s: la derivada da picos en cada muestra nueva y cero en las repetidas |
| Sesgo de motores | inyectado con `bias_w` | existe de verdad | Una deriva constante que Ki tendría que corregir | Con Kp 3 / Ki 0.5 la recta oscila (campanas de ≈ 30 cm); con Kp 1.0 / Ki 0.1 / Kd 8.0 el desvío final fue de 0.5–1.5 cm (E6) | Con retardo ≈ 0.7 s, Ki alto desestabiliza y Kd alto amortigua; `/odom` marca ≈ 3 cm más que la cinta (desfase sistemático) |
| Error de `/odom` | aleatorio por muestra + empuje del piso que no ve | sistemático (`r`, `b_eff`) | Un sesgo por `r` y `b_eff` mal calibrados | Con `r` 0.03145 y `b_eff` 0.2138 no hubo sesgo sistemático en el giro (88.1° ± 3.5°). En 3B `/odom` cierra a 2–4 cm y la cinta mide 19–36 cm (exploratorias) | Lo que domina es el derrape, no la calibración; el nodo vuelve a anclar cada lado en la posición de `/odom` (`core_cuadrado.py`, línea 213), sin referencia física del cuadrado |
| Verdad terreno | `/sim/pose` | cinta métrica y transportador | – | – | – |

## Resultados lado a lado

Cierres en cm. Simulador: media de las 3 corridas con `noise:=low`.

| Prueba | Ganancias | Sim: cierre `/odom` | Sim: cierre REAL | Robot: cierre `/odom` | Robot: cierre cinta |
|---|---|---|---|---|---|
| 3A | – (lazo abierto) | 4.6 | 16.1 | 97.4 | 107.9 |
| 3B | Sim: Kp 3, Ki 0, Kd 4; `kp_yaw` 10, `kd_yaw` 0.6 · Real: Kp 1.0, Ki 0.1, Kd 8.0; `kp_yaw` 1.0, `kd_yaw` 0.3 | 0.5 | 58.7 | [COMPLETAR] (exploratorias: 1.8–3.7) | [COMPLETAR] (exploratorias: 19–36) |
| 3C | Sim: Kp 3, Ki 0.5, Kd 4; `kp_yaw` 10, `kd_yaw` 0.6 | 0.4 | 30.1 | – | – |

**Lectura.** En el simulador y en el robot real el PID de 3B cierra el lazo sobre `/odom` y cree cerrar a unos pocos centímetros; la diferencia con lo real es de decenas de centímetros. El lazo abierto (3A) cerró mejor que el PID en el simulador (16.1 frente a 58.7 cm) y peor en el robot real (107.9 cm), porque el giro por tiempo se pasa en el piso real.
