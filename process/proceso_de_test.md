# Proceso de test del modelo

Autor: **gera**.

Última actualización: **25/10/2026**.

Este documento registra los experimentos del modelo de ventas para conservar qué se probó, sobre qué período, qué resultado produjo y qué decisión se tomó.

El objetivo es estimar las ventas netas de la semana siguiente para una ubicación operativa.

---

## 1. Cómo leer este documento

Cada prueba debe responder cuatro preguntas:

1. ¿Qué variables utilizamos?

2. ¿Qué semanas se usaron para entrenamiento y prueba?

3. ¿Cuánto se equivocó el modelo?

4. ¿La nueva versión mejoró sobre una referencia evaluada en las mismas semanas?

Una métrica menor no demuestra una mejora cuando cambia el período de prueba.

Por eso, las comparaciones definitivas deben usar las mismas filas y las mismas fechas.

---

## 2. Protocolo básico

- **Ubicación inicial:** `SOHO`.

- **Objetivo:** `venta_neta` semanal en USD, incluidas las devoluciones válidas.

- **Semana:** domingo a sábado.

- **Entrenamiento y prueba:** separación cronológica 80/20 con `shuffle=False`.

  El Test 8 utiliza un protocolo distinto: eventos de 2022–2024 para entrenamiento, evento de 2025 para prueba y estimación de 2026 después de ajustar con 2022–2025.

- **Fuga de información:** todas las variables deben estar disponibles antes de comenzar la semana objetivo.

- **Integridad:** las vistas del modelo no pueden modificar `df`, eliminar transacciones válidas ni alterar las ventas netas consolidadas.

- **Control contable:** 2,435,854 filas, 37 columnas y **$287,699,163.91 USD** en ventas netas.

### Métricas

| Métrica | Lectura sencilla | Objetivo |
| :--- | :--- | :--- |
| MAE | Error promedio semanal en USD | Menor es mejor |
| RMSE | Error que penaliza más las semanas con fallos grandes | Menor es mejor |
| R² | Proporción aproximada de la variación explicada | Mayor es mejor; 1 sería perfecto |

---

## 3. Resumen de experimentos realizados

| Test | Variables | Semanas de prueba | MAE prueba | RMSE prueba | R² prueba | Lectura |
| :--- | :--- | ---: | ---: | ---: | ---: | :--- |
| 1 | Semana anterior | 50 | $20,414.25 | $26,189.08 | 0.07 | Primera referencia aprendida |
| 2 | Semana anterior + hace dos semanas | 49 | $20,073.75 | $26,090.93 | 0.09 | Mejora pequeña; la segunda semana aporta poco |
| 3 | Semana anterior + misma semana del año anterior | 39 | $15,994.29 | $21,398.12 | 0.13 | Mejor resultado observado, con otro período de prueba |
| 3A | Copiar la misma semana del año anterior | 39 | $18,121.61 | $22,541.30 | 0.03 | Referencia estacional evaluada junto con el Test 3 |
| 4 | Test 3 + Navidad | 39 | $16,149.27 | $21,500.69 | 0.12 | No mejora; Navidad no aparece en prueba |
| 5 | Test 3 + San Valentín | 39 | $15,544.93 | $20,818.67 | 0.17 | Mejor MAE general, con solo una semana del evento |
| 6 | Test 3 + Día de la Madre | 39 | $16,044.99 | $21,397.85 | 0.13 | Resultado prácticamente igual al Test 3 |
| 7 | Test 3 + los tres indicadores | 39 | $15,615.03 | $20,852.56 | 0.17 | Mejora pequeña; cobertura de eventos insuficiente |
| 9 | Árbol pequeño con las cinco variables del Test 7 | 39 | $16,960.66 | $22,628.69 | 0.03 | Mayor error que la regresión con las mismas variables |

> [!IMPORTANT]
> Los tests 1, 2 y 3 no son directamente comparables porque utilizan períodos de prueba diferentes.
>
> El Test 3 y la referencia 3A sí son comparables: utilizan exactamente las mismas 39 semanas de 2026.
>
> Los tests 4 a 7 y el Test 9 también utilizan esas mismas 39 semanas y son comparables con el Test 3.

