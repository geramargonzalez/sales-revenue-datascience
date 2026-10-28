# Alcance y criterios de modelado: 2022–2025

Decisión registrada por **gera**, 27/10/2026, a partir de la indicación del usuario y la sugerencia del profesor.

## Objetivo

Predecir las ventas netas semanales por ubicación con datos de 2022 a 2025, usando historial y calendario comercial en dos modelos supervisados de regresión: lineal y Gradient Boosting, evaluados con MAE y RMSE.

La finalidad es apoyar la planificación comercial y financiera.

Ambos algoritmos son modelos supervisados de regresión: la respuesta es un importe continuo en USD.

## Datos y control contable

El alcance actual incluye únicamente transacciones con `date >= '2022-01-01'` y `date < '2026-01-01'`.

Este corte por fecha calendario se aplica a una vista analítica; el archivo original y la base contable completa se conservan.

Se mantienen las exclusiones contables de `rpt_ignored == True` y `txn_type` en `Reversal` o `Reversed`, junto con las devoluciones válidas y los clientes anónimos.

| Indicador | Recorte 2022–2025 |
| :--- | ---: |
| Líneas de transacción | 2.103.340 |
| Ventas netas | USD 242.277.286,76 |
| Ventas netas web | USD 158.030.710,35 |
| Participación web | 65,2272 % |
| Promedio anual de participación de noviembre y diciembre | 31,3668 % |
| Primera fecha observada | 02/01/2022 |
| Última fecha observada | 31/12/2025 |

El recorte temporal deja fuera 332.514 líneas y USD 45.421.877,15 de 2026.

La base completa sigue conciliando 2.435.854 líneas y **USD 287.699.163,91**; la diferencia corresponde al alcance temporal, no a una modificación de las transacciones.

Los descriptivos se recalcularon en una lectura por bloques de `dataset/transactionRevenue_combined_2022-0926.csv`, sin escribir sobre el archivo.

## Variables y horizonte

La unidad del modelo es una semana completa de domingo a sábado por ubicación.

| Rol | Variables |
| :--- | :--- |
| Objetivo | Suma semanal de `net_sales`, denominada `venta_neta` |
| Agrupación | `location_name` y fecha semanal |
| Historial | `venta_semana_anterior` y `venta_anio_anterior` |
| Calendario conocido | `es_navidad`, `es_san_valentin` y `es_dia_madre` |
| Claves auxiliares | `date`, `retail_year` y `retail_week` |

Las 37 columnas del esquema depurado no se utilizarán todas como predictores.

Los importes de la semana que se intenta predecir no pueden usarse como entradas de esa misma predicción.

La comparación anual debe alinear año y semana minorista, sin asumir siempre 52 semanas; el primer año aporta historial y puede quedar sin observaciones utilizables como objetivo al requerir el rezago anual.

La evaluación prevista es de una semana por vez, con la venta real de la semana anterior disponible en cada paso.

## Modelos y evaluación propuesta

Se compararán `LinearRegression` y `GradientBoostingRegressor`, además de una referencia que copie la misma semana del año anterior cuando esté disponible.

Gradient Boosting agrega árboles sucesivos para corregir los errores del conjunto y permite estudiar relaciones no lineales entre historial y calendario.

Se recomienda comenzar con la implementación de scikit-learn, ya disponible en el entorno, y árboles pequeños; esto es un punto de partida educativo y no una garantía de mejora.

Configuración inicial propuesta: `n_estimators=100`, `learning_rate=0.05`, `max_depth=2`, `min_samples_leaf=5`, `loss='squared_error'` y `random_state=42`.

La configuración se validará dentro del entrenamiento; evitar una selección o parada temprana que mezcle aleatoriamente las fechas.

Se mantendrá una división cronológica 80/20 de las semanas utilizables, con las mismas fechas y observaciones para todos los modelos.

Si se usa un modelo conjunto por ubicaciones, el corte se realiza por fechas semanales únicas, conservando todas las ubicaciones de una semana en el mismo tramo.

Las fechas exactas, cantidades de semanas y cobertura de eventos se determinarán después de preparar las variables del nuevo recorte.

## Métricas

| Métrica | Uso | Lectura |
| :--- | :--- | :--- |
| MAE | Principal para comparar configuraciones | Error absoluto promedio por semana y ubicación, en USD; menor es mejor |
| RMSE | Complementaria | Da mayor peso a los errores grandes y se expresa en USD; menor es mejor |
| WAPE | Apoyo comercial | `100 × suma(abs(predicción - real)) / suma(abs(real))`, si el denominador es positivo |
| Sesgo medio | Control de dirección | `promedio(predicción - real)`; positivo sobreestima, negativo subestima |

MAPE no se recomienda como criterio principal cuando hay semanas con ventas cero o cercanas a cero.

R² puede reportarse como indicador secundario; puede ser negativo y no equivale a un porcentaje de exactitud.

Las comparaciones requieren las mismas semanas y ubicaciones; las métricas de ventanas anteriores no se trasladan al nuevo alcance.

## Estado y siguiente paso

### Revisión de la indicación docente: 28/10/2026

La revisión confirma que el objetivo, la propuesta de modelos y las métricas de este documento coinciden con lo solicitado por el profesor: predecir un importe semanal mediante aprendizaje supervisado de regresión y comparar una regresión lineal con un modelo de boosting.

`RandomForestRegressor` combina árboles, pero no implementa gradient boosting; su prueba histórica no cubre por sí sola ese requisito.

Se verificó que `GradientBoostingRegressor` está disponible en scikit-learn 1.9.1 del entorno `.venv`, pero todavía no aparece implementado en el notebook de `gera_playground`.

Para una práctica sencilla se mantiene **MAE como principal** y **RMSE como complemento**; WAPE y sesgo sirven para comunicar escala y dirección del error, mientras que R² queda como indicador adicional.

WAPE se calcula sobre la misma población y ventana: una reducción entre períodos con distinto volumen de ventas no demuestra por sí sola una mejora del pronóstico.

Se conserva el protocolo ya documentado de 80/20 cronológico dentro de 2022–2025; reservar exactamente el año 2025 completo sería una alternativa de evaluación que requiere redefinir y ejecutar el corte, no una descripción de las pruebas actuales.

Los datos de 2022 pueden aportar historial al rezago anual aunque sus primeras semanas no puedan utilizarse como objetivos de entrenamiento; las cantidades y fechas exactas se contarán al preparar la nueva vista.

La presentación se actualizó al nuevo alcance y contiene 12 diapositivas, incluida la de métricas y la de Boosting que preparó el usuario.

Los modelos de esta propuesta **todavía deben implementarse y evaluarse con el recorte 2022–2025**; esta tarea no reentrenó modelos ni modificó el notebook.

Los experimentos históricos conservan su protocolo original como registro; sus resultados no constituyen una evaluación del nuevo alcance.

## Fuentes metodológicas

- [GradientBoostingRegressor: documentación oficial](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingRegressor.html).

- [Métricas de regresión: documentación oficial](https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics).

- [TimeSeriesSplit: validación temporal](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html).

- [Pronóstico con variables rezagadas y evaluación temporal](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html).

- [WAPE y sus límites al comparar series con tendencia](https://robjhyndman.com/hyndsight/wape.html).
