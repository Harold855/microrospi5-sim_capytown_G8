# E7 — Predicciones de 3B: cuadrado de 2 × 2 m con PID sobre `/odom` (ROSCar físico)

**CapyTown RC-1 · Grupo 8 · ROSCar 4 · 18 de noviembre de 2026, 18:34 h**

**Estado:** Predicciones para las tres corridas oficiales `run1`, `run2` y `run3`, formuladas después de E5, E6, E7-3A y las corridas experimentales de E7-3B. Este documento debe conservarse sin modificaciones después de iniciar la primera corrida oficial.

**Versión:** revisión 2; corrección de la procedencia de las ganancias, del juicio de probabilidad y de la explicación del reanclaje del controlador. Se conserva el documento original como referencia.

**Transparencia metodológica:** Las experimentales de 3B ya fueron ejecutadas sin registrar previamente una predicción formal definitiva. Por ello, los resultados experimentales se consideran antecedentes conocidos y no se presentan como validaciones independientes de estas predicciones. Las tres corridas oficiales permitirán evaluar el comportamiento de la configuración seleccionada.

## Condiciones fijas

| Concepto | Valor |
|---|---|
| Experimento | `experimento=cuadrado` (PID sobre `/odom`) |
| Nodo | `scripts_pdi/cuadrado_controller.py`, controlador original sin modificar |
| Plataforma | ROSCar 4, Raspberry Pi 5, ROS 2 Humble |
| Ganancias de línea | `kp=1.0`, `ki=0.1`, `kd=8.0` |
| Ganancias de giro | `kp_yaw=1.0`, `ki_yaw=0.0`, `kd_yaw=0.3` |
| `side` | `2.0 m` |
| `linear_speed` | `0.10 m/s` |
| `max_angular` | `1.0 rad/s` |
| `line_offset` | `0.0 m` |
| `bias_w` | `0.0 rad/s` |
| Medición física | Distancia centro inicial → centro final con cinta; rumbo final con transportador |
| Evidencias | CSV, rosbag de `/odom`, `/cmd_vel`, `/tf`, mediciones físicas y observaciones |
| Rúbrica | Tres corridas 3B; media del cierre físico ≤25 cm y menor que el cierre de 3A |

### Nota de procedencia y cambios realizados

La configuración procede de la transferencia desde el simulador hacia el robot real y de las pruebas de sintonización:

1. **Ganancias de línea:** la referencia del simulador era `3.0 / 0.5 / 4.0`. En E6 se seleccionó `1.0 / 0.1 / 8.0` a partir de las pruebas físicas de recta.
2. **Ganancias de giro elegidas en el simulador:** en la fila **2p (elegida = 2p1)** se utilizó `kp_yaw=10.0`, `ki_yaw=0.0`, `kd_yaw=0.6`. La combinación `3.0 / 0.0 / 0.4` corresponde a parámetros de referencia del material del curso, **no** a la combinación propia seleccionada por el Grupo 8. Se confirma en `tablas_simulador.md` y `hoja_resultados.csv`.
3. **Transferencia a E5:** se partió de `kp_yaw=10.0` y se redujo a `kp_yaw=1.0` para el robot físico, conservando `ki_yaw=0.0` y `kd_yaw=0.6`. La configuración real de giro utilizada como antecedente de 3B fue `1.0 / 0.0 / 0.6`.
4. **Ajuste experimental de 3B:** en la experimental `exp1` se utilizó `kd_yaw=0.6`; después se redujo únicamente este parámetro a `0.3`, manteniendo `kp_yaw=1.0` y `ki_yaw=0.0`. La configuración elegida para las corridas oficiales es `1.0 / 0.0 / 0.3`.
5. **Límite angular:** se utiliza `max_angular=1.0 rad/s` en el robot real, frente al límite de referencia de `2.0 rad/s` utilizado en el simulador.

**Cadena de transferencia del giro:** simulador **`10.0 / 0.0 / 0.6`** → E5 **`10.0 → 1.0` en `kp_yaw`** → primera experimental 3B **`1.0 / 0.0 / 0.6`** → posteriores experimentales y corridas oficiales **`1.0 / 0.0 / 0.3`** (se reduce `kd_yaw`).

