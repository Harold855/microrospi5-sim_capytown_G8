# Predicciones previas — E5: Giro de 90° con ROSCar físico

## 1. ¿Cuánto tardará en estabilizarse dentro de ±2° del objetivo?

**Predicción:** aproximadamente **2.4 segundos**, según `/odom`.

**¿Por qué?** Con una velocidad angular máxima de 1.0 rad/s, completar 90° a velocidad constante requeriría idealmente:

$$
t_{\min}=\frac{\pi/2\ \mathrm{rad}}{1.0\ \mathrm{rad/s}}\approx1.57\ \mathrm{s}
$$

Se estima un asentamiento más lento porque el controlador reduce la velocidad al acercarse al objetivo y el robot presenta inercia, fricción y retardos. Los 2.4 s son una estimación, no un resultado calculado a partir de las ganancias.

## 2. ¿Cuánto sobrepasará el ángulo objetivo?

**Predicción:** un sobreimpulso de **2°**, alcanzando aproximadamente **92° según `/odom`**.

$$
M_p=\frac{92^\circ-90^\circ}{90^\circ}\times100\%\approx2.22\%
$$

**¿Por qué?** La configuración 2p1 no presentó sobreimpulso en el simulador. Se espera que conserve una respuesta amortiguada, aunque la inercia y la respuesta de los motores físicos podrían producir un pequeño exceso.

## 3. ¿Cuál será el error angular final real?

**Predicción:** aproximadamente **2° de error absoluto**, medido con transportador respecto del giro objetivo.

$$
E_{\mathrm{final,real}}=\left|90^\circ-\theta_{\mathrm{final,real}}\right|\approx2^\circ
$$

**¿Por qué?** En el simulador, 2p1 terminó con un error de aproximadamente 0.22° según `/odom`. Se estima un error real mayor por posibles deslizamientos, diferencias de calibración y limitaciones de la odometría. Un giro final de 88° o 92° correspondería al error previsto.

## 4. ¿Cómo se comportará el robot en los últimos grados del giro?

**Predicción:** reducirá progresivamente su velocidad y se detendrá **sin oscilaciones sostenidas**; podrían aparecer pequeñas correcciones.

**¿Por qué?** La contribución proporcional disminuye al reducirse el error y la derivativa tiende a amortiguar el movimiento. El ruido de odometría y la respuesta de los motores podrían generar correcciones breves, aunque no se asegura que ocurran.
