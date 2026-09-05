# Seguimiento del Proyecto (process.md)

Este documento registra el avance, control de tareas, resolución de incidencias y próximos pasos del proyecto de acuerdo con los lineamientos definidos en [`Gemini.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/Gemini.md).

---

## 1. Configuración del Entorno y Control de Versiones

* **Rama activa de trabajo:** `gera` (según regla: `gerardo.gonzalez@estudiantes.utec.edu.uy` -> rama `gera`).
* **Nomenclatura obligatoria de commits:** `Fase <number_of_task> : <description_of_the_task>`.
* **Idioma:** Español estricto en comentarios, documentación y descripciones de celdas.

---

## 2. Progreso Actual y Pasos Completados

### Fase 0: Inicialización y Entorno de Ejecución
- [x] Lectura e incorporación de los lineamientos de trabajo y buenas prácticas de [`Gemini.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/Gemini.md).
- [x] Detección y corrección de la falta de dependencias en el kernel de Jupyter (`ModuleNotFoundError: No module named 'pandas'`).
- [x] Creación del entorno virtual aislado `.venv` con Python 3.11 (`/opt/homebrew/bin/python3.11`).
- [x] Instalación de dependencias base de análisis y visualización: `pandas` (3.0.5), `ipykernel` (7.3.0), `matplotlib` (3.11.1), `seaborn` (0.13.2), `numpy` (2.4.6).
- [x] Creación del archivo de dependencias [`requirements.txt`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/requirements.txt).
- [x] Registro del kernel `Python (.venv - Sales Revenue)` (`sales-revenue-env`) en Jupyter para su uso directo en el IDE.

### Fase 1: Carga de Datos y Limpieza Contable
- [x] Verificación del dataset transaccional unificado [`sales-revenue-jewery.ipynb`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/sales-revenue-jewery.ipynb).
- [x] Comprobación de la estructura del dataset (40 columnas, histórico 2022 a 2026, diccionario de datos en [`README.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/README.md)).
- [x] Corrección al idioma español de todos los títulos markdown y comentarios en celdas existentes que se encontraban en inglés, manteniendo intacta la estructura original de las celdas.
- [x] **Limpieza de Tarjetas de Regalo:** Identificación y exclusión de registros donde `rpt_ignored == True` (28,759 filas eliminadas, pasivos con $0 COGS).
- [x] **Limpieza de Anulaciones de Transacciones:** Identificación y exclusión de registros con `txn_type` igual a `'Reversal'` o `'Reversed'` (208 filas eliminadas: 132 Reversal y 76 Reversed).
- [x] **Consolidación del Dataset Limpio:**
  - Total de filas originales: 2,437,140.
  - Total de filas excluidas: 28,967.
  - Total de filas resultantes conservadas en `df`: 2,408,173.
  - Transacciones resultantes compuestas únicamente por `'Sale'`, `'Mixed'` y `'Return'`.

---

## 3. Problemas Encontrados y Resoluciones

| Problema / Incidencia | Causa Raíz | Resolución |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'pandas'` | El notebook se ejecutaba sobre el Python global del sistema (`/usr/bin/python3` v3.9.6) sin entorno virtual ni librerías de ciencia de datos instaladas. | Se creó el entorno virtual `.venv` con Python 3.11, se instalaron las librerías necesarias (`pandas`, `ipykernel`, etc.), se generó `requirements.txt` y se registró el kernel `sales-revenue-env` en Jupyter. |
| Inconsistencia de nombre de notebook (`exploration.ipynb` vs `sales-revenue-jewery.ipynb`) | El archivo fue renombrado en el commit `fff8244` pero la pestaña previa permanecía abierta en el editor. | Se verificó la referencia al archivo canónico [`sales-revenue-jewery.ipynb`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/sales-revenue-jewery.ipynb). |
| Presencia de texto y comentarios en inglés en el notebook | Celdas iniciales contenían comentarios y encabezados en inglés no alineados con la regla 2 de `Gemini.md`. | Se tradujeron todas las descripciones y comentarios al español respetando la regla de no alterar la estructura de las celdas preexistentes. |

---

## 4. Próximos Pasos y Acciones Pendientes

- [ ] **Fase 2 : Preparación y Tratamiento de Valores Faltantes**
  - Identificar la frecuencia y porcentaje de valores nulos/missing values por columna en el dataset limpio.
  - Documentar y aplicar la estrategia para cada campo relevante (drop, imputación o conservación documentada).
  - Verificar conversiones de tipo requeridas (fechas, booleanos, numéricos).
- [ ] **Fase 3 : Análisis Exploratorio de Datos (EDA)**
  - **a. Análisis Univariado:**
    - Distribución de métricas financieras clave (`gross_sales`, `net_sales`, `discount_total`, `cogs`, `margin`, `qty`) con histogramas y estadísticas descriptivas.
    - Distribución de frecuencias de variables categóricas (`department`, `class`, `brand`, `location_name`, `is_web`).
  - **b. Análisis Bivariado:**
    - Comportamiento de ingresos por canal (`is_web` vs tiendas físicas).
    - Patrones temporales y estacionales según el calendario 4-5-4 (`retail_year`, `retail_quarter`, `retail_month`).
    - Matriz de correlación entre variables de precios, costos, márgenes y descuentos.
- [ ] **Control Git:**
  - Mantener los commits en la rama `gera` siguiendo el formato `Fase <n> : <descripción>`.
