# Guía de estudio para la defensa — RC-1 (Grupo 8)

**Para quién:** todos los integrantes. La defensa sortea a **uno**, hace **4 preguntas del banco**, **sin código ni informe a la vista**, y **al menos una** es del trabajo de **otro rol**. El puntaje (2 pt) es del grupo: 0.5 completa y justificada · 0.3 correcta sin justificación · 0.2 parcial · 0.
**Cómo usarla:** cada pregunta tiene una *respuesta corta* (30 s), el *porqué* y *los datos propios* que la respaldan. Memoricen los datos; justificar vale más que acertar.
**Estado:** E1–E6 con datos finales; **los resultados oficiales de E7 (3B × 3) están marcados `[Pendiente E7]`** y se completan al terminar. Todo lo que no se midió aquí se dice como «no sabemos».

## 0. Datos que hay que saber de memoria

| Tema | Dato |
|---|---|
| Robot / grupo | ROSCar 4 · Grupo 8 · `ROS_DOMAIN_ID=8` · Raspberry Pi 5 · ROS 2 Humble |
| Odometría | `/odom_raw` (firmware, ruedas) → `odom_corrector` → `/odom` a **≈ 11 Hz** (50 Hz en el simulador) |
| Calibración propia | `r` = 0.03145 m, `b_eff` = 0.2138 m (firmware: 0.0325 / 0.24) → `k_lin` 0.9677, `k_ang` 1.0863 |
| Línea, simulador → real | `Kp/Ki/Kd` **3.0 / 0.5 / 4.0 → 1.0 / 0.1 / 8.0** |
| Giro, simulador → real | `kp_yaw` **10 → 1.0**; `kd_yaw` 0.6 → **0.3** (solo en 3B) |
| Velocidades | `linear_speed` 0.10 m/s · `max_angular` 1.0 rad/s (2.0 en el simulador) |
| E5 giro real | `kp_yaw` 10 oscila ±15–20° (T ≈ 2.6 s); con 1.0: `FIN` en 5.0–8.7 s; corrida elegida 91° (error 1°); 7 medidas 88.1° ± 3.5° |
| E6 recta real | 0.6 cm der., 1.5 cm izq., 0.5 cm der. (meta ≤ 5 cm). Con `Kd` 4 en pruebas previas: ≈ 10 y ≈ 2 cm |
| E7-3A (lazo abierto) | cierre `/odom` 97.4 cm · **cierre real 107.9 cm** · yaw `/odom` 381.7° · `FIN` 87.9 s · primer giro ≈ 115° |
| E7-3B exploratorias | cierre real > 36, 36.5, 25.9, 19.1 cm; cierre `/odom` 2.0 / 1.8 / 3.7 / 3.4 cm; `FIN` ≈ 102–110 s |
| E7-3B oficiales | `[Pendiente E7]` run1 / run2 / run3 y media (meta ≤ 25 cm y < 3A) |
| Sensibilidad angular | 1° de error de yaw = 2·tan(1°) = **3.49 cm** a los 2 m (≈ 9.8 cm en cuatro lados) |
| Simulador | 1D error final 0.30 cm · giro propio (2p): sobreimpulso 0 %, asentamiento 1.01 s · 3B: `/odom` 0.5 cm frente a **58.7 cm real** |

## 1. Banco de preguntas con respuestas

### 1. Dibujen el lazo con r, e, u e y para la recta. ¿Qué es cada una en el robot?
- **r** (referencia): estar sobre la línea virtual, es decir, error lateral 0 (más el `line_offset`).
- **y** (salida medida): la posición lateral `d` del robot respecto de la línea, calculada con `/odom`.
- **e** = `d + line_offset` (positivo = a la izquierda de la línea).
- **u**: la velocidad angular ω que el PID envía en `/cmd_vel`. La velocidad lineal `v` es constante (0.10 m/s).
- La planta es el robot (motores, ruedas, retardo). El sensor es `/odom`, a ≈ 11 Hz en el real.
- **Dibujo:** r → (+/−) → e → PID → u=ω → robot → y (posición lateral) → `/odom` → retroalimentación al sumador.

