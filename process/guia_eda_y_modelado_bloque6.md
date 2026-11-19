# Guía de Reorganización del EDA (Bloque 4) y Ayuda para el Modelado (Sección 6)

Documento de referencia operativa elaborado por **gera** (`19/11/2026`) sobre [`sales-revenue-jewery.ipynb`](../sales-revenue-jewery.ipynb).

Resume la reestructuración del **Bloque 4 (Análisis exploratorio)** y explica cómo cada bloque del nuevo EDA respalda directamente el entrenamiento, la selección de variables y la lectura de errores de los modelos en los **Bloques 5 y 6**.

---

## 1. Resumen de la Reorganización del Bloque 4

El Bloque 4 anterior acumulaba más de `30` gráficos orientados principalmente a *Business Intelligence* general (distribuciones por línea de ticket `line_id`, matrices de correlación entre importes contemporáneos, horarios web y contraste repetido de hipótesis).

Siguiendo la lógica del notebook de referencia de clase (`Hospital_LOS_Prediction_CLASE1.ipynb`) y las clases de series temporales (*Índice de Variación Estacional* `IVE`, desestacionalización y diagnóstico de variabilidad), el Bloque 4 quedó organizado en **dos partes explícitas** dentro de `107` celdas totales (`3,148,642` líneas y `$346,748,552.11 USD` en `2018–2025`, sin modificar `df`):

| Parte | Sección | Qué hace ahora | Cambio frente a la versión anterior |
| :--- | :--- | :--- | :--- |
| **Parte I** (Modelado) | **4.0 Base de análisis** | Define `2018–2025`, segmentos, `TIENDAS_FISICAS`, `tickets_venta` y series semanales `W-SAT` (`Empresa` y `Williamsburg`) | Incorpora directamente la serie semanal base usada como objetivo en los Bloques 5–6 |
| **Parte I** (Modelado) | **4.1 Control y calendario 4-5-4** | Cuadre anual contra cifras de control y correspondencia `retail_month` / `retail_quarter` | Retira el panel duplicado de hipótesis (`4.1.2`) y enfoca en la semana `53` de `2024` |
| **Parte I** (Modelado) | **4.2 Madurez de ubicaciones** | Ranking de ventas netas, historial observado en meses y tabla `ficha_tiendas` | Muestra gráficamente el umbral de `>= 100` semanas continuas tras `t-52` |
| **Parte I** (Modelado) | **4.3 Univariado del objetivo (`venta_neta`)** | `boxplot` + histograma con media y mediana sobre la serie semanal real (`Williamsburg` y `Empresa`) | Reemplaza las `10` distribuciones por línea de ticket (`cogs`, `margin`, `discount_total`) |
| **Parte I** (Modelado) | **4.4 Dinámica temporal multi-horizonte** | Serie mensual, estacionalidad `1–53`, **`IVE` por Quarter (`Q1–Q4`)**, serie desestacionalizada, dispersión anual, `CV %` por horizonte, `ly_date_key` y `ACF/PACF` | Incorpora el análisis explícito por **Quarter (`Q1–Q4`)**, variabilidad y compensación `Semana -> Mes -> Quarter -> Año`, y retira `hour` |
| **Parte I** (Modelado) | **4.5 Bivariado `X -> y`** | *Lag plots* (`t-1` y `t-52` con recta `OLS`, octiles y color por campaña), `barplot` por evento y `Quarter`, y correlación con antecedentes reales | Reemplaza los `8` heatmaps por línea (`gross_sales`, `cogs`, `margin`) por cruces directos entre predictores y `venta_neta` |
| **Parte II** (Negocio) | **4.6 Devoluciones** | Balance por canal, pico post-navideño (`sem. 1–5`), rezago, motivos y clase | Se conserva íntegro como contexto comercial |
| **Parte II** (Negocio) | **4.7 Producto y rentabilidad** | Departamentos, subclases, márgenes, Pareto `80/20` y descuentos | Se conserva íntegro como contexto comercial |
| **Parte II** (Negocio) | **4.8 Clientes y geografía** | Recurrencia (`CLIENTE_ANONIMO` excluido temporalmente) y mapas web (`ZIP`) | Se conserva íntegro como contexto comercial |

