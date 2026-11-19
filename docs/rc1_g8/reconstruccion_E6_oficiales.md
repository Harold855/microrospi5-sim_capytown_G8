# E6 — Hipótesis reconstruidas tras las corridas oficiales y contraste con los resultados

**CapyTown RC-1 · Grupo 8 · ROSCar 4 · 17 de noviembre de 2026**
**Documento:** reconstrucción metodológica **posterior** a las pruebas, basada en la sintonización previa, seguida del contraste con los registros de las corridas.

> **Nota de integridad académica.** Este documento se redactó **después** de realizar las corridas `run1`, `run2` y `run5`, y su autor **ya conocía sus resultados**. Por ello, las cuatro hipótesis de la sección A **no son predicciones escritas antes de ejecutar las corridas**: se formularon a partir de las pruebas de sintonización previas (principalmente las experimentales 12 y 13) y no deben contarse como predicciones previas en el informe. La única predicción de E6 escrita antes de correr está en `predicciones_E6_exp1.md` y corresponde a **otras ganancias** (Kp 3.0, Ki 0.5, Kd 4.0). La fecha real de este archivo es la de su commit.

## Condiciones de la prueba

- **Controlador:** `scripts_pdi/cuadrado_controller.py` original, sin modificar.
- **Modo:** `experimento=recta`, ROS 2 Humble en ROSCar físico.
- **Longitud objetivo:** `side=2.0 m`; **velocidad de referencia:** `linear_speed=0.10 m/s`.
- **Separación inicial:** `line_offset=+0.10 m`; el centro del robot se coloca aproximadamente **10 cm a la izquierda de la línea**, mirando hacia el extremo del tramo y orientado en paralelo a ella (alineación comprobada con dos lecturas, rueda delantera y trasera del mismo lado, con tolerancia de ±5 mm).
- **Sesgo artificial:** `bias_w=0.0`; **límite de velocidad angular:** `max_angular=1.0 rad/s`.
- **Ganancias usadas en las corridas contrastadas:** **`Kp=1.0`, `Ki=0.1`, `Kd=8.0`**.
- **Criterio del reto:** documentar **tres corridas**; la desviación lateral física final respecto de la línea objetivo debe ser **≤ 5 cm**. La medición se hace con cinta, perpendicularmente desde el centro del ROSCar a la raya negra, una vez detenido. El último `e_line` del CSV **no sustituye** esa medición.

### Planteo de hipótesis sobre la configuración final

La primera predicción (`predicciones_E6_exp1.md`) estudiaba `Kp=3.0`, `Ki=0.5`, `Kd=4.0` y anticipaba ≈ 13 cm de desviación lateral física, 3–5 cruces de la línea y oscilaciones importantes. **Esa predicción no se traslada a las oficiales**, porque hubo una sintonización real posterior.

La sintonización consistió en **13 pruebas exploratorias numeradas (exp1–exp13; exp5 es inválida: la cinta métrica quedó delante del robot y se enredó en las ruedas)**, además de pruebas de parada. Hubo cambios de `Kp`, `Ki` y `Kd` respecto de la configuración de partida del simulador; ver «Reglas pendientes» al final.

Antes de las oficiales se ejecutaron las experimentales **12 y 13**, ambas con `Kp=1.0`, `Ki=0.1`, `Kd=8.0`. Sus resultados según `/odom`:

| Indicador preliminar | Exp. 12 | Exp. 13 |
|---|---:|---:|
| Tiempo a `FIN` | 21.03 s | 20.97 s |
| Recorrido por `/odom` | 2.00 m | 2.00 m |
| `e_line` mínimo | −3.6 cm | −3.7 cm |
| `e_line` máximo | +10.0 cm | +10.0 cm |
| `\|e_line\|` final | 3.1 cm | 3.0 cm |
| Cruces significativos (umbral ±0.5 cm) | 1 | 1 |
| Mayor permanencia continua dentro de ±2 cm | 5.73 s | 5.73 s |
| Asentamiento definitivo dentro de ±2 cm | No detectado | No detectado |
| Yaw final según `/odom` | +1.0° | +2.1° |
| Inversiones de `w` en los últimos 2 s (`\|w\| ≥ 0.05`) | 0 | 0 |

En la experimental 13 se observó una **desviación física aproximada de 5 cm hacia la derecha**; en la 12 no hubo medición física. Dos ensayos no permiten asignar una probabilidad confiable de éxito.

---

# A. Hipótesis reconstruidas para las corridas oficiales

**Estado temporal de esta sección:** hipótesis formuladas **después** de las corridas, a partir de la evidencia de sintonización previa (principalmente las experimentales 12 y 13). Los rangos propuestos coinciden con lo observado en esas dos experimentales, lo que está justificado por ser la evidencia en la que se basan, pero el autor conocía los resultados de las oficiales al escribirlos.

## Hipótesis 1. Tiempo hasta `FIN` y asentamiento en ±2 cm

**Hipótesis:** con la pista libre y la odometría funcionando, el ROSCar alcanzará `FIN` en **20–23 s**, cerca de 21 s. El error `e_line` entrará en la banda de ±2 cm por intervalos, **sin permanecer necesariamente dentro de ella hasta el final**.

