# Estudio para la defensa · Parte 2: el robot real (E5–E7)

**RC-1 · Grupo 8 · ROSCar 4 (`ROS_DOMAIN_ID=8`).** Documento para los tres integrantes. En la defensa el docente evalúa a cada uno según su rol, con dos notas: **40 %** reproducir delante de él el giro de 90° (E5), la recta de 2 m (E6) y el cuadrado de 2 × 2 m con 3B < 25 cm (E7), más el **BONUS** (+2 pt, 3B < 10 cm); y **60 %** las respuestas a sus preguntas, que son sobre todo del **código y los scripts**: qué hace cada parte, qué recibe, qué produce, qué mueve el robot, qué registra los resultados, adónde van y cómo se hacen las gráficas.

Complementa a `estudio_simulacion_E1_E4.md`: allí está la anatomía del nodo del curso y del PID con todas las líneas de `core_cuadrado.py`. Aquí se resume lo necesario y se explica lo propio del robot real.

**Etiquetas:** [Seguro] leído en el código, en un script del repositorio o medido · [Probable] inferencia fuerte · [Por confirmar] hay que comprobarlo en el contenedor (sección 12) · **[Pendiente E7]** se completa al terminar 3B.

---

## 1. El mapa del robot real

```
 Raspberry Pi 5 (pi@roscar4, SSH 10.42.0.1)
 ┌─────────────────────────────────────────────────────────────────────┐
 │ contenedor micro_ros_agent  ◄── enlace a la placa ──►  placa del robot   │
 │        │ (puente ROS 2 ↔ placa)                       │ motores/enc. │
 │        ▼                                              │              │
 │ contenedor ros2_dev                                    │              │
 │   YB_Car_Node ── publica /odom_raw (≈ 11 Hz) ─┐        │              │
 │        ▲  (único suscriptor de /cmd_vel)       ▼        │              │
 │        │                              odom_corrector ──► /odom (≈ 11 Hz)
 │        │ /cmd_vel (30 Hz)                       (capytown_esan)        │
 │   cuadrado_controller.py (+ core_cuadrado.py) ◄──────── /odom         │
 │        │                                                              │
 │        └─► CSV (log_csv) → copia al PC → plots / hoja / git           │
 │   scripts/rc1_correr.sh  (orquesta una corrida: checks, bag, ceros)   │
 └─────────────────────────────────────────────────────────────────────┘
 Verdad terreno: cinta métrica (cierre y desvío lateral) y transportador (giro)
```

### Quién hace qué (robot real)

| Pregunta | Respuesta | Dónde |
|---|---|---|
| ¿Quién **inicia** una corrida? | La persona, con `scripts/rc1_correr.sh <giro\|recta\|3a\|3b> <nombre> …` (dentro del contenedor, con el bringup corriendo) | `rc1_correr.sh` |
| ¿Quién **calcula** la velocidad? | El mismo nodo del curso, **sin modificar**: `Runner.update` | `core_cuadrado.py` 140–193 |
| ¿Quién **manda** la orden? | `cuadrado_controller.py` publica `/cmd_vel` (v, ω) a 30 Hz | nodo del curso |
| ¿Quién **mueve** el robot? | `YB_Car_Node`: recibe `/cmd_vel` y comanda los motores de la placa [Seguro: es el único suscriptor de `/cmd_vel`; cómo habla con la placa no se inspeccionó] | contenedor `ros2_dev` |
| ¿Quién produce `/odom`? | `odom_corrector` reescala `/odom_raw` con los parámetros de rueda del grupo | paquete `capytown_esan` |
| ¿Quién **para** al terminar bien? | El nodo: en `FIN`, v = ω = 0 en cada ciclo | `core_cuadrado.py` 183–187 |
| ¿Quién para si el nodo **muere** antes de `FIN`? | **Nadie, por sí solo**: el robot conserva la última orden. Lo compensa `parar()` del script (ceros durante 3 s) y la persona en el interruptor | `rc1_correr.sh` 106–111 |
| ¿Quién **registra**? | El nodo (CSV), el script (`<csv>.nodo.log` y el bag), la persona (cinta/transportador) | sección 9 |
| ¿Quién **analiza**? | `rc1_analiza_real.py` (métricas desde `/odom`) | `scripts/` |
| ¿Quién **anota** en la hoja? | `rc1_anotar_real.py` | `scripts/` |
| ¿Quién da la **medida real**? | Cinta y transportador, dos personas | – |

---

## 2. Arrancar el entorno real (siempre en este orden)

