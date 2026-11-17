# RC-1 — Predicciones previas (Grupo 8, S-003)

**Proyecto:** CapyTown RC-1 - Control PID: del simulador al robot real  
**ROS_DOMAIN_ID:** 8  
**Fecha y hora de registro:** 10/11/26 23:16:15

## 1. Recta de 2 m, arranque 10 cm a la izquierda, Kp = 3, Kd = 0, Ki = 0

**Pregunta:** ¿Llega a la línea y se queda, o la cruza una y otra vez? Dibujar `e(t)`. ¿Qué cambia al añadir Kd?

- **Predicción:** con control **solo P**, el robot comenzará con `e(0) = +10 cm`, corregirá hacia la derecha y **cruzará la línea virtual al menos dos veces** durante la recta de 2 m. Esperamos que las oscilaciones **se mantengan apreciables** durante el recorrido, en lugar de desaparecer rápidamente. Con el sesgo angular `bias_w = +0.06 rad/s` del Experimento 1, la oscilación se producirá alrededor de un **equilibrio positivo próximo a +2 cm**, y no alrededor de cero. Al añadir **Kd = 4** y mantener el **mismo Kp = 3** y `Ki = 0`, esperamos una oscilación amortiguada: menos cruces de `e = 0`, amplitud decreciente y aproximación a ese mismo equilibrio positivo.
- **Razonamiento:** en la recta, `ω = −PID(e)`. Con solo P, el robot corrige el desplazamiento actual, pero no amortigua suficientemente el movimiento lateral. El sesgo de giro se compensa aproximadamente cuando `−Kp·e + bias_w = 0`; por eso `e_eq ≈ 0.06/3 = 0.02 m = +2 cm`. Kd incorpora la rapidez de cambio del error y amortigua la respuesta, pero por sí solo no elimina un sesgo constante.

**Croquis previsto de `e(t)`** (dos curvas esquemáticas; `P` = solo P, `D` = P+D y `*` = superposición):

```text
 e(cm)
  10 | **PP                                  PPPPPP
   8 |   DDPP                             PPP      PPP
   6 |     DDPP                         PP            PP
   4 |       DD*P                      P                P
  +2 | ·········D*DD·········DDDDDDDD**DDDDDDDDDDDDDDDDDD*  equilibrio ~+2 cm
   0 | -----------PPDDDDDDDDD------PP---------------------  línea virtual
  -2 |              PP            P
  -4 |                PPP      PPP
  -6 |                   PPPPPP
     +---------------------------------------------------> t (s)
        0        2        4        6        8        10
```

## 2. Cuadrado de 2 × 2 m con PID sobre `/odom`, `noise:=low`

**Pregunta:** ¿El cierre REAL será mayor, menor o igual al que imprime el nodo? Dar los dos números en cm.

- **Cierre según `/odom` (cm): de 0 a 10 cm; estimación central: 5 cm.**
- **Cierre REAL según `/sim/pose` (cm): de 15 a 30 cm; estimación central: 20 cm.**
- **Predicción explícita:** **cierre según `/odom`: 5 cm; cierre REAL: 20 cm**, con los rangos anteriores para contemplar la variación entre corridas. Predecimos que el cierre REAL será **mayor** que el odométrico bajo `noise:=low`.
- **Razonamiento:** el simulador introduce un empujón aleatorio del piso que puede desplazar y rotar al robot. El PID se guía por `/odom`, que no mide directamente ese empujón; por ello puede corregir el recorrido estimado sin eliminar todo el desplazamiento real. Esta predicción se centra **solo en la perturbación no observada del piso**, sin atribuir la diferencia al derrape físico de cuatro ruedas. La aleatoriedad justifica expresar las distancias como rangos.

## 3. Un grado de error de yaw

**Pregunta:** ¿Cuántos cm se desvía el robot al final de un lado de 2 m? ¿Y tras cuatro lados con un grado de error en cada giro?

