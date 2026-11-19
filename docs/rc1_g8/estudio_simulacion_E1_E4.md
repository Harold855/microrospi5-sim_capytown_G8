# Estudio para la defensa · Parte 1: la simulación (E1–E4)

**RC-1 · Grupo 8 · ROSCar 4.** Documento para los tres integrantes. La defensa no es solo repetir la prueba: el docente pregunta **cómo funciona el código**, quién hace cada cosa, qué recibe, qué produce, dónde se guardan los resultados y cómo se hacen las gráficas. Este documento cubre E1–E4 (simulador); el otro (`estudio_robot_real_E5_E7.md`) cubre E5–E7.

**Etiquetas:** [Seguro] leído en el código o en un archivo del repositorio · [Probable] inferencia fuerte · [Por confirmar] hay que comprobarlo en el contenedor (comandos en la sección 11).
**Dónde está el código del curso:** `cuadrado_controller.py` y `core_cuadrado.py` **no están en el repositorio** (son del docente, van en `scripts_pdi/`, que git ignora). Las líneas citadas de `core_cuadrado.py` son del archivo original (sha256 `a45a46af…`).

---

## 1. El mapa completo en una página

```
                      ┌──────────────────────────────────────────────┐
  (1) persona ───────►│ ros2 launch yahboomcar_sim sim.launch.py ...  │  lanza el simulador
                      └──────────────────────────────────────────────┘
                                         │ crea el nodo sim_robot (sim_node.py + vehicle.py)
                                         ▼
   ┌────────────────────────┐  /odom (50 Hz)   ┌─────────────────────────────┐
   │ cuadrado_controller.py │◄─────────────────│ sim_node.py  (clase SimRobot)│
   │  (usa core_cuadrado.py)│                  │  vehicle.py: mueve el robot  │
   │  PID + máquina de      │─────────────────►│  virtual y calcula /odom     │
   │  estados               │  /cmd_vel (30 Hz)│                              │
   └──────────┬─────────────┘                  └──────────────┬──────────────┘
              │ log_csv                                        │ /sim/pose (pose REAL)
              ▼                                                ▼
     csv/exp…_sim_*.csv                         docs/rc1/cierre_real.py (cinta virtual)
              │                                                │
              ▼                                                ▼
   docs/rc1/09_plot_csv.py → PNG                csv/exp…_sim_cinta_*.csv y PNG «odom vs. real»
              │                                                │
              └────────────► scripts/rc1_anotar.py ◄───────────┘
                                   │
                                   ▼
                          hoja_resultados.csv  (registro central)
```

### Quién hace qué (simulador)

| Pregunta | Respuesta | Dónde está en el código |
|---|---|---|
| ¿Quién **inicia** la ejecución del experimento? | La persona: lanza el simulador y luego el nodo del curso | `sim.launch.py`; `python3 scripts_pdi/cuadrado_controller.py --ros-args $(python3 scripts/rc1_args.py simulador …)` |
| ¿Quién **calcula** la velocidad? | El nodo del curso: `Runner.update()` | `core_cuadrado.py`, líneas 140–193 |
| ¿Quién **manda** esa velocidad? | El nodo del curso publica `/cmd_vel` (v y ω) a 30 Hz | `cuadrado_controller.py` (temporizador, publisher `/cmd_vel`) |
| ¿Quién **mueve** el robot virtual? | `Vehicle.step()`, llamado por `SimRobot._update()` | `vehicle.py` `step`; `sim_node.py` `_update` (línea 343) |
| ¿Quién produce `/odom`? | `SimRobot._publish_odom()` a partir de la pose de odometría del vehículo | `sim_node.py` línea 396 |
| ¿Quién da la pose **real**? | `SimRobot._publish_truth()` → `/sim/pose` | `sim_node.py` línea 442 |
| ¿Quién **para** al terminar? | El nodo: en estado `FIN` pone `v = ω = 0` en cada ciclo | `core_cuadrado.py` líneas 183–187 |
| ¿Quién para si el nodo **muere**? | El simulador: si no llega `/cmd_vel` en `cmd_timeout` = 0.5 s, ordena velocidad 0 | `sim_node.py` línea 350 |
| ¿Quién para si no llega `/odom`? | El nodo: a los 0.5 s sin `/odom` publica `Twist()` en cero | `cuadrado_controller.py` (`odom_timeout`) |
| ¿Quién **registra** la corrida? | El nodo escribe un CSV (`log_csv`); `cierre_real.py` escribe otro con las dos poses | ver sección 7 |
| ¿Quién **grafica**? | `09_plot_csv.py` (del CSV del nodo) y `cierre_real.py --png` (odom vs. real) | ver sección 8 |
| ¿Quién **anota** en la hoja? | `rc1_anotar.py` (E4) o a mano/`rc1_tablas.py` (E2, E3) | `scripts/` |

