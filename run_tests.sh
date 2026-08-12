#!/usr/bin/env bash
set -e

source venv/bin/activate

# Sin argumento corre todo tests/; con argumento corre solo lo que le pases
# (ej: ./run_tests.sh tests/test_steps_imagenes.py)
OBJETIVO="${1:-tests/}"

pytest "$OBJETIVO" -v -s --html=reporte_html/reporte.html --self-contained-html

open reporte_html/reporte.html
