# RC-1 — Tabla de transferencia: simulador → robot real

Con las **mismas ganancias**: ¿qué dio el simulador y qué dio el robot? ¿Qué cambió y por qué? (Anexo A.3 del reto.)
La columna «Esperábamos» se llena antes de la sesión de laboratorio; «Observado» y «Por qué» después.
Mientras exista el texto «[COMPLETAR]», `scripts/rc1_verificar.py` marca la tabla como pendiente.

| Aspecto | Simulador | Robot real | Esperábamos | Observado | Por qué |
|---|---|---|---|---|---|
| Motores e inercia | solo límites de aceleración (`accel_lin`, `accel_ang`) | respuesta de motores e inercia | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] |
| Derrape de las 4 ruedas (χ) | no existe | `b_eff = χ·b` | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] |
| Retardo de `/odom` | ≈ 0 | hay retardo; además ≈ 11 Hz medidos en el RC-0 frente a 50 Hz del simulador | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] |
| Sesgo de motores | inyectado con `bias_w` | existe de verdad | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] |
| Error de `/odom` | aleatorio por muestra + empuje del piso que no ve | sistemático (`r`, `b_eff`) | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] |
| Verdad terreno | `/sim/pose` | cinta métrica y transportador | – | – | – |

## Resultados lado a lado (completar con los CSV)

| Prueba | Ganancias | Sim: cierre `/odom` | Sim: cierre REAL | Robot: cierre `/odom` | Robot: cierre cinta |
|---|---|---|---|---|---|
| 3A | – | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] |
| 3B | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] |
| 3C | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] | – | – |