---

## 4. Detalle de las pruebas

### Test 1: venta de la semana anterior

**Hipótesis:** la venta reciente contiene información suficiente para estimar la semana siguiente.

```python
VARIABLES_RL = [
    'venta_semana_anterior'
]
```

| Elemento | Resultado |
| :--- | :--- |
| Semanas utilizables | 246 |
| Entrenamiento | 196 semanas, del 15/01/2022 al 11/10/2025 |
| Prueba | 50 semanas, del 18/10/2025 al 26/09/2026 |
| MAE entrenamiento | $17,717.77 |
| RMSE entrenamiento | $24,256.06 |
| R² entrenamiento | 0.56 |
| MAE prueba | $20,414.25 |
| RMSE prueba | $26,189.08 |
| R² prueba | 0.07 |

**Conclusión:** la semana anterior aporta señal, pero explica muy poco de las variaciones futuras fuera del entrenamiento.

**Decisión:** conservarla como variable básica.

### Test 2: una y dos semanas anteriores

**Hipótesis:** agregar otra semana reciente ayuda a representar la tendencia de corto plazo.

```python
VARIABLES_RL = [
    'venta_semana_anterior',
    'venta_hace_2_semanas'
]
```

| Elemento | Resultado |
| :--- | :--- |
| Semanas utilizables | 245 |
| Entrenamiento | 196 semanas, del 22/01/2022 al 18/10/2025 |
| Prueba | 49 semanas, del 25/10/2025 al 26/09/2026 |
| MAE entrenamiento | $17,609.35 |
| RMSE entrenamiento | $24,269.66 |
| R² entrenamiento | 0.56 |
| MAE prueba | $20,073.75 |
| RMSE prueba | $26,090.93 |
| R² prueba | 0.09 |

Coeficientes aprendidos:

| Variable | Coeficiente |
| :--- | ---: |
| `venta_semana_anterior` | 0.6991 |
| `venta_hace_2_semanas` | 0.0641 |

**Conclusión:** el resultado mejora ligeramente, pero el coeficiente de la segunda semana es pequeño.

**Decisión:** no asumir todavía que la segunda semana mejora el modelo, porque también cambió el período de prueba.

### Test 3: semana anterior y misma semana del año anterior

**Hipótesis:** la misma semana minorista del año anterior representa la estacionalidad comercial mejor que una segunda semana consecutiva.

```python
VARIABLES_RL = [
    'venta_semana_anterior',
    'venta_anio_anterior'
]
```

`venta_anio_anterior` se obtiene uniendo `retail_year` y `retail_week` con el año menos uno.

No se usa `.shift(52)`, porque un año minorista puede contener 53 semanas.

| Elemento | Resultado |
| :--- | :--- |
| Semanas utilizables | 194 |
| Entrenamiento | 155 semanas, del 07/01/2023 al 27/12/2025 |
| Prueba | 39 semanas, del 03/01/2026 al 26/09/2026 |
| MAE entrenamiento | $16,753.99 |
| RMSE entrenamiento | $21,109.83 |
| R² entrenamiento | 0.61 |
| MAE prueba | $15,994.29 |
| RMSE prueba | $21,398.12 |
| R² prueba | 0.13 |

Coeficientes aprendidos:

| Variable | Coeficiente |
| :--- | ---: |
| `venta_semana_anterior` | 0.5350 |
| `venta_anio_anterior` | 0.3578 |

La fórmula aproximada es:

```text
Predicción = 6,347.38
             + 0.5350 × venta de la semana anterior
             + 0.3578 × venta de la misma semana del año anterior
```

**Conclusión:** ambos antecedentes aportan información, aunque el modelo solo explica cerca del 13% de la variación observada en prueba.

**Decisión:** conservar la comparación anual y continuar probando variables de calendario.

### Test 3A: referencia de la misma semana del año anterior

**Hipótesis:** una referencia sencilla puede ser competitiva sin entrenar un modelo.