---

## 2. El simulador por dentro (`yahboomcar_ws/src/yahboomcar_sim/`)

| Archivo | Qué hace | Recibe | Produce |
|---|---|---|---|
| `launch/sim.launch.py` | Lanza el TF estático del lidar, el nodo `sim_robot` (ejecutable `sim_robot`, nombre de nodo `yahboomcar_sim`) y RViz opcional. Define los argumentos `world`, `start`, `noise`, `robot_radius`, `rviz`, etc. | argumentos | procesos |
| `yahboomcar_sim/sim_node.py` | Núcleo. Clase `SimRobot`. Cada 1/50 s ejecuta `_update` | `/cmd_vel`, `/beep`, `/initialpose`, servicio `/sim/reset` | `/odom` + TF, `/sim/pose`, `/scan`, `/imu/data_raw`, `/vel_raw`, `/voltage`, `/camera/*`, `/sim/collision` |
| `yahboomcar_sim/vehicle.py` | **Lo que mueve al robot virtual.** Cinemática con límites, colisión, empujón del piso y odometría con error | velocidad ordenada | pose real y pose de odometría |
| `yahboomcar_sim/world.py` | Lee el mapa `.yaml` + `.pgm` | mapa | rejilla de ocupación |
| `worlds/arena_rc1.*` | Arena abierta de 4 × 4 m del reto | – | – |
| `race.py`, `track*.py`, `camera.py`, `pilot.py`, `autopilot_node.py` | Pistas, cámara y piloto automático. **No se usan en el RC-1** | – | – |
| `test/test_core.py` | 25 pruebas del núcleo sin ROS | – | `unittest` |

### El ciclo del simulador, paso a paso (`sim_node.py`)

1. **Línea 237:** `create_subscription(Twist, 'cmd_vel', self._on_cmd, 10)`. `_on_cmd` (línea 289) solo guarda el último mensaje y la hora en que llegó (`self.cmd`, `self.last_cmd_time`).
2. **Línea 280:** `create_timer(self.dt, self._update)`, con `dt = 1/update_rate` (50 Hz).
3. **`_update` (línea 343):**
   - calcula `dt` real;
   - **línea 350:** `stale` = «el último `/cmd_vel` es más viejo que `cmd_timeout` (0.5 s)». Si está viejo, `cmd = (0, 0, 0)`;
   - llama a `veh.step(cmd, dt)` (mueve el robot virtual);
   - publica `/odom` (`_publish_odom`) y `/sim/pose` (`_publish_truth`).

### Qué hace `Vehicle.step()` (`vehicle.py`)

| Paso | Qué ocurre | Por qué importa |
|---|---|---|
| 1 | Recorta la orden a las velocidades máximas | `max_wz` = 3 rad/s del vehículo (el nodo ya recorta a `max_angular`) |
| 2 | `slew()` limita la **aceleración** (`accel_lin` 2.5 m/s², `accel_ang` 8 rad/s²) | Es lo único «dinámico» del simulador: no hay inercia ni retardo del motor |
| 3 | **Empujón del piso:** un ruido aleatorio `dv` (proceso Ornstein–Uhlenbeck, `floor_noise` m/s) que mueve y gira al robot | Las ruedas **no lo miden**, así que `/odom` no lo ve |
| 4 | Integra la **pose real** (`x, y, yaw`) con colisión contra las paredes | Es lo que lee `/sim/pose` |
| 5 | Integra la **odometría** (`ox, oy, oyaw`): velocidad real **menos** el empujón del piso, multiplicada por `1 + N(0, odom_noise)` | Es lo que lee `/odom` |

**Consecuencia clave [Seguro]:** `/odom` y `/sim/pose` salen de la misma simulación, pero `/odom` no incluye el empujón del piso. Por eso el nodo cree que cierra el cuadrado a < 1 cm mientras el robot virtual queda a 13–89 cm.

**Niveles de ruido** (`noise:=`, `sim_node.py` líneas 81–86):

| Nivel | `floor_noise` (empujón, m/s) | `odom_noise` (error de odometría) |
|---|---|---|
| `none` | 0 | 0 |
| `low` (trabajo) | 0.02 | 1 % |
| `medium` (una corrida por prueba) | 0.04 | 2 % |
| `high` | 0.10 | 5 % |

**Reinicio:** `/sim/reset` → `_on_reset` (línea 329) → `_teleport` (línea 316) → `Vehicle.reset`, que pone `ox = oy = oyaw = 0`. En el simulador `/odom` **arranca en 0** en cada reinicio; en el robot real no (ver el otro documento).

**Lo que el simulador NO modela [Seguro]:** inercia y retardo de los motores (solo limita la aceleración), derrape de las ruedas al girar, el `/odom` a ≈ 11 Hz del robot real (aquí 50 Hz) y el sesgo real de los motores.