1. **Hora del Pi** (no tiene batería de reloj; se pierde en cada arranque): `sudo timedatectl set-time "AAAA-MM-DD HH:MM:SS"` en el host.
2. **Terminal 1 (bringup):**
```bash
docker exec -it ros2_dev bash
source /opt/ros/humble/setup.bash; source /root/yahboomcar_ws/install/setup.bash
export ROS_DOMAIN_ID=8
ros2 launch capytown_esan bringup.launch.py wheel_params:=/root/wheel_params_g8.yaml
```
3. **Terminal 2 (corridas):** mismas tres líneas de `source`/`export` y `cd /root/microrospi5-sim_capytown_G8`.
4. **Comprobar:** `ros2 node list` (`/YB_Car_Node`, un solo `/odom_corrector`), `ros2 topic hz /odom` (≈ 11 Hz), `ros2 topic echo /battery --once` (≥ 70).
5. **Seguridad (Anexo C):** zona de 2 × 2 m + 15 cm libre, persona con la mano en el interruptor, otra lista para tomar el robot, primera prueba con las ruedas en el aire.

### Las piezas del robot real

| Pieza | Qué hace | Recibe | Produce |
|---|---|---|---|
| `YB_Car_Node` | Driver de la placa: mueve los motores [Seguro] | `/cmd_vel`, `/beep`, `/servo_s1`, `/servo_s2` | `/odom_raw`, `/imu`, `/battery`, `/scan` |
| `micro_ros_agent` | Puente entre ROS 2 y la placa [Por confirmar los detalles] | – | – |
| `odom_corrector` | Corrige la odometría de fábrica con el radio y la separación de ruedas **del grupo** | `/odom_raw` | `/odom` + TF `odom→base_footprint` |
| `bringup.launch.py` (`capytown_esan`) | Lanza `odom_corrector` con el YAML de `wheel_params:=` | ruta del YAML | el nodo |
| `wheel_params_g8.yaml` | Calibración propia | – | parámetros |
| Interruptor del robot | **El único paro garantizado** | persona | corta los motores |

**Cálculo de `odom_corrector`** (confirmado con `ros2 param dump` y el log):
```
firmware: r0 = 0.0325 m, b0 = 0.24 m       propio: r = 0.03145 m, b_eff = 0.2138 m
k_lin = r / r0 = 0.9677        k_ang = (r / b_eff) / (r0 / b0) = 1.0863
/odom = /odom_raw con la distancia × k_lin y el giro × k_ang
```
El paquete `capytown_esan` **no está en nuestro repositorio**; lo anterior sale del volcado de parámetros y de los logs.

---

## 3. El nodo del curso en el robot real (resumen)

Es el **mismo** `cuadrado_controller.py` + `core_cuadrado.py` que en el simulador (verificado con su `sha256` antes de cada corrida). Lo que cambia es la planta y los parámetros. Detalle completo en `estudio_simulacion_E1_E4.md`, secciones 3.1–3.5. Lo imprescindible:

| Idea | Código |
|---|---|
| Estados: `ESPERA → AVANZA ⇄ GIRA → FIN` | `Runner` |
| `e_line = d + line_offset`; `w = −PID(e_line)` | línea 158 y 166 |
| `e_yaw = normalize(yaw_target − yaw)`; `w = +PID_yaw(e_yaw)` | líneas 172 y 178 |
| Fin del lado: `s ≥ side`; fin del giro: `|e_yaw| < yaw_tol` durante `settle_time` | líneas 167 y 179–181 |
| Salida: `w = clamp(w, ±max_w) + bias_w` | línea 189 |
| `FIN`: `closure_error = hypot(x − x0, y − y0)`, v = ω = 0 | líneas 183–187 |
| El siguiente lado arranca desde el robot: `self.sx, self.sy = x, y` | línea 213 |

### Lo que descubrimos en el robot real (y que explica cosas)

1. **`/odom` es lento:** ≈ 11 Hz (períodos 0.07–0.15 s) frente a los 30 Hz del control. El nodo reusa la misma pose varias veces; la derivada llega en ráfagas y produce *chatter* en ω.
2. **Tras `FIN` el nodo sigue escribiendo filas `FIN`** en el CSV (≈ 18 s a 30 Hz en la recta) hasta que `timeout` lo corta. El proceso no termina solo.
3. **El `Twist()` final del nodo falla** con `RCLError: publisher's context is invalid` al apagarse. Es inofensivo si el robot ya está parado, pero **si el nodo muere en movimiento, la última orden queda pegada**.
4. **`timeout` sin `--foreground` no recibe el Ctrl+C** [Probable]: por eso el Ctrl+C no frenó en las corridas de exp5 de la recta ni en 3A. `rc1_correr.sh` usa `timeout --foreground` desde el commit `fc2c8ff`; **su efecto no está verificado en el robot**.
5. **`/odom` no se reinicia entre corridas:** el CSV trae x, y, yaw **absolutos**; el nodo y `09_plot_csv.py` miden relativo al inicio.

---

## 4. El script de corrida: `scripts/rc1_correr.sh`

**Qué es:** un envoltorio que arma y ejecuta el mismo comando que antes se escribía a mano. **No modifica** el nodo del curso.