Adicionalmente, en el cuadrado se utiliza `line_offset=0.0 m`, porque no se reproduce el desplazamiento lateral de referencia de `0.10 m` utilizado en E6.

Las ganancias de las tres corridas oficiales se mantendrán constantes, salvo que una condición de seguridad obligue a suspender la validación.

## Evidencia utilizada y sus limitaciones

| Fuente | Datos disponibles | Qué transferimos | Qué no podemos transferir directamente |
|---|---|---|---|
| E5: giro físico | Con `kp_yaw=1.0`, el giro físico fue cercano a 90°; se observaron diferencias entre el giro estimado y el físico | La configuración de giro permite aproximarse al objetivo | Un giro aislado no garantiza cuatro giros consecutivos precisos |
| E6: recta PID | Desvíos físicos finales de 0.6 cm, 1.5 cm y 0.5 cm; ganancias `1.0 / 0.1 / 8.0` | El PID lateral mostró buen control en recta | No garantiza el mismo resultado después de cada esquina |
| E7-3A: lazo abierto | Cierre físico 107.9 cm; `/odom` 97.4 cm; yaw odométrico 381.7°; `FIN` 87.9 s | Referencia física para medir la mejora de 3B | No podemos atribuir todo el error exclusivamente al giro |
| E7-3B: exp1 | `kd_yaw=0.6`; cierre `/odom` 2.0 cm; físico superior a aproximadamente 36 cm; orientación final visual ≈25° hacia la izquierda | Identificar que un cierre odométrico pequeño no asegura un buen cierre físico | La medida física no fue suficientemente precisa para tratarla como un valor exacto |
| E7-3B: exp2 | `kd_yaw=0.3`; cierre `/odom` 1.8 cm; cierre físico provisional ≈36.5 cm | Evaluar la nueva ganancia angular | El cierre físico es aproximado y tiene incertidumbre de medición |
| E7-3B: exp4 | `kd_yaw=0.3`; cierre físico 25.94 cm; `/odom` 3.7 cm; `FIN` 102.2 s | Estimar el cierre y el tiempo de una corrida con la configuración final | Una corrida no representa la variabilidad total |
| E7-3B: exp5 | `kd_yaw=0.3`; cierre físico 19.10 cm; `/odom` 3.4 cm; `FIN` 103.5 s | Confirmar que la configuración puede cerrar por debajo de 25 cm | No garantiza que las tres corridas oficiales reproduzcan el resultado |
| Modelo / simulador | En una referencia simulada de 3B, cierre `/odom` menor a 1 cm y cierre real del orden de 59 cm | La odometría puede diferir significativamente de la trayectoria real | No se deben aplicar directamente esas magnitudes al robot físico |

**Síntesis de los antecedentes:** la reducción de `kd_yaw` a `0.3` estuvo asociada a una disminución de las correcciones angulares negativas bruscas. Sin embargo, todavía existe variabilidad física considerable. No podemos afirmar que el cambio de ganancia sea la única causa de la mejora.

## 1. ¿Cuánto tardará el robot hasta `FIN`?

**Predicción central: ≈103 segundos por corrida.**

**Rango orientativo: 97–112 segundos.**

**Justificación:**

Las cuatro rectas de 2 m a una velocidad ordenada de 0.10 m/s requieren nominalmente:

$$
t_{\text{rectas}}=\frac{4(2.0)}{0.10}=80\text{ s}
$$

Los cuatro giros con PID pueden añadir aproximadamente entre 20 y 24 segundos. Por tanto, la duración total esperada es cercana a 100–104 segundos, con variaciones producidas por asentamiento y correcciones.

Los resultados experimentales apoyan esta estimación: exp2 llegó a `FIN` en 101.6 s; exp4 en 102.2 s; exp5 en 103.5 s. La exp1, con `kd_yaw=0.6`, tardó 109.5 s.

**Comprobación:** identificar la primera fila `FIN` del CSV y el mensaje correspondiente del nodo. No confundir este instante con el cierre posterior del proceso Python por `timeout`.

