#!/bin/bash

# =================================================================
# Script de Lanzamiento de Utilidades LINUX
# Versión: 1.0 (Traducción de Lanzar-Utilidad.ps1 para modos de datos)
# =================================================================

set -e

# --- 1. Definición de Rutas ---
# (!! AJUSTA ESTA RUTA !!)
RUTA_GESTORPPT="/home/lencina/proyectos/UbuntuXLS"



CURRENT_PROJECT_DIR=$(dirname "$(readlink -f "$0")")
VENV_ACTIVATE_PATH="$HOME/.venv-wsl/bin/activate"
RUTA_SRC="$RUTA_GESTORPPT/src"

# --- 2. Configuración de Entorno ---
echo "--- Lanzador de Utilidades de Linux iniciado ---"
if [ -f "$VENV_ACTIVATE_PATH" ]; then
    source "$VENV_ACTIVATE_PATH"
fi
export PYTHONPATH="$RUTA_SRC"
echo "PYTHONPATH establecido a '$RUTA_SRC'"

# --- 3. Parseo de Argumentos (Simplificado) ---
# Espera argumentos como: -Modo -match -ArchivoFuente x.csv -ArchivoLog y.csv
MODO=""
PYTHON_ARGS=() # Array para argumentos de Python

while (( "$#" )); do
  case "$1" in
    -Modo)
      MODO="$2"
      shift 2
      ;;
    *)
      # Añadir el resto de argumentos (ej. -ArchivoFuente, x.csv) al array
      PYTHON_ARGS+=("$1")
      shift
      ;;
  esac
done

# --- 4. Lógica de cada modo ---
SCRIPT_PYTHON=""

case "$MODO" in
  -match)
    SCRIPT_PYTHON="$RUTA_GESTORPPT/utilidades/Match_logs.py"
    ;;
    
  -reporte-hash)
    SCRIPT_PYTHON="$RUTA_GESTORPPT/utilidades/ReporteHash.py"
    INPUT_FILE="$CURRENT_PROJECT_DIR/data/output/PreProcesamiento.xlsx"
    if [ ! -f "$INPUT_FILE" ]; then
        echo "Error: No se encontró el archivo de entrada en '$INPUT_FILE'." >&2
        exit 1
    fi
    PYTHON_ARGS=("$INPUT_FILE") # Sobrescribe los args, solo necesita este
    ;;
    
  -compara-hash)
    SCRIPT_PYTHON="$RUTA_GESTORPPT/utilidades/ComparaHash.py"
    # Reconstruimos los args. Asume que se pasan como -ArchivoMaster master.xlsx
    MASTER_FILE_PATH="$CURRENT_PROJECT_DIR/data/output/${PYTHON_ARGS[1]}"
    COMPARADO_PATH="$CURRENT_PROJECT_DIR/data/output/PreProcesamiento.xlsx"
    PYTHON_ARGS=("$MASTER_FILE_PATH" "$COMPARADO_PATH")
    ;;
    
  generar_csv)
    SCRIPT_PYTHON="$RUTA_GESTORPPT/utilidades/genera_csv_tablas_to_ppt.py"
    # Asume que se pasa como -ArchivoExcel tablas.xlsx
    EXCEL_FILE_PATH="$CURRENT_PROJECT_DIR/data/output/${PYTHON_ARGS[1]}"
    PYTHON_ARGS=("$EXCEL_FILE_PATH")
    ;;
    
  *)
    echo "Error: Modo de utilidad no reconocido o no migrado a Linux: '$MODO'." >&2
    exit 1
    ;;
esac

# --- 5. Ejecutar el script de utilidad ---
echo "Ejecutando (Linux): python3 $SCRIPT_PYTHON ${PYTHON_ARGS[@]}"
python3 "$SCRIPT_PYTHON" "${PYTHON_ARGS[@]}"

echo "--- Ejecución de la utilidad de Linux completada. ---"