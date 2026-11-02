# Validador Metodológico: Series Temporales, Pronóstico Semanal y Proyección Anual (2018–2025)

Documento de validación técnica registrado por **gera**, 02/11/2026, como respaldo metodológico y de auditoría de [`sales-revenue-jewery.ipynb`](../sales-revenue-jewery.ipynb).

---

## 1. Propósito y Control Contable de Partida

Este documento valida la incorporación de series temporales en el Análisis Exploratorio (Sección 4.4) y en el Modelado Predictivo (Bloques 5, 6 y 7), detallando las variables empleadas, los tamaños muestrales de entrenamiento y prueba, la metodología de proyección anual a 52 semanas y la verificación formal de ausencia de sobreajuste (*overfitting*) y de fuga de información (*data leakage*).

Todas las vistas analíticas y de modelado operan sin alterar la base contable consolidada `df`:

| Indicador de control | Valor verificado |
| :--- | ---: |
| Filas de la base contable limpia (`df`) | `3,481,156` |
| Columnas depuradas (`df`) | `37` |
| Balance consolidado `net_sales` (2018–2026) | `$392,170,429.26 USD` |
| Tramo 2022–2026 preservado | `$287,699,163.91 USD` |
| Vista `df_eda` (años completos 2018–2025) | `3,148,642` filas (`$346,748,552.11 USD`) |

---

## 2. Validación Estadística de Series Temporales en el EDA (Sección 4.4)

Antes de construir modelos, se validó la estructura temporal de las `416` semanas completas del período 2018–2025:

1. **Crecimiento interanual homologado con `ly_date_key` (2019–2025):**

   El cruce de cada fecha con su equivalente del calendario minorista del año anterior alcanza una cobertura del `98.9%` al `100.0%` de las fechas anuales.

   Las tasas de variación homologadas (`+23.7%` en 2019, `+0.8%` en 2020, `+61.2%` en 2021, `+30.7%` en 2022, `+13.3%` en 2023, `+12.8%` en 2024 y `+14.0%` en 2025) confirman que el crecimiento observado es estructural y no un artefacto de corrimiento de fechas.

2. **Descomposición semanal (Tendencia, Estacionalidad de 52 semanas y Residuo):**

   Mediante una media móvil centrada simétrica ($2 \times 52$ semanas), la serie exhibe una **fuerza de tendencia $F_T = 0.664$** y una **fuerza estacional $F_S = 0.721$**.

3. **Funciones de Autocorrelación (ACF) y Autocorrelación Parcial (PACF):**

   Calculadas hasta el rezago 56 mediante la recursión de Durbin-Levinson (banda de significancia al 95%: $\pm 0.096$), los rezagos operativos clave resultan estadísticamente significativos y justifican los predictores del Bloque 6:

   | Rezago | Significado operativo | ACF ($r_k$) | PACF ($\phi_{kk}$) | Significativo al 95% |
   | :--- | :--- | ---: | ---: | :--- |
   | $t - 1$ | Semana inmediata anterior | `0.823` | `0.823` | Sí |
   | $t - 2$ | Hace 2 semanas | `0.681` | `0.010` | Sí |
   | $t - 4$ | Hace 1 mes minorista (4 sem.) | `0.405` | `-0.077` | Sí |
   | $t - 13$ | Hace 1 trimestre (13 sem.) | `0.287` | `0.003` | Sí |
   | $t - 26$ | Hace 1 semestre (26 sem.) | `0.250` | `-0.063` | Sí |
   | $t - 52$ | Misma semana del año previo (52 sem.) | `0.720` | `0.320` | Sí |

---

## 3. Variables Utilizadas por Cada Modelo (Bloque 6)

La unidad de análisis del modelado es la **semana completa cerrada en sábado (`W-SAT`)** para la ubicación operativa configurada (`UBICACION_RL = 'Williamsburg'`).

### 3.1 Variable Objetivo (`y`)

* **`venta_neta`**: suma semanal de `net_sales` (en USD) registrada en la tienda durante la semana objetivo $t$.

### 3.2 Predictores del Modelo Semanal (Secciones 6.1 a 6.4)

Todas las variables explicativas se construyen utilizando estrictamente información cerrada hasta la semana $t-1$ o fechas conocidas de calendario:

#### A. Conjunto Base (`VARIABLES_RL` — 9 variables: usado en `Regresión lineal` y `Boosting de árboles`)

1. **`venta_semana_anterior`**: venta neta observada en la semana $t-1$.

2. **`media_movil_4s`**: promedio móvil de las ventas netas entre $t-1$ y $t-4$.