---

## 3. El nodo del curso (el mismo código en simulador y robot real)

### 3.1 `cuadrado_controller.py` (nodo ROS 2) y `core_cuadrado.py` (la lógica)

El nodo no tiene lógica de control propia: la envuelve.

| | `cuadrado_controller.py` | `core_cuadrado.py` |
|---|---|---|
| Qué es | Nodo ROS 2 | Biblioteca sin ROS |
| Recibe | `/odom` | `(x, y, yaw, dt)` |
| Produce | `/cmd_vel`, `/line_error`, `/yaw_error`, el CSV | `(v, w, info)` |
| Ritmo | Temporizador de 30 Hz (`control_rate`) | – |
| Contiene | `main()` (línea 158: `main()`), suscripción, publicación, escritura del CSV, vigilante de `/odom` | `PID`, `Params`, `Runner`, `metricas`, `simular` |

**Cómo arranca:** la persona ejecuta el script; `main()` crea el nodo y hace `spin`. En cada tick del temporizador, si hay una pose de `/odom` reciente, llama a `Runner.update(x, y, yaw, dt)` y publica `/cmd_vel` con el `(v, w)` que devuelve. La primera llamada encuentra el estado `ESPERA` y ejecuta `start()` (línea 143–144 de `update`).

### 3.2 La máquina de estados (`Runner`, `core_cuadrado.py`)

```
ESPERA ──start()──► AVANZA ◄──────────────┐          (experimento recta/cuadrado)
                      │ s ≥ side            │
                      ▼                     │ _turn_done()
                    GIRA ───────────────────┘          (cuadrado: 4 lados)
                      │ k ≥ n_sides  /  giro90  /  recta
                      ▼
                     FIN
```

| Función | Líneas | Qué hace |
|---|---|---|
| `start(x, y, yaw)` | ≈ 125–138 | Guarda el inicio. Si el experimento es `giro90`: `yaw_target = yaw + π/2` y estado `GIRA` (líneas 135–136); si no: estado `AVANZA` (línea 138) |
| `update(x, y, yaw, dt)` | 140–193 | Una muestra del lazo. Devuelve `(v, w, info)` |
| `_side_done()` | 195–204 | Fin de un lado: en `recta` pasa a `FIN`; si no, `yaw_target = yaw_obj + π/2`, estado `GIRA`, reinicia el PID del giro |
| `_turn_done(x, y)` | 206–216 | Fin del giro: `k += 1`, `yaw_obj = yaw_target` (línea 209); si es `giro90` o `k ≥ n_sides` pasa a `FIN` (línea 210); si no, **`self.sx, self.sy = x, y`** (línea 213: el siguiente lado arranca desde donde está el robot), `AVANZA` y reinicia el PID de línea |

### 3.3 Qué calcula cada estado (`update`)

| Estado | Líneas | Cálculo |
|---|---|---|
| `AVANZA` | 153–169 | `psi = yaw_obj`; `s` = avance sobre la línea y `d` = desvío lateral (+ = izquierda), proyectando `(x − sx, y − sy)` sobre `psi` (líneas 154–157). **`e_line = d + line_offset`** (línea 158). `v = p.v`. Lazo cerrado: **`w = −pid_line.step(e_line, dt)`** (línea 166); bang-bang: `w = 0` si `|e| < deadband`, si no `−copysign(w0, e)` (líneas 163–164). Termina cuando `s ≥ side` (línea 167). En `cuadrado_abierto`: termina **solo por tiempo**, `t_state ≥ side/v` (línea 161) |
| `GIRA` | 171–181 | **`e_yaw = normalize(yaw_target − yaw)`** (línea 172). Lazo cerrado: **`w = pid_yaw.step(e_yaw, dt)`** (línea 178); termina cuando `|e_yaw| < yaw_tol` durante `settle_time` (líneas 179–181; 2° y 0.3 s por defecto). En `cuadrado_abierto`: `w = turn_w` y termina por tiempo `(π/2)/(turn_w·turn_scale)` (líneas 173–176) |
| `FIN` | 183–187 | La primera vez calcula **`closure_error = hypot(x − x0, y − y0)`** (línea 186); `v = w = 0` |
| salida | 188–189 | **`w = clamp(w, −max_w, +max_w) + bias_w`**: el sesgo se suma **después** del recorte |

Dos detalles que suelen preguntar:
- **Por qué `w = −PID` en la recta y `+PID` en el giro:** `e_line > 0` significa «a la izquierda de la línea», y para volver hay que girar a la derecha (ω < 0). En el giro, `e_yaw = objetivo − actual` ya tiene el signo del giro que hay que hacer.
- **Por qué `bias_w` va después del `clamp`:** el sesgo imita un motor que empuja de más y el controlador no puede «recortarlo».

### 3.4 El PID (`class PID`, `core_cuadrado.py`)