```bash
scripts/rc1_correr.sh <giro|recta|3a|3b> <nombre> [clave=valor …] [--dry-run] [-y] [--sin-bag] [--sin-chequeos]
```

| Prueba | Base que añade | CSV | Límite (`timeout`) | Bag |
|---|---|---|---|---|
| `giro` | `experimento=giro90` | `csv/exp2_real_giro90_<nombre>.csv` | 15 s | no |
| `recta` | `experimento=recta line_offset=0.10 ki=0.5` | `csv/exp1d_real_<nombre>.csv` | 40 s | no |
| `3a` | `experimento=cuadrado_abierto` | `csv/exp3a_real[_<nombre>].csv` | 150 s | `bags/rc1_real_3a[_<nombre>]` |
| `3b` | `experimento=cuadrado` | `csv/exp3b_real_<nombre>.csv` | 180 s | `bags/rc1_real_3b_<nombre>` |

**Pasos (en orden, en el script):**
1. **Comprobaciones:** `sha256` del nodo (`HASH_CTRL`, `HASH_CORE`), `ROS_DOMAIN_ID=8`, un solo `/odom_corrector`, un único publicador en `/odom`, `/YB_Car_Node` presente, batería ≥ 70, hora del contenedor, y que no existan ya el CSV ni el bag.
2. **Confirmación:** pide escribir `SI` (robot alineado, zona despejada, persona en el interruptor).
3. **Bag** (solo 3A/3B): `ros2 bag record /odom /cmd_vel /tf -o <bag>` (línea 114) — los tres tópicos que pide el reto.
4. **Nodo:** `timeout --foreground -s INT <T> python3 scripts_pdi/cuadrado_controller.py --ros-args $(python3 scripts/rc1_args.py robot_real <base> <extras> log_csv=<csv>)` (línea 122), con la salida a `<csv>.nodo.log` (`tee`).
5. **`parar()`** (línea 106, activada por `trap parar EXIT INT TERM`, línea 111): publica ceros 3 s (`ros2 topic pub -r 10 -t 30 /cmd_vel … "{}"`) y cierra el bag.
6. **Resumen:** extrae del log la línea `FIN. error de cierre = … cm, yaw acumulado = … deg, tiempo = … s` y propone el comando de `rc1_anotar_real.py`.

**Trucos que conviene saber:** `scripts/rc1_args.py` lee `config/rc1_pid.yaml` (bloque `robot_real`) y los `clave=valor` extra **pisan** los del YAML; los cambios **no se acumulan** entre corridas (cada una parte del YAML). La plantilla `recta` fija `ki=0.5`; para `ki=0.1` hay que pasarlo explícitamente. La sugerencia `ki=0.5` que imprime el script al final es una plantilla fija **incorrecta** para estas corridas.

---

## 5. E5 — Giro de 90° (2 pt)

**Qué se pide:** bringup con `/odom` verificado; `giro90` con transportador y **error final ≤ 3°**. El docente aclaró que **una** prueba basta (la corrida que acredita E5 es `r3`).

**Ejecución:** `scripts/rc1_correr.sh giro <nombre>` → `experimento=giro90`, `kp_yaw=1.0`, `ki_yaw=0.0`, `kd_yaw=0.6`, `max_angular=1.0`, `linear_speed=0.10`.

### Quién hace el giro, dónde y cómo se controla
| Pregunta | Respuesta |
|---|---|
| ¿Dónde inicia? | `main()` de `cuadrado_controller.py` → primer ciclo → `Runner.update` encuentra `ESPERA` y ejecuta `start()` |
| ¿Quién fija el objetivo? | `start()`, líneas 135–136: `yaw_target = yaw + π/2`, estado `GIRA` |
| ¿Quién calcula ω? | `update`, estado `GIRA`: `e_yaw = normalize(yaw_target − yaw)` (172); `w = pid_yaw.step(e_yaw, dt)` (178); recorte a `max_angular` (189) |
| ¿Quién publica la orden? | El nodo, en `/cmd_vel` (solo `angular.z`; v = 0 en `GIRA`) |
| ¿Quién gira físicamente? | `YB_Car_Node` → ruedas izquierda y derecha en sentidos opuestos |
| ¿De dónde sale el `yaw` medido? | De `/odom` (`odom_corrector`, con `k_ang` = 1.0863) |
| ¿Quién decide que terminó? | `|e_yaw| < yaw_tol` durante `settle_time` (179–181) → `_turn_done` (línea 210) → `FIN` |
| ¿Quién para? | En `FIN`: v = ω = 0 (183–187); además `parar()` del script |

