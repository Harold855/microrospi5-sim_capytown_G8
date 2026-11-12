# RC-1 · Grupo 8 · RosCar 4 — Tablas de la Parte D (Experimento 3: cuadrado de 2 x 2 m en el simulador)

Generado con `python3 scripts/rc1_tablas.py` (sección «Experimento 3») a partir de `hoja_resultados.csv` y `csv/exp3*_sim_*.csv`.
Arena `arena_rc1`, nodo del curso sin modificar, una prueba a la vez. 3 corridas con `noise:=low` y 1 con `noise:=medium` por prueba (12 en total).
Ninguna corrida tocó una pared: las 12 terminaron.
Gráficas: `plots/exp3{a,b,c}_sim_{run1,run2,run3,medium}.png` (nodo) y `plots/exp3{a,b,c}_sim_cinta_*.png` (pose real). Falta el CSV de la cinta de 3A run2 (se sobrescribió por error de nombre; se conservan su gráfica y sus valores en la hoja).

Cierre «`/odom`» = lo que cree el robot (y lo que imprime el nodo); cierre «real» = distancia a la marca de inicio según `/sim/pose` (`cierre_real.py`). `\|e\|` medio = error lateral medio en las rectas, calculado de `csv/exp3*_sim_*.csv`.

| Prueba | Corrida | Ruido | Cierre `/odom` (cm) | Cierre real (cm) | Yaw real (°) | Yaw `/odom` (°) | \|e\| medio rectas (cm) | Tiempo (s) |
|---|---|---|---|---|---|---|---|---|
| 3A | run1 | low | 8.9 | 10.8 | 360.5 | 361.6 | 1.19 | 47.9 |
| 3A | run2 | low | 1.6 | 12.8 | 342.9 | 357.4 | 1.19 | 47.9 |
| 3A | run3 | low | 3.2 | 24.6 | 356.5 | 359.7 | 0.76 | 47.9 |
| 3A | medium | medium | 10.2 | 24.8 | 345 | 361.6 | 2.03 | 47.9 |
| 3B | run1 | low | 0.3 | 37.3 | 373.7 | 359.9 | 0.87 | 45.6 |
| 3B | run2 | low | 0.3 | 88.7 | 328.8 | 360.0 | 0.90 | 45.9 |
| 3B | run3 | low | 1 | 50 | 351.3 | 360.3 | 0.87 | 45.5 |
| 3B | medium | medium | 0.5 | 46 | 372.5 | 360.3 | 0.89 | 45.7 |
| 3C | run1 | low | 0.5 | 41.6 | 354.4 | 360.6 | 0.83 | 45.6 |
| 3C | run2 | low | 0.1 | 13.4 | 364 | 360.0 | 0.86 | 45.6 |
| 3C | run3 | low | 0.7 | 35.3 | 347.5 | 360.3 | 0.84 | 45.3 |
| 3C | medium | medium | 0.4 | 56.8 | 377.3 | 360.2 | 0.86 | 45.5 |

#### Resumen con `noise:=low` (3 corridas) y la corrida `medium`

| Prueba | Real low: corridas (cm) | Real low: media | Real low: mín–máx | `/odom` low: media | Real medium (cm) | Corridas low ≤ 40 cm |
|---|---|---|---|---|---|---|
| 3A lazo abierto | 10.8 / 12.8 / 24.6 | **16.1** | 10.8–24.6 | 4.6 | 24.8 | 3 de 3 |
| 3B PID sobre /odom | 37.3 / 88.7 / 50 | **58.7** | 37.3–88.7 | 0.5 | 46 | 1 de 3 |
| 3C PID + Ki | 41.6 / 13.4 / 35.3 | **30.1** | 13.4–41.6 | 0.4 | 56.8 | 2 de 3 |

#### Predicción contra medición (cierre `/odom` / cierre real, cm)

| Prueba | Corrida | Predijeron | Se midió | Diferencia real |
|---|---|---|---|---|
| 3A | low (las 3 corridas) | 25 / 35 | 1.6–8.9 / 10.8–24.6 | -24.2; -22.2; -10.4 |
| 3A | medium | 40 / 65 | 10.2 / 24.8 | -40.2 |
| 3B | low (las 3 corridas) | 5 / 20 | 0.3–1 / 37.3–88.7 | +17.3; +68.7; +30.0 |
| 3B | medium | 10 / 40 | 0.5 / 46 | +6.0 |
| 3C | low (las 3 corridas) | 8 / 24 | 0.1–0.7 / 13.4–41.6 | +17.6; -10.6; +11.3 |
| 3C | medium | 15 / 48 | 0.4 / 56.8 | +8.8 |

Meta de la rúbrica (E4): 3B o 3C con cierre real ≤ 40 cm. La redacción no aclara si es cada corrida, la media o al menos una; pendiente de confirmar con el docente.

| Lectura de E4 | 3B | 3C |
|---|---|---|
| Cada corrida low ≤ 40 cm | ✗ | ✗ |
| Media de las 3 low ≤ 40 cm | ✗ | ✓ |
| Al menos una corrida low ≤ 40 cm | ✓ | ✓ |

## Qué muestran las tablas

- **[Seguro]** Con el PID (3B y 3C) el robot cree que cierra a < 1 cm, pero el cierre real es de 13 a 89 cm. `/odom` no ve el empujón del piso, que gira al robot; el yaw real difiere del de `/odom` hasta 31° (3B run2: 328.8° contra 360.0°).
- **[Seguro]** En el simulador la 3A (lazo abierto) tuvo el mejor cierre real (media low 16.1 cm), mejor que la 3B (58.7) y la 3C (30.1). Eso es lo contrario de lo que se pide en el robot real (E7: 3B mejor que 3A). Aquí no hay derrape de ruedas, que es lo que degrada el lazo abierto en el robot.
- **[Seguro]** La 3C tuvo menos cierre real medio que la 3B (30.1 contra 58.7 cm). **[Especulando]** Se debe a Ki, pero 3B y 3C difieren también en `bias_w` (0.03 contra 0.05) y las corridas low de una misma prueba varían hasta 28 cm entre sí; con tres corridas no se puede atribuir la diferencia a Ki.
- **[Probable]** `noise:=medium` empeora algo el cierre real del PID (46.0 y 56.8 cm), pero con una corrida por nivel no se puede separar del ruido entre corridas: la 3B medium cae dentro del rango de sus corridas low y la 3C medium queda 15 cm por encima de su máximo.
- **E4:** pendiente de la respuesta del docente sobre si la meta de 40 cm es por corrida, por media o por al menos una. Solo la lectura «cada corrida» no se cumple.
- **Predicciones:** el cierre `/odom` se sobrestimó en las 3 pruebas (el PID cierra casi perfecto sobre su propia medida). El cierre real se subestimó en 3B (+17 a +69 cm en low) y se sobrestimó en 3A (−10 a −24 cm). No se modificaron.