---

## 2. Cómo Ayuda el Nuevo EDA a Entrenar e Interpretar los Modelos de la Sección 6

Cada hallazgo cuantificado en la **Parte I (`4.0`–`4.5`)** responde una decisión de entrenamiento de **`Regresión lineal (OLS)`**, **`GradientBoostingRegressor`** y **Series Temporales** en la **Sección 6**:

### 2.1 Ayuda directa a `Regresión lineal (OLS)` (`6.1`, `6.2`, `6.4a`, `6.5`, `6.8`)

1. **Justificación visual de las variables de calendario (`4.5` $\rightarrow$ `6.1` y `6.2`):**
   * En semanas normales, el *lag plot* entre `venta_neta` ($t$) y `venta_semana_anterior` ($t-1$) muestra una relación lineal limpia (`r = 0.773`, `Spearman = 0.771`, pendiente `OLS = 0.78`, alineada con la mediana por octiles).
   * Sin embargo, las `9` semanas de **`Previa Navidad`** (`media = $161,205 USD` frente a `$74,914 USD` en semana normal) se disparan por encima de la recta, y las `26` semanas **`Post-evento`** caen por debajo al arrastrar el `t-1` del pico.
   * **Impacto práctico al entrenar:** explica por qué `OLS Base` (`6.1`) comete su mayor error en `20/12/2025` (`-$86,861 USD`) y `04/01/2025` (`+$48,069 USD`), y por qué sumar los `6` indicadores binarios (`6.2`) reduce el `MAE` lineal en **`-20.27%`** (`$13,308.92` $\rightarrow$ `$10,611.67 USD`).

2. **Por qué `shift(52)` = `364` días es obligatorio (`4.1` $\rightarrow$ `6.5`):**
   * La tabla de control (`4.1`) demuestra que `2024` tuvo **`53` semanas minoristas** (`+$0.48M`).
   * Si en el entrenamiento anual se empareja por `retail_week`, todo `2025` queda corrido `371` días; al fijar `venta_hace_52_semanas` (`364` días exactos), la referencia anual reduce su `MAE` un **`-14.1%`** y `OLS` mejora un **`-1.5%`** (`6.5`).

3. **Por qué la poda `VIF <= 5` estabiliza los coeficientes sin `Ridge` (`4.5` $\rightarrow$ `6.3` y `6.4a`):**
   * La tabla bivariada confirma que `t-1` (`0.773`), `media_movil_4s` (`0.701`) y `t-2` (`0.601`) están fuertemente correlacionados con `venta_neta` y entre sí.
   * **Regla para entrenar:** agregar medias móviles redundantes (`6.3`) invierte signos en `OLS` (`venta_hace_2_semanas = -0.219`, `es_cierre_navidad = +$22,501`), mientras podar `media_movil_4s`, `12s` y `8s` por `VIF > 5.0` (`6.4a`) deja `11` variables con `VIF <= 3.47` y un ajuste limpio (`MAE = $10,492.45 USD`, `R² = 0.65`).

### 2.2 Ayuda directa a `GradientBoostingRegressor` (`6.1`–`6.4b`, `6.6`)

1. **Límite de extrapolación y cambio de nivel (`4.3` y `4.4` $\rightarrow$ Sesgo y sobreajuste):**
   * En `4.3` (`Williamsburg`: media `$78,793 USD`, máximo `$289,352 USD`) y `4.4`, se observa que `Williamsburg` alcanzó su nivel medio más alto en `2022–2023` (`~$100k–$105k/sem.`) y moderó su promedio en `2024–2025` (`~$79.5k` $\rightarrow$ `$70.8k/sem.`), mientras el total de la empresa creció casi `4x` (`$19.1M` $\rightarrow$ `$72.5M`).
   * **Impacto práctico al entrenar:** los árboles de `GradientBoostingRegressor` promedian las observaciones en hojas finitas y no extrapolan tendencias lineales ni escalas nuevas; eso explica su razón **`Prueba / Entreno` de `1.21x` a `1.41x`** (frente a `0.80x–0.93x` de `OLS`) y su mayor `MAE` en `Williamsburg` (`$12,635.63 USD` vs. `$10,611.67 USD`).