### Historia de la sintonía (lo que hay que poder contar)
- **Partida:** las ganancias del simulador (`kp_yaw` 10, `kd_yaw` 0.6): en el real **oscilaba ±15–20° (período ≈ 2.6 s)**, no se asentaba. Causa: retardo del motor y `/odom` a 11 Hz.
- **Re-sintonía #1:** `kp_yaw` 10 → **1.0**. Resultado: `FIN` en 5.0–8.7 s, sin sobreimpulso.
- **Medidas con transportador (7):** 85°, 90°, 87°, 83°, 93°, 91°, 88°: media 88.1°, desviación ≈ 3.5°; 5 de 7 dentro de ±3°.
- **Evidencia que acredita E5:** `r3`, 91° (error 1°). Todas las demás siguen registradas (`docs/rc1_g8/registro_E5_giro_real.md`).
- **Calibración:** con `r` y `b_eff` propios no hubo sesgo sistemático; la dispersión es deslizamiento y medida.

### Registro de E5
CSV `csv/exp2_real_giro90_*.csv` (copia de `r3` en `exp2_real_giro90.csv`); PNG `plots/exp2_real_giro90_r*.png`; hoja: filas `2 / real` con las predicciones; `rc1_figuras_giro.py` compara predicción y medida.

---

## 6. E6 — Recta de 2 m (2 pt)

**Qué se pide:** 3 corridas con CSV y cinta; **desvío lateral final medido ≤ 5 cm** (el docente: al menos una < 5 cm).
**Montaje:** línea de 2.4 m en el piso; el robot arranca con su centro **10 cm a la izquierda** de la línea virtual (`line_offset=0.10`), alineado en paralelo (tope fijo y dos lecturas de distancia, rueda delantera y trasera, ±5 mm).

### Quién hace la recta, dónde y cómo se controla
| Pregunta | Respuesta |
|---|---|
| ¿Cómo empieza? | `start()` (línea 138): estado `AVANZA` |
| ¿Quién calcula ω? | `update`, estado `AVANZA`: `psi = yaw_obj`; `d` = desvío lateral; **`e_line = d + line_offset`** (158); **`w = −pid_line.step(e_line, dt)`** (166) |
| ¿Quién fija la velocidad lineal? | `v = p.v` = `linear_speed` = 0.10 m/s (línea 159) |
| ¿Cuándo termina? | `s ≥ side` (167) → `_side_done` (línea 197–199): en `recta` pasa a `FIN` |
| ¿Qué mide el CSV? | `e_line` es **según `/odom`**, no el desvío físico; el criterio lo da la cinta |
| ¿Quién para? | `FIN` (v = ω = 0); luego `parar()` |

### Ganancias y su historia
| | Línea (`kp / ki / kd`) | Cambio frente a la partida |
|---|---|---|
| Simulador / partida | 3.0 / 0.5 / 4.0 | – |
| Real, final | **1.0 / 0.1 / 8.0** | `kp` 3 → 1, `ki` 0.5 → 0.1, `kd` 4 → 8 |

- Con la partida el robot oscilaba (±13 cm en `/odom`, ≈ 30 cm físicos).
- `ki` 0.5 era el más desestabilizante (retardo ≈ 0.7 s); `kd` alto amortigua la oscilación causada por el retardo.
- **Honestidad:** hubo ≈ 13 pruebas exploratorias (exp1–exp13, exp5 inválida por la cinta métrica) y las ganancias finales superan el máximo de tres re-sintonías (ver sección 11).

### Resultados oficiales de E6
| Corrida | Desvío físico (cinta) | Cierre `/odom` | `FIN` | Yaw `/odom` |
|---|---|---|---|---|
| `run1` | **0.6 cm** derecha | 200.9 | 20.9 s | +2.0° |
| `run2` | **1.5 cm** izquierda | 200.8 | 21.0 s | −0.8° |
| `run5` (anotada como `run3`) | **0.5 cm** derecha | 200.6 | 21.0 s | +1.6° |

`run3` (fallo físico: el ROSCar se trabó con la cinta métrica) y `run4` (mal posicionado, 6 cm) se conservan y se declaran. Media de las tres válidas: 0.87 cm.

**Qué mostró el CSV:** según `/odom` el error final fue 2.7–3.8 cm (sesgo de ≈ 3 cm respecto de la cinta); `FIN` cae justo en el **valle del sobrepaso** (el mínimo de `e_line` coincide con el final), así que el resultado depende de dónde corta el tramo de 2 m.

---

## 7. E7 — El cuadrado de 2 × 2 m (4 pt) y el BONUS

**Qué se pide:** 3A una vez y 3B tres veces, con cinta y bags; **media de 3B ≤ 25 cm y menor que la de 3A**. En la demo: una corrida de 3B y el BONUS (3B < 10 cm, con 3A para comparar).