**Qué la refutaría:** tiempos repetidamente fuera de 97–112 segundos o incapacidad de alcanzar `FIN` dentro del límite de ejecución, siempre que no se trate de una interrupción externa.

## 2. ¿Cuál será el cierre físico de cada corrida y su media?

**Predicción central de una corrida: ≈27 cm.**

**Rango individual orientativo: 15–45 cm.**

**Predicción de la media de las tres corridas: ≈27 cm, con un rango orientativo de 18–38 cm.**

**Probabilidad subjetiva de que la media sea ≤25 cm: ≈25–30 % (confianza muy baja; juicio de ingeniería, no probabilidad estadística calculada).**

**Justificación:**

Las tres experimentales con `kd_yaw=0.3` y alguna medida física disponible dieron aproximadamente:

- Exp2: 36.5 cm, medición provisional.
- Exp4: 25.94 cm.
- Exp5: 19.10 cm.

La media descriptiva de estos antecedentes es aproximadamente:

$$
\frac{36.5+25.94+19.10}{3}\approx27.18\text{ cm}
$$

Se propone **27 cm como estimación central para la configuración final `kd_yaw=0.3`**, sin tratar esta pequeña muestra como una distribución estadística representativa.

**Tratamiento explícito de `exp1`:** su cierre físico se estimó en **más de 36 cm**, pero esa corrida empleó **`kd_yaw=0.6`**, una condición de control distinta de la seleccionada para las oficiales. **No se excluye de la evidencia ni se oculta:** se mantiene en la tabla de antecedentes y se utiliza para discutir sensibilidad ante cambios de parámetros. **Sí se excluye del promedio descriptivo de corridas con `kd_yaw=0.3`**, porque combinar configuraciones diferentes confundiría el pronóstico de la configuración final.

Como comprobación de sensibilidad, **si se incorporase `exp1` asignándole provisionalmente 36 cm como cota inferior**, la media descriptiva de las cuatro experimentales sería **mayor que**:

$$
\frac{36+36.5+25.94+19.10}{4}=29.385\text{ cm}
$$

Es decir, **superior a ≈29.4 cm**, sin convertir el «más de 36 cm» de `exp1` en una medición exacta. Esta media mezclada no se adopta como predicción central porque `exp1` usa otra ganancia, y `exp2` tiene medición física provisional.

**Juicio de cumplimiento revisado:** se adopta una valoración prudente de **≈25–30 %** para la probabilidad de que la **media de tres oficiales** sea ≤25 cm. Es una **estimación subjetiva de confianza muy baja**: los cierres de `exp2`, `exp4` y `exp5` muestran dispersión, dos de tres exceden individualmente 25 cm, y `exp1` confirma que otra configuración produjo un cierre físicamente desfavorable. No se obtiene 25–30 % contando éxitos ni aplicando una fórmula estadística: **cuatro corridas heterogéneas y con mediciones aproximadas no permiten estimar una probabilidad fiable**. La predicción central de ≈27 cm sigue siendo consistente con un riesgo significativo de no satisfacer el umbral.

Aunque `exp5` cumplió individualmente los 25 cm, `exp2` y `exp4` muestran que no se puede asegurar el cumplimiento del promedio oficial.

**Sensibilidad geométrica:** un error angular de 1° sostenido durante una recta de 2 m puede producir aproximadamente:

$$
d_\perp=2\tan(1^\circ)\approx3.49\text{ cm}
$$

Si un error de orientación se mantiene durante más distancia, el desplazamiento puede crecer. Sin embargo, los errores de cuatro esquinas pueden acumularse o compensarse; no existe una sensibilidad fija de 10 cm por grado para todo el cuadrado.

**Comprobación:** medir cada cierre con cinta entre el centro inicial y el centro final, registrar `c1`, `c2` y `c3`, y calcular:

$$
\overline{c}_{3B}=\frac{c_1+c_2+c_3}{3}
$$

**Qué la refutaría:** una media notablemente fuera del rango de 18–38 cm indicaría que la variabilidad real no estuvo bien representada. Una media superior a 25 cm supondría incumplir el criterio de la rúbrica, aunque era un resultado contemplado por esta predicción.

## 3. ¿Cuánto indicará `/odom` como error de cierre?