La predicción consiste en copiar directamente la venta de la misma semana minorista del año anterior.

| Método sobre las mismas 39 semanas | MAE | RMSE | R² |
| :--- | ---: | ---: | ---: |
| Regresión lineal del Test 3 | $15,994.29 | $21,398.12 | 0.13 |
| Misma semana del año anterior | $18,121.61 | $22,541.30 | 0.03 |

**Conclusión:** la regresión reduce el MAE en **$2,127.32 USD**, equivalente a **11.7%**, frente a la referencia anual.

**Decisión:** utilizar la referencia anual como control mínimo en los próximos experimentos.

### Test 4: indicador de Navidad

**Hipótesis:** las semanas minoristas 47 a 51 representan el aumento de ventas de fin de año.

**Variables:** antecedentes del Test 3 más `es_navidad`.

| Método | MAE | RMSE | R² |
| :--- | ---: | ---: | ---: |
| Test 4 | $16,149.27 | $21,500.69 | 0.1200 |
| Test 3 | $15,994.29 | $21,398.12 | 0.1284 |

**Cobertura:** 15 semanas de Navidad en entrenamiento y ninguna en prueba.

**Conclusión:** las métricas generales empeoran y el período de prueba no contiene Navidad.

**Decisión:** no considerar validado el indicador; volver a probarlo con una ventana que incluya las semanas 47 a 51.

### Test 5: indicador de San Valentín

**Hipótesis:** la semana minorista 6 contiene un patrón especial de ventas.

**Variables:** antecedentes del Test 3 más `es_san_valentin`.

| Método | MAE | RMSE | R² |
| :--- | ---: | ---: | ---: |
| Test 5 | $15,544.93 | $20,818.67 | 0.1749 |
| Test 3 | $15,994.29 | $21,398.12 | 0.1284 |

**Cobertura:** tres semanas de San Valentín en entrenamiento y una en prueba.

**Conclusión:** es el menor MAE general y reduce el error promedio en **$449.36 USD por semana**, equivalente a **2.8%**.

La única semana del evento es una muestra demasiado pequeña para concluir que el indicador funcionará en otros años.

**Decisión:** conservarlo como candidato exploratorio y validarlo con más años o ventanas temporales sucesivas.

### Test 6: indicador de Día de la Madre

**Hipótesis:** la semana minorista 18 contiene un patrón especial de ventas.

**Variables:** antecedentes del Test 3 más `es_dia_madre`.

| Método | MAE | RMSE | R² |
| :--- | ---: | ---: | ---: |
| Test 6 | $16,044.99 | $21,397.85 | 0.1284 |
| Test 3 | $15,994.29 | $21,398.12 | 0.1284 |

**Cobertura:** tres semanas de Día de la Madre en entrenamiento y una en prueba.

**Conclusión:** el MAE empeora en **$50.70 USD** y las otras métricas permanecen casi iguales.

**Decisión:** no conservarlo por ahora; se necesita mayor cobertura para evaluar el evento.

### Test 7: los tres indicadores

**Hipótesis:** combinar los tres eventos ayuda a representar la estacionalidad comercial.

**Variables:** antecedentes del Test 3 más `es_navidad`, `es_san_valentin` y `es_dia_madre`.

| Método | MAE | RMSE | R² |
| :--- | ---: | ---: | ---: |
| Test 7 | $15,615.03 | $20,852.56 | 0.1723 |
| Test 3 | $15,994.29 | $21,398.12 | 0.1284 |
| Referencia anual | $18,121.61 | $22,541.30 | 0.0328 |

**Conclusión:** reduce el MAE en **$379.26 USD por semana**, equivalente a **2.4%**, frente al Test 3.

También supera la referencia anual, pero no alcanza el MAE del Test 5.

**Decisión:** mantenerlo en el notebook para experimentar, sin promoverlo como modelo validado.

---

## 5. Indicadores de calendario

Los indicadores de eventos son columnas con valor `1` cuando la semana pertenece al evento y `0` en el resto.

Son válidos para pronosticar porque el número de semana y las fechas comerciales se conocen antes de observar las ventas objetivo.