```
u = Kp·e + Ki·∫e dt + Kd·(e − e_ant)/dt
integral += e·dt, y se limita a ±integral_limit (0.5)       (anti-windup)
la derivada vale 0 en la primera muestra
reset() al empezar cada lado y cada giro
```

| Ganancia | Para qué sirve | Si la subes | Si es 0 |
|---|---|---|---|
| `Kp` | Corrige en proporción al error | responde más rápido; con retardo oscila | no corrige |
| `Ki` | Elimina el error de régimen permanente (sesgo) | quita el sesgo, pero añade retardo y puede inestabilizar; riesgo de wind-up | queda un error constante |
| `Kd` | Amortigua: reacciona a la velocidad del error | menos oscilación; con ruido o datos repetidos da picos | oscila más |

**Ejemplo numérico** (Kp 3, Ki 0.5, Kd 4, e = 0.060, e_ant = 0.063, integral previa 0.100, dt = 1/30): P = 0.18; integral = 0.100 + 0.060/30 = 0.102 → I = 0.051; D = 4·(−0.003)·30 = −0.36; PID = −0.129; en la recta **ω = −PID = +0.129 rad/s**. [Por confirmar] el orden exacto de actualización de la integral en `PID.step` (comando en la sección 11).

### 3.5 Parámetros del nodo (`-p clave:=valor`)

| Parámetro | Defecto | Qué es | Valor de trabajo en el simulador |
|---|---|---|---|
| `experimento` | `cuadrado` | `recta`, `giro90`, `cuadrado`, `cuadrado_abierto` | según la prueba |
| `linear_speed` | 0.20 | velocidad lineal (m/s) | 0.20 |
| `kp`, `ki`, `kd` | 3.0, 0.0, 4.0 | PID de la línea (error en m) | 3.0, 0.0–0.5, 4.0 |
| `kp_yaw`, `ki_yaw`, `kd_yaw` | 3.0, 0.0, 0.4 | PID del giro (error en rad) | 10.0, 0.0, 0.6 (propia 2p) |
| `integral_limit` | 0.5 | tope del anti-windup | 0.5 |
| `max_angular` | 2.0 | tope de ω (rad/s) | 2.0 |
| `line_offset` | 0.0 | la línea virtual queda a esta distancia a la derecha | 0.10 en la recta |
| `bias_w` | 0.0 | sesgo de motor inyectado (rad/s) | 0.06 (recta), 0.03 (3B), 0.05 (3C) |
| `side` | 2.0 | largo del lado (m) | 2.0 |
| `log_csv` | `""` | CSV de la corrida | `csv/exp…_sim_*.csv` |
| `odom_timeout` | 0.5 | s sin `/odom` antes de frenar | 0.5 |
| `controlador` | `pid` | `pid` o `bangbang` | `bangbang` solo en 1A |

`scripts/rc1_args.py` lee `config/rc1_pid.yaml` (bloques `simulador` y `robot_real`), los convierte a `-p …` con punto decimal (evita `kd:=0`) y deja que los `clave=valor` extra pisen los del YAML.

---

## 4. E1 — Simulador en marcha (1 pt)

**Qué se pide:** arena lanzada, `/odom` ≈ 50 Hz, `sim_log.txt` con la diferencia odom vs. real y la captura de `rqt_graph`.

**Cómo se hizo:**
```bash
ros2 launch yahboomcar_sim sim.launch.py world:=arena_rc1 start:=1.0,1.0,0.0 robot_radius:=0.14 noise:=low rviz:=false
ros2 service call /sim/reset std_srvs/srv/Empty     # robot a la salida, /odom en 0
```

| Evidencia | Qué muestra |
|---|---|
| `sim_log.txt`, sección `=== topic list` | Los tópicos activos: `/cmd_vel`, `/odom`, `/sim/pose`, `/scan`, `/imu/data_raw`, `/tf`… |
| `=== hz /odom` | `average rate: 49.963 … 48.514`: **≈ 50 Hz** (el nodo publica a `update_rate` = 50) |
| `=== sim/pose` | La pose real existe como tópico aparte |
| `=== cierre manual con teleop, noise:=high` | Dos corridas manuales: `/odom` y real difieren (corrida 2: cierre 33.4 frente a 53.6 cm; el yaw de `/odom` se separa hasta 42° del real) |
| `=== paso 5: frenado por falta de /cmd_vel` | Un solo `/cmd_vel` y el robot se detuvo solo en ≈ 0.58 s: es `cmd_timeout` = 0.5 s (`sim_node.py`) |
| `plots/rqt_graph_sim.png` | El grafo de nodos y tópicos |

**Preguntas que pueden hacer en E1** (respuestas en la sección 9): ¿qué nodo produce `/odom`? ¿qué es `/sim/pose`? ¿por qué se detiene el robot si dejas de mandar `/cmd_vel`? ¿qué significa `noise:=low`?