**Predicción central: ≈3 cm por corrida.**

**Rango orientativo: 1–7 cm.**

**Justificación:**

Las experimentales de 3B produjeron cierres odométricos de 2.0, 1.8, 3.7 y 3.4 cm. Estos valores muestran un cierre pequeño y relativamente consistente en el sistema de coordenadas utilizado por el controlador.

El PID corrige las trayectorias usando `/odom`, pero no mide directamente el desplazamiento físico del robot sobre el suelo. Por ello, esperamos un cierre odométrico pequeño aun cuando el cierre físico sea de varias decenas de centímetros.

Por ejemplo, en exp5:

- Cierre `/odom`: 3.4 cm.
- Cierre físico: 19.10 cm.
- Diferencia entre las magnitudes: 15.70 cm.

Esta diferencia no debe confundirse con el error de una medición individual: son distancias de cierre calculadas a partir de dos fuentes distintas.

**Comprobación:** comparar el `error de cierre` de la primera línea `FIN` con la distancia física obtenida mediante cinta.

**Qué la refutaría:** cierres odométricos repetidamente mayores a 7 cm o un comportamiento sistemático que indique que el controlador ya no está siguiendo su propia referencia estimada.

## 4. ¿Cuál será el yaw acumulado y el rumbo final?

**Predicción de yaw acumulado según `/odom`: ≈359°.**

**Rango previsto para `/odom`: 354°–364°.**

**Predicción del yaw físico acumulado: cercano a 360°, con un intervalo orientativo amplio de 330°–390° y confianza baja.**

**Predicción del rumbo físico final: cercano al rumbo inicial, con una desviación posible de aproximadamente ±25°.**

**Justificación:**

Los valores odométricos experimentales fueron próximos a una vuelta:

- Exp1: 359.2°.
- Exp2: 358.2°.
- Exp4: 358.5°.
- Exp5: 358.7°.

Sin embargo, el yaw acumulado que calcula el nodo no es necesariamente igual al giro físico real.

En 3A se observó un sobreviraje físico importante en la primera esquina, cercano a 115° en lugar de 90°. Las experimentales de 3B mostraron desviaciones físicas en ciertas esquinas, aunque el controlador corrigió la orientación según `/odom`.

Por ese motivo, la predicción del yaw físico es bastante menos precisa que la predicción del yaw odométrico.

**Comprobación:**

- CSV: yaw acumulado según `/odom`.
- Transportador: orientación física final respecto de la marca inicial.
- Vídeo o marcas intermedias: observación de los giros por esquina, si están disponibles.

**Limitación:** el transportador al final solo permite medir el rumbo relativo, módulo 360°. No demuestra por sí solo el giro total acumulado. Tampoco debe confundirse el yaw acumulado con la dirección final del robot.

**Qué la refutaría:** un yaw odométrico claramente fuera de 354°–364° o una orientación física final consistentemente más alejada que el intervalo previsto.

## 5. ¿3B tendrá un cierre menor que 3A y cumplirá los 25 cm?

**Resultado medido de 3A: 107.9 cm de cierre físico.**

**Predicción: es muy probable que la media de 3B sea menor que 107.9 cm.**

**Probabilidad subjetiva de que 3B mejore a 3A: ≈95 %, con baja confianza estadística.**

**Probabilidad subjetiva de que la media de 3B sea ≤25 cm: ≈25–30 %, con confianza muy baja.**

**Justificación:**

El cierre de 3A fue de 107.9 cm, mientras que las experimentales de 3B tuvieron cierres físicos considerablemente menores.

Esto respalda la expectativa de que el control PID permita mejorar el cierre respecto al lazo abierto. Sin embargo, el umbral de 25 cm es más exigente y no fue alcanzado de forma consistente en las experimentales.

Como el cierre medido de 3A es 107.9 cm, cualquier media de 3B ≤25 cm necesariamente también será menor que el cierre de 3A. Por tanto, **la probabilidad asignada al cumplimiento simultáneo de ambos criterios es la misma que la del criterio ≤25 cm: aproximadamente 25–30 % bajo este juicio subjetivo**. Esta cifra no constituye una frecuencia empírica ni un cálculo estadístico validado.