Como primera aproximación se utilizan las semanas propuestas en `process/ideas.md`:

```python
semanal_rl['es_navidad'] = semanal_rl['retail_week'].between(47, 51).astype(int)
semanal_rl['es_san_valentin'] = semanal_rl['retail_week'].eq(6).astype(int)
semanal_rl['es_dia_madre'] = semanal_rl['retail_week'].eq(18).astype(int)
```

Estas semanas son hipótesis iniciales y todavía deben comprobarse contra las fechas reales de cada año.

### Cobertura disponible

| Evento | Semanas en entrenamiento | Semanas en prueba |
| :--- | ---: | ---: |
| Navidad | 15 | 0 |
| San Valentín | 3 | 1 |
| Día de la Madre | 3 | 1 |

Los tests conservan las mismas 194 filas, las mismas 155 semanas de entrenamiento y las mismas 39 semanas de prueba del Test 3.

La prueba termina el 26 de septiembre de 2026, por lo que no puede evaluar directamente la Navidad de ese año.

San Valentín y Día de la Madre tienen una sola observación cada uno en prueba.

El MAE del modelo completo dentro de esa única semana es **$13,723.92 USD** para San Valentín y **$7,936.67 USD** para Día de la Madre.

La referencia anual obtiene **$1,507.82 USD** y **$24,556.14 USD**, respectivamente.

Estos resultados describen dos semanas concretas y no permiten generalizar el comportamiento del evento.

### Lectura simple

- **Mejor MAE general:** Test 5, con San Valentín.

- **Modelo con los tres indicadores:** mejora pequeña frente al Test 3.

- **Navidad:** todavía no está evaluada fuera del entrenamiento.

- **Decisión:** conservar los resultados como exploratorios y usar validación temporal con más ventanas antes de elegir una configuración.

---

## 6. Plantilla para registrar una nueva prueba

Copiar y completar este bloque después de cada experimento:

```markdown
### Test N: nombre breve

**Fecha:** DD/MM/AAAA.

**Hipótesis:** qué esperamos que mejore y por qué.

**Variables:** lista de variables utilizadas.

**Ubicación:** ubicación evaluada.

**Entrenamiento:** cantidad de semanas y fechas.

**Prueba:** cantidad de semanas y fechas.

| Método | MAE | RMSE | R² |
| :--- | ---: | ---: | ---: |
| Candidato |  |  |  |
| Referencia anual |  |  |  |

**Resultado por evento:** cantidad de semanas y MAE dentro del evento.

**Conclusión:** qué aprendimos.

**Decisión:** conservar, descartar o volver a probar.
```

---

## 7. Verificaciones técnicas acumuladas

- [x] `train_test_split` se importa en la celda inicial y la división se ejecuta con `shuffle=False`.

- [x] Las fechas de entrenamiento terminan antes de comenzar las fechas de prueba.

- [x] `venta_semana_anterior` utiliza `shift(1)`.

- [x] `venta_hace_2_semanas` utiliza `shift(2)`.

- [x] `venta_anio_anterior` coincide con la misma combinación de semana minorista y año menos uno.

- [x] La regresión y la referencia anual se comparan sobre índices idénticos.

- [x] Los tests 4 a 7 utilizan las mismas 194 filas y las mismas 39 semanas de prueba.

- [x] Los indicadores contienen únicamente valores `0` y `1` y coinciden con las semanas minoristas definidas.

- [x] Las predicciones son finitas.

- [x] Se conservan 2,435,854 filas, 37 columnas y **$287,699,163.91 USD** de ventas netas.

- [x] Las compras con `CLIENTE_ANONIMO` permanecen incluidas.

---

## 8. Advertencia sobre el conjunto de prueba

Las pruebas repetidas ya utilizaron los resultados del período de prueba para elegir variables.

Por lo tanto, estas 39 semanas funcionan ahora como validación exploratoria y no como una prueba final completamente independiente.

Antes de promover un modelo real se debe reservar una ventana final no utilizada o aplicar validación temporal con ventanas sucesivas.

---