### 7.1 3A — lazo abierto (`experimento=cuadrado_abierto`)
| Pregunta | Respuesta |
|---|---|
| ¿Cómo decide el fin de un lado? | **Solo por tiempo**: `t_state ≥ side / v` = 20 s (línea 161); no usa `/odom` |
| ¿Cómo gira? | `w = turn_w` (0.8 rad/s) durante `(π/2) / (turn_w · turn_scale)` ≈ 1.96 s (líneas 173–176) |
| ¿Qué retroalimentación tiene? | Ninguna: el error de cada giro y de cada recta se acumula |
| ¿Qué se midió? | Cierre `/odom` **97.4 cm**; cierre real (cinta) **107.9 cm** (89 + 61 cm); yaw `/odom` 381.7°; `FIN` 87.9 s; primer giro ≈ **115°** |
| Hoja | `3A / real / unica` |

### 7.2 3B — lazo cerrado sobre `/odom` (`experimento=cuadrado`)
| Pregunta | Respuesta |
|---|---|
| ¿Cómo va una recta? | Igual que en E6: `e_line`, `w = −PID` (líneas 153–169) |
| ¿Cómo gira? | `e_yaw = normalize(yaw_target − yaw)`, `w = +PID_yaw` (171–181); `yaw_target = yaw_obj + π/2` (línea 200) |
| ¿Qué es `yaw_obj`? | El **rumbo nominal** de cada lado: avanza 90° por lado (línea 209), independiente del rumbo real del robot |
| ¿Dónde arranca cada lado? | **`self.sx, self.sy = x, y`** (línea 213): en la posición **que dice `/odom`** al terminar el giro |
| ¿Cuántos lados? | `k ≥ n_sides` (4) → `FIN` (línea 210) |
| ¿Qué calcula al final? | `closure_error` = distancia al origen según `/odom` (línea 186) |
| Ganancias | Línea 1.0 / 0.1 / 8.0; giro `kp_yaw` 1.0, `ki_yaw` 0, `kd_yaw` **0.3** (0.6 al principio) |

**La lección central de 3B [Seguro, del código]:** el nodo **no tiene ninguna referencia física del cuadrado**. Cada lado se vuelve a anclar en la posición odométrica del robot y usa rumbos nominales, así que cualquier desplazamiento físico que `/odom` no vea (derrape, giro de más) **se acumula sin que el lazo lo corrija**. Por eso `/odom` dice 2–4 cm y la cinta mide decenas de cm.

**Exploratorias de 3B (todas declaradas):**
| Prueba | `kd_yaw` | Cierre `/odom` | Cierre físico | `FIN` |
|---|---|---|---|---|
| exp1 | 0.6 | 2.0 cm | > 36 cm | 109.5 s |
| exp2 | 0.3 | 1.8 cm | ≈ 36.5 cm | 101.6 s |
| exp4 | 0.3 | 3.7 cm | 25.9 cm | 102.2 s |
| exp5 | 0.3 | 3.4 cm | 19.1 cm | 103.5 s |

**Según `/odom` (exp2 y exp4):** cada giro termina ≈ 1.5° corto (por la tolerancia `yaw_tol`) y los errores laterales máximos en las rectas son 0.8–3.8 cm; en el piso, el robot se pasaba 10–15° en algunas esquinas, que `/odom` no registra. Bajar `kd_yaw` a 0.3 redujo ≈ 10 veces el *chatter* de ω (74 → 7 muestras con ω < −0.2), pero no mejoró el cierre físico de forma medible.

**Resultados oficiales de 3B:** **[Pendiente E7]** run1 / run2 / run3 y media (meta ≤ 25 cm y < 107.9 cm). Predicciones en `docs/rc1_g8/predicciones_E7_3B.md` (a subir antes de correr). **BONUS:** **[Pendiente E7]**.

---

## 8. Parámetros: simulador frente a robot real

| Parámetro | Simulador | Robot real | Por qué |
|---|---|---|---|
| `linear_speed` | 0.20 m/s | **0.10 m/s** | velocidades suaves del Anexo C |
| `max_angular` | 2.0 rad/s | **1.0 rad/s** | seguridad y límite de la planta |
| `kp / ki / kd` (línea) | 3.0 / 0–0.5 / 4.0 | **1.0 / 0.1 / 8.0** | retardo ≈ 0.7 s y `/odom` a 11 Hz hacen oscilar con ganancias altas |
| `kp_yaw / ki_yaw / kd_yaw` | 10 / 0 / 0.6 | **1.0 / 0 / 0.6** (E5 y 3B-exp1); **1.0 / 0 / 0.3** (3B final) | con 10 el giro oscilaba ±15–20°; 0.3 reduce el chatter |
| `bias_w` | 0.03–0.06 (inyectado) | **0** | el robot real trae su propio sesgo |
| `line_offset` | 0.10 en la recta | 0.10 en E6; **0.0** en el cuadrado | en el cuadrado no hay desplazamiento inicial |
| `/odom` | ≈ 50 Hz | ≈ 11 Hz | planta real |
| `integral_limit` | 0.5 | 0.5 | anti-windup |

