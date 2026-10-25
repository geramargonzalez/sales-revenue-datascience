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

> [!IMPORTANT]
> Los tests 1, 2 y 3 no son directamente comparables porque utilizan períodos de prueba diferentes.
>
> El Test 3 y la referencia 3A sí son comparables: utilizan exactamente las mismas 39 semanas de 2026.
>
> Los tests 4 a 7 también utilizan esas mismas 39 semanas y son comparables con el Test 3.

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