**Justificación:** el tiempo ideal sin correcciones es 2.0 m / 0.10 m/s = 20 s. Las experimentales 12 y 13 tardaron ≈ 21 s y registraron una permanencia continua máxima de 5.73 s en la banda, sin asentamiento definitivo.

**Verificación:** primer registro `FIN`, tiempo desde el inicio de `AVANZA`, ventanas continuas con `|e_line| ≤ 0.02 m`.

## Hipótesis 2. Desviación lateral física final y límite de 5 cm

**Hipótesis:** con alineación inicial correcta y sin interferencias, la desviación lateral física final será de **unos pocos centímetros**, con una banda orientativa de **2–6 cm**. Cumplir ≤ 5 cm es posible pero no está garantizado; la medición aproximada de 5 cm de la experimental 13 obliga a tratarlo como incierto.

**Justificación:** las experimentales 12 y 13 terminaron con errores estimados por `/odom` de ≈ 3 cm, y solo la 13 tuvo estimación física (≈ 5 cm). No hay evidencia suficiente para una distribución de errores físicos ni para un porcentaje de éxito.

**Verificación:** cinta perpendicular desde el centro del robot a la raya negra, conservando el lado (derecha/izquierda), contra ≤ 5 cm. Anotar por separado el `e_line` final de `/odom` y la orientación física.

## Hipótesis 3. Cruces de la línea y magnitud del sobrepaso

**Hipótesis:** **aproximadamente un cruce significativo** de la línea virtual y un sobrepaso al lado opuesto de **≈ 3–5 cm según `/odom`**. `e_line` comienza cerca de +10 cm (por `line_offset`) y alcanza valores negativos moderados.

**Justificación:** las experimentales 12 y 13 registraron un solo cruce (±0.5 cm) y un `e_line` mínimo de −3.6 a −3.7 cm. Con `Kd=4.0` la experimental 11 mostró dos cruces y un sobrepaso de 7.51 cm, de modo que el aumento de `Kd` amortiguó **en esas pruebas concretas**.

**Verificación:** contar cruces durante `AVANZA` (umbral ±0.5 cm), mínimo y máximo de `e_line` y de `w`, saturaciones con `|w| ≥ 0.99`. El sobrepaso estimado no equivale a una amplitud física medida.

## Hipótesis 4. Final del PID, orientación y órdenes en los últimos segundos

**Hipótesis:** `FIN` en torno a 21 s con `v=0` y `w=0` en la primera fila `FIN`; yaw final según `/odom` **dentro de ±5°**; último `|e_line|` de `AVANZA` de **≈ 2–5 cm**; sin inversiones angulares bruscas al terminar.

**Justificación:** las experimentales 12 y 13 terminaron con yaw de +1.0° y +2.1° y sin inversiones de `w` en los últimos 2 s. No se puede inferir de ahí el ángulo físico.

**Verificación:** primera fila `FIN`, última fila `AVANZA`, últimos 2 s de `w`, inversiones (`|w| ≥ 0.05`), yaw relativo y, si es posible, ángulo físico con transportador.

**Advertencia indispensable:** un `v=0, w=0` en el CSV **no prueba** que la orden haya llegado a los motores. Se observó repetidamente `RCLError: Failed to publish: publisher's context is invalid` al terminar el controlador, y en la exploratoria 5 un `Ctrl+C` no detuvo el movimiento. La prueba de parada posterior (`paro2`) **no tiene resultado registrado**, de modo que la parada controlada con `Ctrl+C` **no está verificada**. La parada física de motores y una persona en el interruptor siguen siendo requisitos de seguridad.

---

# B. Contraste con los resultados registrados

**Esta sección contiene observaciones, no predicciones.**

## B.1 Registro de todas las corridas

| Intento | Ganancias (Kp / Ki / Kd) | Tiempo a `FIN` | Yaw final `/odom` | Desviación lateral física | Estado |
|---|---|---:|---:|---:|---|
| **Run 1** | 1.0 / 0.1 / 8.0 | 20.9 s | +2.0° | **0.6 cm derecha** | Válida |
| **Run 2** | 1.0 / 0.1 / 8.0 | 21.0 s | −0.8° | **1.5 cm izquierda** | Válida |
| **Run 3** | No se confirmo | No aportan | No aportan | No se evaluo | Ocurrio un fallo físico durante la corrida (el Roscar se trabo con la cinta métrica y no pudo avanzar) |
| **Run 4** | No se confirmo | No aportado | No se aportan | **6 cm izquierda** | Invalida(Robot mal posicionado al inicio, excede el límite) |
| **Run 5** | 1.0 / 0.1 / 8.0 | 21.0 s | +1.6° | **0.5 cm derecha** | Válida (anotada en la hoja como `run3`, con la nota «CSV run5») |

Las tres corridas consideradas válidas (`run1`, `run2`, `run5`):

