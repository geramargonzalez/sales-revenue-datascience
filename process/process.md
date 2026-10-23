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

  Cambios principales: cuota web global 63.5% (antes 63.8%); comparación inicialmente calculada a 39 semanas y corregida a 38 semanas completas en la Fase 7; Wedding Annex con 32 tickets de $1,815 en los últimos 12 meses; mediana de `net_sales` por línea de venta $94.00; `markdown` presente en el 80.0% de las líneas de venta; 58,205 líneas con margen cero; correlación de `markdown` con `net_sales` de -0.52.

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
- [x] **Metadatos del Kernel (commit `b4b7bd6`, por Gerardo):** La versión de Python declarada en los metadatos del notebook pasó de 3.11.16 a 3.9.6.

  El cambio afecta solo a ese campo de metadatos: no modifica celdas ni salidas, y el notebook se ejecutó con Python 3.11 del entorno `.venv`.
- [x] **Salidas del Notebook (commit `4358454`, por Gerardo):** El código y el texto de las 72 celdas no cambiaron.

  Cambiaron las salidas guardadas de 8 celdas (8, 11, 13, 20, 21, 23, 35 y 39), donde los tipos de dato pasan a mostrarse como `object` en lugar de `str`, y se vació el contador de ejecución de 17 celdas de las secciones 4.2 a 4.8, que conservan sus salidas.
- [x] **Fusión de Ramas:**
  - Primera fusión: `camilo` se fusionó en `gera` y en `main` por avance rápido (*fast-forward*), sin conflictos.
  - Pull request #1: Gerardo fusionó `gera` en `main` desde GitHub (commit de fusión `33e3177`), lo que adelantó el `main` remoto.
  - Segunda fusión: `gera` se fusionó en ese `main` actualizado con el commit de fusión `2c762ee`, sin conflictos y sin forzar el envío; después `gera` y `camilo` avanzaron hasta ese commit.

  Las tres ramas quedaron en el mismo commit, tanto en local como en el remoto.

### Fase 7: Robustez del Preprocesamiento y Comparabilidad Temporal (Aplicado por **gera**)

- [x] **Preservación de `return_lag_days`:** La columna original dejó de sobrescribirse y conserva sus valores nulos, ceros explícitos y rezagos superiores a 90 días.

  El recorte comercial se aplica únicamente en `return_lag_days_analisis`, dentro de una vista temporal de devoluciones.

- [x] **Semántica de Nulos:** Se conservaron 2,239,455 nulos estructurales globales en `return_lag_days`, incluidos 33,071 dentro de las 160,921 líneas de devolución.

  Los 12,038 ceros explícitos de devoluciones permanecen diferenciados de los nulos.

- [x] **Corrección del Diagnóstico de Rezago:** Las métricas se calculan sobre las devoluciones con rezago informado: 127,850 líneas, media original de 84.36 días, mediana de 17 días y 21,785 valores superiores a 90 días (17.04%).

- [x] **Eliminación Protegida de Columnas Vacías:** Se verificó en el CSV original y después del filtro contable que `item_season`, `promo_name` y `promo_amt` tienen cero valores informados.

  La celda ahora valida existencia y ausencia total antes de eliminarlas; una extracción futura con información detendrá el proceso en lugar de descartarla.

- [x] **Corte Temporal Único:** Todas las comparaciones interanuales utilizan la semana minorista 38, última semana de 2026 con siete fechas.

  La semana 39, con tres fechas y 499 líneas, se muestra como parcial y queda excluida de las métricas comparables.

- [x] **Entorno Reproducible:** Los metadatos del notebook vuelven a declarar Python 3.11.16 y el kernel `sales-revenue-env` (`Python (.venv - Sales Revenue)`).

- [x] **Actualización de la Habilidad EDA:** Se documentaron la conservación de nulos estructurales, la validación previa al descarte, la variable derivada de rezago y el corte semanal compartido.