**Qué cada parámetro mueve (para explicar el comportamiento):**
- `kp`: cuánto corrige por unidad de error. Alto → más rápido, pero con retardo oscila.
- `ki`: elimina el error constante; añade retardo.
- `kd`: amortigua; con `/odom` a 11 Hz y control a 30 Hz da picos en cada muestra nueva.
- `kp_yaw`, `ki_yaw`, `kd_yaw`: lo mismo, para el giro (error en rad).
- `max_angular`: techo de ω; en el real satura al inicio de cada giro.

---

## 9. Dónde se registra cada cosa y cómo se hace cada gráfica

| Qué | Archivo | Quién lo crea |
|---|---|---|
| Datos de la corrida | `csv/…csv`: `t, x, y, yaw, v, w, e_line, e_yaw, estado` | el nodo del curso (`log_csv`) |
| Lo que imprimió el nodo | `csv/….nodo.log` (incluye `FIN. error de cierre…`) | `rc1_correr.sh` (`tee`) |
| Bag de ROS 2 | `bags/rc1_real_3a…`, `bags/rc1_real_3b_…` (`/odom`, `/cmd_vel`, `/tf`) | `rc1_correr.sh` (`ros2 bag record`) |
| Medida física | cinta/transportador, **a mano** | dos personas |
| Registro central | `hoja_resultados.csv` | `rc1_anotar_real.py` |
| Análisis automático | pantalla, JSON o `plots/<nombre>_analisis.png` | `rc1_analiza_real.py` |
| Gráfica clásica | `<csv>.png` (trayectoria + yaw o error lateral) | `docs/rc1/09_plot_csv.py` (versión parcheada) |

### `scripts/rc1_analiza_real.py`
Lee uno o varios CSV del nodo, **detecta el tipo** (giro, recta, cuadrado) y calcula: tiempo hasta `FIN`, errores de línea, cruces de la línea (umbral ±0.5 cm), permanencia en ±2 cm, inversiones de ω, yaw acumulado, cierre según `/odom` y, en el cuadrado, cada lado y cada giro. `--criterios e5|e6|e7a|e7b` contrasta con las predicciones; `--png` dibuja; propone el comando de `rc1_anotar_real.py`. **Lo que mide sale de `/odom`: no sustituye la cinta ni el transportador.** Solo usa la biblioteca estándar (matplotlib solo para `--png`).

### `scripts/rc1_anotar_real.py`
`python3 scripts/rc1_anotar_real.py <2|1D|3A|3B> <etiqueta> clave=valor … [--nota "…"]`. Identifica la fila por (prueba, planta=real, etiqueta); si no existe la crea con las ganancias de `robot_real`. Columnas propias: `cierre_odom_cm`, `cierre_real_cm`, `yaw_acum_deg`; el resto (por ejemplo `desvio_cm`, `bag`) va a `notas` como `clave=valor;`. **Usa el módulo en `desvio_cm`** y deja el lado en la nota.

### `docs/rc1/09_plot_csv.py`
`leer()` carga el CSV, resta la pose inicial y la rota al primer rumbo; en la **recta** descarta las filas `FIN` (parche del grupo); calcula las métricas con `core_cuadrado.metricas` y guarda `<csv>.png` (trayectoria + yaw o error lateral).

### `scripts/rc1_verificar.py`
Estima el avance contra la rúbrica. E6 y E7 cuentan solo las filas con etiqueta `run1..3`.

**Copia al repositorio:** el CSV, el log y el bag se copian del contenedor al host (`docker cp`) y de ahí al PC (`scp`); el commit se hace **desde el clon del PC**, no desde el Pi (el reloj del Pi no es fiable).

---

## 10. Simulado frente a real: la tabla que más se pregunta

| Aspecto | Simulador | Robot real | Dato propio |
|---|---|---|---|
| Quién mueve | `vehicle.py` (cinemática) | `YB_Car_Node` + motores | – |
| `/odom` | 50 Hz, ruido multiplicativo | ≈ 11 Hz, ruedas corregidas | – |
| Verdad terreno | `/sim/pose` | cinta y transportador | – |
| Empujón / derrape | empujón del piso (no visto por `/odom`) | derrape de las 4 ruedas (`b_eff = χ·b`) | 3B real 19–36 cm frente a `/odom` 2–4 cm |
| Retardo de motores | no (solo aceleración) | sí (≈ 0.5–0.7 s) | `kp_yaw` 10 oscila ±15–20° |
| Paro si falla el mando | `cmd_timeout` 0.5 s | **ninguno** | exp5 de la recta, 3A |
| Cierre del cuadrado (PID) | 3B 58.7 cm (real) / 0.5 (`/odom`) | 3B 19–36 cm / 2–4 cm | – |
| 3A (lazo abierto) | 16.1 cm (real) | **107.9 cm** (real) | el giro por tiempo se pasa |

