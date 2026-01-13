# PROTOCOLO DE ACTUALIZACIÓN - CURSO PYTHON Y PANDAS
Autor: Eduardo Lencina
Sistema: Ubuntu + VS Code + Quarto
Publicación: GitHub Pages (carpeta /docs)



==============================================================================
PASO 0: INICIO DE SESIÓN
==============================================================================
1. Abrir terminal en la carpeta del proyecto.
2. Activar el entorno virtual (VITAL para que Quarto encuentre Jupyter):
   $ source venv/bin/activate

==============================================================================
PASO 1: CREAR LA NUEVA CLASE (.ipynb)
==============================================================================
1. Crear un nuevo archivo .ipynb (ej: `clase_04.ipynb`).
2. INSERTAR CELDA 1 (Tipo: RAW / Raw NBConvert):
   Copia y pega este encabezado YAML obligatorio:
   -------------------------------------------------------
   ---
   title: "Clase XX: Título del Tema"
   subtitle: "Subtítulo descriptivo"
   author: "Eduardo Lencina"
   date: last-modified
   lang: es
   format:
     html:
       theme: flatly
       toc: true
       code-fold: show
       code-tools: true
   ---
   -------------------------------------------------------

3. INSERTAR CELDA 2 (Tipo: RAW / HTML):
   Estilos corporativos (Azul #003366):
   -------------------------------------------------------
   <style>
     h1, h2, h3, h4 { color: #003366 !important; }
     a { color: #003366; }
     .callout-header { background-color: #003366 !important; color: white !important; }
   </style>
   -------------------------------------------------------

==============================================================================
PASO 2: ESTRUCTURA DE PESTAÑAS (El "Sándwich")
==============================================================================
Si vas a usar pestañas (Código | Gráfico), recuerda el orden de celdas:

1. [CELDA MARKDOWN]  ::: {.panel-tabset}
                     ## 🐍 Código

2. [CELDA PYTHON]    (Tu código ejecutable normal)

3. [CELDA MARKDOWN]  :::

NOTA: Para cambiar tipo de celda rápido:
- Seleccionar celda + Tecla 'M' = Markdown
- Seleccionar celda + Tecla 'Y' = Python

==============================================================================
PASO 3: REGISTRAR EN EL SITIO
==============================================================================
1. Abrir el archivo `_quarto.yml`.
2. Agregar la nueva clase bajo `navbar` o `sidebar`:
   - href: clase_04.ipynb
     text: Clase 4

==============================================================================
PASO 4: CONSTRUIR EL SITIO (RENDER)
==============================================================================
1. Asegúrate de estar en el venv.
2. Ejecuta en la terminal:
   $ quarto render

   *Si da error de "Jupyter not found", ejecutar antes:
   $ export QUARTO_PYTHON=~/proyectos/ClasesFlacso/venv/bin/python

3. Verifica que la carpeta `docs/` se haya actualizado.
4. (Opcional) Ver en local antes de subir:
   $ quarto preview

==============================================================================
PASO 5: PUBLICAR EN GITHUB
==============================================================================
Una vez renderizado correctamente:

1. $ git status      (Debe mostrar cambios en docs/ y tu nueva clase)
2. $ git add .
3. $ git commit -m "Agregada Clase XX y sitio actualizado"
4. $ git push

¡Listo! Esperar 1 minuto y revisar la web.