- **Un lado (cm): 3.49 cm** de desviación lateral si mantiene un error de orientación constante de `+1°` durante 2 m.
- **Cuatro lados (cm): 9.79 cm** de error de cierre, suponiendo lados exactamente de 2 m y que **cada giro es de +91° en lugar de +90°**, siempre con el mismo signo de error.
- **Cálculo:** para un lado, `d = 2·sin(1°) = 0.03490 m ≈ 3.49 cm`. Para el cuadrado, los cuatro rumbos de avance serán `0°, 91°, 182° y 273°`. La posición final respecto del inicio se estima mediante:

  \[
  x_f = 2\sum_{k=0}^{3}\cos(91^\circ k)\approx 0.07099\;\text{m},
  \qquad
  y_f = 2\sum_{k=0}^{3}\sin(91^\circ k)\approx -0.06736\;\text{m}.
  \]

  \[
  C = \sqrt{x_f^2+y_f^2}\approx 0.09786\;\text{m}=\boxed{9.79\;\text{cm}}.
  \]

  El cuarto giro de `91°` dejaría una orientación acumulada de `364°`, aunque no alteraría el cierre de posición si ocurre después del cuarto lado. El valor de 9.79 cm corresponde exclusivamente a este escenario de errores iguales y del mismo signo.

## 4. Ganancias del simulador copiadas al robot real

**Pregunta:** ¿Qué esperan ver al copiar las ganancias del simulador al robot real? Dar dos diferencias entre la planta virtual y la real que lo expliquen.

- **Predicción:** al utilizar en el ROSCar físico las **mismas ganancias de giro de 90°** que en el simulador, **esperamos un tiempo de asentamiento dentro de ±2° mayor en el robot real**. La comparación seguirá las condiciones que fija el protocolo, **sin igualar artificialmente los límites de velocidad**: en la simulación se utiliza el límite habitual `max_angular:=2.0 rad/s`, mientras que para la primera prueba del robot físico se exige `-p max_angular:=1.0` y `-p linear_speed:=0.10`. En el experimento `giro90`, la velocidad lineal es cero, de modo que el límite angular es la restricción relevante. **Predecimos que el límite angular menor también prolongará el giro y, por tanto, contribuirá a aumentar su tiempo de asentamiento.** Si el giro real se asienta igual o más rápido que el simulado, esta predicción no se cumple.
- **Razonamiento sobre el límite de velocidad:** con `kp_yaw = 10` y un error inicial de `90° = π/2 rad`, **solo el término proporcional** solicitaría aproximadamente `10·(π/2) = 15.7 rad/s`, antes de aplicar la saturación y sin contar los términos I y D. Por ello, la orden queda limitada a **2.0 rad/s en la simulación** y a **1.0 rad/s en el robot real**. Aun sin considerar aceleraciones, una rotación de 90° a esas velocidades máximas necesitaría como mínimo aproximadamente **0.79 s** y **1.57 s**, respectivamente. Esos tiempos son límites cinemáticos idealizados, **no tiempos de asentamiento predichos**; el PID debe desacelerar y estabilizarse cerca de 90°.
- **Diferencia 1 — dinámica de los motores:** el simulador aplica límites matemáticos de velocidad y aceleración, mientras que el ROSCar físico tiene motores con respuesta, inercia y retardos propios. Esperamos que esa dinámica influya en cómo desacelera y se estabiliza cerca del ángulo objetivo.
- **Diferencia 2 — frecuencia de odometría:** el simulador publica `/odom` aproximadamente a **50 Hz**; en el ROSCar utilizado durante RC-0 se observó una frecuencia cercana a **11 Hz**. Si se mantiene en RC-1, el controlador de 30 Hz recibirá mediciones nuevas menos a menudo y su corrección angular podrá reaccionar más tarde.

**Alcance de la predicción:** como el protocolo impone un límite angular diferente en cada entorno, una mayor duración en el robot **no se podrá atribuir exclusivamente** a la inercia de los motores ni a la frecuencia de `/odom`. El límite `max_angular` es una causa adicional y explícita de la diferencia esperada.
