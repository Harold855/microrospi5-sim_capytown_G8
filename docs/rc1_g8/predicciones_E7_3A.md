# E7 — Predicciones de la prueba 3A: cuadrado de 2 × 2 m en lazo abierto

**CapyTown RC-1 · Grupo 8 · ROSCar 4**  
**Estado:** predicciones finalizadas **antes de ejecutar E7-3A**, elaboradas después de completar la sintonización E6.  

## Condiciones fijas y criterio de evaluación

| Concepto | Condición prevista |
|---|---|
| Experimento | `experimento=cuadrado_abierto` (lazo **abierto**) |
| Nodo | `scripts_pdi/cuadrado_controller.py` original, sin modificar |
| Lado del cuadrado | `side=2.0 m` |
| Velocidad lineal ordenada | `linear_speed=0.10 m/s` |
| Velocidad angular ordenada | `turn_w=0.8 rad/s` |
| Factor de giro | `turn_scale=1.0` (sin calibración adicional) |
| Sesgo artificial | `bias_w=0.0` |
| Límite angular | `max_angular=1.0 rad/s` |
| Tiempo nominal de cada recta | `2.0 / 0.10 = 20.0 s` |
| Tiempo nominal de cada giro de 90° | `(π/2) / 0.8 ≈ 1.9635 s` |
| Tiempo nominal de cuatro rectas y cuatro giros | `4×20 + 4×1.9635 ≈ 87.85 s` |
| Medición fundamental | Cierre físico: distancia entre el **centro inicial y el centro final** del robot, con cinta; medir también orientación final con transportador |

**Rúbrica:** para E7, se ejecuta 3A **una vez** y 3B **tres veces**. La **media del cierre físico de 3B** debe ser ≤25 cm y, además, **menor que el cierre físico de 3A**. **No** se exige que el cierre de 3A sea ≤25 cm. Guardar el CSV y rosbag de 3A.

## ¿Qué aporta realmente E6 para predecir E7-3A?

| Evidencia de E6 (PID en recta) | Resultado | Qué podemos —y no podemos— transferir a 3A |
|---|---|---|
| Ganancias de línea definitivas | `Kp=1.0`, `Ki=0.1`, `Kd=8.0` | **No se usan para corregir la trayectoria de 3A**, porque es lazo abierto. Sí serán una referencia para 3B. |
| Tiempo de las corridas oficiales válidas | `run1 ≈20.9 s`; `run2 ≈21.1 s`; `run5 ≈21.0 s` | Hace plausible que el robot recorra un tramo de 2 m ordenado a 0.10 m/s en algo más de 20 s. **No valida** el tiempo exacto en lazo abierto. |
| Distancia entre inicio y final según `/odom` | `200.9`, `200.8`, `200.6 cm` | Evidencia estabilidad **estimada** del avance longitudinal con PID, **no** mide físicamente el largo de cada lado en 3A. |
| Desviación lateral física de E6 | `0.6 cm` derecha, `1.5 cm` izquierda, `0.5 cm` derecha | Demuestra buena precisión **con el lazo cerrado**. **No permite suponer** el mismo desvío en las rectas sin corrección de 3A. |
| Yaw relativo según `/odom` en E6 | `+2.0°`, `−0.8°`, `+1.6°` | Describe el final de una recta con PID. **No calibra** un giro abierto de 90° a `turn_w=0.8`. |

**Hipótesis principal:** el giro abierto podría exceder 90° en torno a un **9 %**; ello produciría unos **98° por esquina**. Esta suposición viene de observaciones anteriores de E5 en otro régimen, **no** de E6, y **no constituye calibración física** del giro abierto. Si el giro es cercano a 90°, las predicciones de cierre cambian de manera sustancial.

## 1. ¿Cuánto girará realmente el robot en cada esquina?