2. **Pocas muestras por evento anual (`4.5` $\rightarrow$ `max_depth=2`):**
   * En `344` semanas continuas, cada feriado aparece solo entre **`6` y `9` veces** (`Previa Navidad: 9`, `Cierre Navidad: 7`, `Black Friday: 7`, `San Valentín: 7`, `Día de la Madre: 6`).
   * **Regla para entrenar:** con `min_samples_leaf=5` y `max_depth=2`, `Boosting` casi no aprovecha indicadores binarios poco frecuentes (`es_black_friday` recibe `0.00%` de importancia en el Ensayo 3) y pierde precisión al sumar variables continuas colineales (`17.15%` en `6.2` $\rightarrow$ `18.34%` en `6.4a` $\rightarrow$ `17.76%` en `6.4b`).

### 2.3 Ayuda directa a Series Temporales, `Quarter` y Generalización (`6.4b`, `6.6`, `6.8`)

1. **Justificación estadística de rezagos y Fourier (`4.4` $\rightarrow$ `6.4b`):**
   * Las fuerzas de tendencia ($F_T = 0.664$) y estacionalidad ($F_S = 0.721$) junto con `ACF/PACF` (`t-1 = 0.823`, `t-2 = 0.681`, `t-4 = 0.405`, `t-52 = 0.720` / `PACF = 0.320`) respaldan la combinación de rezagos autorregresivos más los `4` armónicos de Fourier en **`OLS Reducido + Fourier`** (`MAE = $10,488.87 USD` / `14.23%`, `R² = 0.66`).

2. **Estacionalidad por `Quarter` (`IVE`) y compensación por horizonte (`4.4` $\rightarrow$ `6.8`):**
   * A nivel compañía, `Q4` concentra un **`IVE = 1.461`** (`38.69%` del año) frente a **`IVE = 0.776`** en `Q1` (`17.26%`); en `Williamsburg`, `Q4` marca `IVE = 1.215` frente a `0.851` en `Q1`.
   * Al desestacionalizar y agregar horizontes en `Williamsburg` (`2021–2025`), la dispersión relativa cae de **`28.76%` (semanal)** a **`27.62%` (mensual)**, **`25.47%` (*quarter*)** y **`23.13%` (anual)**, explicando por qué en la proyección ciega de `2025` (`6.8`) el error de `OLS + Fourier` desciende de **`17.21%` (semanal)** a **`9.75%` (mensual)**, **`7.46%` (trimestral)** y **`+0.60%` (anual)**.

3. **Criterio de madurez para validación multi-ubicación (`4.2` $\rightarrow$ `6.6`):**
   * La ficha de cobertura (`4.2`) muestra qué ubicaciones poseen al menos `>= 100` semanas continuas tras `t-52`: únicamente **`Web Warehouse` (`96` meses)**, **`Williamsburg` (`96`)**, **`Wedding Annex` (`96`)** y **`SOHO` (`74`)**, explicando por qué las `9` tiendas recientes (`2` a `30` meses) quedan fuera del corte `6.6` hasta acumular más historia anual.

---

## 3. Lista de Verificación Rápida al Experimentar en la Sección 6

1. **Antes de cambiar `UBICACION_RL`:** revisar en `4.2` que la tienda tenga al menos `>= 100` semanas continuas tras `t-52` y observar en `4.4` si su tendencia reciente crece (`Web Warehouse`) o se estabiliza (`Williamsburg`).

2. **Si probás nuevas variables en `6.1`–`6.4`:** validar siempre su relación en el *lag plot* de `4.5`, medir `VIF <= 5` solo en entrenamiento y verificar `Prueba / Entreno` para descartar sobreajuste.

3. **Si ampliás el uso de `GradientBoostingRegressor`:** considerar variables en tasas/variaciones o transformación logarítmica sobre series con tendencia fuerte (`Web Warehouse` / `Total empresa`), donde los niveles futuros superan al rango histórico de entrenamiento.

4. **Si evaluás horizontes `Mensual`, `Quarter` o `Anual` (`6.8`):** revisar la tabla de `IVE` trimestral y el `CV (%)` por horizonte en `4.4` para distinguir qué parte del error responde a volatilidad semanal compensable y qué parte refleja cambio real de tendencia.
