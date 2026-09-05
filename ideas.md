

1. Análisis de Temporalidad y Estacionalidad (Time Series)
⚬	Distribución de ventas por mes y hora: Puedes agrupar las ventas netas (net_sales) utilizando las columnas del calendario minorista 4-5-4 (retail_year, retail_month, retail_week).
⚬	Hipótesis a validar: El documento menciona que noviembre y diciembre concentran el 32% de las ventas del año. Puedes visualizar esto con un gráfico de barras por mes.
⚬	Franjas horarias: Analiza la columna hour para descubrir los picos de tráfico en las tiendas físicas versus las compras online a lo largo del día.
2. Rendimiento por Canal y Ubicación (Location & Channel Performance)
⚬	Online vs. Físico: Utiliza la columna is_web (y evita usar loc_ecommerce_flag que tiene errores) para comprobar si el canal online efectivamente representa alrededor del 62% de la venta total.
⚬	Filtro de tiendas operativas: Excluye ubicaciones administrativas o pop-ups (como 'Returns and Holds' o 'Jewelry Studio') y compara el rendimiento de las 14 tiendas operativas (SOHO, Chicago, etc.).
⚬	El caso de "Wedding Annex": Dado que el documento indica que este es un negocio distinto (con unos 50 tickets mensuales y un ticket medio altísimo de 2,000 USD), sepáralo de las tiendas tradicionales para un análisis de clúster o segmento premium.
3. Profundidad en el Comportamiento de Devoluciones (Returns EDA)
⚬	Tasa de devolución estacional: Filtra los datos donde is_return = TRUE. El documento señala que enero es el peor mes para las devoluciones (alcanzando hasta un 27%). Un gráfico de líneas comparando ventas brutas vs devoluciones por retail_month ilustraría muy bien esto.
⚬	Análisis por tienda: Compara la tasa de devoluciones entre tiendas para validar las grandes variaciones mencionadas (ej. Williamsburg 17% frente a Boston 7%).
⚬	Tiempo de retorno: Usa la columna return_lag_days para hacer un histograma que muestre cuántos días tardan, en promedio, los clientes en devolver un artículo.
4. Rentabilidad y Mix de Productos (Product & Margin Analysis)
⚬	Jerarquía de productos: Agrupa las ventas netas (net_sales) y las unidades (qty) por department, class y subclass1 para identificar los productos estrella.
⚬	Márgenes reales: Calcula la rentabilidad cruzando net_sales con el costo de la mercancía (cogs) para obtener el margin real de cada marca (brand) o departamento.
⚬	Impacto de promociones: Relaciona el descuento total (discount_total) o las rebajas (markdown) con el nombre de la promoción (promo_name) para ver qué campañas generaron más volumen de ventas brutas (gross_sales).
5. Análisis de Clientes y Geografía (Customer Insights)
⚬	Retención de clientes (Cohortes): Agrupa las transacciones por customer_id y fecha (date_key o date) para calcular cuántos clientes compran más de una vez (recurrencia).
⚬	Área de influencia (Geospatial): Utiliza el código postal de envío (ship_to_postal), cruzándolo con la ciudad (loc_city) y el estado (loc_state) de la tienda, para mapear desde dónde compran los clientes y qué distancia están dispuestos a recorrer o enviar los productos.