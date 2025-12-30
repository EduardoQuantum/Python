import subprocess
import sys
import argparse
from pathlib import Path
import os

# --- Rutas de Configuración Fijas ---
RUTA_GESTORPPT = Path("/home/lencina/proyectos/UbuntuXLS")
RUTA_SRC = RUTA_GESTORPPT / "src"
# El VENV se activa por VSC, pero lo mantenemos para referencia de la ruta de los binarios
VENV_ACTIVATE_PATH = Path(os.environ.get("HOME", "/home/lencina")) / ".venv-wsl" / "bin" / "activate"

# Usamos sys.executable que VSC ya resolvió para apuntar al python del venv
PYTHON_BIN = sys.executable 

def run_python_command(command, error_message):
    """
    Ejecuta un comando de Python directamente, confiando en que VSC ya configuró el VENV.
    Captura stdout y stderr en tiempo real.
    """
    try:
        # Ejecutamos el comando directamente con el Python resuelto por VSC
        subprocess.run(command, check=True, text=True, stderr=sys.stderr, stdout=sys.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR PYTHON: {error_message}", file=sys.stderr)
        print(f"Comando fallido: {e.cmd}", file=sys.stderr)
        sys.exit(e.returncode)

def main():
    """Contiene la lógica principal del pipeline Tidy."""
    
    # 1. Definición y Parsing de Argumentos
    parser = argparse.ArgumentParser(description="Orquestador Tidy Data (Python nativo).")
    parser.add_argument("modo", help="Modo de utilidad a ejecutar (ej: -harmoni, -dimension).")
    parser.add_argument("archivo_excel", help="Nombre del archivo Excel de entrada.")
    args = parser.parse_args()
    
    # 2. Configuración de Entorno
    os.environ["PYTHONPATH"] = str(RUTA_SRC)
    print(f"PYTHONPATH establecido a '{RUTA_SRC}'")
    
    # --- Rutas de Proyecto Dinámicas ---
    CURRENT_PROJECT_DIR = Path(__file__).parent 
    PROJECT_ROOT_DIR = CURRENT_PROJECT_DIR.parent
    
    # 3. Definición de las Rutas de Trabajo
    # ... (Lógica de Tidy Harmoni/Dimension) ...
    # [SIN CAMBIOS EN LA LÓGICA DE PIPELINE, solo en el wrapper]

    modo = args.modo
    
    if modo == "harmoni":
        RUTA_UTILIDADES = RUTA_GESTORPPT / "utilidades" / "Harmoni"
        RUTA_TRABAJO = PROJECT_ROOT_DIR / "TidyHarmoni"
        RUTA_AUXILIAR = RUTA_TRABAJO / "AuxiliarHarmoni"
        
        ARCHIVOS = [
            RUTA_TRABAJO / args.archivo_excel,
            RUTA_AUXILIAR / "intermedio_harmoni_01.xlsx",
            RUTA_AUXILIAR / "intermedio_harmoni_03.xlsx",
            RUTA_AUXILIAR / "intermedio_harmoni_04.xlsx",
            RUTA_AUXILIAR / "intermedio_harmoni_05.xlsx",
            RUTA_AUXILIAR / "intermedio_harmoni_06.xlsx",
            RUTA_AUXILIAR / "PreProcesamiento.xlsx"
        ]
        PIPELINE = [
            ("Paso 1: Pre-procesamiento", "harmoni_01.py"),
            ("Paso 2: Consolidar Metadatos", "harmoni_03.py"),
            ("Paso 3: Limpiar Etiquetas", "harmoni_04.py"),
            ("Paso 4: Enriquecer con Hashes", "harmoni_05.py"),
            ("Paso 5: Transformar a Largo", "harmoni_06.py"),
            ("Paso 6: Pivotear a Formato Final", "harmoni_07.py"),
        ]

    elif modo == "dimension":
        RUTA_UTILIDADES = RUTA_GESTORPPT / "utilidades" / "Dimension"
        RUTA_TRABAJO = PROJECT_ROOT_DIR / "Dimension"
        RUTA_AUXILIAR = RUTA_TRABAJO / "AuxExcelTidy"
        
        ARCHIVOS = [
            RUTA_TRABAJO / args.archivo_excel,
            RUTA_AUXILIAR / "ProcesamientoAuxiliar01.xlsx",
            RUTA_AUXILIAR / "ProcesamientoAuxiliar02.xlsx",
            RUTA_AUXILIAR / "ProcesamientoAuxiliar03.xlsx",
            RUTA_AUXILIAR / "PreProcesamiento.xlsx"
        ]
        PIPELINE = [
            ("Capítulo 1: Dimensionamiento", "procesamiento_dimension_excel.py"),
            ("Capítulo 2: Creación de Hashes", "procesamiento_hash02.py"),
            ("Capítulo 3: Formato Largo", "procesamiento_hash03.py"),
            ("Capítulo 4: Ensamblaje Final", "procesamiento_hash04.py"),
        ]

    else:
        print(f"ERROR: Modo de utilidad Tidy no reconocido: '{modo}'.", file=sys.stderr)
        sys.exit(1)

    # 4. Crear carpetas
    os.makedirs(RUTA_TRABAJO, exist_ok=True)
    os.makedirs(RUTA_AUXILIAR, exist_ok=True)

    print(f"\n--- INICIANDO PIPELINE ({modo}) ---")
    
    # 5. Ejecutar el Pipeline Secuencial
    for i, (paso, script) in enumerate(PIPELINE):
        script_path = RUTA_UTILIDADES / script
        archivo_entrada = ARCHIVOS[i]
        archivo_salida = ARCHIVOS[i+1]
        
        print(f"\n>>> Ejecutando: {paso} ({script})...")
        
        if i > 0 and not archivo_entrada.exists():
            print(f"--- ERROR: No se encontró el archivo de entrada intermedio: {archivo_entrada} ---", file=sys.stderr)
            sys.exit(1)

        # Comando: [PYTHON_BIN] [script_path] [entrada] [salida]
        command = [str(PYTHON_BIN), str(script_path), str(archivo_entrada), str(archivo_salida)]
        run_python_command(command, f"El script {script} falló durante el paso {paso}.")
        
        print(f">>> {paso} completado.")

    print("\n" + ("="*45))
    print("--- PIPELINE COMPLETADO CON ÉXITO ---")
    print(f"El archivo final se encuentra en: {archivo_salida}")
    print(("="*45))


if __name__ == "__main__":
    main()