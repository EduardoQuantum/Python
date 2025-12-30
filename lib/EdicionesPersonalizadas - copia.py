# --- Bloque para ELIMINAR filas por 3 condiciones en TODOS los DataFrames ---

print(f"\n--- Aplicando filtro de eliminación en todos los DataFrames ---")

# Creamos una copia de las claves para poder iterar de forma segura
nombres_de_hojas = list(gestor.dfs_en_proceso.keys())

for nombre_hoja in nombres_de_hojas:
    df_original = gestor.dfs_en_proceso.get(nombre_hoja)

    if df_original is None or df_original.empty:
        continue # Ignoramos hojas vacías o no encontradas
    
    # Verificamos si la hoja tiene las columnas necesarias para evitar errores
    columnas_requeridas = ['OrdenColumna', 'HashColumna', 'NombreColumna']
    if not all(col in df_original.columns for col in columnas_requeridas):
        logging.warning(f"La hoja '{nombre_hoja}' no contiene las columnas requeridas para el filtro. Se omitirá.")
        continue

    # 1. Define las tres condiciones
    condicion_orden = (df_original['OrdenColumna'] == 54)
    condicion_hash = (df_original['HashColumna'] == '6737a24f')
    condicion_nombre = (df_original['NombreColumna'] == 'Movistar')
    
    # 2. Combina las condiciones para crear una máscara de las filas A ELIMINAR
    mascara_a_eliminar = (condicion_orden) & (condicion_hash) & (condicion_nombre)

    # 3. Filtra el DataFrame, manteniendo solo las filas que NO cumplen la condición
    #    El operador '~' invierte la máscara (selecciona lo que es Falso).
    df_filtrado = df_original[~mascara_a_eliminar].copy()

    # 4. Actualiza el DataFrame en el gestor
    gestor.dfs_en_proceso[nombre_hoja] = df_filtrado
    
    num_eliminadas = len(df_original) - len(df_filtrado)
    if num_eliminadas > 0:
        print(f"-> Hoja '{nombre_hoja}': Se eliminaron {num_eliminadas} filas.")

# --- Fin del Bloque ---