## 9. Test 8: Black Friday por año

**Fecha:** 25/10/2026.

**Ubicación:** SOHO.

**Pregunta:** ¿qué habríamos predicho para Black Friday 2025 usando solamente 2022, 2023 y 2024?

### Diseño de la prueba

- Una fila contiene la venta neta del evento en un año, incluidas devoluciones y compras anónimas.

- La regresión lineal usa como única variable el tiempo transcurrido desde 2022.

- Entrenamiento: los tres Black Friday de 2022–2024.

- Prueba: Black Friday 2025, una observación cuyo importe no se utiliza al ajustar el modelo de prueba.

- Referencia de prueba: copiar las ventas de Black Friday 2024.

- Pronóstico: ajustar un modelo nuevo con los cuatro eventos de 2022–2025 y estimar 2026.

No se usan todas las semanas ni todas las transacciones como ejemplos de entrenamiento; se agregan los importes de cada evento.

Black Friday se calcula como el viernes posterior al cuarto jueves de noviembre, sin fijar un número de semana minorista.

| Año | Black Friday | Función inicial | Venta del viernes (USD) | Venta de la semana domingo–sábado (USD) |
| :--- | :--- | :--- | ---: | ---: |
| 2022 | 25/11/2022 | Entrenamiento | $41,494.55 | $178,863.02 |
| 2023 | 24/11/2023 | Entrenamiento | $41,146.75 | $169,827.33 |
| 2024 | 29/11/2024 | Entrenamiento | $36,652.17 | $130,318.51 |
| 2025 | 28/11/2025 | Prueba | $26,852.70 | $113,738.20 |
| 2026 | 27/11/2026 | Pronóstico; sin dato real | No disponible | No disponible |

En el dataset, Black Friday 2024 pertenece a la semana minorista 48; los eventos de 2022, 2023 y 2025 pertenecen a la 47.

### Test 8: solo el viernes, opción predeterminada

| Método para 2025 | Predicción (USD) | Venta real (USD) | Error absoluto (USD) | Error absoluto (%) |
| :--- | ---: | ---: | ---: | ---: |
| Regresión entrenada con 2022–2024 | $34,922.11 | $26,852.70 | $8,069.41 | 30.05% |
| Copiar Black Friday 2024 | $36,652.17 | $26,852.70 | $9,799.47 | 36.49% |

**Conclusión:** la regresión sobreestima 2025; mejora frente a copiar 2024, pero su error del 30.05% sigue siendo grande en este evento.

**Estimación para 2026:** después de ajustar con 2022–2025, la regresión estima **$24,431.51 USD** para el viernes.

La referencia que repite Black Friday 2025 estima **$26,852.70 USD**.

No se puede medir el error de 2026 porque no hay venta real en la extracción.

### Test 8S: opción semanal

Cambiar `PERIODO_BF = 'semana'` compara toda la semana de domingo a sábado que contiene Black Friday.

| Método para 2025 | Predicción (USD) | Venta real (USD) | Error absoluto (USD) | Error absoluto (%) |
| :--- | ---: | ---: | ---: | ---: |
| Regresión entrenada con 2022–2024 | $111,125.11 | $113,738.20 | $2,613.09 | 2.30% |
| Copiar la semana de Black Friday 2024 | $130,318.51 | $113,738.20 | $16,580.31 | 14.58% |

**Estimación semanal para 2026:** regresión **$89,465.94 USD**; referencia que repite 2025 **$113,738.20 USD**.

Cada ventana histórica de SOHO tiene seis días con registros; el conteo se muestra sin imputar filas ni asumir que un día sin registros representa ventas cero o cierre confirmado.

La ventana de 2026 queda ausente, sin convertirla en cero.

**Interpretación:** el resultado semanal es cercano al valor observado en 2025, pero corresponde a un objetivo distinto del viernes y a un único evento de prueba.

El menor porcentaje de error semanal no demuestra que se pueda predecir mejor el viernes; tampoco constituye una validación estable del pronóstico de 2026.

### Límites y decisión