### 2. Cálculo con Kp = 3, Ki = 0.5, Kd = 4, e = 0.060, e_ant = 0.063, integral previa = 0.100, dt = 1/30
Con la forma estándar (`integral = integral_prev + e·dt`; D sobre el error):
- **P** = 3 · 0.060 = **0.18**
- integral = 0.100 + 0.060/30 = 0.102 → **I** = 0.5 · 0.102 = **0.051**
- **D** = 4 · (0.060 − 0.063)/(1/30) = 4 · (−0.090) = **−0.36**
- PID = 0.18 + 0.051 − 0.36 = **−0.129**; en la recta **ω = −PID = +0.129 rad/s**.
- *Comprobar antes de la defensa en el código (`class PID` de `core_cuadrado.py`)* si el nodo actualiza la integral antes de calcular I y si recorta con `integral_limit` (0.5; aquí no llega). Si el orden es otro, I cambia a 0.05.

### 3. ¿Por qué ω = −PID(e) en la recta? ¿Qué pasa si se invierte el signo?
- `e > 0` significa que el robot está a la **izquierda** de la línea; para volver hay que girar a la **derecha**, y en este robot ω > 0 gira a la **izquierda**. Por eso ω = −PID(e).
- Con el signo invertido el lazo es de **realimentación positiva**: cuanto más se aleja, más gira hacia afuera y diverge.
- El giro usa `ω = +PID(e_yaw)` con `e_yaw = yaw_obj − yaw`, porque ahí el error ya está definido en el sentido del giro.

### 4. ¿Por qué solo P oscila alrededor de la línea y qué hace Kd?
- La posición lateral es la **integral del rumbo**, que a su vez es la integral de ω. Con P puro hay un efecto restaurador sin amortiguamiento y, con el retardo del robot real, el sistema cruza la línea una y otra vez.
- **Kd** reacciona a la *velocidad* del error: se anticipa y **amortigua**. En el simulador, 1B (solo P) tuvo 2 cruces y 1C (P + D) tuvo 0.
- En el real, subir `Kd` a 8.0 redujo el sobrepaso de ≈ 7.5 cm (`Kd` 4) a ≈ 3.7 cm, con 1 solo cruce.

### 5. ¿Qué elimina Ki? ¿Qué es el wind-up y cómo lo evita el nodo?
- **Ki** elimina el **error en régimen permanente** (sesgo constante), por ejemplo la deriva sesgada de un motor.
- **Wind-up:** si el error persiste (saturación o error grande), la integral crece sin límite y luego provoca un sobreimpulso enorme al volver.
- El nodo lo evita con un **límite de la integral** (`integral_limit`, 0.5 en nuestras corridas) y con `reset` al empezar cada lado.
- En el real `Ki` 0.5 resultó el más desestabilizante (retardo ≈ 0.7 s); por eso se bajó a 0.1.

### 6. ¿Por qué se sintoniza en el orden Kp → Kd → Ki y con un parámetro por prueba?
- **Kp** primero: da la respuesta básica. **Kd** después: amortigua la oscilación que crea Kp. **Ki** al final y solo si queda sesgo, porque añade retardo y puede inestabilizar.
- **Un parámetro por prueba:** para poder atribuir cada cambio de comportamiento a una causa.
- **Honestidad que conviene tener preparada:** en el real hicimos más cambios de los permitidos (ver la tabla de la sección 2 de esta guía).

