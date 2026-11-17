---
title: "RC-1 · Grupo 8 — Lista de comprobación de la sesión de laboratorio (E6 y E7)"
subtitle: "RosCar 4 · ROS_DOMAIN_ID=8 · imprimir y llevar"
---

**Fecha:** ____ / ____ / 2026  **Hora de inicio:** ______  **Batería al empezar:** ______ %

**Roles** (escribir un nombre por rol):

| Rol | Nombre |
|---|---|
| Posiciona el robot y tiene el interruptor | |
| Mide con cinta / transportador | |
| Segunda lectura y anota en papel | |
| Teclado y comandos | |
| Cámara y fotos | |

**Regla de oro:** las predicciones se suben a git **antes** de correr la prueba que predicen, y no se modifican después. Los commits se hacen desde el clon de la PC, no desde el Pi.

# 0. Antes de salir de casa

- [ ] Clon actualizado (`git pull`), con `scripts/rc1_correr.sh`, `rc1_anotar_real.py`, `rc1_analiza_real.py` y `config/rc1_pid.yaml` (`kp_yaw` 1.0).
- [ ] `scripts_pdi/` (nodo del curso) en la carpeta del clon, para llevarlo al Pi (no viene en git).
- [ ] Predicciones ya subidas: E6 experimental 1 (`10c9a56`) y E7 3A (`39c65f9`).
- [ ] Borradores listos: E6 oficiales, E7 3B y BONUS (se cierran en el laboratorio).
- [ ] Token de GitHub a mano; plan para subir desde el clon con `git -c credential.helper= push ...` (y `-c http.sslBackend=openssl` si git se queda mudo).
- [ ] Materiales: cinta métrica ≥ 3 m, cinta adhesiva, 2 reglas largas («L» de tope y línea), escuadra, transportador circular, lápiz, esta hoja, celular con soporte.
- [ ] Preguntas al docente (si hay oportunidad): ¿la corrida en vivo de 3B y la del bonus son la misma? ¿se permite una de calentamiento? ¿quién mide?

# 1. Llegada y puesta en marcha (≈ 10–15 min)

- [ ] **Hora del Pi** (se pierde cada vez). En el host: `sudo timedatectl set-time "AAAA-MM-DD HH:MM:SS"` (hora de Lima) y comprobar `date -Is` y `docker exec ros2_dev date -Is`.
- [ ] **Terminal 1, bringup** (no cerrarla):
  `docker exec -it ros2_dev bash` → `source /opt/ros/humble/setup.bash; source /root/yahboomcar_ws/install/setup.bash; export ROS_DOMAIN_ID=8` → `ros2 launch capytown_esan bringup.launch.py wheel_params:=/root/wheel_params_g8.yaml`
  El log debe decir **b_eff=0.2138 … k_ang=1.0863**.
- [ ] **Herramientas en el contenedor:** desde la PC `scp -r` del clon al Pi y en el host del Pi `docker cp ~/microrospi5-sim_capytown_G8 ros2_dev:/root/` (con `scripts_pdi/` dentro).
- [ ] **Terminal 2** (contenedor, en `/root/microrospi5-sim_capytown_G8`): `scripts/rc1_correr.sh giro prueba --dry-run` imprime bien las banderas (kp_yaw 1.0, max_angular 1.0, linear_speed 0.1, bias_w 0.0).
- [ ] Comprobaciones que el script repite: hash del nodo (`d618e71722c4153d`), un solo `/odom_corrector`, un solo publicador de `/odom`, `/battery` ≥ 70.
- [ ] `ros2 bag record` funciona (prueba de 3 s y borrar el bag de prueba).
- [ ] **Marcas del piso** (ver sección 2).
- [ ] Interruptor al alcance; nadie toca el robot ni los cables durante una corrida; ≥ 60 cm libres a cada lado de la trayectoria.

# 2. Marcas y montaje

**E6, recta:** cinta de **2.4 m**, paralela al rumbo, **10 cm a la derecha del centro del robot**; cruz de inicio perpendicular; robot contra un tope (regla en «L»), lados del robot paralelos a la cinta (misma separación en el frente y atrás, ±2 mm).

**E7, cuadrado de 2 × 2 m** (+ 15 cm de margen): cruz de inicio con rumbo, esquinas marcadas **fuera** de la trayectoria de las ruedas; robot contra un tope; fotos de la posición inicial.

**Medición:** E6 = distancia **perpendicular** del centro del robot a la línea; E7 = distancia de la marca de inicio al **centro** del robot, y rumbo final con transportador. Dos personas, dos lecturas, foto.

# 3. E6 — recta real (≈ 25–30 min)

- [ ] **Experimental 1** (ganancias de partida Kp 3, Ki 0.5, Kd 4; predicciones ya subidas):
  `scripts/rc1_correr.sh recta exp1`