- **Promedio de la desviación lateral física absoluta:** (0.6 + 1.5 + 0.5) / 3 = **0.87 cm**; máximo 1.5 cm; las tres bajo 5 cm.
- **Promedio de tiempo a `FIN`:** (20.9 + 21.0 + 21.0) / 3 ≈ **21.0 s**.
- **Yaw según `/odom`:** +2.0°, −0.8°, +1.6°.
- El «error de cierre» del nodo (≈ 200.9, 200.8, 200.6 cm) es la distancia recorrida, **no** un error lateral.

## B.2 Verificación de las cuatro hipótesis con los CSV de `run1`, `run2` y `run5`

| Hipótesis | Dato registrado (`run1` / `run2` / `run5`) | Veredicto |
|---|---|---|
| **1.** `FIN` en 20–23 s; sin asentamiento permanente en ±2 cm | `FIN` 20.9 / 21.0 / 21.0 s; permanencia continua en ±2 cm de 6.30 / 3.80 / 6.37 s; sin asentamiento definitivo | **Se cumple** |
| **2.** Desviación física de 2–6 cm | 0.6 / 1.5 / 0.5 cm | **No se cumple la banda: los valores quedan por debajo** (mejor de lo previsto); las tres cumplen ≤ 5 cm |
| **3.** Un cruce; sobrepaso de 3–5 cm según `/odom` | 1 / 1 / 1 cruce; sobrepaso (|`e_line` mín.|) 4.2 / **2.7** / 3.3 cm | **Cruces: se cumple. Sobrepaso: se cumple en dos de tres; `run2` queda 0.3 cm fuera de la banda** |
| **4.** Yaw `/odom` dentro de ±5°; último `\|e_line\|` de 2–5 cm; `v=w=0` en `FIN` | Yaw +2.0 / −0.8 / +1.6°; `\|e_line\|` final 3.8 / 2.7 / 3.2 cm; `v=w=0` en la primera fila `FIN` en las tres; 0 inversiones de `w` en los últimos 2 s | **Se cumple** (el log no certifica la parada física) |

**`/odom` frente a la cinta.** Según `/odom` el error lateral final es de ≈ 2.7–3.8 cm, mientras que la cinta mide 0.5–1.5 cm. Hay un desfase sistemático de ≈ 3 cm entre ambos, de causa no determinada con estos datos. **El criterio de E6 lo da la cinta**, no `/odom`.

**Sobre el analizador.** Las líneas `[cumple]/[NO cumple]` que imprime `rc1_analiza_real.py --criterios e6` se refieren a las predicciones de la experimental 1 (Kp 3.0, Ki 0.5, Kd 4.0). **No** son una evaluación de estas corridas ni de las hipótesis de este documento.

## B.3 Registro e integridad de las evidencias

- Se conservan los CSV y los `*.nodo.log` de **todos** los intentos (`run1`–`run5`) y de las exploratorias, incluidos incidentes y descartes.
- En la hoja de resultados: `run1` = 0.6 cm derecha; `run2` = 1.5 cm izquierda; tercera corrida válida (CSV `run5`) = 0.5 cm derecha, con nota del descarte de `run3` (fallo físico, sin medición válida) y de `run4` (6 cm, mala colocación inicial). No se eliminan silenciosamente.
- El mensaje automático de `rc1_correr.sh` que sugiere anotar `ki=0.5` es una plantilla fija **incorrecta para estas corridas**: el controlador confirmó en su inicio `ki=0.1`.
- Se distinguen tres magnitudes: **error físico lateral** (cinta), **`e_line` estimado** (`/odom`) y **«error de cierre» longitudinal** (≈ 200 cm).

## Reglas pendientes de confirmar con el docente

1. **Re-sintonías.** Frente a la configuración de partida del simulador (Kp 3.0 / Ki 0.5 / Kd 4.0, `kp_yaw` 10), la configuración final cambia `kp_yaw` (E5), `Kp`, `Ki` y `Kd`: **cuatro cambios**, con un límite de tres en la Parte E. Falta confirmar si el límite cuenta las pruebas exploratorias o solo la configuración final frente a la de partida, y si un cuarto cambio está permitido.
2. **Repeticiones.** Falta confirmar si se admiten repeticiones por fallo físico o de colocación, o si solo cuentan las primeras tres corridas. Hasta entonces, no se afirma que `run1`, `run2` y `run5` sean las tres corridas oficialmente aceptadas.

## Conclusión

Tras la sintonización, la configuración `Kp=1.0`, `Ki=0.1`, `Kd=8.0` produjo dos experimentales previas (12 y 13) muy parecidas: ≈ 21 s, un cruce y sobrepaso de ≈ 3.6–3.7 cm según `/odom`. Las corridas válidas `run1`, `run2` y `run5` alcanzaron desviaciones físicas de **0.6, 1.5 y 0.5 cm** (promedio 0.87 cm), todas bajo el límite de 5 cm; de las cuatro hipótesis reconstruidas, tres se cumplen y la de la banda de error físico (2–6 cm) queda por debajo. El resultado se obtuvo tras **13 pruebas exploratorias** y con una combinación de `Kd` 8 y un protocolo de alineación inicial estricto, y con estos datos no se puede repartir el mérito entre ambos. 
