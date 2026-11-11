# RC-1 — Control PID: del simulador al robot real

**Grupo 8 · S-003** | Integrantes: [COMPLETAR] | RosCar 4 · ROS_DOMAIN_ID=8 | `noise:=low` (trabajo) y `medium` (estrés)

> Entrega: `informe.pdf`, **una sola página**. Esta plantilla es la estructura que pide el reto; el texto lo escribe el grupo.

## (a) Predicción
Qué predijimos (4 preguntas de la sección 3) y con qué razonamiento. Qué acertó y qué no, con el dato al lado.

## (b) Hoja de resultados
Tabla compacta de `hoja_resultados.csv`: prueba, ganancias, métrica clave. Las métricas de E2 y E3 van aquí:

| Prueba | \|e\| medio (cm) | t asentamiento | Error final |
|---|---|---|---|
| 1A–1D | | | |
| 2a–2c, 2p | (sobreimpulso %) | ±2° | |

## (c) Cierre `/odom` vs. real
Simulador (`cierre_real.py`) y robot (cinta): números lado a lado y la gráfica odom vs. real de la mejor corrida.

## (d) Por qué cambió el comportamiento al pasar al robot
Con las mismas ganancias: qué cambió y por qué (inercia, derrape χ, retardo y frecuencia de `/odom`, sesgo de motores, error sistemático de `r` y `b_eff`).

## (e) Qué cambiaríamos para el RC-2
Dos o tres cambios concretos, justificados con lo medido.
