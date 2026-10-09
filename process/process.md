# Seguimiento del Proyecto (process/process.md)

Este documento registra el avance, control de tareas, resolución de incidencias y próximos pasos del proyecto de acuerdo con los lineamientos definidos en [`AGENTS.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/AGENTS.md).

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
- [x] **Incorporación de Tabla Comparativa al Notebook:** Se agregaron las celdas `outlier_comparison_md` y `outlier_comparison_code` con la tabla comparativa detallada de métricas e impacto antes vs. después.

### Fase 3: Análisis y Tratamiento de Valores Faltantes (Aplicado por **gera**)
- [x] **Diagnóstico Exhaustivo de Nulos:**
  - Evaluación integral de las 40 columnas en las 2,408,173 filas del dataset limpio.
  - Identificación de 14 columnas con datos faltantes y clasificación según naturaleza del negocio:
    - *Vacíos en Origen (100% nulos):* `item_season`, `promo_name`, `promo_amt` (no poblados en extracción POS/BigQuery; documentados para descarte analítico/ML).
    - *Nulos Estructurales (*Missing by Design*):* `return_reason` (93.56%), `return_lag_days` (91.95%), `orig_location_name` (91.76%). Nulos en ventas normales porque no existió devolución.
    - *Nulos Condicionales por Canal:* `ship_to_postal` (40.51% global; solo 1.49% nulo en web vs 94.58% nulo en tiendas presenciales).
    - *Financiero:* `markdown` (23.07% nulos; indica venta a precio de lista completo MSRP sin rebaja).
    - *Catálogo y Clientes:* `customer_id` (2.97%), `subclass1` (32.22%), `brand` (8.47%), `class` (0.13%), `department` (5 filas), `associate_id` (3 filas).
- [x] **Visualización del Perfil de Nulos:**
  - Incorporación de gráficos con `seaborn` y `matplotlib`: ranking porcentual de nulos y evidencia empírica de nulos condicionales/estructurales.
- [x] **Tratamiento e Imputación sin Pérdida de Datos:**
  - **Eliminación de Columnas 100% Nulas:** Se descartaron formalmente las 3 columnas vacías en origen (`item_season`, `promo_name`, `promo_amt`) por carecer de varianza y utilidad analítica, reduciendo el dataset de 40 a **37 columnas** (por **gera**).
  - **Variables Numéricas Restantes (`return_lag_days`, `markdown`):** Imputación con `0.0`. En `return_lag_days`, `0.0` representa 0 días de retraso para ventas ordinarias o devoluciones inmediatas; en `markdown` representa $0.00 de descuento.
  - `customer_id`: Imputación con `'CLIENTE_ANONIMO'`.
  - `brand`, `subclass1`, `class`, `department`, `associate_id`: Imputación con etiquetas explícitas (`'Sin Marca / Genérico'`, `'Sin Subclase'`, etc.).
  - `ship_to_postal`: Imputación condicional según canal (`'COMPRA_EN_TIENDA'` vs `'NO_DISPONIBLE'`).
  - `return_reason`, `orig_location_name`: Imputación condicional (`'No aplica (Venta)'` en ventas ordinarias; `'No especificado'` / `'No registrada / Misma tienda'` en devoluciones).
- [x] **Control y Balance Contable:**
  - Filas iniciales: **2,408,173** -> Filas finales: **2,408,173** (0 eliminadas, 100% conservadas).
  - Columnas iniciales: **40** -> Columnas finales: **37** (3 descartadas por ausencia absoluta).
  - Ventas Netas (`net_sales`): **$283,387,098.70 USD** (0.00 de variación respecto al balance inicial).
  - Nulos totales restantes en el dataset completo: **0**.
- [x] **Estandarización y Jerarquía de Encabezados (Enfoque A por Fases, por gera):**
  - Homogeneización de todas las celdas Markdown desde la portada hasta el EDA bajo la jerarquía de fases del proyecto (`Fase 0`, `Fase 1`, `Fase 2`, `Fase 3` y `Fase 4`).
  - Incorporación de elementos de diseño visual (bloques `> [!NOTE]`, `> [!IMPORTANT]`, `> [!TIP]`, resúmenes contextuales y tablas comparativas).

### Fase 3.5: Estandarización de `AGENTS.md` y Especificación Agent Skills (Aplicado por **gera**)
- [x] **Adopción del Estándar `AGENTS.md`:** Reestructuración integral del archivo raíz conforme al estándar del *Agentic AI Foundation* (visión general, entorno, flujo Git, reglas de notebooks, límites contables, catálogo de habilidades y definición de terminado).
- [x] **Implementación del Estándar `agentskills.io`:** Creación de la habilidad modular `exploratory-data-analysis` en `skills/exploratory-data-analysis/` con su manifiesto `SKILL.md` (metadatos YAML y guía metodológica) y referencias de consulta (`visualization_standards.md` y `retail_calendar_guide.md`).
- [x] **Consolidación Canónica en `skills/`:** Reorganización del repositorio para mantener únicamente la carpeta `skills/` en la raíz sin carpetas intermedias (`.agents/`), logrando una estructura limpia y 100% fiel a la especificación de `agentskills.io`.
- [x] **Preservación de Reglas de Negocio:** Mantenimiento estricto del flujo de ramas (`gera`), nomenclatura de commits (`Fase <n> : <desc>`), idioma español en comentarios y cuadre contable.

### Fase 3.6: Reorganización de Archivos de Seguimiento e Ideas (Aplicado por **gera**)
- [x] **Centralización en `process/`:** Traslado de [`process.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/process/process.md) e [`ideas.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/process/ideas.md) dentro de la carpeta `process/` para despejar la raíz del repositorio.
- [x] **Actualización de Rutas Globales:** Modificación de [`AGENTS.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/AGENTS.md) y de la habilidad de EDA ([`SKILL.md`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/skills/exploratory-data-analysis/SKILL.md)) para referenciar `process/process.md` e integrar `process/ideas.md` como catálogo de hipótesis analíticas de negocio.
- [x] **Limpieza de Archivos Redundantes:** Eliminación definitiva de `CLAUDE.md` y `Gemini.md` consolidando a `AGENTS.md` como fuente de verdad canónica.