---

## 5. E2 — La recta (1A–1D) (1 pt)

**Qué se pide:** 1A–1D con CSV y tabla; 1D con error final ≤ 2 cm.
**Montaje:** el robot arranca **10 cm a la izquierda** de la línea virtual (`line_offset:=0.10`, línea 158), con `bias_w:=0.06` (sesgo de motor que obliga a corregir).

| Prueba | Qué cambia | Código que se ejecuta | Resultado clave |
|---|---|---|---|
| 1A bang-bang | `controlador:=bangbang` | `core_cuadrado.py` líneas 163–164: `w = 0` dentro de la banda muerta, si no `−copysign(w0, e)` | \|e\| medio 6.27 cm; 3 cruces; no se asienta |
| 1B solo P | `kd:=0.0` (Kp 3, Ki 0) | línea 166 con Ki = Kd = 0 | \|e\| medio 6.03 cm; 2 cruces; no se asienta |
| 1C P + D | Kd 4 | línea 166 con Ki = 0 | \|e\| medio 3.10 cm; 0 cruces; residuo ≈ 2.1 cm |
| 1D PID | Ki 0.5 | línea 166 completa | error final **0.30 cm**; asienta en 5.80 s |

**Por qué cada ganancia (lo que enseña el experimento):**
- 1A: el bang-bang siempre empuja con la misma fuerza y por eso zigzaguea.
- 1B: P puro corrige, pero la posición lateral es la integral del rumbo; sin amortiguamiento, oscila.
- 1C: Kd amortigua y baja los cruces a 0, pero queda un error por el sesgo `bias_w`.
- 1D: Ki integra el error residual y lo lleva a ≈ 0.

**Cómo se ejecuta una prueba (ejemplo 1D):**
```bash
python3 scripts_pdi/cuadrado_controller.py --ros-args \
    $(python3 scripts/rc1_args.py simulador experimento=recta line_offset=0.10 bias_w=0.06 ki=0.5 log_csv=csv/exp1d_sim.csv)
```
La gráfica: `PYTHONPATH=scripts_pdi python3 docs/rc1/09_plot_csv.py csv/exp1d_sim.csv --experimento recta` (usa la versión parcheada que descarta las filas `FIN` de la recta).

---

## 6. E3 — El giro de 90° (2a–2c y combinación propia) (1 pt)

**Qué se pide:** 2a–2c con tabla y una combinación propia con sobreimpulso ≤ 10 % y asentamiento ≤ 3 s.
**Qué código ejecuta un giro:** `experimento=giro90`.
1. `start()` (líneas 135–136): `yaw_target = yaw + π/2` y estado `GIRA`.
2. `update`, estado `GIRA` (líneas 171–181): `e_yaw = normalize(yaw_target − yaw)`; **`w = pid_yaw.step(e_yaw, dt)`**; el giro termina cuando `|e_yaw| < yaw_tol` durante `settle_time`.
3. `_turn_done` (línea 210): como el experimento es `giro90`, pasa a `FIN`.
4. En `FIN`, `v = w = 0` (líneas 183–187).

| Prueba | `kp_yaw` / `ki_yaw` / `kd_yaw` | Sobreimpulso | Asentamiento | Lectura |
|---|---|---|---|---|
| 2a | 1.0 / 0 / 0 | 0 % | 3.83 s | Respuesta exponencial, lenta |
| 2b | 10.0 / 0 / 0 | 4.32 % | 1.20 s | Rápido pero sobrepasa (93.88°) |
| 2c | 10.0 / 0 / 1.2 | 0 % | 1.34 s | Kd amortigua el sobreimpulso |
| **2p (propia)** | **10.0 / 0 / 0.6** | **0 %** | **1.01 s** | Cumple E3; error final 0.22° |

Otras combinaciones probadas: 2p2 (10 / 0 / 2.0, 1.27 s) y 2p3 (5 / 0 / 0, 1.13 s). Se eligió 2p1 por ser la más rápida sin sobreimpulso.

**Métricas** (`metricas` en `core_cuadrado.py`, calculadas por `09_plot_csv.py`): sobreimpulso (% sobre 90°), asentamiento (último instante fuera de ±2°), error final, cruces de 90°.
**Saturación:** en 2b/2c `w_max = 2.0` rad/s: el tope `max_angular` se alcanza al inicio.

---

## 7. E4 — El cuadrado de 2 × 2 m (1 pt)

**Qué se pide:** 3A, 3B y 3C con 3 corridas (`noise:=low`) y 1 con `medium`; cierre según `/odom` y REAL; 3B **o** 3C con cierre real ≤ 40 cm.

