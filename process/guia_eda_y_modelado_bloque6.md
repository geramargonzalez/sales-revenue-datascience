# Guía de Reorganización del EDA (Bloque 4) y Ayuda para el Modelado (Sección 6)

Documento de referencia operativa elaborado por **gera** (`19/11/2026`) sobre [`sales-revenue-jewery.ipynb`](../sales-revenue-jewery.ipynb).

Resume la reestructuración del **Bloque 4 (Análisis exploratorio)** y explica cómo cada bloque del nuevo EDA general (desacoplado de ubicaciones particulares) respalda el entrenamiento, la selección de variables y la lectura de errores de los modelos en los **Bloques 5 y 6**, donde recién se configura la ubicación de ejemplo (`UBICACION_RL = 'Williamsburg'`).

---

## 1. Resumen de la Reorganización del Bloque 4

El Bloque 4 anterior acumulaba más de `30` gráficos orientados principalmente a *Business Intelligence* general (distribuciones por línea de ticket `line_id`, matrices de correlación entre importes contemporáneos, horarios web y contraste repetido de hipótesis).

Siguiendo la lógica del notebook de referencia de clase (`Hospital_LOS_Prediction_CLASE1.ipynb`) y las clases de series temporales (*Índice de Variación Estacional* `IVE`, desestacionalización y diagnóstico de variabilidad), el Bloque 4 quedó organizado en **dos partes explícitas** dentro de `107` celdas totales (`3,148,642` líneas y `$346,748,552.11 USD` en `2018–2025`, sin modificar `df`) y con **Parte I (`4.0`–`4.5`) completamente agnóstica de la ubicación**:

| Parte | Sección | Qué hace ahora | Cambio frente a la versión anterior |
| :--- | :--- | :--- | :--- |
| **Parte I** (Modelado) | **4.0 Base de análisis** | Define `2018–2025`, segmentos, `TIENDAS_FISICAS`, `tickets_venta` y series semanales cerradas `W-SAT` (`Empresa`, `Tiendas físicas` y `Panel ubicación-semana`) | Incorpora directamente la unidad temporal semanal usada como objetivo en los Bloques 5–6 sin atar el EDA a una sucursal |
| **Parte I** (Modelado) | **4.1 Control y calendario 4-5-4** | Cuadre anual contra cifras de control y correspondencia `retail_month` / `retail_quarter` | Retira el panel duplicado de hipótesis (`4.1.2`) y enfoca en la semana `53` de `2024` |
| **Parte I** (Modelado) | **4.2 Madurez de ubicaciones** | Ranking de ventas netas, historial observado en meses y tabla `ficha_tiendas` de las `13` sedes con registro `2018–2025` | Muestra gráficamente el umbral de `>= 100` semanas continuas tras `t-52` para fundamentar la selección posterior |
| **Parte I** (Modelado) | **4.3 Univariado del objetivo (`venta_neta`)** | `boxplot` + histograma con media y mediana (`Total empresa` y `Tiendas físicas agregadas`) más tabla comparativa (`Empresa`, `Web Warehouse`, `Tiendas físicas` y `Panel ubicación-semana`) | Reemplaza las `10` distribuciones por línea de ticket (`cogs`, `margin`, `discount_total`) |
| **Parte I** (Modelado) | **4.4 Dinámica temporal multi-horizonte** | Serie mensual, estacionalidad `1–53`, **`IVE` por Quarter (`Q1–Q4`)** por canal, serie desestacionalizada, dispersión anual empresa, `CV %` por horizonte (`2021–2025`), `ly_date_key` y `ACF/PACF` | Incorpora el análisis por **Quarter (`Q1–Q4`)**, dispersión multiplicativa y compensación `Semana -> Mes -> Quarter -> Año`, y retira `hour` |
| **Parte I** (Modelado) | **4.5 Bivariado `X -> y`** | *Lag plots* (`t-1` y `t-52` sobre `Total empresa` con recta `OLS`, octiles y campañas), `barplot` por evento y `Quarter`, y tabla de correlaciones `Empresa` frente a `Mediana sedes maduras` | Reemplaza los `8` heatmaps por línea (`gross_sales`, `cogs`, `margin`) por cruces directos entre predictores y `venta_neta` |
| **Parte II** (Negocio) | **4.6 Devoluciones** | Balance por canal, pico post-navideño (`sem. 1–5`), rezago, motivos y clase | Se conserva íntegro como contexto comercial |
| **Parte II** (Negocio) | **4.7 Producto y rentabilidad** | Departamentos, subclases, márgenes, Pareto `80/20` y descuentos | Se conserva íntegro como contexto comercial |
| **Parte II** (Negocio) | **4.8 Clientes y geografía** | Recurrencia (`CLIENTE_ANONIMO` excluido temporalmente) y mapas web (`ZIP`) | Se conserva íntegro como contexto comercial |