**Comprobación:** verificar ambas condiciones con los tres cierres físicos oficiales:

$$
\overline{c}_{3B}\leq25\text{ cm}
$$

$$
\overline{c}_{3B}<107.9\text{ cm}
$$

**Qué la refutaría:** una media ≥107.9 cm contradiría la ventaja pronosticada respecto a 3A. Una media superior a 25 cm incumpliría el umbral principal de E7.

## 6. ¿Qué aportará más error al cierre físico?

**Predicción principal:** las esquinas y el rumbo físico de salida después de cada giro serán las fuentes de error más importantes, seguidas de la deriva durante las rectas.

**Justificación:**

E6 demostró que el PID de recta puede limitar el desvío lateral físico final a menos de 2 cm en pruebas aisladas.

En contraste, las experimentales de 3B mostraron desviaciones físicas al completar algunos giros, pese a que `/odom` indicaba una trayectoria aparentemente bien controlada.

En exp4, los errores laterales máximos calculados desde `/odom` durante las rectas fueron aproximadamente de 0.8 a 3.1 cm. Esto indica que el controlador mantiene su referencia estimada relativamente cerca de la trayectoria, pero no prueba que el robot siga físicamente el cuadrado ideal.

**Mecanismo específico del controlador (`scripts_pdi/core_cuadrado.py`):** después de completar cada giro, el método `_turn_done(x, y)` ejecuta en la **línea 213**:

```python
self.sx, self.sy = x, y
```

Esto **reancla el inicio de la siguiente recta en la posición que indica `/odom` al terminar la esquina**, incluso si la posición física quedó desplazada respecto del vértice ideal del cuadrado. A la vez, en la línea 209, `self.yaw_obj = self.yaw_target` conserva el **rumbo objetivo nominal**, que avanza en incrementos de 90° (`self.yaw_target = self.yaw_obj + pi/2` al finalizar cada lado, línea 200). Durante `AVANZA`, el error transversal se obtiene de `x`, `y` de `/odom`, del ancla `(sx, sy)` y de ese rumbo nominal (líneas 154–158); **no se calcula con una referencia externa de la geometría física dibujada en el suelo**.

Por tanto, la trayectoria puede desplazarse o deformarse físicamente mientras cada recta presenta un error `e_line` pequeño: **el PID corrige con respecto a la línea virtual reanclada en `/odom`, no fuerza el retorno a los cuatro vértices físicos ideales**. El programa calcula la distancia al origen en `FIN`, pero no emplea ese error de cierre para corregir la posición final. El deslizamiento y la discrepancia entre `/odom` y el movimiento real amplifican este mecanismo.

**Comprobación:** observar el rumbo de salida y la posición física tras cada esquina, registrar desviaciones con cinta o marcas, contrastarlas con `e_line`, `yaw` y `(x,y)` del CSV, y comparar la trayectoria física y la odométrica. Un `e_line` pequeño junto a vértices físicos desplazados sería compatible con el reanclaje descrito.

**Qué la refutaría:** giros físicamente cercanos a 90° acompañados de grandes desviaciones durante las rectas, indicando que estas últimas dominan el error.

## 7. ¿Cuánta variabilidad habrá entre las tres corridas?

**Predicción:** la diferencia entre el mayor y el menor cierre físico de las tres corridas será de aproximadamente 15 cm.

**Rango orientativo de esa diferencia: 5–30 cm.**

**Justificación:**

Las experimentales realizadas con `kd_yaw=0.3` produjeron cierres físicos aproximados de 36.5, 25.94 y 19.10 cm, con una diferencia máxima de alrededor de 17.4 cm.

Esta dispersión puede depender de variaciones de alineación inicial, adherencia, deslizamiento, condiciones de batería y dinámica de los giros. No contamos con mediciones suficientes para cuantificar por separado cada causa.

La proximidad entre exp4 y exp5, cuya diferencia fue de 6.84 cm, es favorable, pero no garantiza que las corridas oficiales presenten una dispersión igualmente pequeña.

**Comprobación:**

$$
R=\max(c_1,c_2,c_3)-\min(c_1,c_2,c_3)
$$