Tres puntos para aprender una tendencia y uno para comprobarla son una muestra muy pequeña.

No se calcula R² sobre la única observación de prueba y no se interpreta el error individual como garantía para 2026.

Esta tendencia utiliza solo año y ventas del evento; no incorpora campañas, precios ni cambios comerciales.

Las fechas de 2025 ya formaron parte de entrenamientos de experimentos anteriores; esta prueba respeta su propio corte, pero no es una evaluación completamente nueva para el proyecto.

**Decisión:** conservar el ejercicio para aprender a separar entrenamiento, prueba y pronóstico; no promover un modelo con este único resultado.

**Verificación:** ambas opciones ejecutadas en `sales-revenue-env`, fechas y agregaciones comprobadas, predicción de prueba contrastada con un ajuste lineal independiente y base conservada en 2,435,854 filas, 37 columnas y $287,699,163.91 USD.

---

## 10. Test 9: árbol de decisión frente a regresión lineal

**Fecha:** 25/10/2026.

**Hipótesis:** un árbol pequeño puede representar relaciones entre las variables que la regresión lineal no recoge y reducir el error semanal.

**Ubicación y objetivo:** SOHO; ventas netas de la semana siguiente en USD, con devoluciones y compras anónimas incluidas.

**Variables comunes:** `venta_semana_anterior`, `venta_anio_anterior`, `es_navidad`, `es_san_valentin` y `es_dia_madre`.

**Entrenamiento:** 155 semanas, desde el 07/01/2023 hasta el 27/12/2025.

**Prueba:** 39 semanas, desde el 03/01/2026 hasta el 26/09/2026.

Ambos modelos reutilizan exactamente las mismas matrices de la partición cronológica 80/20 del ejercicio de regresión.

La predicción se evalúa una semana por vez y supone que ya se conoce la venta real de la anterior.

### Configuración fijada antes de evaluar

```python
DecisionTreeRegressor(
    max_depth=3,
    min_samples_leaf=10,
    random_state=42
)
```

El árbol aprende tres niveles y siete grupos finales, cada uno con al menos diez semanas de entrenamiento.

No se buscaron hiperparámetros ni se ajustó la configuración al ver los resultados de prueba.

### Resultados

| Modelo | MAE entrenamiento (USD) | MAE prueba (USD) | RMSE prueba (USD) | R² prueba |
| :--- | ---: | ---: | ---: | ---: |
| Regresión lineal con los tres indicadores (Test 7) | $16,068.27 | $15,615.03 | $20,852.56 | 0.1723 |
| Árbol de decisión pequeño | $14,753.35 | $16,960.66 | $22,628.69 | 0.0252 |
| Referencia de la misma semana del año anterior | No se entrena | $18,121.61 | $22,541.30 | 0.0328 |

**Lectura sencilla:** el árbol se equivoca **$1,345.63 USD más por semana (8.6%)** que la regresión lineal en prueba.

El árbol reduce el error en 17 de las 39 semanas, pero su error promedio es mayor.

Su ventaja en entrenamiento no se mantiene en prueba; esto no demuestra que todos los árboles sean peores, solo que esta configuración no supera la regresión en este período.

Frente a la referencia anual, el árbol obtiene menor MAE, pero peor RMSE y R².

### Decisión y controles

**Decisión:** conservar la regresión lineal como la mejor de las dos alternativas de este ejercicio y mantener el árbol como comparación educativa.

Esta comparación no cambia el modelo campeón del flujo avanzado de 14 ubicaciones.

Las 39 semanas ya se utilizaron para explorar indicadores y otros cambios; se necesita una evaluación temporal adicional antes de elegir un modelo definitivo.

**Verificación:** ejecución desde un kernel limpio `sales-revenue-env`, coincidencia de variables e índices, entrenamiento del árbol con las 155 filas previstas, límites de profundidad y tamaño de hoja, métricas contrastadas y predicciones finitas.

Se conservaron la base de 2,435,854 filas y 37 columnas, los clientes anónimos, los 2,239,455 nulos de `return_lag_days` y las ventas netas por **$287,699,163.91 USD**.