### 7. ¿Qué pasa con el giro de 90° al subir el Kp del giro y qué aporta Kd? Muestren sus curvas
- Subir `kp_yaw` hace el giro más rápido, pero con retardo y `/odom` lento **sobrepasa y oscila**. En el simulador `kp_yaw` 10 asienta en 1.0 s sin sobreimpulso (2p); en el real **no se asienta**: oscila ±15–20° (T ≈ 2.6 s).
- Con `kp_yaw` 1.0 el giro real termina sin sobreimpulso en 5.0–8.7 s (más lento, pero estable).
- **Kd** del giro amortigua. Con `/odom` a 11 Hz y control a 30 Hz, la derivada da picos en cada muestra nueva y ceros en las repetidas (dientes de sierra en ω); bajar `kd_yaw` de 0.6 a 0.3 redujo esas inversiones ≈ 10 veces (74 → 7 muestras).
- Curvas: `plots/` del simulador (2a/2b/2c/2p) y el CSV de E5.

### 8. ¿Qué diferencia hay entre el cierre que imprime el nodo y el cierre medido con cinta? ¿Cuál es el real?
- El nodo imprime la distancia entre la pose inicial y la final **según `/odom`**. El **real** es el de la **cinta** (centro inicial a centro final).
- Datos: 3A real: `/odom` 97.4 frente a **107.9 cm**. 3B exploratorias: `/odom` 2–4 cm frente a **19–36 cm**.
- 3B parece perfecto para `/odom` porque el nodo cierra el lazo sobre `/odom`, y `/odom` no ve el deslizamiento de las ruedas.

### 9. Un grado de error de yaw: ¿cuántos cm a los 2 m? ¿Por qué obliga a cerrar el lazo del giro?
- 2 · tan(1°) ≈ **3.49 cm** por lado (≈ 9.8 cm en cuatro lados).
- En lazo abierto (3A) el giro por tiempo no se corrige: 8° de error por esquina dan ≈ 73 cm de cierre. Por eso 3B mide el yaw y corrige.
- Pero 3B corrige sobre `/odom`, no sobre el giro físico: queda limitado por lo que `/odom` no ve.

### 10. ¿Qué es /sim/pose, por qué no existe en el robot real y qué la reemplaza allí?
- Es la **pose REAL del robot en el simulador** (una «cinta métrica virtual»), distinta de `/odom` (estimada).
- No existe en el real porque no hay un sensor de posición absoluta. La reemplaza la **cinta métrica y el transportador**, con dos personas.

### 11. ¿Qué es el empujón del piso y por qué /odom no lo ve? ¿Qué sensor sí vería el giro que causa?
- En el simulador, el piso empuja y rota al robot (modela el deslizamiento de las ruedas). `/odom` se calcula de las **velocidades de las ruedas**, que no cambian con ese empuje.
- El sensor que **sí** vería el giro es el **giroscopio / IMU** (`/imu`). En nuestro robot `/imu` existe y nadie lo usa; propuesta para el RC-2.

### 12. Nombren dos cosas que el simulador no modela y cómo cambiarán los resultados en el real
- **Retardo e inercia de los motores:** el simulador solo limita la aceleración. En el real exige menos ganancia (`kp_yaw` 10 → 1.0, `Ki` 0.5 → 0.1).
- **Frecuencia de `/odom` y derrape:** 11 Hz frente a 50 Hz, y derrape de las cuatro ruedas (`b_eff = χ·b`). Dan chatter derivativo y un cierre real de decenas de cm.
- También: sesgo real de los motores, error de `r` y `b_eff`, y el límite de `max_angular`.

### 13. Si el lazo se cierra sobre /odom, ¿por qué calibrar r y b_eff (RC-0) sigue importando?
- `/odom` integra las velocidades de las ruedas con `r` y `b_eff`. Si están mal, el PID cierra con una medida sesgada, **y el robot converge al valor equivocado** (por ejemplo, un `k_ang` errado da giros de 90° ± ~8 % en el piso).
- Nuestro ajuste: `r` 0.0325 → 0.03145 y `b` 0.24 → 0.2138 (`k_lin` 0.9677, `k_ang` 1.0863). Con eso no hubo sesgo sistemático en E5; la dispersión restante (±3.5°) es deslizamiento y medida.

