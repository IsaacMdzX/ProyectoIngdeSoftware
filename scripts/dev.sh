#!/usr/bin/env bash
set -Eeuo pipefail

# Ir a la raíz del proyecto (carpeta padre de scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJ_ROOT}"

# Activar o crear venv
if [[ -d "venv" ]]; then
  source venv/bin/activate
else
  echo "[dev] No se encontró ./venv. Creando entorno virtual..."
  python3 -m venv venv
  source venv/bin/activate
  echo "[dev] Instalando dependencias..."
  pip install --upgrade pip
  pip install -r Requeriments.txt || true
fi

# Cargar variables desde .env si existe (para FLASK_RUN_HOST/PORT/DEBUG, etc.)
if [[ -f ".env" ]]; then
  # exporta automáticamente variables definidas en .env al entorno
  set -a
  source .env
  set +a
fi

# Variables de entorno de Flask (con defaults si no vienen de .env)
export FLASK_APP=${FLASK_APP:-run.py}
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_RUN_HOST=${FLASK_RUN_HOST:-127.0.0.1}
export FLASK_RUN_PORT=${FLASK_RUN_PORT:-5000}

echo "[dev] Iniciando Flask en http://${FLASK_RUN_HOST}:${FLASK_RUN_PORT}"
exec flask run