- [x] **Ejecución y Control Contable:** Las 38 celdas de código del notebook se ejecutaron desde un kernel nuevo sin errores.

  Se conservaron **2,435,854 filas**, **37 columnas** y ventas netas por **$287,699,163.91 USD**, con cero variación y cero nulos no estructurales.

### Fase 8: Organización por Bloques y Revisión de Textos (Aplicado por **gera**, 20/10/2026)

- [x] **Referencia de clase:** Se revisó la organización de `EducacionProjectUTEC/Teorico/Ejemplo proyecto ML/Faltas_medicas.ipynb` como ejemplo de estructura, sin modificar ese archivo ni trasladar su contenido médico o sus instrucciones al proyecto.

- [x] **Presentación e índice:** Se incorporaron contexto, objetivo, alcance actual e índice navegable de los bloques 0 a 10.

  Los bloques de presentación, carga, validación inicial, limpieza y análisis exploratorio contienen el trabajo actual; ingeniería de variables, modelado, optimización, análisis de errores e importancia de variables quedan expresamente pendientes.

- [x] **Estructura preservada:** Se mantuvieron las 72 celdas, sus tipos, identificadores y orden; la nueva organización utiliza los encabezados de las celdas existentes.

- [x] **Revisión de textos:** Se reescribieron las 34 celdas Markdown con descripciones del propósito, la población analizada y las limitaciones de los resultados.

  Se corrigió la referencia antigua a 39 semanas por el corte de 38 y las cuotas web correspondientes; se distinguieron datos ausentes, ceros explícitos, asociaciones descriptivas y etapas todavía no desarrolladas.

- [x] **Etiquetas de presentación:** Se añadieron nombres legibles en español para variables en tablas y gráficos, sin renombrar las columnas de origen.

  Se aclararon los denominadores de rezago, tickets sin devoluciones y envíos con ZIP válido, y se identificaron los períodos parciales y la antigüedad observada de las tiendas.

- [x] **Comprobaciones estructurales:** Sintaxis de las celdas de código y enlaces de los 11 bloques verificados.

- [x] **Validación final:** Las 38 celdas de código se reejecutaron sin errores en `sales-revenue-env` con Python 3.11.16; se revisaron las etiquetas de los gráficos y se corrigió una leyenda que cubría un porcentaje.

  Los 671 valores numéricos comparados en 17 celdas con tablas coinciden con la versión anterior; se conservan **2,435,854 filas**, **37 columnas** y ventas netas por **$287,699,163.91 USD**.

**Próximos pasos:** confirmar el horizonte y la agregación del pronóstico antes de desarrollar los bloques de modelado; mantener las incidencias de extracción y costos pendientes descritas más abajo.

---

### Fase 9: Revisión de Código y Propuestas de Mejora (Aplicado por **gera**, 21/10/2026)

- [x] **Alcance:** revisión de las fases 7 y 8 frente a `main` (`bf51b02`), más los metadatos locales del notebook, mediante la habilidad `mattpocock-skills:code-review`.

- [x] **Revisión independiente:** evaluación de estándares y requisitos documentados, con resultados completos en [revision_fase_9.md](revision_fase_9.md).

- [x] **Incidencia detectada:** el cambio local selecciona `python3` y declara Python 3.9.6, en desacuerdo con `.venv` y `sales-revenue-env`; se documentó la propuesta de restauración sin modificar el notebook.

- [x] **Mejoras propuestas:** centralizar las validaciones repetidas, comparar el rezago original completo y validar el contrato de carga, incluidos los identificadores únicos.

- [x] **Verificación:** las 38 celdas de código ejecutaron sin errores en un kernel nuevo `sales-revenue-env` con Python 3.11.16; se conservaron las 72 celdas y su estructura.

  El cierre confirmó **2,435,854 filas**, **37 columnas**, **2,239,455 nulos originales del rezago** y **$287,699,163.91 USD** de ventas netas; la semana 38 mantiene el corte comparable y la 39 contiene tres fechas.