- [ ] Medir con cinta y anotar en la tabla de abajo. Cortar **ya** si el centro se desvía ≈ 30 cm o hay correcciones bruscas (anotar «abortada»).
- [ ] Copiar el CSV al clon y analizar: `python3 scripts/rc1_analiza_real.py csv/exp1d_real_exp1.csv --criterios e6 --png`
- [ ] **Decidir las ganancias finales** (3 min):
  - Si no oscila y el desvío es < 5 cm → se queda igual.
  - Si oscila → re-sintonía con **un solo parámetro** (candidata: `ki=0.1`); anotar `cambio=...`; queda máximo 2 re-sintonías en la Parte E.
- [ ] **Escribir y subir las predicciones de las oficiales** (indicando que son posteriores a la experimental). Comprobar `git log -1` antes de correr.
- [ ] **Tres corridas oficiales:** `scripts/rc1_correr.sh recta run1`, `run2`, `run3` (con `ki=…` si cambió). Medir cada una.
- [ ] Criterio del docente: **basta una con desvío < 5 cm**; reportar las tres.

# 4. E7 — cuadrado real (≈ 25–30 min)

- [ ] **3A (una vez):** `scripts/rc1_correr.sh 3a -` (≈ 90 s; predicciones ya subidas; `turn_scale` 1.0). Puede correrse mientras se escriben las de 3B.
- [ ] Medir: cierre con cinta y rumbo con transportador; anotar.
- [ ] **Cerrar y subir la versión final de las predicciones de 3B** (ganancias de la línea de E6, fecha, «redactadas después de E5 y E6 y antes de 3B»). Comprobar `git log -1` **antes** de correr.
- [ ] **3B ×3:** `scripts/rc1_correr.sh 3b run1`, `run2`, `run3` (≈ 100–105 s cada una; bag y CSV automáticos).
- [ ] Medir cada una y calcular la media de los tres cierres reales: ¿≤ 25 cm? ¿menor que el de 3A?
- [ ] **BONUS:** solo es en vivo; su borrador se cierra con los resultados de 3B.

# 5. Al terminar (en el laboratorio)

- [ ] Copiar **todos** los CSV, los bags y los `.nodo.log` al clon: en el host del Pi `rm -rf ~/csv_lab ~/bags_lab` y `docker cp ros2_dev:/root/microrospi5-sim_capytown_G8/csv ~/csv_lab`, `docker cp ros2_dev:/root/microrospi5-sim_capytown_G8/bags ~/bags_lab`; en PowerShell `scp -r pi@10.42.0.1:~/csv_lab ...` (y los bags).
- [ ] Fotos y esta hoja (medidas) guardadas.
- [ ] Apagar el robot, ponerlo a cargar.
- [ ] Revocar el token y borrar el clon de la PC compartida; cerrar sesión de GitHub.

# 6. Después (en casa)

- [ ] `python3 scripts/rc1_analiza_real.py csv/<archivo> --criterios … --png` por cada CSV (los gráficos **no salen solos**).
- [ ] Anotar la hoja: `python3 scripts/rc1_anotar_real.py 1D run1 ki=0.5 desvio_cm=…` (y `3A`, `3B` con `cierre_real_cm=…`, `yaw_acum_deg=…`, `bag=…`).
- [ ] `python3 scripts/rc1_verificar.py` y revisar qué falta.
- [ ] Completar el informe (E6 y E7), la tabla de transferencia, `avance_parteE.txt`, el README y las ganancias finales en `config/rc1_pid.yaml`; etiqueta `v1.0-rc1`.

# 7. Si falta tiempo (qué no se negocia)

1. **Seguridad y el interruptor.**
2. **Las medidas manuales y las fotos** (no se pueden reconstruir después).
3. **Predicciones subidas antes** de cada prueba (E6 oficiales, 3B).
4. Corridas oficiales de E6 (3), 3B (3), 3A (1); si no cabe todo, E6 y 3B primero.
5. Copiar los CSV antes de irse.
6. Lo demás (gráficos, anotaciones, informe) se hace en casa.

# 8. Hoja de medidas (rellenar en el laboratorio)

**E6 — recta (distancia perpendicular del centro del robot a la línea, cm)**

| Corrida | Hora | `FIN` (s) | Medida 1 | Medida 2 | ¿Abortada? | Observaciones / foto |
|---|---|---|---|---|---|---|
| exp1 | | | | | | |
| exp2 | | | | | | |
| run1 | | | | | | |
| run2 | | | | | | |
| run3 | | | | | | |

**E7 — cuadrado (cierre en cm = marca de inicio → centro del robot; rumbo final en grados)**

| Corrida | Hora | `FIN` (s) | Cierre `/odom` (nodo) | Cinta 1 | Cinta 2 | Rumbo final (transportador) | Observaciones / foto |
|---|---|---|---|---|---|---|---|
| 3A | | | | | | | |
| 3B run1 | | | | | | | |
| 3B run2 | | | | | | | |
| 3B run3 | | | | | | | |
| **Media 3B** | | | | | | | |

**Ganancias usadas** — línea: Kp ____ Ki ____ Kd ____ · giro: kp_yaw 1.0 ki_yaw ____ kd_yaw 0.6 · re-sintonías hechas en la Parte E: ____ de 3.

**Incidencias** (qué pasó, a qué hora, qué se hizo):

&nbsp;

&nbsp;

&nbsp;