**Predicción central:** aproximadamente **98° por esquina**, con un intervalo orientativo de **94° a 102°**. Esto equivale a un sobreviraje de **+8°** por esquina, con un rango tentativo de +4° a +12°.

**Fundamento:** en 3A el robot ejecuta el giro por **tiempo**, no detiene el giro al alcanzar el yaw medido. La consigna angular nominal es de 0.8 rad/s durante 1.9635 s, equivalente a 90° ordenados. Un incremento físico hipotético de 9 % llevaría a ~98.1°. El resultado físico depende de los motores, fricción, inercia, alimentación y respuesta real a esa velocidad; las corridas E6 no midieron esos factores en giro abierto.

**Comprobación:** marcar u observar la dirección de cada lado en vídeo, comparar el rumbo antes y después de cada esquina, y anotar la orientación final con transportador. El rumbo final **no basta por sí solo** para reconstruir los cuatro giros por separado.

**Qué refutaría la hipótesis:** giros sistemáticamente cercanos a 90°–92°, subviraje o variaciones amplias entre esquinas.

## 2. ¿Cuál será el cierre físico REAL del cuadrado?

**Predicción central condicionada al sobreviraje:** **≈75 cm** entre el centro inicial y el final, con rango exploratorio **≈30–125 cm**. No es un objetivo de ejecución ni un error medido.

Para cuatro lados idealmente de 2 m y un mismo giro `θ` en las cuatro esquinas, la posición final hipotética es:

\[
\vec r = 2\sum_{k=0}^{3}\left(\cos(k\theta),\ \sin(k\theta)\right)\quad [\mathrm m],
\qquad C=\|\vec r\|.
\]

| Giro físico por esquina supuesto | Sobreviraje | Cierre geométrico teórico |
|---|---:|---:|
| 90° | 0° | 0 cm |
| 92° | +2° | 19 cm |
| 94° | +4° | 38 cm |
| **98°** | **+8°** | **73 cm** |
| 102° | +12° | 105 cm |

El valor ≈75 cm redondea el escenario geométrico de 98°. El rango más amplio incorpora cambios de longitud física, sesgos de avance, patinaje y transitorios; esos efectos pueden **aumentar o reducir** el cierre, y no deben sumarse como distancias escalares.

**Comprobación:** antes de mover el robot, marcar el **centro inicial**; tras `FIN` y con el robot completamente detenido, medir la **distancia recta centro inicial–centro final**. No confundir esa distancia con el error lateral de E6 ni con la longitud total recorrida (≈8 m de rectas nominales).

**Qué refutaría la hipótesis central:** cierre muy bajo, por ejemplo inferior a 25 cm, acompañado de esquinas cercanas a 90°; o un cierre muy distinto del calculado por geometría, que indicaría efectos adicionales.

## 3. ¿Qué cierre informará `/odom`?

**Predicción central de baja confianza:** **≈70 cm** según `/odom`, con un rango tentativo **≈30–115 cm** en el escenario de sobreviraje. **No se asegura** que sea próximo al cierre físico.

**Fundamento:** en 3A la odometría **no controla** las ruedas, pero sí estima la pose para el CSV y el mensaje de `FIN`. En la hipótesis de que el yaw de `/odom` siga de cerca el giro físico —como ocurrió de forma aproximada en algunas observaciones de E5—, el cierre odométrico sería comparable al geométrico. Sin embargo, incluso pequeños errores de orientación integrados a lo largo de cuatro tramos pueden crear una brecha considerable. Los buenos resultados físicos de E6 obtenidos con PID **no validan** la precisión de odometría durante el giro abierto.

**Comprobación:** tomar el `error de cierre` que imprima el nodo al llegar a `FIN` y compararlo con la cinta. Calcular por separado `cierre_odom_cm − cierre_fisico_cm` y su valor absoluto. **El primero es una estimación del robot; el segundo es la medida que se evalúa.**