**Próximos pasos:** evaluar las propuestas del informe antes de implementarlas; completar las decisiones de extracción, costos y horizonte predictivo ya registradas.

---

### Fase 10: Centralización de las Validaciones de Nulos (Aplicado por **gera**, 21/10/2026)

- [x] **Función compartida:** se definió `validar_nulos(datos, nulos_rezago_esperados)` en la celda existente `e1b6d29c`, con parámetros explícitos y sin modificar el DataFrame recibido.

  La función comprueba la ausencia de nulos fuera de `return_lag_days`, verifica el conteo esperado del rezago y devuelve el resumen por columna.

- [x] **Tres puntos de control conservados:** las celdas `e1b6d29c`, `eda_vistas_code` y `eda_control_final` utilizan la misma función; el primer control reutiliza el resumen para evitar recorridos repetidos del dataset.

- [x] **Estructura y alcance:** se conservaron las 72 celdas, sus tipos, identificadores y orden, las salidas guardadas y los metadatos locales preexistentes.

  El commit incluye únicamente los cambios de código de esta fase y su documentación; los metadatos locales del kernel permanecen sin incorporar.

- [x] **Pruebas puntuales:** se verificó un caso válido con nulos, cero explícito y rezago superior a 90 días, sin mutaciones; se comprobó el rechazo de un nulo financiero y de aumentos o reducciones del conteo de nulos del rezago.

- [x] **Ejecución completa:** las 38 celdas de código ejecutaron sin errores en un kernel nuevo `sales-revenue-env` con Python 3.11.16 de `.venv`.

  El cierre conservó **2,435,854 filas**, **37 columnas**, **2,239,455 nulos del rezago** y ventas netas por **$287,699,163.91 USD**.

**Incidencia resuelta:** duplicación de las reglas de validación de nulos identificada en la Fase 9.

**Próximos pasos:** evaluar las propuestas restantes del informe: comparación completa del rezago, contrato de carga y selección del kernel.

---

### Fase 11: Objetivo Predictivo, Contrato de Carga y Confidencialidad (Aplicado por **gera**, 21/10/2026)

- [x] **Objetivo predictivo definido:** al cierre de cada semana minorista se estimarán las ventas netas de la semana siguiente por ubicación operativa, para apoyar la planificación comercial y operativa.

  La unidad futura de modelado será ubicación-semana y el objetivo conservará el efecto contable de las devoluciones válidas.

- [x] **Contrato de carga:** se validan las 40 columnas requeridas, la integridad y unicidad de `line_id`, las fechas, las categorías de `txn_type`, las columnas booleanas y los valores finitos de `net_sales` antes de limpiar la base.

  La extracción actual presenta cero columnas ausentes, cero identificadores nulos o duplicados, cero fechas o categorías inválidas y cero importes no finitos.

- [x] **Procedimiento temporal:** se documentó la agregación semanal, la separación cronológica de entrenamiento, validación y prueba, el desplazamiento de variables históricas y el ajuste del preprocesamiento únicamente con entrenamiento.

  La tabla semanal, las variables y los cortes concretos permanecen sin implementar hasta la validación del diseño.

- [x] **Confidencialidad:** el nombre de la empresa se anonimiza al cargar las columnas de marca y ubicación, antes de mostrar datos, tablas o gráficos.

  Las referencias visibles fueron sustituidas por nombres de ubicación sin prefijo y por la etiqueta `Marca propia`; el CSV de origen no se modifica.

- [x] **Entorno:** se restauraron los metadatos `sales-revenue-env`, `Python (.venv - Sales Revenue)` y Python 3.11.16.

- [x] **Verificación:** las 38 celdas de código ejecutaron en orden y sin errores; se conservaron las 72 celdas, sus identificadores y su orden.

  Los 671 valores numéricos de las 17 tablas existentes permanecen iguales. El cierre conserva **2,435,854 filas**, **37 columnas**, **2,239,455 nulos del rezago** y ventas netas por **$287,699,163.91 USD**.

