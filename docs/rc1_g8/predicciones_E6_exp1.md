# Predicciones E6 — Recta 1D con ROSCar físico

**Grupo 8 · ROSCar 4 · Predicciones**

**Condiciones de ejecución:** nodo original, sin modificaciones; recorrido de **2.0 m**; `linear_speed=0.10 m/s`; `line_offset=0.10 m` (el robot parte 10 cm a la izquierda de la línea virtual); `bias_w=0.0` (sin sesgo *inyectado*); `max_angular=1.0 rad/s`. Se usan las ganancias 1D procedentes del simulador: **Kp=3.0, Ki=0.5, Kd=4.0**. Esta es **la primera corrida experimental**, no el resumen de las tres oficiales.

**Criterio E6 del documento:** realizar **tres corridas oficiales** con CSV y cinta, con **desviación lateral final física ≤5 cm**. El objetivo operativo será **<5 cm**, dejando un margen respecto del límite. En la sustentación presencial, según la aclaración del docente, se hará una sola demostración. La desviación se mide **perpendicularmente desde el centro final del robot a la línea objetivo**; no es el error longitudinal ni necesariamente el `e_line` estimado por `/odom`.

Estas predicciones son **hipótesis previas** basadas en la función `simular` de `core_cuadrado.py`, no observaciones ni resultados medidos del ROSCar físico. El modelo reproduce aproximadamente el caso simulado (`v=0.20 m/s`: error final 0.48 cm frente a 0.30 cm observado, asentamiento de ~5.8 s), pero no garantiza transferencia a la planta real.

## 1. ¿Cuánto tardará el robot en completar la recta y se asentará dentro de ±2 cm de la línea?

**Predicción:** si alcanza `FIN`, lo hará **aproximadamente entre 20 y 30 s** desde el comienzo efectivo del movimiento. **No se prevé un asentamiento lateral sostenido dentro de ±2 cm** con estas ganancias durante la corrida experimental 1. Puede atravesar momentáneamente esa banda, pero volver a salir de ella; incluso es posible **no alcanzar `FIN` durante 60 s** en una condición desfavorable del modelo.

$$
t_{\mathrm{ideal}}=\frac{2.0\ \mathrm{m}}{0.10\ \mathrm{m/s}}=20\ \mathrm{s}
$$

**¿Por qué?** A 0.10 m/s, 20 s es el tiempo cinemático ideal para avanzar 2 m sin pérdidas de avance. Los escenarios con retardo y acción integral presentan oscilaciones de varios centímetros a decenas de centímetros; **cruzar la banda ±2 cm no equivale a permanecer dentro de ella**. Por ello, no se extrapola el asentamiento de 5.80 s del simulador como «10–15 s de asentamiento» del robot físico. El rango 20–30 s es un pronóstico **condicionado a completar la distancia**, no un límite de seguridad ni un tiempo garantizado.

**Comprobación CSV:** primera fila `FIN` entre **20 y 30 s**, si aparece; calcular la diferencia entre su instante y el primer instante efectivo de `AVANZA`. Buscar si existió una permanencia **continua** de al menos **0.3 s** con `|e_line| ≤ 0.02 m` antes de `FIN`. **Se predice que no** habrá esa permanencia, aunque sí puede haber entradas breves en la banda. Un `FIN` posterior, ausente o sin avance suficiente se registrará como discrepancia o corrida no completada, nunca como éxito supuesto.

## 2. ¿Cuál será la desviación lateral final REAL y qué posibilidad hay de cumplir <5 cm?

**Predicción central:** **≈13 cm de desviación lateral absoluta física** al terminar, **si la respuesta se asemeja al escenario intermedio** del modelo. Rango orientativo: alrededor de **4–20 cm**, con posibilidad de desviaciones mayores o de no finalizar. La **probabilidad estimada de quedar por debajo de 5 cm es ≈30 %**, como **juicio de ingeniería de baja confianza**, **no** como probabilidad estadística calibrada ni como frecuencia real demostrada.

**¿Por qué?** Los tres escenarios examinados con las ganancias iniciales dieron:

| Retardo de pose del modelo | `e_line` al finalizar o detener la simulación | ¿Llegó a `FIN`? | ¿Dentro de 5 cm según el modelo? |
|---|---:|---|---|
| 0.30 s | +4.5 cm | Sí | Sí |
| 0.50 s | −12.7 cm | Sí | No |
| 0.67 s | −21.8 cm **a los 60 s** | **No** | No se obtuvo resultado final |

El valor central de **≈13 cm** se toma del caso intermedio (**12.7 cm** en magnitud). La cifra orientativa **≈30 %** refleja que **solo uno de los tres escenarios considerados** terminó por debajo de 5 cm y supone, *solo para ilustrar la incertidumbre*, que las condiciones fueran comparables en plausibilidad. **No existen datos que permitan asignar probabilidades reales a los retardos**, y además el modelo no reproduce el deslizamiento, la zona muerta ni la diferencia `/odom`–suelo. En consecuencia, **no debe presentarse el 30 % como una probabilidad medida o validada**.

**Comprobación física y CSV:** anotar el **desvío perpendicular real en cm con cinta** y decidir el criterio con ese valor (**≤5 cm** según rúbrica; **<5 cm** como meta preventiva). Guardar aparte el último `e_line` previo a `FIN`, que es **estimación por odometría**, y comparar ambas magnitudes sin tratarlas como equivalentes. Si no hay `FIN`, reportar el desvío al detenerse, **no** un «error final de llegada».

## 3. ¿Oscilará y cuántas veces cruzará la línea virtual?