| Prueba | Experimento | Parámetros | Qué mide |
|---|---|---|---|
| 3A lazo abierto | `cuadrado_abierto` | `turn_w`, `turn_scale` | no usa `/odom` para decidir: avanza `side/v` s y gira un tiempo fijo (líneas 161 y 173–176) |
| 3B PID sobre `/odom` | `cuadrado` | Kp 3, Ki 0, Kd 4, `kp_yaw` 10, `kd_yaw` 0.6, `bias_w` 0.03 | lazo cerrado en línea y giro |
| 3C PID + Ki | `cuadrado` | `ki` 0.5, `bias_w` 0.05 | igual, con Ki |

**El orden de ejecución de una corrida (importa):**
1. `ros2 service call /sim/reset …` (robot a la salida, `/odom` en 0).
2. **Primero** `cierre_real.py` en otra terminal (graba `/sim/pose` y `/odom` desde el inicio).
3. Luego el nodo del curso con `log_csv`.
4. Cuando el nodo imprime `FIN. error de cierre = … cm, yaw acumulado = … deg`, **Ctrl+C** en el nodo y en `cierre_real.py`.
5. `cierre_real.py` imprime el cierre según `/odom` y el REAL y guarda CSV y PNG.
6. `rc1_anotar.py` pasa los números a la hoja.

**Resultados (cierre real, `noise:=low`):**

| Prueba | Corridas (cm) | Media | `/odom` decía |
|---|---|---|---|
| 3A | 10.8 / 12.8 / 24.6 | 16.1 | 1.6–8.9 cm |
| 3B | 37.3 / 88.7 / 50.0 | 58.7 | 0.3–1.0 cm |
| 3C | 41.6 / 13.4 / 35.3 | 30.1 | 0.1–0.7 cm |

Con `medium`: 3A 24.8, 3B 46.0, 3C 56.8 cm (real).
**Cumplimiento de E4:** la media de 3C (30.1 cm) cumple ≤ 40 cm, pero su corrida 1 (41.6 cm) no; la lectura de la meta (por corrida, por media o «al menos una») se debe confirmar con el docente.

**Por qué el PID «cree» cerrar y no cierra:** el nodo cierra el lazo sobre `/odom`, y `/odom` no ve el empujón del piso (`vehicle.py`). Por eso 3A, que no depende de `/odom`, cerró mejor en el simulador (algo que en el robot real se espera al revés).

**Cómo se ve en la gráfica:** `plots/exp3c_sim_cinta_run2.png` dibuja la trayectoria según `/odom` (cierra) y la REAL (no cierra) sobre el cuadrado ideal; se separan sobre todo en las esquinas.

---

## 8. Dónde van los resultados y cómo se hacen las gráficas

### 8.1 El CSV del nodo (`log_csv`)

Columnas: **`t, x, y, yaw, v, w, e_line, e_yaw, estado`**.
- `t`: tiempo (s); `x, y, yaw`: la pose de `/odom` (**absoluta**, no relativa al inicio); `v, w`: lo que se ordenó; `e_line`, `e_yaw`: los errores de ese instante; `estado`: `AVANZA`, `GIRA`, `FIN`.
- El nodo escribe una fila por ciclo (30 Hz). **Después de `FIN` sigue escribiendo filas `FIN`** hasta que se cierra.
- El mensaje `FIN. error de cierre…` sale de `info['closure']` y `info['yaw_total']` (líneas 147, 186 y 191–192).

### 8.2 `docs/rc1/cierre_real.py` — la «cinta métrica virtual»
- Es un nodo (`Cinta`) que se suscribe a **`/sim/pose`** y **`/odom`** y, con un temporizador de 0.05 s (20 Hz), guarda una fila: `t, x_real, y_real, yaw_real, x_odom, y_odom, yaw_odom`.
- Al cerrar con Ctrl+C: `resumen()` calcula, para `/odom` y para el real, el **cierre** (distancia entre la primera y la última fila) y el **yaw acumulado** (suma de diferencias normalizadas).
- `grafica()` dibuja las dos trayectorias en el marco del primer rumbo, más el cuadrado ideal si se da `--lado`.
- **Solo funciona en el simulador:** en el robot real `/sim/pose` no existe.

### 8.3 `docs/rc1/09_plot_csv.py` — gráfica y métricas de un CSV del nodo
- `leer()` carga el CSV; **resta la pose inicial y la rota** al primer rumbo (por eso las gráficas parten de (0, 0) aunque el CSV tenga coordenadas absolutas).
- **Parche del grupo:** en la `recta`, descarta las filas `FIN` (donde `e_line = 0`) antes de calcular métricas.
- Llama a `metricas()` de `core_cuadrado.py`, imprime los números y guarda `<csv>.png` junto al CSV: trayectoria a la izquierda y, a la derecha, el yaw (giro) o el error lateral (recta/cuadrado). Hay que moverlo a `plots/`.