**Alcance detenido para revisión:** no se construyeron todavía las variables históricas, la partición temporal ni los modelos.

---

### Fase 12: Tabla Semanal, Evaluación Temporal y Trazabilidad (Aplicado por **gera**, 22/10/2026)

- [x] **Tabla ubicación-semana:** se construyó una vista separada de la base contable con 247 semanas cerradas entre domingo y sábado y 2,076 combinaciones de ubicación y semana desde la primera actividad observada de cada local.

  La semana 47 de 2022 se conserva porque cubre de domingo a sábado aunque no tiene líneas en uno de sus días; la semana 39 de 2026 se excluye porque la extracción termina el miércoles.

- [x] **Ausencias diferenciadas:** dos semanas de Wedding Annex carecen de líneas y se marcan como `semana_sin_registros` sin convertirlas en ventas cero.

  La base `df` no se filtra ni se modifica para el modelado.

- [x] **Variables sin fuga:** se incorporaron rezagos de 1, 2, 4 y 13 semanas, medias móviles desplazadas, antigüedad observada, codificación cíclica de la semana y venta de la misma semana minorista del año anterior.

  La referencia estacional usa el año anterior y recurre a la semana previa cuando ese historial no existe.

- [x] **Cortes temporales comunes:** entrenamiento del 9 de enero de 2022 al 22 de marzo de 2026, validación del 29 de marzo al 21 de junio de 2026 y prueba final del 28 de junio al 20 de septiembre de 2026.

  La comparación utiliza 1,694 filas de entrenamiento, 182 de validación y 182 de prueba.

- [x] **Comparación inicial:** tres configuraciones de bosque aleatorio se evaluaron únicamente en validación mediante MAE, RMSE, WAPE y sesgo.

  `bosque_conservador` obtuvo el mejor WAPE de validación, con 15.47%, frente a 18.22% de la referencia.

- [x] **Compuerta de promoción:** el candidato seleccionado alcanzó 25.84% de WAPE en prueba y la referencia estacional 20.63%.

  El candidato no se promovió; la referencia permanece como campeón y el resultado queda visible en el notebook.

- [x] **Trazabilidad local:** cada ejecución registra parámetros, métricas, cortes, versiones, huellas de datos y código, predicciones de prueba y el artefacto del candidato en `artefactos_mlops/`.

  El directorio se excluye de Git porque contiene artefactos regenerables y modelos binarios.

- [x] **Dependencias:** se añadieron `scikit-learn`, `scipy`, `joblib` y sus dependencias al entorno y a `requirements.txt`.

- [x] **Ejecución y revisión visual:** las 38 celdas se ejecutaron desde un kernel nuevo y el gráfico final se inspeccionó a resolución completa sin etiquetas cortadas ni superpuestas.

  Se conservaron las 72 celdas, sus identificadores y su orden, además de **2,435,854 filas**, **37 columnas**, **2,239,455 nulos del rezago** y ventas netas por **$287,699,163.91 USD**.

**Incidencia resuelta:** una semana histórica con seis días que contienen líneas no se interpreta automáticamente como extracción parcial; el cierre del período se determina por sus límites de domingo a sábado.

