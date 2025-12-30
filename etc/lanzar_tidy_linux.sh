#!/bin/bash

# =================================================================
# Script de Lanzamiento de Tidy Data (LINUX)
# Versión: 1.1 (Corregido el bug de parseo de IFS)
# =================================================================

# Detener el script si un comando falla
set -e

# --- 1. CONFIGURACIÓN PRINCIPAL ---
# (!! AJUSTA ESTA RUTA !!)
RUTA_GESTORPPT="/home/lencina/proyectos/UbuntuXLS"

PYTHON_EXECUTABLE="python3"

# Directorio del proyecto actual (desde donde se ejecuta este script)
RUTA_PROYECTO=$(dirname "$(readlink -f "$0")")

# --- 2. PARSEO DE ARGUMENTOS ---
MODO=""
ARCHIVO_EXCEL=""

while (( "$#" )); do
  case "$1" in
    -Modo)
      MODO="$2"
      shift 2
      ;;
    -ArchivoExcel)
      ARCHIVO_EXCEL="$2"
      shift 2
      ;;
    *) # Ignorar argumentos desconocidos
      shift
      ;;
  esac
done

if [ -z "$MODO" ] || [ -z "$ARCHIVO_EXCEL" ]; then
    echo "Error: Se requieren los argumentos -Modo y -ArchivoExcel." >&2
    exit 1
fi

# --- 3. LÓGICA DEL SCRIPT ---
echo "--- Lanzador Tidy de Linux iniciado para el modo: $MODO ---"

# --- 4. CONFIGURACIÓN DE ENTORNO ---
VENV_ACTIVATE_PATH="$HOME/.venv-wsl/bin/activate"
if [ -f "$VENV_ACTIVATE_PATH" ]; then
    echo "Activando entorno virtual de Linux..."
    source "$VENV_ACTIVATE_PATH"
fi

export PYTHONPATH="$RUTA_GESTORPPT/src"
echo "PYTHONPATH establecido."

# --- 5. DEFINICIÓN DE PIPELINES ---
declare -a pipeline # Declarar un array vacío