---

## 2. Cómo Ayuda el Nuevo EDA a Entrenar e Interpretar los Modelos de la Sección 6

Cada hallazgo cuantificado en la **Parte I (`4.0`–`4.5`)** responde una decisión de entrenamiento de **`Regresión lineal (OLS)`**, **`GradientBoostingRegressor`** y **Series Temporales** en la **Sección 6** (ilustrada allí con `UBICACION_RL = 'Williamsburg'` y generalizada a las cuatro sedes maduras en `6.6`):

### 2.1 Ayuda directa a `Regresión lineal (OLS)` (`6.1`, `6.2`, `6.4a`, `6.5`, `6.8`)

1. **Justificación visual de las variables de calendario (`4.5` $\rightarrow$ `6.1` y `6.2`):**

   * En `364` semanas del total empresa (`2019–2025`), el *lag plot* entre `venta_neta` ($t$) y `venta_semana_anterior` ($t-1$) muestra una relación lineal limpia (`Pearson = 0.814`, `Spearman = 0.888`, pendiente `OLS = 0.82`, coincidente con la mediana por octiles en semanas normales).

   * Sin embargo, las `9` semanas de **`Previa Navidad`** (`media = $2,610,251 USD`) y `Black Friday` (`media = $1,993,580 USD`) se despegan por encima de las `300` semanas normales (`media = $787,280 USD`), mientras las `27` semanas **`Post-evento`** caen por debajo de la recta de regresión (`mediana = $771,147 USD`).

   * **Impacto práctico al entrenar:** explica por qué `OLS Base` (`6.1`) subestima las semanas de campaña y sobreestima el arranque de enero, y por qué sumar los `6` indicadores binarios (`6.2`) reduce el `MAE` lineal en **`-20.27%`** (`$13,308.92` $\rightarrow$ `$10,611.67 USD`) en la serie ejemplo (`Williamsburg`).

2. **Por qué `shift(52)` = `364` días es obligatorio (`4.1` $\rightarrow$ `6.5`):**

   * La tabla de control (`4.1`) demuestra que `2024` tuvo **`53` semanas minoristas** (`+$0.48M`).

   * Si en el entrenamiento anual se empareja por `retail_week`, todo `2025` queda corrido `371` días; al fijar `venta_hace_52_semanas` (`364` días exactos), la referencia anual reduce su `MAE` un **`-14.1%`** y `OLS` mejora un **`-1.5%`** (`6.5`).

3. **Por qué la poda `VIF <= 5` estabiliza los coeficientes sin `Ridge` (`4.5` $\rightarrow$ `6.3` y `6.4a`):**

   * La tabla bivariada confirma que a nivel empresa `venta_semana_anterior` (`0.814`), `media_movil_4s` (`0.700`) y `venta_hace_2_semanas` (`0.699`) están fuertemente correlacionados con `venta_neta` y solapados entre sí (y también entre las sedes maduras, con mediana `0.767`, `0.653` y `0.608`).

   * **Regla para entrenar:** agregar medias móviles redundantes (`6.3`) desestabiliza signos en `OLS`, mientras podar `media_movil_4s`, `12s` y `8s` por `VIF > 5.0` (`6.4a`) deja `11` variables con `VIF <= 3.47` y un ajuste estable (`MAE = $10,492.45 USD`, `R² = 0.65`).

### 2.2 Ayuda directa a `GradientBoostingRegressor` (`6.1`–`6.4b`, `6.6`)

1. **Asimetría extrema, crecimiento de escala y límite de extrapolación (`4.3` y `4.4`):**

   * En `4.3` se documenta asimetría positiva marcada en todos los niveles (`Empresa = 2.54`, `Web Warehouse = 3.10`, `Tiendas físicas agregadas = 0.88`, `Panel ubicación-semana = 5.39`), junto con crecimiento acumulado de casi `4x` (`$19.1M` en `2018` $\rightarrow$ `$72.5M` en `2025`) y dispersión semanal creciente en dólares (`4.4`).

   * **Impacto práctico al entrenar:** los árboles de `GradientBoostingRegressor` promedian observaciones en hojas finitas y no extrapolan tendencias lineales ni nuevos máximos fuera del rango visto en entrenamiento; al mismo tiempo, en tiendas maduras individuales donde la mediana de `t-52` baja a `r = 0.332` (`4.5`) por aperturas recientes (`2023–2025`), las particiones de entrenamiento sufren cambios de nivel (`Prueba / Entreno` de `1.21x` a `1.41x` en `Williamsburg`, `MAE = $12,635.63 USD` frente a `$10,611.67 USD` en `OLS`).