**Lección común [Seguro]:** un lazo cerrado es tan bueno como el sensor que lo cierra. En ambos casos el PID cierra sobre `/odom`; en el simulador `/odom` no ve el empujón del piso y en el robot real no ve el derrape.

---

## 11. Seguridad, paros y honestidad (hay que saber explicarlos)

### Quién para qué
| Situación | Quién para | Verificado |
|---|---|---|
| El nodo llega a `FIN` | El propio nodo (v = ω = 0 en cada ciclo) | Sí |
| El nodo muere antes de `FIN` | Nadie: el robot conserva la última orden. `parar()` publica ceros 3 s; la persona usa el interruptor | Parcial |
| No llega `/odom` en 0.5 s | El nodo (`odom_timeout`) | Por diseño |
| Ctrl+C | Debería activar `parar()`; con `timeout` sin `--foreground` no llegaba | **`--foreground` aplicado, prueba pendiente** |

### Lo que hay que contar sin esconderlo
- **Re-sintonías:** frente a la partida del simulador la configuración final cambia **cinco parámetros** (`kp_yaw`, `kp`, `ki`, `kd`, `kd_yaw`) y el reto permite **tres**. La consulta al docente está pendiente. Las pruebas exploratorias están todas guardadas.
- **Predicciones:** las de E6 con las ganancias finales y las de 3B se escribieron **después** de varias exploratorias y así están declaradas; la de 3A se subió antes de correr.
- **Descartes:** `run3` (fallo físico) y `run4` (6 cm, mal posicionado) de E6.
- **Ctrl+C:** no frenaba la recta en una corrida ni 3A; el único paro garantizado es el interruptor.

---

## 12. Qué comprobar en el contenedor (para no contestar «de memoria» lo que no se leyó)

```bash
grep -n "class PID" -A28 scripts_pdi/core_cuadrado.py
grep -n "yaw_tol\|settle_time\|control_rate\|odom_timeout\|n_sides" scripts_pdi/core_cuadrado.py scripts_pdi/cuadrado_controller.py
grep -n "create_subscription\|create_publisher\|create_timer\|log_csv\|csv\|finally\|Twist()" scripts_pdi/cuadrado_controller.py
ros2 param dump /odom_corrector
ros2 node info /YB_Car_Node
```
Con eso sabes: cómo se actualiza la integral, cuánto valen `yaw_tol` y `settle_time`, en qué función se escribe el CSV y se publica `/cmd_vel`, qué tópicos usa cada nodo.

---

## 13. Banco de preguntas probables (con respuesta corta)

### Arquitectura y flujo
1. **¿Qué nodo mueve el robot real?** `YB_Car_Node`: es el único suscriptor de `/cmd_vel` y comanda los motores de la placa.
2. **¿Quién calcula las velocidades?** El nodo del curso (`Runner.update` en `core_cuadrado.py`); `cuadrado_controller.py` solo lo llama a 30 Hz y publica `/cmd_vel`.
3. **¿De dónde viene `/odom` y qué es `odom_corrector`?** De `/odom_raw` (`YB_Car_Node`, ruedas) corregido con `k_lin` 0.9677 y `k_ang` 1.0863 (radio 0.03145 y separación 0.2138).
4. **¿Por qué se calibró `r` y `b_eff`?** Porque el lazo cierra sobre `/odom`: si las ruedas están mal, el robot converge al valor equivocado (≈ 8° de error por giro con valores ajenos).
5. **¿Qué hace `rc1_correr.sh`?** Comprueba el entorno, graba el bag (3A/3B), ejecuta el nodo con `timeout --foreground`, publica ceros al terminar o cortar y propone la anotación.
6. **¿Qué hace `rc1_args.py`?** Convierte el bloque `robot_real` de `config/rc1_pid.yaml` en `-p` con punto decimal; los `clave=valor` extra pisan el YAML.
7. **¿Dónde se registran los resultados y adónde van?** CSV del nodo y `.nodo.log` en `csv/`, bags en `bags/`, medidas a mano; `rc1_anotar_real.py` los pasa a `hoja_resultados.csv`; se copian al PC y se suben a git.
8. **¿Cómo se generan las gráficas?** `09_plot_csv.py` (trayectoria y error/yaw por CSV) y `rc1_analiza_real.py --png`.

