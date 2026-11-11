#!/usr/bin/env python3
"""rc1_args — imprime las banderas `-p` de cuadrado_controller desde config/rc1_pid.yaml.

Evita el error típico del reto (kd:=0 en vez de kd:=0.0): todo número sale con punto decimal.
No lanza nada ni mueve nada: solo escribe texto.

Uso:
    python3 scripts/rc1_args.py <simulador|robot_real> [clave=valor ...]

    python3 scripts/rc1_args.py simulador experimento=recta line_offset=0.10 bias_w=0.06 log_csv=csv/exp1b_sim.csv
    python3 cuadrado_controller.py --ros-args $(python3 scripts/rc1_args.py robot_real experimento=giro90)

Las claves dadas en la línea de comandos pisan las del YAML (un parámetro por prueba).
"""
import os
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("Falta PyYAML:  pip install pyyaml  (en ROS 2 Humble ya viene: python3-yaml)")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML = os.path.join(RAIZ, "config", "rc1_pid.yaml")
NODO = "cuadrado_controller"


def valor(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(float(v))          # 3 -> 3.0, 0 -> 0.0
    return str(v)


def convertir(txt):
    """Texto de la línea de comandos -> número si lo es (con punto decimal), si no, texto."""
    try:
        return float(txt)
    except ValueError:
        return txt


def main(argv):
    if len(argv) < 2 or argv[1] not in ("simulador", "robot_real"):
        sys.exit(__doc__)
    with open(YAML, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    params = dict(cfg[argv[1]][NODO]["ros__parameters"])
    for extra in argv[2:]:
        if "=" not in extra:
            sys.exit(f"Argumento '{extra}' sin '=': usa clave=valor")
        k, v = extra.split("=", 1)
        params[k] = convertir(v)
    print(" ".join(f"-p {k}:={valor(v)}" for k, v in params.items()))
    if cfg[argv[1]].get("estado") == "PENDIENTE":
        print(f"AVISO: el bloque '{argv[1]}' sigue PENDIENTE (no son ganancias finales)", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
