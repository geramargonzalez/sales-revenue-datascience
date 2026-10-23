---
name: exploratory-data-analysis
description: Guía integral para la ejecución del Análisis Exploratorio de Datos (EDA) en datasets de transacciones y ventas minoristas (retail). Incluye análisis univariado y bivariado de métricas financieras, estacionalidad con el calendario minorista 4-5-4, matrices de correlación y estándares de visualización en Jupyter notebooks. Utilizar al realizar análisis exploratorio, generar gráficos estadísticos o inspeccionar distribuciones de transacciones.
compatibility: Python 3.11+, pandas, seaborn, matplotlib, jupyter
metadata:
  author: gerardo
  version: "1.0"
---

# Habilidad: Análisis Exploratorio de Datos (EDA)

Esta habilidad define el procedimiento estandarizado para llevar a cabo el análisis exploratorio de datos (EDA) en el proyecto de ciencia de datos de ingresos de ventas de joyería, garantizando rigor metodológico, consistencia visual y cumplimiento de las restricciones contables del negocio.

---

## 1. Principios y Restricciones Operativas

Antes de realizar el análisis exploratorio, consultar y aplicar las secciones 3 («Reglas Generales de Código y Notebooks») y 4 («Límites Operativos y Cuadre Contable») de [`AGENTS.md`](../../AGENTS.md), fuente de referencia de las reglas generales del repositorio.

---

## 2. Flujo de Trabajo Paso a Paso

### Paso 1: Verificación de Estado del Dataset
Antes de generar visualizaciones, confirmar el estado de los datos:
1. Verificar dimensiones (`shape`): 2,435,854 filas y 37 columnas.
2. Confirmar que no existan nulos accidentales; se permiten únicamente los nulos estructurales de `return_lag_days`, que deben conservarse para distinguirlos de los ceros explícitos.
3. Antes de eliminar `item_season`, `promo_name` y `promo_amt`, validar que las tres columnas existan y continúen 100% nulas.
4. Verificar tipos de datos (`dtypes`) de variables financieras y temporales.

---

### Paso 2: Análisis Univariado

#### Variables Cuantitativas Financieras
Analizar la distribución de:
- `gross_sales` (Ventas brutas)
- `net_sales` (Ventas netas)
- `discount_total` (Descuentos totales)
- `cogs` (Costo de bienes vendidos / Cost of Goods Sold)
- `margin` (Margen bruto)
- `qty` (Cantidad de unidades por transacción)

**Procedimiento:**
- Calcular estadísticas descriptivas: media, mediana, desviación estándar, percentiles (p25, p75, p90, p99), mínimo y máximo.
- Visualizar mediante histogramas con KDE para forma de distribución y diagramas de caja (*boxplots*) para identificar dispersión.
- Explicar asimetría (*skewness*) y concentración de valores (ej. transacciones de alto valor vs. compras habituales).

#### Variables Categóricas
Analizar frecuencia y participación de:
- `department` (Departamentos comerciales: Joyería fina, Relojería, etc.)
- `class` (Clase de producto)
- `brand` (Marcas principales vs. genéricos)
- `location_name` (Puntos de venta / Tiendas físicas)
- `is_web` (Proporción canal digital vs. físico)

---

### Paso 3: Análisis Bivariado y Multivariado

#### Relación Canal y Rentabilidad
- Comparar `net_sales`, `margin` y tasa de descuento promedio entre transacciones web (`is_web == 1`) y tiendas físicas (`is_web == 0`).
- Evaluar ticket promedio por canal.

#### Comportamiento Temporal y Estacionalidad (Calendario 4-5-4)
- Analizar ingresos a través del calendario minorista NRF 4-5-4:
  - Comparativa interanual por `retail_year`.
  - Tendencia trimestral por `retail_quarter` (Q1 a Q4, identificando el impacto clave de la temporada festiva en Q4).
  - Distribución mensual por `retail_month` (1 a 12).
- Definir un único corte comparable con la última semana de siete fechas completas y reutilizarlo en todas las comparaciones interanuales.
- Mostrar las semanas parciales solo como observaciones descriptivas, identificadas explícitamente y excluidas de métricas interanuales.
- Para mayor detalle del calendario minorista, consultar [retail_calendar_guide.md](references/retail_calendar_guide.md).

#### Matriz de Correlación
- Calcular correlación de Pearson y Spearman entre variables numéricas (`gross_sales`, `net_sales`, `markdown`, `discount_total`, `cogs`, `margin`, `qty`, `return_lag_days_analisis`).
- Conservar `return_lag_days` sin modificaciones y aplicar el tope de 90 días únicamente en la variable derivada `return_lag_days_analisis` de la vista de devoluciones.
- Desplegar mapa de calor (*heatmap*) con mapa de colores divergente y anotaciones numéricas legibles.
- Documentar multicolinealidad o relaciones directas entre costos, descuentos y margen.

---

### Paso 4: Síntesis de Hallazgos y Conclusiones
Cada bloque de análisis debe finalizar con una celda Markdown que sintetice:
- Principales patrones observados.
- Implicaciones de negocio para la gestión de inventario y precios.
- Recomendaciones para la fase posterior de ingeniería de características (*feature engineering*) y modelado predictivo.

---

## 3. Documentación de Referencia

Para consultar lineamientos específicos de visualización y convenciones de negocio:
- [Estándares de Visualización](references/visualization_standards.md): Paletas cromáticas, formatos de moneda y diseño visual en `matplotlib` y `seaborn`.
- [Guía del Calendario Minorista 4-5-4](references/retail_calendar_guide.md): Estructura del calendario NRF y patrones estacionales en joyería.
- [Hipótesis y Preguntas de Negocio](../../process/ideas.md): Banco de hipótesis sobre estacionalidad, tiendas físicas vs. online, devoluciones y rentabilidad para guiar el análisis exploratorio.