**Próximos pasos:** analizar el deterioro fuera de muestra por ubicación y evento comercial, y evaluar variables adicionales solo si están disponibles al cierre de la semana pronosticada.

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
| `return_lag_days` confundía nulos con devoluciones del día cero | El recorte sobrescribía la columna original y la imputación posterior convertía los nulos estructurales en `0.0`. | (Por **gera**) Se conservó la columna original y se creó `return_lag_days_analisis` únicamente en la vista de devoluciones. |
| Comparaciones interanuales con cortes de 38 y 39 semanas | Una sección usaba la semana máxima disponible y otra validaba que tuviera siete fechas. | (Por **gera**) Se centralizó `SEMANA_CORTE_COMPARABLE` en la semana 38; la semana 39 se identifica como parcial. |
| Eliminación incondicional de columnas supuestamente vacías | El código asumía que las tres columnas continuarían nulas en futuras extracciones. | (Por **gera**) Se añadieron validaciones de existencia y conteo no nulo antes de ejecutar `.drop()`. |
| Salida guardada con error de `boxplot` bajo Python 3.9 | Los metadatos apuntaban al kernel genérico y las salidas no representaban el entorno `.venv`. | (Por **gera**) Se restauró `sales-revenue-env`, se fijó Python 3.11.16 en los metadatos y se reejecutó el notebook completo sin errores. |
| Textos y etiquetas con alcances ambiguos o desactualizados | Persistían referencias a 39 semanas y las etiquetas no distinguían importes por línea, tickets sin devoluciones, rezagos informados o envíos con ZIP válido. | (Por **gera**, Fase 8) Se revisaron títulos, descripciones, leyendas y conclusiones para declarar el período y la población de cada resultado, conservando los cálculos. |
| Nombre de la empresa visible en textos, código y resultados | Las columnas de marca y ubicación conservaban directamente las etiquetas de origen. | (Por **gera**, Fase 11) Se aplica anonimización al cargar, antes de cualquier salida, y se verificó que el notebook no contenga referencias visibles al nombre. |
| El bosque aleatorio mejora validación pero empeora en prueba | La ventana final contiene un patrón distinto al período de validación y el candidato no generaliza mejor que la referencia estacional. | (Por **gera**, Fase 12) Se aplicó una compuerta de promoción sobre prueba; la referencia conserva el estado de campeón y el candidato queda registrado para el análisis de errores. |

---

## 4. Próximos Pasos y Acciones Pendientes

- [ ] **Ingeniería de características adicional (propuestas de las notas de Camilo, respaldadas por la Fase 4):**
  - Calendario: indicadores de Navidad (semanas 47 a 51), San Valentín (semana 6) y Día de la Madre (semana 18), y número de semanas del mes minorista.
  - Atributos del local: días con ventas y señales verificadas de apertura o cierre; la antigüedad observada ya forma parte del primer modelo.
  - Tasas en lugar de importes: descuento sobre venta bruta, margen sobre venta neta y devoluciones sobre venta bruta.
- [ ] **Modelado y MLOps:**
  - Explicar el deterioro del bosque entre validación y prueba por ubicación, semana y evento comercial.
  - Evaluar validación temporal con ventanas sucesivas antes de ampliar la búsqueda de modelos.
  - Mantener la referencia estacional como campeón hasta que un candidato la supere fuera de muestra.
- [ ] **Análisis del EDA aún no realizados:** crecimiento interanual con `ly_date_key`, descomposición y autocorrelación de la serie semanal, cohortes de clientes y Pareto de artículos.
- [ ] **Decisiones pendientes:**
  - Corregir o no `retail_calendar_guide.md` (el año minorista de este dataset comienza en enero).
  - Tratamiento de las líneas con costo cero antes de analizar margen.
  - Obtener la cifra de control oficial de 2026 con septiembre incluido para reemplazar la referencia de $41.11M (enero a agosto) en la sección 4.1.1.
  - `markdown` de 2022 conserva el cálculo de la extracción anterior; volver a extraer 2022 con la consulta actual o excluir ese año al analizar `markdown`.
  - Confirmar con el negocio qué evento explica el pico de las semanas 30 y 31 (finales de julio).
  - Confirmar si la fecha del canal web es la de compra o la de procesamiento del pedido.
  - Volver a extraer los últimos días de septiembre de 2026.
- [ ] **Control Git:**
  - Mantener commits siguiendo el formato `Fase <n> : <descripción>`.
  - La Fase 6 se trabajó en la rama `camilo` por indicación de Gerardo y luego se fusionó en `gera` y `main`; mantener las tres ramas sincronizadas.