### Fase 3.7: Restricción de Exclusión Mínima de `CLIENTE_ANONIMO` (Aplicado por **gera**)
- [x] **Nueva Restricción Operativa:** Se agregó en la sección 4 de [`AGENTS.md`](../AGENTS.md) y en los principios de la habilidad de EDA ([`SKILL.md`](../skills/exploratory-data-analysis/SKILL.md)) la regla de conservar por defecto las filas con `customer_id == 'CLIENTE_ANONIMO'` (2.97% del dataset).
- [x] **Alcance de la Excepción:** La exclusión solo procede en métricas por cliente (recurrencia, cohortes, RFM, concentración), sobre una vista temporal, sin modificar `df` y reportando el porcentaje de filas y de `net_sales` excluido.
- [x] **Motivo:** Evitar que la etiqueta imputada se interprete como un único cliente real, sin perder esas transacciones en el resto del análisis ni alterar el cuadre contable.

### Fase 4: Análisis Exploratorio de Datos - Bloques A y G (Aplicado por **gera**)
- [x] **Banco de Ideas del EDA:** Se definieron siete bloques de análisis (A. validación de hipótesis, B. temporalidad, C. canal y ubicación, D. devoluciones, E. producto y rentabilidad, F. clientes y geografía, G. univariado y correlaciones). En esta fase se implementaron los bloques **A** y **G**.
- [x] **4.0 Verificación de Estado y Vistas de Análisis:**
  - Configuración visual global según `visualization_standards.md` (paleta institucional y formateadores de moneda y porcentaje).
  - Máscaras y vistas auxiliares (`es_devolucion`, `es_operativa`, `ventas_fin`, `devoluciones_fin`, `aux`) que no modifican `df`.
  - Cuantificación de segmentos que distorsionan el análisis: `is_employee_sale` sin ningún valor verdadero, 40 líneas mayoristas, departamento `System` (5.37% de las líneas, 0.28% de la venta), ubicaciones no operativas (0.81% de la venta) y ventas con costo cero (10.67% de las líneas, 9.90% de la venta).