2. **Pocas muestras por evento anual (`4.5` $\rightarrow$ `max_depth=2`):**

   * En siete años (`2019–2025`), cada feriado aparece solo entre **`7` y `9` veces** (`Previa Navidad: 9`, `Cierre Navidad: 7`, `Black Friday: 7`, `Día de la Madre: 7`, `San Valentín: 7`).

   * **Regla para entrenar:** con `min_samples_leaf=5` y `max_depth=2`, `Boosting` tiene pocos ejemplos por hoja para aislar eventos puntuales y pierde precisión al añadir predictores colineales (`17.15%` en `6.2` $\rightarrow$ `18.34%` en `6.4a` $\rightarrow$ `17.76%` en `6.4b`).

### 2.3 Ayuda directa a Series Temporales, `Quarter` y Generalización (`6.4b`, `6.6`, `6.8`)

1. **Justificación estadística de rezagos y Fourier (`4.4` $\rightarrow$ `6.4b`):**

   * Las fuerzas de tendencia ($F_T = 0.664$) y estacionalidad ($F_S = 0.721$) del total empresa junto con `ACF/PACF` (`t-1 = 0.823`, `t-2 = 0.681`, `t-4 = 0.405`, `t-52 = 0.720` / `PACF = 0.320`) respaldan la combinación de rezagos autorregresivos más los `4` armónicos de Fourier en **`OLS Reducido + Fourier`** (`MAE = $10,488.87 USD` / `14.23%`, `R² = 0.66`).

2. **Estacionalidad por `Quarter` (`IVE`) entre canales y compensación por horizonte (`4.4` $\rightarrow$ `6.8`):**

   * A nivel compañía, `Q4` concentra un **`IVE = 1.461`** (`38.69%` del año, `$16.77M` por trimestre) frente a **`IVE = 0.776`** en `Q1` (`17.26%`); al abrir por canal, `Web Warehouse` alcanza **`IVE = 1.587`** en `Q4` mientras las tiendas físicas agregadas marcan **`IVE = 1.225`**.

   * Sobre la serie desestacionalizada del total empresa (`2021–2025`), la dispersión relativa cae de **`23.39%` (semanal)** y **`23.37%` (mensual)** a **`21.52%` (*quarter*)**, mientras el acumulado **anual** (`23.06%`) refleja el crecimiento de escala (`$38.1M` $\rightarrow$ `$72.5M`); en las sedes individuales evaluadas en `6.8`, esa compensación temporal reduce el error de proyección de `OLS + Fourier` desde **`17.21%` (semanal)** hasta **`9.75%` (mensual)**, **`7.46%` (trimestral)** y **`+0.60%` (anual)**.

3. **Criterio de madurez para validación multi-ubicación (`4.2` y `4.5` $\rightarrow$ `6.6`):**

   * La ficha de cobertura (`4.2`) identifica de forma objetiva qué ubicaciones cumplen `>= 100` semanas continuas tras `t-52`: únicamente **`Web Warehouse` (`96` meses)**, **`Williamsburg` (`96`)**, **`Wedding Annex` (`96`)** y **`SOHO` (`74`)**, dejando fuera de `6.6` a las `9` tiendas más recientes (`2` a `30` meses) hasta acumular más historia anual.

   * A su vez, el contraste en `4.5` entre el total empresa (`t-52` `r = 0.932`) y la mediana de sedes maduras (`t-52` `r = 0.332` frente a `t-1` `r = 0.767`) anticipa que cada sede madura presenta distinta estabilidad interanual al evaluar `6.6`.

---

## 3. Lista de Verificación Rápida al Experimentar en la Sección 6

1. **Antes de elegir o cambiar `UBICACION_RL` en el Bloque 5:** revisar en `4.2` que la sede tenga al menos `>= 100` semanas continuas tras `t-52` y verificar en `4.4`–`4.5` la diferencia de estacionalidad (`IVE`) entre canal web y tiendas físicas.

2. **Si probás nuevas variables en `6.1`–`6.4`:** validar su relación en el *lag plot* y tabla bivariada de `4.5`, medir `VIF <= 5` solo en entrenamiento y verificar `Prueba / Entreno` para descartar sobreajuste.

3. **Si ampliás el uso de `GradientBoostingRegressor`:** considerar variables en tasas/variaciones o transformación logarítmica sobre series con tendencia fuerte (`Web Warehouse` o `Total empresa`), donde los niveles futuros superan al rango histórico de entrenamiento.

4. **Si evaluás horizontes `Mensual`, `Quarter` o `Anual` (`6.8`):** revisar la tabla de `IVE` trimestral por canal y el `CV (%)` por horizonte en `4.4` para distinguir qué parte del error responde a ruido semanal compensable y qué parte refleja cambio de escala entre años.
