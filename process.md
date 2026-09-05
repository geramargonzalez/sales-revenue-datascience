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

### Fase 1: Carga de Datos e Inspección Preliminar
- [x] Verificación del dataset transaccional unificado [`sales-revenue-jewery.ipynb`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/sales-revenue-jewery.ipynb).
- [x] Comprobación de la estructura del dataset (40 columnas, histórico 2022 a 2026, diccionario de datos en [`README.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/README.md)).

---

## 3. Problemas Encontrados y Resoluciones

| Problema / Incidencia | Causa Raíz | Resolución |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'pandas'` | El notebook se ejecutaba sobre el Python global del sistema (`/usr/bin/python3` v3.9.6) sin entorno virtual ni librerías de ciencia de datos instaladas. | Se creó el entorno virtual `.venv` con Python 3.11, se instalaron las librerías necesarias (`pandas`, `ipykernel`, etc.), se generó `requirements.txt` y se registró el kernel `sales-revenue-env` en Jupyter. |
| Inconsistencia de nombre de notebook (`exploration.ipynb` vs `sales-revenue-jewery.ipynb`) | El archivo fue renombrado en el commit `fff8244` pero la pestaña previa permanecía abierta en el editor. | Se verificó la referencia al archivo canónico [`sales-revenue-jewery.ipynb`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/sales-revenue-jewery.ipynb). |

---

## 4. Próximos Pasos y Acciones Pendientes

- [ ] **Fase 2 : Preparación y Limpieza de Datos**
  - Consolidar todas las importaciones de librerías estrictamente al inicio del notebook.
  - Asegurar que todas las descripciones, encabezados y comentarios de celdas estén en español (traduciendo cualquier texto en inglés).
  - Preservar la estructura original de las celdas existentes.
  - Identificar y analizar valores nulos / missing values y definir estrategia de tratamiento (drop, imputación o conservación documentada).
- [ ] **Fase 3 : Análisis Exploratorio de Datos (EDA)**
  - **a. Análisis Univariado:**
    - Distribución de variables numéricas clave (`gross_amt`, `net_amt`, `discount_amt`, `qty`, etc.) mediante histogramas, boxplots y métricas estadísticas.
    - Distribución de frecuencias de variables categóricas (`department`, `class`, `brand`, `location_name`, `is_web`).
  - **b. Análisis Bivariado:**
    - Relación entre canales de venta (`is_web` vs físico) e ingresos.
    - Tendencia temporal y estacionalidad por calendario 4-5-4 (`retail_year`, `retail_quarter`, `retail_month`).
    - Matriz de correlación entre variables financieras y transaccionales.
- [ ] **Control Git:**
  - Mantener commits en la rama `gera` siguiendo el formato `Fase <n> : <descripción>`.