3. **`venta_hace_52_semanas`**: venta neta observada exactamente 52 semanas antes ($t-52$, 364 días antes).

4. **`es_black_friday`**: indicador binario (`1` si el sábado de cierre cae del 24 al 30 de noviembre).

5. **`es_previa_navidad`**: indicador binario (`1` si el sábado de cierre cae del 15 al 24 de diciembre).

6. **`es_cierre_navidad`**: indicador binario (`1` si el sábado de cierre cae del 25 al 31 de diciembre).

7. **`es_san_valentin`**: indicador binario (`1` si el sábado de cierre cae del 10 al 16 de febrero).

8. **`es_dia_madre`**: indicador binario (`1` si el sábado de cierre cae del 7 al 13 de mayo).

9. **`es_post_evento`**: indicador binario (`1` en la semana inmediatamente posterior a Black Friday, cierre de Navidad, San Valentín o Día de la Madre).

#### B. Conjunto Ampliado de Series Temporales (`VARIABLES_SERIES_RL` — 18 variables: usado en `SARX + Fourier`)

Suma a las 9 variables de `VARIABLES_RL` cinco señales de ventanas móviles multi-escala/volatilidad y cuatro términos armónicos de Fourier:

10. **`venta_hace_2_semanas`**: venta neta en la semana $t-2$.

11. **`media_movil_8s`**: promedio móvil de las 8 semanas previas ($t-1$ a $t-8$).

12. **`media_movil_12s`**: promedio móvil trimestral de las 12 semanas previas ($t-1$ a $t-12$).

13. **`volatilidad_4s`**: desviación estándar muestral de las ventas en las 4 semanas previas ($t-1$ a $t-4$).

14. **`impulso_4s_12s`**: diferencia `media_movil_4s - media_movil_12s` (*momentum* de corto contra mediano plazo).

15. **`fourier_sin_1`**: $\sin(2\pi \cdot \text{retail\_week} / 52)$ (armónico fundamental anual).

16. **`fourier_cos_1`**: $\cos(2\pi \cdot \text{retail\_week} / 52)$.

17. **`fourier_sin_2`**: $\sin(4\pi \cdot \text{retail\_week} / 52)$ (segundo armónico semestral).

18. **`fourier_cos_2`**: $\cos(4\pi \cdot \text{retail\_week} / 52)$.

#### C. Modelos Univariados (`Holt-Winters` y `Referencia anual`)

* **`Holt-Winters (52 sem.)`**: modela exclusivamente la serie histórica de `venta_neta` mediante nivel ($\alpha = 0.379$), tendencia ($\beta = 0.0019$) y estacionalidad aditiva de 52 semanas ($\gamma = 0.617$), calibrados en entrenamiento.

* **`Referencia anual`**: proyecta $\hat{y}_t = y_{t-52}$ (`venta_hace_52_semanas`).

### 3.3 Predictores de la Proyección Anual de 52 Semanas (Sección 6.5)

Para proyectar las 52 semanas de 2025 al cierre de 2024 sin observar ventas reales de 2025, se prescinde de los rezagos cortos ($t-1$, $t-2$, medias móviles de 2025) y se emplean variables conocidas al `31/12/2024`:

* **`VARIABLES_ANUAL_RL` (8 variables — `Proyección anual Lineal`):** `venta_52s_ajustada`, `media_movil_4s_hace_52s` y los 6 indicadores de `INDICADORES_EVENTOS_RL`.

* **`VARIABLES_ANUAL_SERIES` (12 variables — `Proyección anual SARX + Fourier`):** las 8 variables de `VARIABLES_ANUAL_RL` más los 4 armónicos de `VARIABLES_FOURIER_RL`.

---

## 4. Cantidad de Registros en Entrenamiento y Evaluación

En `Williamsburg` durante el período 2018–2025 se parte de **`372,281` líneas transaccionales**, que al agregarse por sábado de cierre (`W-SAT`) conforman **`416` semanas completas** (excluyendo `2` semanas parciales de borde).

Tras descontar las primeras 52 semanas de 2018 (necesarias para construir `venta_hace_52_semanas`) y las semanas sin operación presencial durante el cierre sanitario de 2020 (`72` semanas en total), quedan **`344` semanas utilizables** en `datos_rl`.

### 4.1 Volúmenes en el Pronóstico Semanal (Secciones 6.2 a 6.4)

