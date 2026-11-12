# RC-1 · Grupo 8 _ Roscar 4 — Tablas del simulador (Experimentos 1 y 2)

> Las tablas del Experimento 3 (Parte D) están en `docs/rc1_g8/tablas_parteD.md`.

Material para el informe y para el requisito de E2 y E3. Las tablas de medidas se generan con
`python3 scripts/rc1_tablas.py` a partir de `hoja_resultados.csv` y de `csv/*.csv`.
Todas las corridas son en la arena `arena_rc1` con `noise:=low`, una prueba a la vez y con el nodo del curso sin modificar.

## 1. Medidas

### Experimento 1 — corregir una línea (recta de 2 m, `noise:=low`)

| Prueba | Control | Kp / Ki / Kd | \|e\| medio (cm) | \|e\| máx (cm) | e mín (cm) | Cruces de la línea | Asentamiento ±2 cm | Error final (cm) |
|---|---|---|---|---|---|---|---|---|
| 1A | bang-bang | — | 6.27 | 11.27 | -6.52 | 3 | no se asienta | 1.92 |
| 1B | solo P | 3.0 / 0.0 / 0.0 | 6.03 | 10.69 | -6.35 | 2 | no se asienta | 1.65 |
| 1C | P + D | 3.0 / 0.0 / 4.0 | 3.10 | 10.00 | 0.89 | 0 | no se asienta | 2.14 |
| 1D | PID | 3.0 / 0.5 / 4.0 | 2.53 | 10.00 | -2.19 | 1 | 5.80 s | 0.30 |

Notas: En las pruebas 1A, 1B y 1C no se alcanzó un asentamiento sostenido dentro de la banda de ±2 cm. Aunque 1A y 1B registraron errores finales inferiores a 2 cm, estos corresponden únicamente al último instante de la corrida y no demuestran estabilidad. La prueba 1D sí alcanzó el asentamiento, con 5.80 s y un error final de 0.30 cm, cumpliendo el criterio E2.

### Experimento 2 — giro de 90° en sitio (`noise:=low`)

| Prueba | kp_yaw | ki_yaw | kd_yaw | Sobreimpulso (%) | Asentamiento ±2° (s) | Error final (°) | Cruces de 90° | \|ω\| máx (rad/s) |
|---|---|---|---|---|---|---|---|---|
| 2a | 1.0 | 0.0 | 0.0 | 0.00 | 3.83 | 1.41 | 0 | 1.57 |
| 2b | 10.0 | 0.0 | 0.0 | 4.32 | 1.20 | 0.03 | 1 | 2.00 |
| 2c | 10.0 | 0.0 | 1.2 | 0.00 | 1.34 | 0.15 | 0 | 2.00 |
| 2p1 | 10.0 | 0.0 | 0.6 | 0.00 | 1.01 | 0.22 | 0 | 2.00 |
| 2p2 | 10.0 | 0.0 | 2.0 | 0.00 | 1.27 | 0.53 | 0 | 2.00 |
| 2p3 | 5.0 | 0.0 | 0.0 | 0.00 | 1.13 | 0.30 | 0 | 2.00 |

**Ganancias seleccionadas para el giro:** Kp_yaw = 10.0, Ki_yaw = 0.0 y Kd_yaw = 0.6, correspondientes a la prueba 2p1. Esta configuración obtuvo 0 % de sobreimpulso, 1.01 s de asentamiento y 0.22° de error final. La denominación 2p identifica la selección y no representa una corrida adicional.
Meta de E3: una combinación propia con sobreimpulso ≤ 10 % y asentamiento ≤ 3 s.

## 2. Predicción contra medición

Las predicciones están en `hoja_resultados.csv` y en `docs/rc1_g8/predicciones_rc1.md`.

### Experimento 1 (recta)

| Prueba | Predijeron | Se midió | ¿Se cumplió? |
|---|---|---|---|
| 1A | Zigzag persistente que cruza la línea y no se asienta (texto escrito **después** de una corrida exploratoria) | 3 cruces, amplitud que no decrece (máx. 11.27 cm), no se asienta | Sí (predicción no ciega) |
| 1B | Oscilación alrededor de un equilibrio desplazado por el sesgo; al menos 2 cruces | 2 cruces; centro de la oscilación ≈ +2.17 cm | Sí |
| 1C | Oscilación que disminuye, con un error residual de ≈ 2 cm | 0 cruces; el error converge a ≈ 2.1 cm | Sí |
| 1D | Reducir el residuo y terminar a menos de 2 cm | Error final 0.30 cm | Sí |

Referencia (`SIMULACION.md`) para la 1D: `|e|` medio 2.56 cm, asentamiento 5.75 s, error final 0.49 cm. Medido: 2.53 cm, 5.80 s, 0.30 cm.

### Experimento 2 (giro de 90°)

| Prueba | Predijeron | Se midió | ¿Logró cumplir? |
|---|---|---|---|
| 2a | Sobreimpulso < 5 %; asentamiento > 2 s | 0.00 %; 3.83 s | Sí |
| 2b | Satura a 2 rad/s; sobreimpulso 10–25 %; ≥ 2 cruces de 90°; asentamiento > 3 s | Satura a 2.00 rad/s (sí); 4.32 % (no); 1 cruce (no); 1.20 s (no) | Solo la saturación |
| 2c | Satura a 2 rad/s; sobreimpulso < 5 %; asentamiento ≤ 3 s | 2.00 rad/s; 0.00 %; 1.34 s | Sí |
| 2p1 | Sobreimpulso 1–3.5 %; asentamiento 1.15–1.35 s | 0.00 % (por debajo del rango); 1.01 s (más rápido) | No |
| 2p2 | Sobreimpulso 0–1 %; asentamiento 1.40–2.00 s | 0.00 % (sí); 1.27 s (más rápido) | Solo el sobreimpulso |
| 2p3 | Sobreimpulso 0–3 %; asentamiento 1.60–2.60 s | 0.00 % (sí); 1.13 s (más rápido) | Solo el sobreimpulso |

**Patrón:** En cuatro de las seis pruebas del giro (2b, 2p1, 2p2 y 2p3), el tiempo de asentamiento fue inferior al esperado. En 2a y 2c se cumplieron los rangos o límites previstos. Estos resultados muestran que las respuestas del simulador fueron más rápidas de lo anticipado en varias configuraciones.

## 3. Figuras del giro (Experimento 2)

- `plots/prediccion_giro_reconstruida.png` — **croquis de yaw(t) de 2a, 2b y 2c reconstruido** desde el texto de las predicciones.
  Lo pide la Parte C del reto («dibujar la predicción de yaw(t)»). Se hizo **después** de medir, y la figura lo dice en su título,
  las cajas (rangos de sobreimpulso y de asentamiento) son los números que el grupo, la curva punteada es solo un
  esquema ilustrativo dentro de esos rangos, con parámetros elegidos para dibujarla, **no valores predichos** ni es una predicción nueva.
- `plots/giro_prediccion_vs_medicion.png` — las seis pruebas con la curva medida (verde) sobre las cajas de la predicción.
  Se ve, por ejemplo, que en la 2b la curva medida queda por debajo de la caja de sobreimpulso, y que en 2p1, 2p2 y 2p3 llega a ±2° antes de lo predicho.