### 8.4 Los scripts del grupo
| Script | Qué hace |
|---|---|
| `scripts/rc1_args.py` | Convierte el YAML en banderas `-p` |
| `scripts/rc1_anotar.py` | Anota en la hoja una corrida de E4 (`3A/3B/3C` + `run1/run2/run3/medium`): `cierre_odom_cm`, `cierre_real_cm`, `yaw_real_deg` |
| `scripts/rc1_tablas.py` | Genera tablas Markdown de E2, E3 y E4 desde la hoja y los CSV |
| `scripts/rc1_figuras_giro.py` | Las dos figuras de E3 (predicción reconstruida y comparación con lo medido) |
| `scripts/rc1_verificar.py` | Estima el avance contra la rúbrica (solo lectura) |
| `scripts/rc1_informe_pdf.sh` | `informe.md` → `informe.pdf` |

### 8.5 `hoja_resultados.csv`
Una fila por prueba. Columnas: `prueba, planta, noise, kp, ki, kd, kp_yaw, ki_yaw, kd_yaw, prediccion, cierre_odom_cm, cierre_real_cm, yaw_acum_deg, notas`. Las métricas van en `notas` como `clave=valor;`. `planta` es `sim` o `real`.

---

## 9. Banco de preguntas probables (con respuesta corta)

### Del simulador
1. **¿Qué nodo mueve el robot virtual?** `SimRobot` (`sim_node.py`): cada 1/50 s `_update` llama a `Vehicle.step` (`vehicle.py`).
2. **¿Qué recibe y qué produce `sim_node.py`?** Recibe `/cmd_vel` (y `/beep`, `/initialpose`, el servicio `/sim/reset`); produce `/odom` + TF, `/sim/pose`, `/scan`, `/imu/data_raw`, `/vel_raw`, `/voltage`, `/camera/*`, `/sim/collision`.
3. **¿Qué es `/odom` y qué es `/sim/pose`?** `/odom`: lo que cree el robot (integra su velocidad con error y sin el empujón del piso). `/sim/pose`: la pose real. El cierre «según `/odom`» y el «REAL» salen de ahí.
4. **¿Qué es el empujón del piso y por qué `/odom` no lo ve?** Un ruido aleatorio (Ornstein–Uhlenbeck) que mueve y gira el robot en `Vehicle.step`; la odometría resta ese empujón (integra «lo que miden las ruedas»).
5. **¿Qué pasa si el nodo del curso deja de mandar `/cmd_vel`?** A los 0.5 s (`cmd_timeout`, línea 350 de `sim_node.py`) el simulador ordena v = ω = 0.
6. **¿Qué hace `noise:=low`?** `floor_noise` 0.02 m/s y `odom_noise` 1 % (líneas 81–86).
7. **¿Qué hace `/sim/reset`?** Lleva el robot a la salida y pone la odometría en 0 (`_teleport`, línea 316).
8. **¿Qué limita el simulador?** Velocidades y aceleraciones (`slew`); no modela inercia, derrape ni retardo del motor.
9. **¿Cuál es el propósito de la simulación?** Sintonizar y entender el PID sin riesgo para el robot, y ver la diferencia entre `/odom` y lo real antes de pasar al robot.

### Del nodo y el PID
10. **¿Qué parte del código calcula la velocidad?** `Runner.update` (`core_cuadrado.py`, líneas 140–193); el nodo ROS solo lo llama y publica.
11. **¿Cuántos estados hay y cuáles?** `ESPERA`, `AVANZA`, `GIRA`, `FIN`.
12. **¿Cómo decide que un lado terminó?** `s ≥ side` (línea 167); en 3A, por tiempo `side/v` (línea 161).
13. **¿Cómo decide que un giro terminó?** `|e_yaw| < yaw_tol` durante `settle_time` (líneas 179–181); en 3A, por tiempo `(π/2)/(turn_w·turn_scale)`.
14. **¿Qué es `e_line`?** `d + line_offset` (línea 158); `d > 0` es a la izquierda. Con `line_offset = 0.10` el robot parte a 10 cm de la línea.
15. **¿Por qué `w = −PID(e_line)`?** Error a la izquierda → hay que girar a la derecha (ω < 0). Si se invierte el signo, la realimentación es positiva y diverge.
16. **¿Para qué sirve `integral_limit`?** Evita el *wind-up*: limita la integral a ±0.5.
17. **¿Qué es `bias_w` y por qué va después del `clamp`?** Un sesgo de motor inyectado (rad/s). Se suma al final porque imita un defecto físico que el controlador no puede recortar.
18. **¿Qué hace Kd y por qué solo P oscila?** P corrige sin amortiguar; con la posición lateral como doble integral, oscila. Kd actúa sobre la velocidad del error y amortigua.
19. **¿Qué hace Ki?** Quita el error constante (por ejemplo, el sesgo `bias_w`).
20. **¿En qué orden se sintoniza y por qué?** Kp → Kd → Ki, un parámetro por prueba, para atribuir cada cambio a una causa.
21. **¿Quién decide `FIN` y quién para el robot?** `Runner.update` pasa a `FIN` y pone v = ω = 0; el nodo publica eso en cada ciclo.
22. **¿Qué hace `rc1_args.py`?** Convierte el bloque `simulador` o `robot_real` de `config/rc1_pid.yaml` en `-p` con punto decimal.