**Predicción:** se esperan **al menos 3 cruces de signo de `e_line`** durante `AVANZA`, con un rango orientativo de **3–5 cruces**. Es probable que el error lateral oscile con amplitudes del orden de **±10–20 cm** en situaciones intermedias, y potencialmente mayores con retardos altos. **No se predice un asentamiento sostenido en ±2 cm a los 10–15 s**: la trayectoria puede cruzar la línea varias veces sin estabilizarse.

**¿Por qué?** Para Kp=3.0, Ki=0.5 y Kd=4.0, el modelo produjo:

| Retardo de pose del modelo | Rango de `e_line` | Cruces de signo |
|---|---:|---:|
| 0.30 s | −10.4 a +10.0 cm | 4 |
| 0.50 s | −18.4 a +22.1 cm | 5 |
| 0.67 s | −39.8 a +24.9 cm | 3; no finalizó |

El PID intenta regresar a la línea, pero la dinámica del actuador y la información de pose retrasada pueden hacer que la corrección se aplique tarde. **Estos rangos pertenecen al modelo**, no son mediciones del robot. El ROSCar recibe `/odom` aproximadamente a 11 Hz, con actualizaciones más lentas que el lazo de control de 30 Hz, lo que añade incertidumbre.

**Comprobación CSV:** contar cruces de signo `e_line` durante `AVANZA`, **predicción ≥3** (registro adicional: cruces que superan ±0.5 cm a ambos lados para distinguir cambios por ruido). Medir `min(e_line)`, `max(e_line)` e inversiones de `w`; verificar si el error entra y sale de la banda ±2 cm. **La amplitud REAL se observará y medirá en el área marcada**, no se inferirá directamente de `/odom`.

## 4. ¿Cómo terminará el PID y cuál será el error lateral en los últimos segundos?

**Predicción:** en el escenario intermedio, el controlador **sí llegará a `FIN` aproximadamente entre 20 y 30 s**, con `v=0` y `w=0` en la primera fila `FIN`, **pero sin haber estabilizado lateralmente la trayectoria**. Se prevé que el último `|e_line|` durante `AVANZA` sea del orden de **13 cm** (referencia cuantitativa central), y que **supere 5 cm**; durante los **últimos 2 s** anteriores a `FIN` se esperan correcciones angulares y **no se espera permanencia continua en ±2 cm**. En el escenario de retardo alto, puede **no aparecer `FIN` antes de 60 s**.

**¿Por qué?** El modelo de retardo intermedio terminó con `e_line≈−12.7 cm`, aun cuando el recorrido alcanzó su condición longitudinal. La acción integral **Ki=0.5** puede contribuir a un comportamiento oscilatorio en la planta retrasada. Este pronóstico de la ventana final de 2 s es una **hipótesis para comprobar**, no una salida temporal cuantificada previamente para esa ventana.

**Comprobación CSV (umbrales explícitos):**

- `FIN` **entre 20 y 30 s** si la corrida finaliza en el escenario central; marcar **no finalizada** si el estado no llega a `FIN` durante el intervalo de observación autorizado.
- Primera fila `FIN`: **`v=0.000` y `w=0.000`**.
- Última fila `AVANZA`: se predice **`|e_line| > 0.05 m`**, con estimación central **≈0.13 m**. Compararla con la medición lateral física, pero **no reemplazarla**.
- Últimos **2 s antes de `FIN`**: revisar `e_line` y `w`; se predice **ausencia de un intervalo continuo de al menos 0.3 s con `|e_line| ≤0.02 m`**. Registrar también el mínimo y máximo de `e_line` en esa ventana.

**Nota posterior, no predicción:** si la corrida experimental revela oscilación o desviación excesiva, se evaluará por separado una re-sintonía documentada, modificando **un parámetro por prueba**, conforme a la consigna. Las variantes del modelo con Ki menor son **hipótesis para planificar pruebas futuras**, no resultados de esta corrida ni parte del criterio 4.

---

## Condiciones de seguridad de la corrida experimental 1

- Realizarla solo con supervisión, batería suficiente, suelo nivelado, `/odom` estable y **parada física de motores operativa**; el controlador original mostró previamente una excepción `RCLError` al cerrarse con `timeout`, por lo que la publicación posterior de mensajes cero **no puede considerarse una parada de emergencia garantizada**.
- Dejar **≥40 cm libres a cada lado de la línea de referencia**, **más el semiancho del robot y un margen de frenado**. Como el robot tiene volumen, **solo 40 cm desde la línea a un obstáculo puede ser insuficiente** si el centro se desvía 30 cm. Conviene despejar **al menos ~60 cm a cada lado** cuando sea posible, además de todo el tramo longitudinal y la zona de parada.
- El integrante responsable del interruptor deberá **cortar físicamente los motores** si el centro del robot se desvía aproximadamente **30 cm o más** de la línea, si se acerca al límite seguro de la zona o si las correcciones se vuelven bruscas. No esperar a que alcance los ±40 cm del escenario más adverso. La supervisión debe ser continua y no depender exclusivamente de SSH, `timeout` o `/cmd_vel`.
- Mantener las referencias físicas fuera de la trayectoria de las ruedas y registrar cualquier parada anticipada como **corrida abortada**, sin inventar un `FIN` ni un error final de llegada.

**Límites del modelo:** los escenarios llamados retardo de **0.30, 0.50 y 0.67 s** corresponden al **retardo de la pose** en 9, 15 y 20 muestras a 30 Hz; **además** se usa `tau` de **0.30, 0.40 y 0.50 s**, respectivamente, para la dinámica del actuador. No son retardos totales medidos del robot. El modelo tampoco representa el mantenimiento de la pose entre lecturas de `/odom` a ~11 Hz, fricción estática, patinaje ni incertidumbre de la cinta. **Los resultados reales decidirán el cumplimiento de E6; el modelo únicamente organiza las predicciones.**