| Esquema de evaluación | Entrenamiento | Evaluación / Prueba | Fechas cubiertas |
| :--- | :--- | :--- | :--- |
| **Partición cronológica 80% / 20%** | **`275` semanas** (`79.9%`, ~5.3 años) | **`69` semanas** (`20.1%`, ~1.3 años) | Entreno: `12/01/2019`–`31/08/2024` \| Prueba: `07/09/2024`–`27/12/2025` |
| **`TimeSeriesSplit` Pliegue 1** | **`144` semanas** | **`40` semanas** | Ventana expansiva cronológica 1 |
| **`TimeSeriesSplit` Pliegue 2** | **`184` semanas** | **`40` semanas** | Ventana expansiva cronológica 2 |
| **`TimeSeriesSplit` Pliegue 3** | **`224` semanas** | **`40` semanas** | Ventana expansiva cronológica 3 |
| **`TimeSeriesSplit` Pliegue 4** | **`264` semanas** | **`40` semanas** | Ventana expansiva cronológica 4 |
| **`TimeSeriesSplit` Pliegue 5** | **`304` semanas** | **`40` semanas** | Ventana expansiva cronológica 5 |

### 4.2 Volúmenes en la Proyección de Año Completo 2025 (Sección 6.5)

Como `ratio_cierre_anual` compara las últimas 12 semanas del año $A-1$ frente al año $A-2$, el historial completo para este modelo comienza en enero de **2020**, reuniendo **`293` semanas utilizables** (`6` años completos):

| Subconjunto | Semanas | Meses / Años equivalentes | Rango de fechas |
| :--- | ---: | :--- | :--- |
| **Entrenamiento (`train_anual_rl`)** | **`241` semanas** | **`60` meses** (`5` años: `2020`–`2024`) | `04/01/2020` al `28/12/2024` |
| **Prueba semanal (`test_anual_rl`)** | **`52` semanas** | **`1` año completo** (`2025`) | `04/01/2025` al `27/12/2025` |
| **Prueba mensual (`mensual_anual_rl`)** | `52` semanas sumadas | **`12` meses calendario** (`2025`) | Enero de 2025 a diciembre de 2025 |

---

## 5. Paso a Paso de la Proyección Anual y Diferencia frente al Pronóstico Semanal

### 5.1 Procedimiento en 6 pasos de la Proyección Anual (Sección 6.5)

1. **Formulación directa a 52 semanas (sin recursión):** en lugar de encadenar 52 predicciones semana a semana (lo que propagaría exponencialmente cualquier error inicial), cada semana $t$ de 2025 se predice directamente desde su homóloga $t-52$ de 2024 y el calendario de 2025.

2. **Cálculo del pulso interanual de cierre (`ratio_cierre_anual`):** se calcula la media de las últimas 12 semanas de cada año (`media_ult12`) y se obtiene el cociente $\text{media\_ult12}_{A-1} / \text{media\_ult12}_{A-2}$, acotado con `.clip(0.8, 1.2)` para evitar que saltos atípicos distorsionen el año siguiente.

3. **Construcción de `venta_52s_ajustada` y `media_movil_4s_hace_52s`:** se pondera la venta de hace 52 semanas por el pulso de cierre (`0.65 + 0.35 * ratio_cierre_anual`) y se acompaña del promedio móvil de 4 semanas de hace un año para suavizar variaciones puntuales.

4. **Incorporación del calendario comercial y Fourier:** se añaden los 6 indicadores de feriados (`INDICADORES_EVENTOS_RL`) y los 4 armónicos anuales (`VARIABLES_FOURIER_RL`).

5. **Entrenamiento estricto hasta 2024:** `LinearRegression` y `make_pipeline(StandardScaler(), Ridge(alpha=10.0))` se entrenan únicamente con las `241` semanas de `2020–2024`.

6. **Predicción y agregación multi-horizonte:** se proyectan las `52` semanas de 2025, se agrupan en `12` meses calendario (`.resample('ME').sum()`) y se compara el presupuesto anual acumulado.

### 5.2 Diferencias Clave entre el Pronóstico Semanal y la Proyección Anual

