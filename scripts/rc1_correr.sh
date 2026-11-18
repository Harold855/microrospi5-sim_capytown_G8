#!/usr/bin/env bash
# rc1_correr.sh — lanza UNA corrida del robot real con las comprobaciones, el CSV, el bag y la orden de parada ya puestos.
# NO modifica el nodo del curso: solo arma y ejecuta el mismo comando que se escribía a mano.
#
# Uso (dentro del contenedor ros2_dev, desde la raíz del repositorio, con el bringup ya corriendo):
#     scripts/rc1_correr.sh <giro|recta|3a|3b> <nombre> [clave=valor ...] [--dry-run] [-y] [--sin-bag] [--sin-chequeos]
#
#   giro   experimento=giro90                 csv/exp2_real_giro90_<nombre>.csv    límite 15 s
#   recta  experimento=recta line_offset=0.10 ki=0.5   csv/exp1d_real_<nombre>.csv límite 40 s
#   3a     experimento=cuadrado_abierto       csv/exp3a_real[_<nombre>].csv        límite 150 s  + bag rc1_real_3a[_<nombre>]
#   3b     experimento=cuadrado               csv/exp3b_real_<nombre>.csv          límite 180 s  + bag rc1_real_3b_<nombre>
#   Los clave=valor extra pisan los del YAML (un parámetro por prueba), por ejemplo:  kp_yaw=1.0  ki=0.1  ki_yaw=0.05
#   Para 3a el <nombre> puede ir vacío ("" o "-"): usa exp3a_real.csv y bags/rc1_real_3a.
#
# Ejemplos:
#     scripts/rc1_correr.sh giro run1
#     scripts/rc1_correr.sh recta exp1
#     scripts/rc1_correr.sh recta run2 ki=0.1
#     scripts/rc1_correr.sh 3a -
#     scripts/rc1_correr.sh 3b run1
#     scripts/rc1_correr.sh 3b run1 --dry-run        # muestra todo sin ejecutar nada
#
# Qué hace, en orden: 1) comprobaciones (hash del nodo, un solo /odom_corrector, un publicador en /odom, batería, hora, archivos que no
# existan ya); 2) pide confirmación («SI»: robot alineado y persona en el interruptor); 3) graba el bag (3a y 3b); 4) lanza el nodo con
# `timeout -s INT`; 5) SIEMPRE publica ceros en /cmd_vel al terminar o al cortar (el robot real conserva la última orden); 6) guarda lo que
# imprimió el nodo en csv/<csv>.nodo.log y propone el comando de rc1_anotar_real.py con los valores de «FIN».
set -u

HASH_CTRL="d618e71722c4153d"   # cuadrado_controller.py original (prefijo del sha256)
HASH_CORE="a45a46afa2d36913"   # core_cuadrado.py original

DRY=0; SI=0; BAG=1; CHEQ=1
POS=()
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    -y) SI=1 ;;
    --sin-bag) BAG=0 ;;
    --sin-chequeos) CHEQ=0 ;;
    *) POS+=("$a") ;;
  esac
done
if [ "${#POS[@]}" -lt 1 ]; then sed -n '2,25p' "$0"; exit 2; fi

PRUEBA="${POS[0]}"; NOMBRE="${POS[1]:-}"; EXTRA=("${POS[@]:2}")
[ "$NOMBRE" = "-" ] && NOMBRE=""
suf=""; [ -n "$NOMBRE" ] && suf="_$NOMBRE"

case "$PRUEBA" in
  giro)  BASE=(experimento=giro90);                         CSV="csv/exp2_real_giro90${suf:-_run}.csv"; T=15;  BAGDIR="" ;;
  recta) BASE=(experimento=recta line_offset=0.10 ki=0.5);  CSV="csv/exp1d_real${suf:-_run}.csv";        T=40;  BAGDIR="" ;;
  3a)    BASE=(experimento=cuadrado_abierto);               CSV="csv/exp3a_real${suf}.csv";             T=150; BAGDIR="bags/rc1_real_3a${suf}" ;;
  3b)    BASE=(experimento=cuadrado);                       CSV="csv/exp3b_real${suf:-_run}.csv";       T=180; BAGDIR="bags/rc1_real_3b${suf:-_run}" ;;
  *) echo "Prueba '$PRUEBA' no válida (giro, recta, 3a, 3b)."; exit 2 ;;
