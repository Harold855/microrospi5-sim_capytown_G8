# RC-1 · Grupo 8 — matriz de pruebas

Reglas del reto: **un parámetro por prueba**, predicción escrita **antes** de correr, orden de sintonía **Kp → Kd → Ki**, decimales con punto (`kd:=0.0`).
Las banderas `-p` salen de `config/rc1_pid.yaml`: `python3 scripts/rc1_args.py <simulador|robot_real> clave=valor ...`.
Todo se ejecuta **desde la raíz del repo**. El nodo del curso (`cuadrado_controller.py` y `core_cuadrado.py`) va en `scripts_pdi/`, que git ignora (material del docente, **no** se versiona; ver README):
`python3 scripts_pdi/cuadrado_controller.py --ros-args $(python3 scripts/rc1_args.py simulador experimento=recta ...)`. Al lanzar el script por su ruta, Python busca `core_cuadrado` junto a él, así que no hace falta `cd`.

> Nombres de archivo: el PDF da ejemplos (`exp3b_real.csv`) que chocan entre el «real» del simulador (`/sim/pose`) y el robot real.
> Aquí se separan: `*_sim*` (nodo en el simulador), `*_sim_cinta_*` (`cierre_real.py`, pose real del simulador) y `*_real*` (RosCar 4).
> Confirmar con la cátedra que esta convención es aceptable.

## Simulador (Partes A–D, en casa, `noise:=low` salvo lo indicado)

```bash
ros2 launch yahboomcar_sim sim.launch.py world:=arena_rc1 start:=1.0,1.0,0.0 robot_radius:=0.14 noise:=low
ros2 service call /sim/reset std_srvs/srv/Empty      # entre pruebas, y reiniciar también el nodo
```

| Prueba | Qué cambia (solo esto) | Parámetros extra al nodo | CSV | Umbral (rúbrica) |
|---|---|---|---|---|
| 1A bang-bang | `controlador:=bangbang` | `experimento:=recta line_offset:=0.10 bias_w:=0.06` | `csv/exp1a_sim.csv` | – |
| 1B solo P | `kd:=0.0` | idem | `csv/exp1b_sim.csv` | – |
| 1C P+D | Kd con el mejor Kp (Kp 3, Kd 4) | idem | `csv/exp1c_sim.csv` | – |
| 1D PID | `ki:=0.5` | idem | `csv/exp1d_sim.csv` | error final ≤ 2 cm (E2) |
| 2a | `kp_yaw:=1.0 kd_yaw:=0.0` | `experimento:=giro90` | `csv/exp2a_sim.csv` | – |
| 2b | `kp_yaw:=10.0 kd_yaw:=0.0` | idem | `csv/exp2b_sim.csv` | – |
| 2c | `kp_yaw:=10.0 kd_yaw:=1.2` | idem | `csv/exp2c_sim.csv` | – |
| 2p (propia) | ≥ 3 combinaciones de `kp_yaw`/`kd_yaw`/`ki_yaw`; la mejor va aquí | idem | `csv/exp2p_sim.csv` | sobreimpulso ≤ 25 %, asentamiento ≤ 3 s (E3) |
| 3A abierto | `experimento:=cuadrado_abierto` | – | `csv/exp3a_sim_run1..3.csv`, `_medium.csv` | – |
| 3B odom+PID | `experimento:=cuadrado bias_w:=0.03` | – | `csv/exp3b_sim_run1..3.csv`, `_medium.csv` | 3B **o** 3C: cierre real ≤ 30 cm en las 3 (E4) |
| 3C PID+Ki | `experimento:=cuadrado ki:=0.5 bias_w:=0.05` | – | `csv/exp3c_sim_run1..3.csv`, `_medium.csv` | idem |

Cada prueba 3x: 3 corridas con `noise:=low` y 1 con `noise:=medium` (`_medium`). Con `medium` el robot puede rozar una pared: si pasa, registrar la prueba como no terminada y explicar por qué.

Antes de cada corrida del Experimento 3, en otra terminal y **antes** del nodo:

```bash
python3 docs/rc1/cierre_real.py --csv csv/exp3b_sim_cinta_run1.csv --png plots/exp3b_sim_cinta_run1.png --lado 2.0
```

Gráficas (con `core_cuadrado.py` importable): `PYTHONPATH=scripts_pdi python3 docs/rc1/09_plot_csv.py csv/exp1d_sim.csv --experimento recta` (usar la versión parcheada de `docs/rc1`; escribe el PNG junto al CSV: moverlo a `plots/`).

## Robot real (Partes E–F, laboratorio, RosCar 4, `ROS_DOMAIN_ID=8`)

Antes de encender nada leer el Anexo C del reto. Primera prueba con las ruedas en el aire (ω > 0 gira a la izquierda). Una persona con la mano en Ctrl+C y otra lista para tomar el robot. Máximo 3 re-sintonías, cada una anotada.

| Orden | Prueba | Parámetros | CSV | Bag |
|---|---|---|---|---|
| 1 | giro90 | ganancias del simulador, `linear_speed:=0.10 max_angular:=1.0` | `csv/exp2_real_giro90.csv` | – |
| 2 | recta 1D | `experimento:=recta line_offset:=0.10`, **sin** `bias_w` | `csv/exp1d_real.csv` | – |
| 3 | 3A ×1 | `experimento:=cuadrado_abierto` | `csv/exp3a_real.csv` | `bags/rc1_real_3a` |
| 4 | 3B ×3 | `experimento:=cuadrado` | `csv/exp3b_real_run1..3.csv` | `bags/rc1_real_3b_run1..3` |

```bash
ros2 topic hz /odom ; ros2 node list | grep -i ekf      # sin EKF: dejar /odom (no usar /odom_raw: evita r y b_eff del RC-0)
ros2 bag record /odom /cmd_vel /tf -o bags/rc1_real_3b_run1
```

Medir con cinta (de la marca de inicio al centro del robot) y con transportador (ángulo final). Anotar en la hoja: `cierre_real_cm` y `yaw_acum_deg`.
Umbral E5: cierre real medio de 3B ≤ 25 cm (la cátedra puede ajustarlo tras el primer turno). Bonus: 3B ≤ 10 cm sin recalibrar, más 3A para comparar.

## Hoja de resultados

`hoja_resultados.csv`: una fila por CSV. Columnas del Anexo E. Valores de `planta`: `sim` o `real`. Valores de `prueba`: `1A 1B 1C 1D 2a 2b 2c 2p 3A 3B 3C` y `2` (giro90 real).
Para que `python3 scripts/rc1_verificar.py` pueda comprobar los umbrales, escribir las métricas en `notas` como `clave=valor;`:

- Recta: `e_medio_cm=2.6; t_as_s=5.8; e_fin_cm=0.5`
- Giro: `sobre_pct=3.0; t_as_s=1.9; e_fin_deg=0.4`
- Cualquier cambio de parámetro respecto de la prueba anterior: `cambio=kd 4.0->0.0`