case "$MODO" in
  -harmoni)
    RUTA_UTILIDADES="$RUTA_GESTORPPT/utilidades/Harmoni"
    RUTA_TRABAJO="$RUTA_PROYECTO/TidyHarmoni"
    RUTA_AUXILIAR="$RUTA_TRABAJO/AuxiliarHarmoni"

    # Verificamos si el usuario pasó una ruta absoluta o solo el nombre
    if [[ "$ARCHIVO_EXCEL" == /* ]]; then
        ARCHIVO_ENTRADA_ORIGINAL="$ARCHIVO_EXCEL"
    else
        ARCHIVO_ENTRADA_ORIGINAL="$RUTA_TRABAJO/$ARCHIVO_EXCEL"
    fi
    
    ARCHIVO_INTERMEDIO_01="$RUTA_AUXILIAR/intermedio_harmoni_01.xlsx"
    ARCHIVO_INTERMEDIO_03="$RUTA_AUXILIAR/intermedio_harmoni_03.xlsx"
    ARCHIVO_INTERMEDIO_04="$RUTA_AUXILIAR/intermedio_harmoni_04.xlsx"
    ARCHIVO_INTERMEDIO_05="$RUTA_AUXILIAR/intermedio_harmoni_05.xlsx"
    ARCHIVO_INTERMEDIO_06="$RUTA_AUXILIAR/intermedio_harmoni_06.xlsx"
    ARCHIVO_FINAL="$RUTA_AUXILIAR/PreProcesamiento.xlsx"
    
    # --- FIX: Usamos '|' como separador ---
    # Formato: "Paso|Script|Entrada|Salida"
    pipeline=(
        "Paso 1: Pre-procesamiento|harmoni_01.py|$ARCHIVO_ENTRADA_ORIGINAL|$ARCHIVO_INTERMEDIO_01"
        "Paso 2: Consolidar Metadatos|harmoni_03.py|$ARCHIVO_INTERMEDIO_01|$ARCHIVO_INTERMEDIO_03"
        "Paso 3: Limpiar Etiquetas|harmoni_04.py|$ARCHIVO_INTERMEDIO_03|$ARCHIVO_INTERMEDIO_04"
        "Paso 4: Enriquecer con Hashes|harmoni_05.py|$ARCHIVO_INTERMEDIO_04|$ARCHIVO_INTERMEDIO_05"
        "Paso 5: Transformar a Largo|harmoni_06.py|$ARCHIVO_INTERMEDIO_05|$ARCHIVO_INTERMEDIO_06"
        "Paso 6: Pivotear a Formato Final|harmoni_07.py|$ARCHIVO_INTERMEDIO_06|$ARCHIVO_FINAL"
    )
    ;;

  -dimension)
    RUTA_UTILIDADES="$RUTA_GESTORPPT/utilidades/Dimension"
    RUTA_TRABAJO="$RUTA_PROYECTO/Dimension"
    RUTA_AUXILIAR="$RUTA_TRABAJO/AuxExcelTidy"

    # Verificamos si el usuario pasó una ruta absoluta o solo el nombre
    if [[ "$ARCHIVO_EXCEL" == /* ]]; then
        ARCHIVO_ENTRADA_ORIGINAL="$ARCHIVO_EXCEL"
    else
        ARCHIVO_ENTRADA_ORIGINAL="$RUTA_TRABAJO/$ARCHIVO_EXCEL"
    fi

    ARCHIVO_INTERMEDIO_01="$RUTA_AUXILIAR/ProcesamientoAuxiliar01.xlsx"
    ARCHIVO_INTERMEDIO_02="$RUTA_AUXILIAR/ProcesamientoAuxiliar02.xlsx"
    ARCHIVO_INTERMEDIO_03="$RUTA_AUXILIAR/ProcesamientoAuxiliar03.xlsx"
    ARCHIVO_FINAL="$RUTA_AUXILIAR/PreProcesamiento.xlsx"

    # --- FIX: Usamos '|' como separador ---
    pipeline=(
        "Capítulo 1: Dimensionamiento|procesamiento_dimension_excel.py|$ARCHIVO_ENTRADA_ORIGINAL|$ARCHIVO_INTERMEDIO_01"
        "Capítulo 2: Creación de Hashes|procesamiento_hash02.py|$ARCHIVO_INTERMEDIO_01|$ARCHIVO_INTERMEDIO_02"
        "Capítulo 3: Formato Largo|procesamiento_hash03.py|$ARCHIVO_INTERMEDIO_02|$ARCHIVO_INTERMEDIO_03"
        "Capítulo 4: Ensamblaje Final|procesamiento_hash04.py|$ARCHIVO_INTERMEDIO_03|$ARCHIVO_FINAL"
    )
    ;;
  
  *)
    echo "Error: Modo no reconocido '$MODO'." >&2
    exit 1
    ;;
esac

# Crear carpetas
mkdir -p "$RUTA_TRABAJO"
mkdir -p "$RUTA_AUXILIAR"

echo ""
echo "--- INICIANDO PIPELINE ($MODO) ---"
START_TIME=$SECONDS

# --- 6. EJECUTAR EL PIPELINE (CORREGIDO) ---
for step in "${pipeline[@]}"; do
    # --- FIX: Usamos '|' como delimitador ---
    IFS='|' read -r PASO SCRIPT ENTRADA SALIDA <<< "$step"
    
    SCRIPT_PATH="$RUTA_UTILIDADES/$SCRIPT"
    echo ""
    echo ">>> Ejecutando: $PASO ($SCRIPT)..."
    STEP_START_TIME=$SECONDS

    # Verificar que el archivo de entrada exista
    if [ ! -f "$ENTRADA" ]; then
        echo "--- ERROR: No se encontró el archivo de entrada para este paso: $ENTRADA ---" >&2
        echo "--- PIPELINE DETENIDO ---" >&2
        exit 1
    fi

    # Ejecutar Python
    $PYTHON_EXECUTABLE "$SCRIPT_PATH" "$ENTRADA" "$SALIDA"
    
    STEP_END_TIME=$SECONDS
    STEP_DURATION=$((STEP_END_TIME - STEP_START_TIME))
    echo ">>> $PASO completado en ${STEP_DURATION}s"

done

END_TIME=$SECONDS
TOTAL_DURATION=$((END_TIME - START_TIME))

echo ""
echo "============================================="
echo "--- PIPELINE COMPLETADO CON ÉXITO ---"
echo "Tiempo total de ejecución: ${TOTAL_DURATION}s"
echo "El archivo final se encuentra en: $ARCHIVO_FINAL"
echo "============================================="