esac
[ "$PRUEBA" = "giro" ] || [ "$PRUEBA" = "recta" ] || [ "$PRUEBA" = "3b" ] && [ -z "$NOMBRE" ] && { echo "Falta el <nombre> de la corrida (run1, exp1, ...)."; exit 2; }
[ "$BAG" = "0" ] && BAGDIR=""

ARGS_CMD=(python3 scripts/rc1_args.py robot_real "${BASE[@]}" "${EXTRA[@]}" "log_csv=$CSV")
NODO_CMD="timeout --foreground -s INT $T python3 scripts_pdi/cuadrado_controller.py --ros-args \$(${ARGS_CMD[*]})"
STOP_CMD='ros2 topic pub -r 10 -t 30 /cmd_vel geometry_msgs/msg/Twist "{}"'

echo "=== rc1_correr: $PRUEBA ${NOMBRE:-(sin nombre)} ==="
echo "CSV:   $CSV"
[ -n "$BAGDIR" ] && echo "Bag:   $BAGDIR"
echo "Nodo:  $NODO_CMD"
echo "Para:  $STOP_CMD"
if [ "$DRY" = "1" ]; then
  echo "--- banderas que recibiría el nodo ---"; "${ARGS_CMD[@]}" 2>&1 | sed 's/^/  /'
  echo "(--dry-run: no se ejecutó nada)"; exit 0
fi

fallo() { echo "ABORTO: $1"; exit 1; }
if [ "$CHEQ" = "1" ]; then
  echo "--- comprobaciones ---"
  [ -f scripts_pdi/cuadrado_controller.py ] || fallo "no existe scripts_pdi/cuadrado_controller.py (¿estás en la raíz del repositorio, dentro del contenedor?)"
  h1=$(sha256sum scripts_pdi/cuadrado_controller.py | cut -c1-16); h2=$(sha256sum scripts_pdi/core_cuadrado.py | cut -c1-16)
  [ "$h1" = "$HASH_CTRL" ] || fallo "cuadrado_controller.py NO es el original (sha $h1)"
  [ "$h2" = "$HASH_CORE" ] || fallo "core_cuadrado.py NO es el original (sha $h2)"
  echo "  nodo original: OK"
  command -v ros2 >/dev/null || fallo "ros2 no está en el PATH (source /opt/ros/humble/setup.bash y el workspace)"
  [ "${ROS_DOMAIN_ID:-}" = "8" ] || fallo "ROS_DOMAIN_ID no es 8 (es '${ROS_DOMAIN_ID:-vacío}')"
  nodos=$(ros2 node list 2>/dev/null)
  n=$(echo "$nodos" | grep -c '^/odom_corrector$')
  [ "$n" = "1" ] || fallo "hay $n nodos /odom_corrector (debe haber 1)"
  echo "$nodos" | grep -q '^/YB_Car_Node$' || fallo "no aparece /YB_Car_Node"
  np=$(ros2 topic info /odom -v 2>/dev/null | grep -c 'Publisher count: 1')
  [ "$np" = "1" ] || fallo "/odom no tiene exactamente 1 publicador"
  echo "  1 /odom_corrector, 1 publicador de /odom, /YB_Car_Node presente: OK"
  bat=$(ros2 topic echo /battery --once 2>/dev/null | awk '/data:/{print $2}')
  echo "  batería: ${bat:-?}"
  if [ -n "${bat:-}" ] && [ "${bat%.*}" -lt 70 ] 2>/dev/null; then fallo "batería < 70"; fi
  echo "  hora del contenedor (UTC): $(date -u -Is)   ← compárala con la hora real"
  [ -e "$CSV" ] && fallo "ya existe $CSV (otro nombre, para no sobrescribirlo)"
  [ -n "$BAGDIR" ] && [ -e "$BAGDIR" ] && fallo "ya existe $BAGDIR (otro nombre)"