- [x] **4.1 Validación de Hipótesis del Documento de Referencia (Bloque A):**
  - Cifras de control: cuadran al centavo por **año calendario** de `date`; por `retail_year` difieren (hasta +$0.48M en 2024 por la semana 53).
  - Canal web: 63.8% global (referencia ~62%), en descenso de 68.4% (2022) a 63.9% (2025).
  - Noviembre y diciembre: entre 29.8% y 32.1% de la venta anual (referencia 32%).
  - Devoluciones: 9.0% de la venta bruta, de 7.9% (2022) a 9.2% (2025); enero entre 15.2% y 21.9%; el 27% de referencia solo se alcanza a nivel semanal (27.9%).
  - Williamsburg 15.4% vs. Boston 6.3% de tasa de devolución (referencia 17% vs. 7%).
  - Wedding Annex: 63 tickets al mes de $1,360 en el histórico; 33 tickets de $1,690 en los últimos 12 meses (referencia ~50 tickets de ~2,000 USD).
- [x] **4.2 Análisis Univariado (Bloque G):**
  - Descriptivos con percentiles y asimetría, separando ventas y devoluciones.
  - Histogramas con KDE y diagramas de caja en escala logarítmica para `gross_sales`, `net_sales`, `cogs`, `margin` y `discount_total`; distribución discreta de `qty`.
  - Participación en líneas y en venta neta de `class`, `brand`, `location_name`, `department`, `is_web` y `txn_type`.
- [x] **4.3 Matriz de Correlación (Bloque G):** Pearson y Spearman por línea de venta, Pearson por línea de devolución (con `return_lag_days`) y Pearson agregado por semana minorista y ubicación.
- [x] **Control y Balance Contable:** Filas **2,408,173**, columnas **37** y ventas netas **$283,387,098.70 USD** sin variación al cierre de la fase (verificado con `assert` en la última celda).
- [x] **Ejecución:** Notebook completo ejecutado sin errores con el kernel `sales-revenue-env` (49 celdas).

### Fase 5: Dataset Combinado con Datos Actualizados (Aplicado por **gera**)
- [x] **Comparación de Extracciones:** `utecFinalTransactionRevenue.csv` tiene las mismas 40 columnas que `transactionRevenue_combined.csv`, pero cubre 2023-01-01 a 2026-09-30 (no incluye 2022).

  En las 1,955,767 líneas comunes `net_sales` suma idéntico ($243,152,260.34).
- [x] **Diferencias en Líneas Comunes:** `markdown` cambia en 752,059 líneas (suma de -$94.05M a -$108.86M); correcciones menores en `customer_id` (1,891), `ship_to_postal` (1,767), `return_lag_days` (53), `cogs` y `margin` (24) e `is_web` (6).
- [x] **Archivo Generado:** `dataset/transactionRevenue_combined_2022-0926.csv`, con 2022 del archivo anterior (481,373 líneas, $49,774,351.74) y 2023 en adelante del archivo nuevo (1,984,983 líneas, $248,079,496.31).

  Las líneas se copiaron como texto, sin reformatear valores, y los archivos de origen no se modificaron.
- [x] **Verificación:** 2,466,356 líneas, 40 columnas, sin `line_id` duplicados, rango 2022-01-02 a 2026-09-30 y `net_sales` sin limpiar de $297,853,848.05 (antes $292,926,612.08).
- [x] **Notebook Apuntado al Dataset Nuevo:** La celda de carga lee `dataset/transactionRevenue_combined_2022-0926.csv`.
- [x] **Balance Recalculado:** Tras la limpieza contable (30,292 líneas `rpt_ignored` y 210 anulaciones excluidas) quedan **2,435,854** filas, **37** columnas y ventas netas de **$287,699,163.91 USD**.

  Antes eran 2,408,173 filas y $283,387,098.70 USD; las cifras de las fases 1 a 4 de este registro corresponden al dataset anterior.