### Por experimento
9. **E5: ¿quién hace el giro y en qué parte del código?** `Runner.update`, estado `GIRA` (líneas 171–181), con objetivo `yaw + π/2` fijado en `start()` (135–136).
10. **E5: ¿cómo lo controla y quién lo para?** PID del giro sobre `e_yaw` (`kp_yaw`, `ki_yaw`, `kd_yaw`); termina con `|e_yaw| < yaw_tol` durante `settle_time` y pasa a `FIN` (línea 210), donde v = ω = 0.
11. **E5: ¿por qué `kp_yaw` 1.0 y no 10?** Con 10 oscilaba ±15–20° (retardo ≈ 0.5–0.7 s y `/odom` a 11 Hz); con 1.0 termina en 5.0–8.7 s sin sobreimpulso.
12. **E6: ¿qué hace la recta y qué mide el PID?** Mantiene el robot sobre una línea virtual: `e_line = d + line_offset`, `w = −PID(e_line)`; termina cuando `s ≥ side`.
13. **E6: ¿qué es `line_offset`?** Desplaza la línea virtual 10 cm a la derecha del inicio: el robot arranca 10 cm a la izquierda de ella.
14. **E6: ¿quién mide el desvío?** La cinta, perpendicular desde el centro del robot a la raya; el `e_line` del CSV viene de `/odom` y no es el desvío físico.
15. **E7 3A: ¿cómo funciona?** Lazo abierto: avanza `side/v` = 20 s y gira un tiempo fijo `(π/2)/(turn_w·turn_scale)`; no corrige nada.
16. **E7 3B: ¿cómo cierra el cuadrado?** Recta con PID de línea y giro con PID de yaw sobre `/odom`; cada lado arranca desde la posición odométrica (`self.sx, self.sy = x, y`, línea 213) con rumbo nominal.
17. **E7: ¿por qué 3B cierra a 2 cm en `/odom` y a 19–36 cm en la cinta?** Porque `/odom` no ve el derrape ni los giros de más, y el nodo no tiene referencia física del cuadrado.
18. **E7: ¿qué significa `FIN`?** El estado final: v = ω = 0 y se calcula `closure_error`; el proceso Python sigue vivo hasta que se corta.

### Ganancias y simulado frente a real
19. **¿Qué hace cada ganancia?** `kp`: corrige en proporción al error; `ki`: quita el error constante; `kd`: amortigua; las `_yaw` lo mismo en el giro.
20. **¿Qué cambió entre las ganancias del simulador y las del real?** Línea 3/0.5/4 → 1.0/0.1/8.0; giro `kp_yaw` 10 → 1.0 (y `kd_yaw` 0.3 en 3B); `max_angular` 2 → 1.0; `linear_speed` 0.2 → 0.1.
21. **¿Dos cosas que el simulador no modela?** Retardo/inercia de los motores y `/odom` lento con derrape de las cuatro ruedas.
22. **¿Por qué se sintoniza un parámetro por prueba?** Para atribuir cada cambio a una causa.

### Seguridad
23. **¿Quién para el robot si el nodo muere?** Nadie por sí solo: el robot conserva la última orden; por eso hay ceros en `parar()` y una persona en el interruptor.
24. **¿Por qué el `Twist()` final falla?** Con Ctrl+C o `timeout`, rclpy ya cerró el contexto cuando el `finally` intenta publicar (`RCLError`).
25. **¿Por qué `timeout --foreground`?** Sin esa opción `timeout` crea su propio grupo de procesos y no recibe el Ctrl+C de la terminal.

### Sobre el trabajo del grupo
26. **¿Cuántas re-sintonías hicieron?** Cinco parámetros distintos frente a un máximo de tres, con ≈ 13 exploratorias de la recta y 5 de 3B, todas guardadas. Consulta pendiente al docente.
27. **¿Qué mejorarían para el RC-2?** Una medida independiente del giro (el giroscopio `/imu`, que existe y nadie usa), controlar a la frecuencia real de `/odom` y más corridas para separar el efecto de cada ganancia del ruido.

---

## 14. Tus 5 minutos antes de la demo en vivo

1. **Una corrida de cada parte**, sin repetir: ensayen el procedimiento completo antes (alineación a ±5 mm, tope fijo, cinta fuera de la trayectoria, persona en el interruptor).
2. E5: `scripts/rc1_correr.sh giro vivo`. E6: `scripts/rc1_correr.sh recta vivo kp=1.0 ki=0.1 kd=8.0 side=2.0`. E7: `scripts/rc1_correr.sh 3b vivo kp=1.0 ki=0.1 kd=8.0 kp_yaw=1.0 ki_yaw=0.0 kd_yaw=0.3 side=2.0 linear_speed=0.10 max_angular=1.0`.
3. Prueba de parada (`Ctrl+C` con `--foreground`) antes de empezar: no corran 3B sin verificarla.
4. Midan con dos personas y digan en voz alta qué miden (cinta y centro del robot).
5. Cada uno repase las preguntas de **su rol** y las de **otro rol**: Integración (simulador, bringup, repo, bags, hoja), Control (ganancias, orden de sintonía, `config/rc1_pid.yaml`), Planificación (predicciones, matriz, seguridad, cinta) y Percepción (gráficas, `/odom` frente a lo real).