**Qué la refutaría:** una variabilidad mayor de 30 cm indicaría que la configuración es menos reproducible de lo previsto. Una diferencia muy pequeña sería un resultado favorable y mostraría mayor repetibilidad que la estimada.

## Límites de las predicciones

Este documento tiene las siguientes limitaciones:

- Las predicciones se elaboran después de conocer las experimentales de 3B; por tanto, no representan una predicción independiente anterior a toda prueba 3B.
- No tenemos mediciones físicas completas de los cuatro ángulos de giro de cada corrida.
- Las mediciones físicas de algunas experimentales fueron aproximadas, particularmente exp1 y exp2.
- No se ha aislado cuantitativamente cuánto error corresponde al deslizamiento, la calibración de odometría, el rumbo de salida o el seguimiento de la recta.
- La diferencia entre el cierre físico y `/odom` no es fija: en exp4 fue aproximadamente 22.2 cm y en exp5 aproximadamente 15.7 cm. En 3A, las distancias de cierre difirieron en unos 10.5 cm.
- La frecuencia observada de `/odom` fue aproximadamente de 11 Hz, mientras el controlador ejecuta su ciclo a 30 Hz. Esta diferencia puede influir en la respuesta de la componente derivativa, pero todavía no se ha demostrado cuánto explica de los errores físicos observados.
- Las probabilidades y los rangos se presentan como estimaciones de ingeniería, no como intervalos de confianza estadísticamente calibrados. El juicio de 25–30 % no se deduce matemáticamente de la media experimental ni de incluir o excluir `exp1`; es una valoración conservadora que debe contrastarse con la validación oficial.
- `exp1` no se incluye en el promedio descriptivo de la configuración final porque empleó `kd_yaw=0.6`; sí se presenta como evidencia histórica y en un análisis ilustrativo de sensibilidad.
- Los rumbos nominales y el reanclaje corresponden a las coordenadas publicadas en `/odom`, sin medición de la geometría física del cuadrado.
- El resultado de `FIN` no debe confundirse con la salida del proceso Python: en experimentos anteriores, el nodo permaneció activo después de alcanzar el objetivo.

### Seguridad

Antes de las corridas oficiales se deberá comprobar una parada física de emergencia efectiva, independiente de `Ctrl+C` y de la conexión remota.

Se mantendrá una zona despejada que incluya el cuadrado nominal de 2 × 2 m, el tamaño del robot y un margen adicional suficiente para desviaciones fuera de las marcas. No debe asumirse que el error de cierre esperado delimita la desviación máxima durante el recorrido.

El límite de `timeout=180 s` es un límite de ejecución administrativa, no una garantía de parada de los motores. La presencia de órdenes `v=0`, `w=0` en `FIN` explica la parada normal programada, pero no demuestra que la parada de emergencia funcione ante una incidencia.

### Registro y validación

Para cada corrida oficial se registrará:

| Corrida | Cierre físico | Cierre `/odom` | Yaw `/odom` | Rumbo físico final | Tiempo a `FIN` |
|---|---|---|---|---|---|
| `run1` | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| `run2` | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| `run3` | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| **Media** | **Pendiente** | — | — | — | — |

**Criterio de decisión:** se considerará cumplido E7-3B cuando las tres corridas oficiales hayan sido registradas con mediciones físicas y su cierre medio sea ≤25 cm y menor que los 107.9 cm obtenidos en 3A.

### Conclusión predictiva

A partir de E5, E6, E7-3A y las experimentales de E7-3B, esperamos que el ROSCar 4 complete el cuadrado con PID en aproximadamente 103 segundos, un cierre según `/odom` cercano a 3 cm y un cierre físico medio próximo a 27 cm.

La evidencia experimental permite anticipar una mejora importante respecto al lazo abierto de 3A, pero no garantiza alcanzar los 25 cm de promedio exigidos por la rúbrica. La validación dependerá de tres corridas oficiales independientes, realizadas con parámetros constantes, mediciones físicas documentadas y condiciones de seguridad verificadas.

Estas predicciones se conservarán como referencia previa a las corridas oficiales, sin reajustarlas retroactivamente según los resultados obtenidos.