- [x] **Cifras de Control Actualizadas:** `VENTAS_NETAS_CONTROL` y los `assert` de dimensiones del notebook, `AGENTS.md`, `skills/exploratory-data-analysis/SKILL.md` y la tabla de archivos de `README.md`.
- [x] **Texto de las Fases 1 a 3 del Notebook:** Se actualizaron los conteos de exclusión, las estadísticas de `return_lag_days` (media 120.45 días, 35.86 tras el recorte, 50,223 registros topados) y los porcentajes de nulos (`markdown` pasa de 23.07% a 19.56%).
- [x] **Ejecución:** Notebook completo ejecutado sin errores con el kernel `sales-revenue-env` (25 celdas de código), con los `assert` de cierre en verde.
- [x] **Textos Interpretativos de la Fase 4:** Se recalcularon las cifras citadas en las secciones 4.0 a 4.3 y se actualizaron las que cambiaron.

  Cambios principales: cuota web global 63.5% (antes 63.8%); comparación homogénea a 39 semanas, de 64.0% (2022) a 54.7% (2026); Wedding Annex con 32 tickets de $1,815 en los últimos 12 meses; mediana de `net_sales` por línea de venta $94.00; `markdown` presente en el 80.0% de las líneas de venta; 58,205 líneas con margen cero; correlación de `markdown` con `net_sales` de -0.52.

  Los veredictos del contraste de hipótesis no cambian.
- [x] **Cifra de Control de 2026:** Se agregó una nota en la sección 4.1.1: la referencia de $41.11M cubre enero a agosto ($41.12M en el dataset) y la diferencia de $4.31M corresponde a septiembre y a 127 líneas nuevas de agosto.
- [x] **Etiquetas de Gráficos:** Las etiquetas de 2026 pasaron de enero-agosto a enero-septiembre en la sección 4.1.2.
- [x] **Ejecución Final:** Notebook completo reejecutado sin errores con el kernel `sales-revenue-env`.

### Fase 6: Integración del EDA de Camilo - Secciones 4.4 a 4.8 (Aplicado por **gera** en la rama `camilo`)
- [x] **Revisión de los Archivos de Camilo:** Se revisaron `EDA_joyeria.ipynb` (97 celdas, 7 bloques temáticos, sin interpretaciones) y `ProyectoNotas.txt` (lista de análisis y variables nuevas propuestas).

  Sus bloques de temporalidad, canal, devoluciones, producto y clientes cubrían los bloques B a F pendientes de la Fase 4; sus bloques univariado y multivariado ya estaban cubiertos por las secciones 4.2 y 4.3.
- [x] **Adaptaciones al Integrar:**
  - Dataset combinado `transactionRevenue_combined_2022-0926.csv` en lugar de `transactionRevenue_combined.csv`.
  - Sin columnas nuevas en `df`: se usan las vistas de la sección 4.0 y una tabla de tickets por `receipt_id`.
  - Participaciones mensuales solo con años completos (2022 a 2025) y crecimiento de 2026 medido a igual semana minorista.
  - Tasa de devolución en importe (devuelto sobre venta bruta), distinguida de la proporción de líneas.
  - Tiendas físicas operativas separadas del canal web y sin pop-ups; margen porcentual solo sobre líneas con costo informado.
  - Códigos postales normalizados a cinco dígitos; motivos de devolución agrupados (el catálogo mezcla códigos vigentes y heredados).
  - Etiquetas en español, paleta institucional e imports centralizados.
- [x] **4.4 Temporalidad y Estacionalidad:** noviembre y diciembre suman el 31.4% del año; las cinco semanas pico (47 a 51) aportan entre 23.0% y 24.0%; el acumulado a la semana 38 crece 5.1% en 2026 frente a 14.9% en 2025.
- [x] **4.5 Canal y Ubicación:** ticket promedio web de $273.7 frente a $226.9 en tienda; diez de las trece tiendas físicas abrieron desde junio de 2023; Wedding Annex con ticket de $1,369.
- [x] **4.6 Devoluciones:** 6.61% de las líneas; tasa en importe de 14.5% en tienda y 5.5% en web; el 32.8% de las devoluciones de compras web se procesa en tienda; la proporción de líneas devueltas sube de 1.2% a 10.7% con el importe.
- [x] **4.7 Producto y Rentabilidad:** margen de joyería de 65.2%; marca propia con 70% frente a cerca de 50% en diseñadores externos; el margen se mantiene hasta un 20% de descuento.
- [x] **4.8 Clientes y Geografía:** exclusión documentada de `CLIENTE_ANONIMO` (2.91% de las filas, 0.84% de `net_sales`) en una vista temporal; el 36.9% de los clientes repite y genera el 68.6% de la venta.
- [x] **Control y Balance Contable:** Filas **2,435,854**, columnas **37** y ventas netas **$287,699,163.91 USD** sin variación (verificado con `assert` en la última celda).
- [x] **Ejecución:** Notebook completo ejecutado sin errores con el kernel `sales-revenue-env` (72 celdas).

