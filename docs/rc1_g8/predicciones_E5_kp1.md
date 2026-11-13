# Predicciones previas — E5: Giro de 90° con ROSCar físico

**Configuración prevista:** controlador original: `kp_yaw=1.0`, `ki_yaw=0.0`, `kd_yaw=0.6` y `max_angular=1.0 rad/s`.

**Contexto:** Estas predicciones se formularon después de las diez corridas exploratorias documentadas en `registro_E5_giro_real.md` y antes de las corridas oficiales E5, cuyos resultados se registrarán por separado.

## 1. ¿Cuánto tardará en estabilizarse dentro de ±2° del objetivo?

**Predicción:** aproximadamente **6 segundos**, según `/odom`.

**¿Por qué?** Con una velocidad angular máxima de 1.0 rad/s, completar 90° a velocidad constante requeriría idealmente:

$$
t_{\min}=\frac{\pi/2\ \mathrm{rad}}{1.0\ \mathrm{rad/s}}\approx1.57\ \mathrm{s}
$$

Sin embargo, el controlador no mantendrá esa velocidad durante todo el giro. Con `kp_yaw=1.0`, la contribución proporcional disminuye a medida que se reduce el error angular. La fricción, la respuesta de los motores y la acción derivativa pueden prolongar la aproximación y generar correcciones antes de cumplir la condición de asentamiento. **Los 6 segundos son una estimación orientativa, no un tiempo calculado exactamente a partir de las ganancias.**

## 2. ¿Cuánto sobrepasará el ángulo objetivo?

**Predicción:** un sobreimpulso pequeño, de aproximadamente **1°**, alcanzando cerca de **91° según `/odom`**.

$$
M_p=\frac{91^\circ-90^\circ}{90^\circ}\times100\%\approx1.11\%
$$

**¿Por qué?** Al utilizar `kp_yaw=1.0`, se espera una corrección proporcional menos agresiva conforme el robot se acerque a 90°. La componente derivativa podría amortiguar parte del movimiento. Aun así, la inercia, el retardo de los motores y las variaciones de odometría podrían producir un sobrepaso distinto al previsto. **Esta predicción se refiere al máximo de `/odom`, no al ángulo físico medido con transportador.**

## 3. ¿Cuál será el error angular final real?

**Predicción:** el ángulo físico final podría encontrarse en un **rango aproximado de 75° a 95°**, equivalente a un **error absoluto de 0° a 15°** respecto del objetivo de 90°, dependiendo principalmente de las condiciones de contacto con el suelo. No se presupone que todas las corridas oficiales cumplan el criterio E5.

$$
E_{\mathrm{final,real}}=\left|90^\circ-\theta_{\mathrm{final,real}}\right|
$$

**¿Por qué?** El rango toma como referencia la dispersión identificada en las corridas exploratorias, sin tratar esos datos como resultados oficiales. Aunque el controlador se detenga cerca de 90° según `/odom`, el giro físico puede diferir debido al deslizamiento de las ruedas, la fricción del suelo y las limitaciones de la estimación odométrica. **El criterio E5 solo se considerará cumplido si el transportador indica entre 87° y 93°**, es decir, un error absoluto no mayor de 3°.

## 4. ¿Cómo se comportará el robot en los últimos grados del giro?

**Predicción:** disminuirá su velocidad angular al aproximarse a 90°, podrá realizar pequeñas correcciones de sentido y terminará en estado `FIN`, sin oscilaciones sostenidas.

**¿Por qué?** Con `kp_yaw=1.0`, la contribución proporcional disminuye conforme el error se acerca a cero. La derivada intenta amortiguar las variaciones, aunque la frecuencia de `/odom`, los retardos y la fricción pueden generar correcciones momentáneas.

**Criterio comprobable en el CSV:** se verificará que aparezca el estado `FIN` con velocidad angular comandada **`w=0.000 rad/s`**; que, antes de entrar a `FIN`, el error `|e_yaw|` permanezca **por debajo de 2° durante al menos 0.3 s consecutivos**; y que, en los **2 s previos a `FIN`**, existan **como máximo dos inversiones de signo de `w`** considerando solo órdenes con `|w| ≥ 0.05 rad/s`. Si no se cumplen estas condiciones, se registrará la diferencia entre la predicción y el comportamiento observado, sin alterar las predicciones.
