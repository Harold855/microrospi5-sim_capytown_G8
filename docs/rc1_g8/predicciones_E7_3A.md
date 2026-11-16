# Predicciones E7 — 3A (cuadrado de 2 × 2 m en lazo abierto) con ROSCar físico

**Grupo 8 · ROSCar 4 · Predicciones formuladas antes de la corrida física 3A**

**Condiciones de ejecución fijadas:** nodo original sin modificar; `experimento=cuadrado_abierto`; `linear_speed=0.10 m/s`; `side=2.0 m` (20 s ordenados por lado); `turn_w=0.8 rad/s`; **`turn_scale=1.0` (sin calibración adicional)**; `bias_w=0.0`; `max_angular=1.0 rad/s`. Cada giro dura nominalmente `(π/2)/(0.8 × 1.0) ≈ 1.96 s`. El cierre real se medirá con cinta entre el centro inicial y el centro final del robot; la orientación final, con transportador.

**Contexto:** las predicciones se formulan tras las corridas de E5. Como hipótesis de trabajo se considera una posible respuesta angular aproximadamente un 9 % mayor que la ideal, sugerida de manera indirecta por observaciones previas de odometría a otra velocidad. No se toma ese factor como una calibración demostrada de la orientación física. La concordancia aproximada entre yaw estimado y físico observada en E5 (cociente cercano a 0.99) también se adopta solo **como hipótesis condicionada** para 3A: no verifica por sí misma el movimiento a 0.8 rad/s ni el cierre de posición.

**Criterio de la rúbrica:** 3A requiere **una corrida física** y su cierre medido; después, el cierre real **promedio de las tres corridas 3B** debe ser ≤25 cm y menor que el cierre de 3A. El valor de 25 cm no es un requisito independiente para 3A.

## 1. ¿Cuánto girará realmente el robot en cada esquina?

**Predicción:** **≈98° por esquina**, es decir, **+8° de sobreviraje** respecto de 90°; rango orientativo **94°–102°** (**+4° a +12°**). Se mantiene `turn_scale=1.0`.

**¿Por qué?** El giro abierto dura ≈1.96 s y no se corrige con `/odom`. Como hipótesis transferida de E5, una respuesta angular ≈9 % superior a la ordenada daría alrededor de 98°; el factor proviene de otro régimen de velocidad y aún **no se ha calibrado físicamente** a `turn_w=0.8 rad/s`.

**Comprobación:** si es posible, medir los rumbos entre lados mediante marcas o vídeo; contrastar también el yaw acumulado del nodo y el rumbo final con transportador. El giro por esquina no puede inferirse con precisión solo de la orientación final.

**Qué lo contradice:** Si observamos esquinas sistemáticamente de **≈90°–92°** (error menor de +2°) o un subviraje sostenido, en vez del sobreviraje de +4° a +12° previsto.

## 2. ¿Cuál será el cierre REAL con cinta (cm)?

**Predicción:** **≈75 cm** como valor central, con rango orientativo **≈30–125 cm**.

**¿Por qué?** Si cada esquina mide 98° y las cuatro rectas son de 2.0 m, la suma vectorial de los rumbos 0°, 98°, 196° y 294° da **≈73 cm** de separación entre el inicio y el final. Con giros de 94°–102°, el modelo geométrico da ≈38–105 cm; se amplía el rango por variaciones de longitud, patinaje y transitorios.

**Comprobación:** medir con cinta la distancia recta entre los centros inicial y final, usando marcas en el suelo, y comparar con la predicción central de 75 cm.

| Giro por esquina supuesto | Error por esquina | Cierre geométrico de cuatro lados de 2 m |
|---|---:|---:|
| 94° | +4° | ≈38 cm |
| **98°** | **+8°** | **≈73 cm** |
| 102° | +12° | ≈105 cm |

**Qué lo contradiría:** obtener un cierre **menor de 25 cm**, especialmente si las esquinas medidas muestran errores inferiores a +2°. Esto debilitaría la hipótesis central de un sobreviraje sistemático de +8°.

La regla informal de «≈10 cm por grado» orienta sobre sensibilidad; los valores de la tabla se calcularon mediante **suma vectorial de los cuatro tramos**, sin sumar directamente cuatro errores lineales.

## 3. ¿Cuánto dirá `/odom` (el cierre que imprime el nodo)?

**Predicción:** **≈70 cm de cierre según `/odom`**, con rango orientativo **≈30–115 cm**. En el escenario central se espera un valor **próximo a los 75 cm reales**; no se predice una brecha sistemática grande entre ambas mediciones.

**¿Por qué?** En 3A no hay corrección basada en `/odom`, pero el nodo calcula el cierre con la pose estimada. **Si** se mantiene para estos giros la concordancia aproximada de E5 (`yaw_odom/yaw_físico ≈0.99`), una esquina física de 98° sería observada como **≈97°–98°** por `/odom`: con cuatro lados ideales de 2 m eso equivale a **≈65–73 cm**, que justifica un valor central de ≈70 cm. El rango cubre el error angular de 94°–102° propuesto en el punto 1 y desviaciones moderadas de odometría y longitud; no supone una desviación arbitraria de 1.5° por esquina.