---

## 3. Problemas Encontrados y Resoluciones

| Problema / Incidencia | Causa Raíz | Resolución |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'pandas'` | El notebook se ejecutaba sobre el Python global del sistema (`/usr/bin/python3` v3.9.6) sin entorno virtual ni librerías de ciencia de datos instaladas. | Se creó el entorno virtual `.venv` con Python 3.11, se instalaron las librerías necesarias (`pandas`, `ipykernel`, etc.), se generó `requirements.txt` y se registró el kernel `sales-revenue-env` en Jupyter. |
| Inconsistencia de nombre de notebook (`exploration.ipynb` vs `sales-revenue-jewery.ipynb`) | El archivo fue renombrado en el commit `fff8244` pero la pestaña previa permanecía abierta en el editor. | Se verificó la referencia al archivo canónico [`sales-revenue-jewery.ipynb`](file:///Users/gerardo/Library/CloudStorage/GoogleDrive-gerardo.gonzalez@estudiantes.utec.edu.uy/My%20Drive/SalesRevenueDataScience%20-%20Proyect/sales-revenue-jewery.ipynb). |
| Presencia de texto y comentarios en inglés en el notebook | Celdas iniciales contenían comentarios y encabezados en inglés no alineados con la regla 2 de `Gemini.md`. | Se tradujeron todas las descripciones y comentarios al español respetando la regla de no alterar la estructura de las celdas preexistentes. |
| Outliers ilógicos en `return_lag_days` (hasta 3,225 días) | Registros vinculados a ventas históricas anteriores a la migración del sistema POS (2014-2017) o fechas dummy de origen. | Se aplicó recorte (*capping*) a 90 días con `.clip(upper=90)`, protegiendo el cuadre de ventas netas (`net_sales`) sin distorsionar las métricas de tiempo. |
| `TypeError: 'NoneType' object is not callable` al invocar `display()` en celda 19 | Se ejecutó accidentalmente la asignación `display = None` (procedente de pruebas o autocompletado), sobrescribiendo la función global de IPython en la memoria del kernel. | (Por **gera**) Se eliminó la asignación `display = None`, se ajustó la celda para desplegar directamente el DataFrame `comparativa_outliers` y se añadió explícitamente `from IPython.display import display` en la celda inicial de importaciones para restablecer la referencia. |
| Elevado volumen aparente de nulos (>90%) en variables de devolución y despacho postal | Confusión potencial entre datos faltantes por error y datos ausentes por diseño operativo (*missing by design*). | (Por **gera**) Se demostró que en ventas no hay devolución ni en tiendas presenciales hay código postal de despacho; se aplicó imputación condicional preservando el 100% de las transacciones sin alterar `net_sales`. |
| `NameError: name 'plt' is not defined` al ejecutar visualizaciones en celda 21 | En la celda 2 de importaciones iniciales (Fase 0), `matplotlib.pyplot` se importó con un alias erróneo (`import matplotlib.pyplot as plts` con 's' final en lugar de `plt`). | (Por **gera**) Se corrigió el alias a `import matplotlib.pyplot as plt` en la celda 2 inicial del notebook, alineándolo con las llamadas estándar `plt.subplots()`, `plt.tight_layout()` y `plt.show()`. |
| `gross_sales` vale 0 en todas las líneas de devolución | El sistema de origen solo registra el importe devuelto en `net_sales` (negativo). | (Por **gera**) La tasa de devolución se calcula como importe devuelto (valor absoluto de `net_sales`) sobre la venta bruta de las líneas de venta. |
| Las cifras de control no cuadran por `retail_year` | El documento de referencia totaliza por año calendario, no por año minorista 4-5-4. | (Por **gera**) Se documentó en la sección 4.1.1 del notebook; para cuadrar contra contabilidad se agrega por año calendario de `date`. |
| `retail_calendar_guide.md` describe un año minorista que comienza en febrero | La guía sigue el calendario NRF genérico; en este dataset el mes minorista coincide con el mes calendario (84.7% a 99.2% de las líneas). | (Por **gera**) Documentado en el notebook. Pendiente decidir si se corrige la guía de la habilidad de EDA. |
| `AttributeError: The '.style' accessor requires jinja2` al formatear tablas | `jinja2` no está instalado en `.venv`. | (Por **gera**) Se evitó `DataFrame.style` y se formatearon las tablas con `Series.map`, sin agregar dependencias. |
| `RuntimeError: FT_Load_Glyph ... division by zero` al dibujar ejes logarítmicos | Las etiquetas en notación matemática de los ejes logarítmicos fallan con la tipografía configurada. | (Por **gera**) Se asignó un formateador de moneda explícito (`FuncFormatter`) a los ejes logarítmicos. |
| `margin` distinto de `net_sales - cogs` en 56,950 líneas (2.36%) | Líneas con `cogs` igual a cero (por ejemplo cargos y tarjetas de regalo) registran margen cero pese a tener venta neta ($2.8M). | (Por **gera**) Documentado en la sección 4.3; pendiente marcar o corregir antes de usar el margen como variable. |

| La fecha y la hora del canal web no reflejan el momento de compra | Solo el 3.8% de la venta web cae en fin de semana y el 13.5% de las líneas web figura a la hora 0; parecen registrar el procesamiento del pedido. | (Por **gera**) Documentado en la sección 4.4; el patrón por día y hora se interpreta solo para tiendas físicas. |
| Septiembre de 2026 incompleto en la extracción | Los días 28 a 30 de septiembre de 2026 casi no tienen líneas (0, 1 y 13). | (Por **gera**) Las comparaciones de 2026 se cortan en la semana minorista 38, que está completa; septiembre queda subestimado en la serie mensual. |
| El EDA de Camilo filtraba `markdown > 0` y el histograma salía vacío | `markdown` se registra con signo negativo. | (Por **gera**) No se trasladó ese gráfico; la distribución de `markdown` está en los descriptivos de la sección 4.2.1. |
| `RuntimeError: failed to load glyph` al dibujar etiquetas pequeñas | La tipografía configurada falla con tamaños de fuente de 8 puntos a baja resolución. | (Por **gera**) Las etiquetas de las secciones nuevas usan un tamaño mínimo de 9 puntos. |

---

## 4. Próximos Pasos y Acciones Pendientes

- [ ] **Ingeniería de características (propuestas de las notas de Camilo, respaldadas por la Fase 4):**
  - Calendario: indicadores de Navidad (semanas 47 a 51), San Valentín (semana 6) y Día de la Madre (semana 18), y número de semanas del mes minorista.
  - Atributos del local: antigüedad de la tienda y días con ventas, derivados de la primera fecha de venta de cada ubicación.
  - Tasas en lugar de importes: descuento sobre venta bruta, margen sobre venta neta y devoluciones sobre venta bruta.
- [ ] **Análisis del EDA aún no realizados:** crecimiento interanual con `ly_date_key`, descomposición y autocorrelación de la serie semanal, cohortes de clientes y Pareto de artículos.
- [ ] **Decisiones pendientes:**
  - Corregir o no `retail_calendar_guide.md` (el año minorista de este dataset comienza en enero).
  - Tratamiento de las líneas con costo cero antes de analizar margen.
  - Obtener la cifra de control oficial de 2026 con septiembre incluido para reemplazar la referencia de $41.11M (enero a agosto) en la sección 4.1.1.
  - `markdown` de 2022 conserva el cálculo de la extracción anterior; volver a extraer 2022 con la consulta actual o excluir ese año al analizar `markdown`.
  - Definir el objetivo del modelo: Camilo plantea clasificar devoluciones (`is_return`); el proyecto apunta a predecir ingresos por ventas.
  - Confirmar con el negocio qué evento explica el pico de las semanas 30 y 31 (finales de julio).
  - Confirmar si la fecha del canal web es la de compra o la de procesamiento del pedido.
  - Volver a extraer los últimos días de septiembre de 2026.
- [ ] **Control Git:**
  - Mantener commits siguiendo el formato `Fase <n> : <descripción>`; la Fase 6 se guardó en la rama `camilo` por indicación de Gerardo.