| Criterio | Pronóstico Semanal (Secciones 6.2–6.4) | Proyección de Año Completo (Sección 6.5) |
| :--- | :--- | :--- |
| **Momento de ejecución** | Cada sábado del año para predecir la semana siguiente ($t+1$). | Al 31 de diciembre para proyectar las 52 semanas del año entrante ($t+1 \dots t+52$). |
| **Información reciente disponible** | Usa ventas de hace 1 a 12 semanas ($t-1, t-2$, medias móviles de 4, 8 y 12 semanas). | **Cero ventas del año proyectado**; solo usa datos hasta $t-52$ (año anterior). |
| **Mejor resultado semanal (`SARX + Fourier`)** | **`MAE = $10,332.94 USD`** \| **`RMSE = $13,691.94 USD`** \| **`R² = 0.69`** | **`MAE = $12,082.95 USD`** \| **`RMSE = $15,519.89 USD`** \| **`R² = 0.62`** |
| **Mejor resultado mensual (`SARX + Fourier`)** | No aplica (horizonte de 1 semana). | **`MAE = $30,598.89 USD`** \| **`RMSE = $42,409.18 USD`** \| **`R² = 0.73`** |
| **Objetivo de negocio** | Operación táctica semanal (dotación de personal, reposición inmediata). | Planificación estratégica anual (*budget* financiero, compras de inventario y metas mensuales). |

---

## 6. Validador de Sobreajuste (*Overfitting*) en la Proyección Anual

Al observar que la venta real acumulada de 2025 en `Williamsburg` fue de **`$3,679,704.43 USD`** frente a **`$3,673,815.65 USD` (`-0.16%`)** en el modelo `Lineal` y **`$3,762,761.30 USD` (`+2.26%`)** en `SARX + Fourier`, es fundamental responder por qué **no existe sobreajuste en el entrenamiento del modelo** y qué explica esa precisión en el acumulado anual:

### 6.1 Evidencia de ausencia de *overfitting* y de *data leakage*

1. **El error semanal fuera de muestra es de ~$12,083 USD (~17% por semana), no cercano a cero:**

   Un modelo sobreajustado o con filtración de datos futuros tendría un error semanal cercano a `$0` y un $R^2 \approx 0.99$.

   Por el contrario, en las 52 semanas de 2025 el modelo comete un `MAE` semanal de **`$12,696.52 USD` ($R^2 = 0.56$)** en la versión Lineal y de **`$12,082.95 USD` ($R^2 = 0.62$)** en `SARX + Fourier`.

2. **Separación temporal estricta (`train_anual_rl.index < '2025-01-01'`):**

   Las 52 semanas de 2025 están 100% excluidas de `.fit()` y del ajuste de `StandardScaler()`.

3. **Baja complejidad paramétrica y regularización $L_2$:**

   El modelo `Lineal` estima únicamente **8 coeficientes** sobre **241 semanas** (~30 observaciones por parámetro), mientras que `SARX + Fourier` estima **12 coeficientes** con penalización **`Ridge(alpha=10.0)`**, impidiendo memorizar fluctuaciones ruidosas del período 2020–2024.

### 6.2 ¿Por qué el error acumulado de las 52 semanas es de solo `-0.16%` / `+2.26%`?

1. **Compensación estadística de errores de signo opuesto al agregar (Ley de los Grandes Números):**

   A nivel semanal, el modelo tiene ~26 semanas en las que subestima la venta real (errores positivos que suman `~+$327,000 USD`) y ~26 semanas en las que sobreestima la venta real (errores negativos que suman `~-$333,000 USD`).

   En el `MAE` semanal se promedian los valores absolutos ($|e_t|$), por lo que ambos signos suman error (`$12,082.95 USD` por semana).

   En cambio, al sumar las 52 semanas para obtener el **total anual** ($\sum_{t=1}^{52} \hat{y}_t$) o al agrupar en **12 meses**, los desvíos positivos y negativos por clima o desplazamiento de compras entre semanas contiguas se cancelan mutuamente, elevando el $R^2$ de `0.62` (semanal) a **`0.73` (mensual)**.

2. **Rol del amortiguador `(0.65 + 0.35 * ratio_cierre_anual)` y comparación entre `Lineal` y `SARX + Fourier`:**

   La variable `venta_52s_ajustada` aplica una regla fija de amortiguación (`65%` peso del nivel previo y `35%` peso del ratio de cierre).

   En 2025 esa ponderación coincidió casi exactamente con la tasa media de crecimiento anual de `Williamsburg`, dejando el saldo neto de las 52 semanas del modelo `Lineal` en `-0.16%`.

   Sin embargo, el modelo **`SARX + Fourier`** —aunque cierra el total anual con una diferencia de **`+2.26%`**— es **superior en todas las métricas de ajuste real**: reduce el `MAE` semanal en `-$613.57 USD`, reduce el `MAE` mensual en `-$5,575.25 USD` (`-15.4%`) y mejora el $R^2$ tanto semanal (`0.62` vs. `0.56`) como mensual (`0.73` vs. `0.69`).
