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

### Fase 2: Corrección de Valores Atípicos (Outliers) en `return_lag_days`
- [x] **Diagnóstico de Outliers:** Identificación de valores extremos de hasta **3,225 días** (~9 años) en `return_lag_days`, generando una media distorsionada de **120.59 días** frente a una mediana real de **19 días** (el 75% ocurre en <= 98 días).
- [x] **Estrategia Seleccionada:** Recorte (*Capping / Winsorizing*) a un umbral máximo de **90 días**, correspondiente a la política comercial extendida de devoluciones y garantías en joyería.
- [x] **Justificación Contable:** Se evitó la eliminación de filas para no restar devoluciones reales ni descuadrar el cálculo acumulado de ventas netas (`net_sales`), preservando las 2,408,173 filas del dataset.
- [x] **Resultados tras el Capping:**
  - Registros de devolución procesados: 193,955 (100% conservados).
  - Media saneada: se redujo de **120.59 días** a **35.91 días**.
  - Mediana: conservada en **19.0 días**.
  - Máximo: acotado a **90.0 días**.
  - Registros topados al límite de 90 días: **49,842**.

---

## 3. Problemas Encontrados y Resoluciones

| Problema / Incidencia | Causa Raíz | Resolución |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'pandas'` | El notebook se ejecutaba sobre el Python global del sistema (`/usr/bin/python3` v3.9.6) sin entorno virtual ni librerías de ciencia de datos instaladas. | Se creó el entorno virtual `.venv` con Python 3.11, se instalaron las librerías necesarias (`pandas`, `ipykernel`, etc.), se generó `requirements.txt` y se registró el kernel `sales-revenue-env` en Jupyter. |
| Inconsistencia de nombre de notebook (`exploration.ipynb` vs `sales-revenue-jewery.ipynb`) | El archivo fue renombrado en el commit `fff8244` pero la pestaña previa permanecía abierta en el editor. | Se verificó la referencia al archivo canónico [`sales-revenue-jewery.ipynb`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/sales-revenue-jewery.ipynb). |
| Presencia de texto y comentarios en inglés en el notebook | Celdas iniciales contenían comentarios y encabezados en inglés no alineados con la regla 2 de `Gemini.md`. | Se tradujeron todas las descripciones y comentarios al español respetando la regla de no alterar la estructura de las celdas preexistentes. |
| Outliers ilógicos en `return_lag_days` (hasta 3,225 días) | Registros vinculados a ventas históricas anteriores a la migración del sistema POS (2014-2017) o fechas dummy de origen. | Se aplicó recorte (*capping*) a 90 días con `.clip(upper=90)`, protegiendo el cuadre de ventas netas (`net_sales`) sin distorsionar las métricas de tiempo. |

---

## 4. Próximos Pasos y Acciones Pendientes

- [ ] **Fase 3 : Tratamiento de Valores Faltantes y Tipos de Datos**
  - Evaluar la frecuencia de nulos por columna en el dataset limpio y definir estrategia (imputación o mantenimiento documentado).
  - Comprobar tipos de datos de fechas (`date`) y numéricos.
- [ ] **Fase 4 : Análisis Exploratorio de Datos (EDA)**
  - **a. Análisis Univariado:**
    - Distribución de variables financieras clave (`gross_sales`, `net_sales`, `discount_total`, `cogs`, `margin`, `qty`) mediante histogramas y boxplots.
    - Distribución de frecuencias de variables categóricas (`department`, `class`, `brand`, `location_name`, `is_web`).
  - **b. Análisis Bivariado:**
    - Comportamiento de ingresos por canal (`is_web` vs tiendas físicas).
    - Patrones temporales y estacionales según el calendario 4-5-4 (`retail_year`, `retail_quarter`, `retail_month`).
    - Matriz de correlación entre variables de ingresos, costos y descuentos.
- [ ] **Control Git:**
  - Mantener commits en la rama `gera` siguiendo el formato `Fase <n> : <descripción>`.
