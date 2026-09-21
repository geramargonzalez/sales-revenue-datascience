# Guía Operativa para Agentes de IA (AGENTS.md)

Este documento define la arquitectura de trabajo, directrices operativas, políticas de control de versiones y estándares de ingeniería para los agentes de IA que operen en este repositorio.

---

## 1. Descripción del Proyecto y Entorno

Este repositorio contiene el proyecto de ciencia de datos para el análisis transaccional y predicción de ingresos por ventas en el sector de joyería minorista (*Sales Revenue Data Science*).

### Entorno y Comandos Principales
- **Versión de Python:** Python 3.11 instalado en el entorno virtual aislado `.venv`.
- **Kernel de Jupyter:** `sales-revenue-env` (`Python (.venv - Sales Revenue)`).
- **Activación del entorno:**
  ```bash
  source .venv/bin/activate
  ```
- **Instalación de dependencias:**
  ```bash
  pip install -r requirements.txt
  ```

---

## 2. Flujo de Trabajo Git y Colaboración

### Sincronización de Ramas
- Al trabajar en una rama distinta de `main`, actualizar siempre la rama activa con los últimos cambios de `main` antes de comenzar una tarea:
  ```bash
  git checkout <rama_activa>
  git merge main
  ```

### Asignación de Ramas por Usuario
- Si el usuario activo es `gerardo.gonzalez@estudiantes.utec.edu.uy` o `geramargonzalez@gmail.com`, trabajar y guardar cambios en la rama `gera`.
- En cualquier otro caso, trabajar y guardar en la rama `camilo`.

### Nomenclatura Estricta de Commits y Push
Al finalizar una tarea, realizar el commit y push utilizando estrictamente el siguiente formato:
```text
Fase <number_of_task> : <description_of_the_task>
```
*Ejemplo:* `Fase 1 : Load Assets and clean CSV`

### Registro de Progreso en `process/process.md`
Para cada tarea ejecutada, es obligatorio crear o actualizar el archivo de seguimiento [`process.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/process/process.md) dentro de la carpeta `process/`. Adicionalmente, consultar [`ideas.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/process/ideas.md) como banco de hipótesis analíticas y de negocio.

Este archivo debe detallar:
- Progreso actual y pasos completados.
- Incidencias encontradas y sus resoluciones.
- Identificación del usuario que aplicó los cambios (ej. `gera`, `camilo`).
- Próximos pasos y acciones pendientes.

---

## 3. Reglas Generales de Código y Notebooks

- **Importación Centralizada:** Todas las librerías y dependencias deben ser importadas exclusivamente al inicio del notebook.
- **Estructura de Celdas:** No alterar la estructura original ni el orden de las celdas preexistentes.
- **Idioma Español Obligatorio:** Asegurar que todas las descripciones, encabezados markdown, comentarios en código y etiquetas de gráficos estén redactados en español.
- **Líneas en Blanco en Markdown:** Al terminar una oración en celdas o archivos markdown, dejar una línea en blanco en la siguiente línea.

---

## 4. Límites Operativos y Cuadre Contable

- **Protección de Datos Consolidados:** Nunca eliminar filas de transacciones válidas sin justificación contable documentada.
- **Balance de Ventas Netas:** Las operaciones de limpieza, filtrado o imputación deben preservar intacto el balance consolidado de ingresos netos:
  ```text
  net_sales = $283,387,098.70 USD
  ```
- **Tratamiento de Nulos:** Distinguir nulos estructurales (*missing by design*) de ausencias accidentales; preferir imputación semántica antes que descarte de registros.

---

## 5. Habilidades Modulares del Agente (Estándar agentskills.io)

El repositorio incorpora el estándar abierto de habilidades modulares [Agent Skills](https://agentskills.io/specification) bajo el directorio [`skills/`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/skills).

Cada habilidad se estructura con su manifiesto `SKILL.md` (metadatos YAML y guía operativa) y documentación complementaria en `references/`:

### Habilidades Disponibles:
- [exploratory-data-analysis](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/skills/exploratory-data-analysis/SKILL.md): Procedimiento completo de análisis univariado, bivariado, calendario retail 4-5-4 y correlaciones.
  - [Estándares de Visualización](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/skills/exploratory-data-analysis/references/visualization_standards.md)
  - [Guía del Calendario Minorista 4-5-4](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/skills/exploratory-data-analysis/references/retail_calendar_guide.md)

---

## 6. Verificación y Criterios de Finalización (Definition of Done)

Antes de dar por concluida cualquier intervención o fase:
1. Confirmar que el código ejecuta sin errores en el kernel `.venv`.
2. Verificar que las ventas netas y métricas contables no sufrieron desviaciones imprevistas.
3. Actualizar [`process.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/process/process.md) con el registro completo de la fase ejecutada y el autor.
4. Generar el commit y push siguiendo la nomenclatura `Fase <n> : <descripción>` en la rama correspondiente (`gera`).