**Comprobación:** leer el `error de cierre` de la primera línea `FIN`, y compararlo con la distancia medida por cinta. Registrar también el yaw acumulado de `/odom`.

**Qué lo contradiría:** un cierre estimado **cercano a cero (p. ej., <25 cm)** mientras el cierre real está cerca de 75 cm, o una diferencia absoluta entre ambos **superior a ≈25 cm**. Esto indicaría que la concordancia observada en E5 no se trasladó a 3A, o que hubo deriva, patinaje u otra discrepancia de pose.

## 4. ¿Cuál será el yaw acumulado real y el tiempo?

**Predicción:** **≈392° acumulados físicamente** (rango **376°–408°**), equivalentes a terminar mirando **≈32°** respecto del rumbo inicial (rango **16°–48°**, módulo 360°). El nodo debería llegar a **`FIN` cerca de 88 s** (rango práctico **≈88–90 s**, si odometría y ejecución se mantienen estables).

**¿Por qué?** Cuatro esquinas de 98° suman 392°; cuatro rectas de 20 s más cuatro giros de 1.96 s suman **87.85 s nominales**. Las transiciones y el ciclo de control pueden agregar pequeñas diferencias de tiempo.

**Comprobación:** registrar el primer `FIN` y el yaw acumulado que imprima el nodo; el transportador final solo permite comprobar el **rumbo final módulo 360°**, no distinguir por sí solo 32° de 392° de giro acumulado. Para estimar este último físicamente se necesitarían observaciones durante el recorrido.

## 5. ¿3A saldrá peor que 3B?

**Predicción:** **sí, probablemente**, con una probabilidad **subjetiva ≈80 %** (banda de juicio **75–85 %**, baja confianza) de que el cierre real de **la única corrida 3A** sea mayor que **el promedio de cierre real de las tres corridas 3B**.

**¿Por qué?** Bajo la hipótesis central de +8° por esquina, 3A cerraría en **≈75 cm**. Para 3B contamos con una estimación previa de **mediana ≈24 cm** y **≈46 % de probabilidad de que el promedio de sus tres corridas sea ≤25 cm**; estos son **resultados de un modelo previo, no mediciones del robot**. La distancia entre las estimaciones centrales favorece claramente a 3B. La probabilidad de 80 % refleja además el escenario alternativo: si el sobreviraje abierto de 3A fuera mucho menor, su cierre podría bajar a ≈19–33 cm y la comparación sería incierta. **El 80 % no se calcula directamente a partir del 46 %; es un juicio condicionado a escenarios.**

**Qué lo contradiría:** que el **cierre real de 3A sea menor o igual al promedio real de los tres cierres de 3B**. Además, si 3A mide ≈19–33 cm, disminuiría sustancialmente la confianza en que 3B lo supere favorablemente.

## 6. ¿Qué parte del recorrido aportará más error?

**Predicción:** **las esquinas** serán el factor dominante. Su contribución geométrica esperada al cierre es **≈73 cm** (rango **38–105 cm** para errores de +4° a +12°); las diferencias de longitud o deriva en recta podrían alterar adicionalmente el resultado en **≈0–30 cm** como orden de magnitud incierto, sin sumarse necesariamente en línea recta.

**¿Por qué?** Un error en la primera esquina cambia el rumbo de todos los lados siguientes; cuatro errores del mismo signo deforman el cuadrado y desplazan la llegada. La velocidad real y la adherencia pueden añadir o compensar parcialmente esa desviación.

**Comprobación:** observar si los lados conservan una longitud similar pero las esquinas se abren progresivamente, registraremos mediante fotos la trayectoria y se contrastará el cierre con el rumbo final.

---

**Límites de las predicciones:** no se han medido para 3A la velocidad lineal física bajo carga, el giro efectivo a 0.8 rad/s, la fricción estática ni los transitorios de arranque y frenada. Tampoco se conoce cuánto se separarán `/odom` y la trayectoria física: una concordancia del yaw cercana al 1 % no garantiza igual precisión en la posición integrada. Los rangos y la probabilidad son hipótesis de planificación experimental, **no resultados ni garantías**.

**Condición de seguridad:** un cierre previsto de decenas de centímetros implica que la trayectoria puede salirse del cuadrado marcado de 2 × 2 m. Verificar antes de la prueba el espacio despejado real alrededor de **todo** el recorrido previsto, no solo junto al punto de salida; disponer de parada física supervisada y abortar ante desviación peligrosa. No reutilizar el límite de `timeout` de 15 s de E5: la duración nominal de 3A es de casi 88 s. La definición de una eventual re-sintonía queda **fuera de estas predicciones** y deberá documentarse por separado, si el docente la autoriza.
