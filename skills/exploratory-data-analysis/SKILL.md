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

Al realizar análisis exploratorio en este repositorio, siempre deben respetarse los siguientes principios:

- **Idioma Español**: Todos los títulos de gráficos, etiquetas de ejes, leyendas, comentarios de código y textos explicativos deben redactarse exclusivamente en español.
- **Espaciado en Markdown**: Al terminar una oración en celdas de texto Markdown, dejar una línea en blanco en la siguiente línea.
- **Integridad Estructural**: No alterar la numeración ni la estructura base de las celdas del notebook.
- **Cuadre Contable**: Ninguna operación exploratoria o de filtrado temporal debe alterar de forma destructiva el balance de ventas netas del dataset consolidado (`net_sales = $283,387,098.70 USD`).

---

## 2. Flujo de Trabajo Paso a Paso

### Paso 1: Verificación de Estado del Dataset
Antes de generar visualizaciones, confirmar el estado de los datos:
1. Verificar dimensiones (`shape`): 2,408,173 filas y 37 columnas.
2. Confirmar ausencia total de valores nulos (`df.isna().sum().sum() == 0`).
3. Verificar tipos de datos (`dtypes`) de variables financieras y temporales.

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
- Para mayor detalle del calendario minorista, consultar [retail_calendar_guide.md](references/retail_calendar_guide.md).

#### Matriz de Correlación
- Calcular correlación de Pearson y Spearman entre variables numéricas (`gross_sales`, `net_sales`, `markdown`, `discount_total`, `cogs`, `margin`, `qty`, `return_lag_days`).
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