**Qué refutaría la hipótesis:** `/odom` cercano a cero mientras la cinta indica decenas de centímetros, o diferencia mayor de unos 25 cm entre ambos cierres; no implicaría fracaso experimental, sino limitaciones de la estimación.

## 4. ¿Cuánto tiempo tomará y cuál será la orientación acumulada?

**Predicción temporal:** **≈88–90 s** hasta el primer `FIN`, condicionado a que el programa ejecute **cuatro lados de 20 s y cuatro giros temporizados de 1.9635 s**, sin interrupciones. Tiempo teórico: **87.85 s**. Comprobar la duración real que use el script auxiliar; **no reutilizar `timeout` de 40 s de E6**.

**Predicción angular condicionada:** si cada esquina gira 98°, el robot suma **≈392° físicos** al completar cuatro esquinas (rango exploratorio **376°–408°**), y termina mirando unos **+32° respecto de su dirección inicial**, módulo 360° (rango +16° a +48°). Si las esquinas son de 90°, sumará 360° y el rumbo final tenderá al inicial.

**Comprobación:** registrar tiempo y primera fila `FIN`; revisar la evolución de yaw estimado y medir el **rumbo físico final** con transportador. El transportador final solo ofrece la orientación módulo 360°, no el número de vueltas acumuladas.

## 5. ¿El cierre de 3A será mayor que el de 3B?

**Predicción cualitativa:** **probablemente sí**, porque 3B corrige errores utilizando `/odom` y 3A no. El borrador propone **≈80 % de confianza subjetiva**, una valoración informal **no estadística** que mantenemos solo como hipótesis; no es una probabilidad calculada a partir de datos experimentales de E7.

**Fundamento y matiz de E6:** en E6, con `Kp=1.0`, `Ki=0.1`, `Kd=8.0`, tres corridas con corrección PID terminaron a 0.6, 1.5 y 0.5 cm de la línea física. Esto favorece la idea de que **corregir rectas ayuda**, pero el cuadrado 3B tiene **cuatro giros y propagación de errores entre lados**, por lo que **no** podemos extrapolar esos centímetros directamente al cierre de 3B. Una predicción anterior para 3B planteó una mediana de ≈24 cm en un modelo hipotético; aún no es una medición y deberá revisarse antes de realizar 3B.

**Comprobación:** comparar el único cierre físico de 3A con el **promedio de los cierres físicos de las tres corridas 3B**. La condición oficial es doble: `promedio_3B ≤25 cm` **y** `promedio_3B < cierre_3A`.

**Qué refutaría la hipótesis:** que 3A cierre igual o mejor que el promedio de 3B.

## 6. ¿En qué partes del recorrido se acumulará más error?

**Predicción:** las **esquinas temporizadas** serán probablemente el factor dominante del cierre, porque cada error de rumbo afecta las rectas posteriores. En el escenario idealizado de +8° por esquina, el cierre geométrico alcanzaría ≈73 cm aunque los cuatro lados midieran exactamente 2 m; errores de avance, patinaje y deslizamiento pueden modificarlo considerablemente.

**Fundamento:** el cuadrado abierto no vuelve a ajustar rumbo ni desplazamiento después de las esquinas. En E6 la corrección de línea sí logró acercar el centro a la referencia, lo que demuestra la importancia del lazo cerrado, **pero esa acción no existe en 3A**.

**Comprobación:** observar y documentar con vídeo o marcas el desplazamiento después de cada giro, longitudes aproximadas y rumbo final. Registrar cualquier deslizamiento o obstáculo que invalide la medición.

---

**Síntesis:** E6 justifica mantener `0.10 m/s` como referencia práctica de avance y demuestra que el robot puede seguir una línea con PID; **no permite predecir precisión centimétrica en 3A**. La predicción central de 3A sigue siendo una trayectoria abierta con posible sobreviraje de ≈8° por esquina, cierre físico ≈75 cm y duración ≈88 s, con incertidumbre especialmente alta en los giros.