### De los resultados y las gráficas
23. **¿De dónde sale el CSV y qué columnas tiene?** Del nodo (`log_csv`): `t, x, y, yaw, v, w, e_line, e_yaw, estado`.
24. **¿Cómo se genera la gráfica odom vs. real?** `cierre_real.py` graba `/sim/pose` y `/odom` a 20 Hz y dibuja ambas trayectorias (`grafica()`).
25. **¿Cómo se generan las gráficas de cada prueba?** `09_plot_csv.py` lee el CSV, lo lleva a coordenadas relativas, calcula las métricas con `core_cuadrado.metricas` y guarda un PNG.
26. **¿Dónde se registran los resultados finales?** En `hoja_resultados.csv` (una fila por prueba) con `rc1_anotar.py` o a mano.
27. **¿Por qué `cierre_real.py` se lanza antes del nodo?** Para registrar la pose desde el inicio; el cierre es la distancia entre la primera y la última fila.
28. **¿Qué diferencia hay entre el cierre del nodo y el real?** El nodo usa `/odom`; el real usa `/sim/pose` (en el robot real, la cinta).
29. **En E4, ¿por qué 3A cerró mejor que 3B?** 3A no depende de `/odom`; 3B cierra sobre una medida que no ve el empujón del piso.
30. **¿Por qué `noise:=medium` en una corrida?** Para ver cómo crece el cierre con más empujón (3C real 56.8 cm).

### Simulado frente a real
31. **Dos cosas que el simulador no modela.** Retardo/inercia de los motores y `/odom` lento (≈ 11 Hz) con derrape de las cuatro ruedas.
32. **¿Qué cambiará en el robot real?** Menos ganancia (`kp_yaw` 10 → 1.0), `Kd` más alto y `Ki` menor en la línea, velocidades 0.10 m/s y `max_angular` 1.0; el cierre real no se mide con `/sim/pose` sino con cinta.
33. **¿Qué sensor vería el giro que causa el empujón?** El giroscopio (`/imu/data_raw` en el simulador, `/imu` en el robot real).

---

## 10. Cifras clave que hay que saber

| Dato | Valor |
|---|---|
| `/odom` simulado | ≈ 50 Hz (`update_rate` 50) |
| Parada por falta de `/cmd_vel` | 0.5 s (`cmd_timeout`) |
| Parada del nodo por falta de `/odom` | 0.5 s (`odom_timeout`) |
| Control del nodo | 30 Hz (`control_rate`) |
| E2 1D | error final 0.30 cm; asentamiento 5.80 s |
| E3 2p | sobreimpulso 0 %; asentamiento 1.01 s; error 0.22° |
| E4 cierre real medio (`low`) | 3A 16.1 · 3B 58.7 · 3C 30.1 cm |
| 1° de yaw a 2 m | 2·tan(1°) = 3.49 cm (≈ 9.8 cm en cuatro lados) |

---

## 11. Qué comprobar en el contenedor (para no responder «de memoria» lo que no se leyó)

El nodo del curso está en `/root/microrospi5-sim_capytown_G8/scripts_pdi/`. Ejecuta y anota las líneas:

```bash
grep -n "class PID" -A28 scripts_pdi/core_cuadrado.py
```
```bash
grep -n "yaw_tol\|settle_time\|control_rate\|odom_timeout\|n_sides\|deadband\|w0" scripts_pdi/core_cuadrado.py scripts_pdi/cuadrado_controller.py
```
```bash
grep -n "create_subscription\|create_publisher\|create_timer\|log_csv\|csv\|def \|finally" scripts_pdi/cuadrado_controller.py
```

Con eso respondes con certeza: cómo se actualiza la integral, cuánto valen `yaw_tol`/`settle_time`, y en qué función se escribe el CSV y se publica `/cmd_vel`.

---

## 12. Cosas honestas que hay que saber explicar

- Las predicciones de E2–E4 se escribieron **antes** de cada prueba; la diferencia con el dato es parte de lo evaluado (3B real: predijimos 20 cm, salió 58.7 cm de media).
- `1A`: la corrida válida fue la tercera tras fijar la predicción (la segunda no se guardó); está anotado en la hoja.
- La convención de nombres de archivo `*_sim*`, `*_sim_cinta_*` y `*_real*` es del grupo (el reto da ejemplos que chocan); está pendiente confirmar con el docente.