fi
mkdir -p csv bags

if [ "$SI" != "1" ]; then
  read -r -p "¿Robot alineado en el tope, zona despejada y persona con la mano en el interruptor? Escribe SI: " r
  [ "$r" = "SI" ] || fallo "cancelado"
fi

BAGPID=""
parar() {
  trap - EXIT INT TERM
  echo; echo "--- orden de parada (ceros en /cmd_vel) ---"
  ros2 topic pub -r 10 -t 30 /cmd_vel geometry_msgs/msg/Twist "{}" >/dev/null 2>&1
  if [ -n "$BAGPID" ]; then kill -INT "$BAGPID" 2>/dev/null; wait "$BAGPID" 2>/dev/null; echo "bag cerrado: $BAGDIR"; fi
}
trap parar EXIT INT TERM

if [ -n "$BAGDIR" ]; then
  ros2 bag record /odom /cmd_vel /tf -o "$BAGDIR" >/dev/null 2>&1 &
  BAGPID=$!; sleep 2; echo "bag grabando: $BAGDIR"
fi

LOG="${CSV%.csv}.nodo.log"
echo "--- corriendo (límite $T s; si sale FIN el nodo termina solo) ---"
ARGS=$("${ARGS_CMD[@]}" 2>/dev/null)
# shellcheck disable=SC2086
timeout --foreground -s INT "$T" python3 scripts_pdi/cuadrado_controller.py --ros-args $ARGS 2>&1 | tee "$LOG"

parar
FIN=$(grep -m1 'FIN\. error de cierre' "$LOG" || true)
echo
if [ -n "$FIN" ]; then
  echo "$FIN" | sed 's/.*FIN/FIN/'
  cierre=$(echo "$FIN" | sed -n 's/.*error de cierre = \([0-9.]*\) cm.*/\1/p')
  yaw=$(echo "$FIN" | sed -n 's/.*yaw acumulado = \([-0-9.]*\) deg.*/\1/p')
  tiempo=$(echo "$FIN" | sed -n 's/.*tiempo = \([0-9.]*\) s.*/\1/p')
else
  echo "SIN FIN (se cortó por el límite de $T s o a mano): anótalo como corrida no terminada y mide dónde quedó el robot."
  cierre=""; yaw=""; tiempo=""
fi
etq="${NOMBRE:-unica}"
echo "--- siguiente: medir con cinta/transportador (dos personas) y anotar ---"
case "$PRUEBA" in
  giro)  echo "python3 scripts/rc1_anotar_real.py 2 $etq e_fin_deg=<error con transportador> cierre_odom_cm=${cierre:-} --nota \"FIN nodo: yaw ${yaw:-?} deg, ${tiempo:-?} s\"" ;;
  recta) echo "python3 scripts/rc1_anotar_real.py 1D $etq ki=0.5 desvio_cm=<cinta> --nota \"FIN nodo: ${tiempo:-?} s\"" ;;
  3a)    echo "python3 scripts/rc1_anotar_real.py 3A $etq cierre_odom_cm=${cierre:-} cierre_real_cm=<cinta> yaw_acum_deg=<transportador> bag=$BAGDIR --nota \"FIN nodo: yaw ${yaw:-?} deg, ${tiempo:-?} s\"" ;;
  3b)    echo "python3 scripts/rc1_anotar_real.py 3B $etq cierre_odom_cm=${cierre:-} cierre_real_cm=<cinta> yaw_acum_deg=<transportador> bag=$BAGDIR --nota \"FIN nodo: yaw ${yaw:-?} deg, ${tiempo:-?} s\"" ;;
esac
echo "CSV: $CSV   log del nodo: $LOG"