### 14. ¿Qué cambiaron entre las ganancias del simulador y las del robot real? ¿Por qué?
- **Línea:** 3.0 / 0.5 / 4.0 → **1.0 / 0.1 / 8.0** (menos `Kp` y `Ki`, más `Kd`), porque con retardo ≈ 0.7 s y `/odom` a 11 Hz el sistema oscilaba (±13 cm en `/odom`, ≈ 30 cm reales).
- **Giro:** `kp_yaw` 10 → 1.0 (oscilaba ±15–20°). En 3B, `kd_yaw` 0.6 → 0.3 por el chatter.
- **`max_angular`** 2.0 → 1.0 por seguridad y por la planta.
- **Declarar** que son cinco parámetros distintos (`kp_yaw`, `kp`, `ki`, `kd`, `kd_yaw`) frente a un máximo de tres, y que se consultó al docente `[completar con su respuesta]`.

### 15. ¿Por qué el nodo frena si no llega /odom en 0.5 s y por qué el simulador frena si no llega /cmd_vel?
- Son **vigilantes de seguridad** (watchdog): sin pose el nodo no puede controlar, y sin órdenes el simulador no mantiene movimiento. En ambos casos se pasa a velocidad cero.
- En el **robot real no hay ese vigilante**: `YB_Car_Node` conserva la **última orden** si el nodo se corta. Lo vimos: el `Twist()` final del nodo falla con `RCLError` al apagarse. Por eso el script publica ceros al terminar, y se exige una persona con la mano en el interruptor.

### 16. Muestren en su gráfica del cuadrado dónde se ve que /odom y la pose real se separan
- Simulador: `plots/exp3c_sim_cinta_run2.png` (la figura del informe): `/odom` cierra a < 1 cm y la pose real queda a 13.4 cm; la separación se ve en las esquinas.
- Real: no hay pose real continua; la separación se mide con la cinta al final. `[Completar con un PNG de 3B oficial: la trayectoria de /odom cierra, la posición física no]`.

## 2. Lo que no conviene improvisar (y cómo responder con honestidad)

| Si preguntan… | Respuesta recomendada |
|---|---|
| «¿Cuántas re-sintonías hicieron?» | Cinco parámetros distintos frente a un máximo de tres (`kp_yaw`, `kp`, `ki`, `kd`, `kd_yaw`), tras ≈ 13 pruebas exploratorias de recta y 5 de 3B (exp1–exp5), todas guardadas. Consultaron al docente: `[respuesta]`. |
| «¿Por qué sus predicciones de E6 son posteriores?» | Las de E6 con las ganancias finales se escribieron después de las corridas; las de `exp1` (otras ganancias) sí fueron previas. Está declarado en `reconstruccion_E6_oficiales.md`. |
| «¿Y las corridas run3 y run4 de E6?» | `run3`: fallo físico (el robot se trabó con la cinta métrica). `run4`: mal posicionado, 6 cm. Se conservan los CSV y se cuentan run1, run2 y run5 como válidas `[confirmar con el docente]`. |
| «¿Por qué 3B no cierra bien si `/odom` dice 2 cm?» | El nodo reancla la línea en cada esquina (`self.sx, self.sy = x, y`, línea 213 de `core_cuadrado.py`) y usa rumbos nominales sobre `/odom`: no tiene referencia física del cuadrado, y los errores del piso se acumulan sin que el lazo los vea. |
| «¿Cuál es la limitación principal?» | El lazo cierra sobre una medida (`/odom`) que no ve el deslizamiento. Mejora para RC-2: giroscopio como medida independiente del giro. |

## 3. Pendiente de completar `[Pendiente E7]`
- Resultados oficiales de 3B (run1–run3, media, comparación con 3A = 107.9 cm).
- Respuesta del docente sobre re-sintonías y repeticiones.
- PNG de la trayectoria de 3B para la pregunta 16.
- Comprobar en el contenedor la fórmula exacta del PID para la pregunta 2.
