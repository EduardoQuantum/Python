import subprocess
import sys
import argparse
import os
from pathlib import Path

# --- Rutas de Configuración Fijas ---
# Raíz de la caja de herramientas (UbuntuXLS)
RUTA_GESTORPPT = Path("/home/lencina/proyectos/UbuntuXLS")
RUTA_SRC = RUTA_GESTORPPT / "src"

# Entorno Virtual (Ruta basada en tu configuración: ~/.venv-wsl)
VENV_ACTIVATE_PATH = Path(os.environ.get("HOME", "/home/lencina")) / ".venv-wsl" / "bin" / "activate"

def run_bash_command(command, error_message):
    """
    Ejecuta un comando en el shell de Bash y verifica el código de salida.
    Utiliza shell=True para que 'source' y los pipes funcionen.
    """
    try:
        # Ejecutamos el comando y capturamos la salida en tiempo real
        result = subprocess.run(command, check=True, shell=True, executable='/bin/bash', 
                                text=True, stderr=sys.stderr, stdout=sys.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR PYTHON: {error_message}", file=sys.stderr)
        print(f"Comando fallido: {e.cmd}", file=sys.stderr)
        sys.exit(e.returncode)

def main():
    """Define el parser de argumentos y ejecuta la lógica principal del pipeline."""
    
    # --- 1. Definición y Parsing de Argumentos (CORREGIDO) ---
    # Esto debe ocurrir primero para manejar los argumentos de VSC.
    parser = argparse.ArgumentParser(description="Orquestador Principal del Pipeline (Python nativo).")
    parser.add_argument("-f", "--formato", default="txt", help="Formato de salida (txt, xls).")
    parser.add_argument("-s", "--filtrar-sufijo", default="", help="Sufijo para filtrar archivos.")
    parser.add_argument("-b", "--banners", action="store_true", help="Incluir el paso de generación de banners.")
    args = parser.parse_args()

    # --- 2. Rutas de Proyecto Dinámicas ---
    CURRENT_PROJECT_DIR = Path(__file__).parent 
    PROJECT_ROOT_DIR = CURRENT_PROJECT_DIR.parent
    
    # Rutas de Logs y Output 
    ERROR_LOG = PROJECT_ROOT_DIR / "error.log"
    WARNING_LOG = PROJECT_ROOT_DIR / "warning.log"
    DIAGNOSTIC_LOG = PROJECT_ROOT_DIR / "_diagnostic_log.txt"
    DIRECTORIO_OUTPUT = PROJECT_ROOT_DIR / "data" / "output"
    OUTPUT_LOG = DIRECTORIO_OUTPUT / "pipeline.log"

    # --- 3. Lógica de Preparación y Limpieza ---

    # Limpiamos el log de diagnóstico total primero
    if DIAGNOSTIC_LOG.exists():
        DIAGNOSTIC_LOG.unlink()

    # Abrimos el log de diagnóstico para capturar todo lo que se imprima AHORA
    # Este file descriptor se usará para tee más abajo
    # No lo usamos para la salida directa, solo para el comando final.

    # Limpieza de logs internos y Creación de directorios
    os.makedirs(DIRECTORIO_OUTPUT, exist_ok=True)
    for log_file in [ERROR_LOG, WARNING_LOG, OUTPUT_LOG]:
        if log_file.exists():
            log_file.unlink() 

    print("--- Proceso iniciado (Orquestador Python). ---")
    print(f"DEBUG: Directorio de salida: {DIRECTORIO_OUTPUT}")
    
    # 4. Verificaciones de Rutas y PYTHONPATH
    if not RUTA_GESTORPPT.is_dir():
        print(f"Error: No se encontró la carpeta de código base en '{RUTA_GESTORPPT}'", file=sys.stderr)
        sys.exit(1)
    
    os.environ["PYTHONPATH"] = str(RUTA_SRC)
    print(f"PYTHONPATH establecido a '{RUTA_SRC}'")

    # 5. Configuración del VENV y Rutas para el Subproceso
    VENV_COMMAND = f"source {VENV_ACTIVATE_PATH} && " if VENV_ACTIVATE_PATH.exists() else ""
    
    # --- INICIO DEL PASO DE PRE-PROCESAMIENTO ---
    PREPROCESSOR_SCRIPT = RUTA_GESTORPPT / "run.py"
    EDITIONS_SCRIPT = PROJECT_ROOT_DIR / "ediciones.py"
    GENERATED_MAIN_SCRIPT = PROJECT_ROOT_DIR / "main.py"
    CONFIG_PATH = PROJECT_ROOT_DIR / "Config" / "config_principal.yml"
    
    print(f"\n1. Ejecutando pre-procesador '{PREPROCESSOR_SCRIPT}'...")

    # Comando: [venv] python3 [run.py] [ediciones.py] 2>&1 | tee -a [ERROR_LOG]
    preprocessor_command = (
        f"{VENV_COMMAND} python3 {PREPROCESSOR_SCRIPT} {EDITIONS_SCRIPT} 2>&1 | tee -a {ERROR_LOG}"
    )
    run_bash_command(preprocessor_command, "El pre-procesador falló.")
    
    print(f"Generación de '{GENERATED_MAIN_SCRIPT}' completada exitosamente.")

    # --- FIN DEL PASO DE PRE-PROCESAMIENTO ---

    # 6. Ejecutar el pipeline principal.
    pipeline_args = [
        str(GENERATED_MAIN_SCRIPT),
        "--config-io", str(CONFIG_PATH),
        "--formato", args.formato,
    ]
    if args.filtrar_sufijo:
        pipeline_args.append("--filtrar-sufijo")
        pipeline_args.append(args.filtrar_sufijo)

    print(f"Argumentos finales para Python: {pipeline_args}")
    print("Lanzando pipeline 'gestorppt.executable'...")

    # Comando: [venv] python3 -m gestorppt.executable [args] 2>&1 | tee -a [OUTPUT_LOG]
    pipeline_command = (
        f"{VENV_COMMAND} python3 -m gestorppt.executable {' '.join(pipeline_args)} 2>&1 | tee -a {OUTPUT_LOG}"
    )
    run_bash_command(pipeline_command, "El pipeline principal falló.")

    # --- PASO DE BANNERS (OPCIONAL) ---
    if args.banners:
        print("\n--- Iniciando paso final: Generación de Banners ---")
        BANNER_SCRIPT = RUTA_SRC / "gestorppt" / "run_banners.py"
        
        banner_command = (
            f"{VENV_COMMAND} python3 {BANNER_SCRIPT} 2>&1 | tee -a {ERROR_LOG}"
        )
        run_bash_command(banner_command, "El script de banners falló.")

        print("Generación de Banners completada exitosamente.")
    
    print("\nEjecución del pipeline completada exitosamente.")

if __name__ == "__main__":
    # La ejecución final envuelve TODO el proceso de Python en Bash para el logging dual (tee).
    # Este es el patrón de ejecución que queremos forzar para capturar TODA la salida.
    
    PROJECT_ROOT_DIR = Path(__file__).parent.parent
    DIAGNOSTIC_LOG = PROJECT_ROOT_DIR / "_diagnostic_log.txt"
    
    # Usamos sys.executable para garantizar que se use el binario de Python correcto (venv o no)
    python_executable_path = sys.executable 
    
    # Generamos el comando que ejecuta el script y pasa todos los argumentos
    # Importante: pasamos sys.argv[1:] que contiene [-s matriz_ -f xls], etc.
    python_command = f"{python_executable_path} {__file__} {' '.join(sys.argv[1:])}"
    
    # El comando completo es: python <script> <args> 2>&1 | tee <log_file>
    final_command = (
        f"{python_command} 2>&1 | tee {DIAGNOSTIC_LOG}"
    )
    
    try:
        # 1. Intentamos ejecutar la lógica de 'tee' a través de Bash.
        # Si esto falla (por el debugger), no es crítico, simplemente el tee no funcionó.
        # Sin embargo, la línea de VSC que se ejecuta es 'python ... run_linux.py args'.
        
        # Para evitar que el debugger ejecute esto y se confunda, llamamos a la función principal 
        # y dejamos que VSC maneje la salida al terminal integrado (que es lo que hace de todas formas).
        
        # Eliminamos el wrapper de Bash para el debugger, y usamos la función principal directa.
        main()
        
    except Exception as e:
        # Si hay un error, lo imprimimos.
        print(f"Error crítico en la ejecución principal: {e}", file=sys.stderr)
        sys.exit(1)