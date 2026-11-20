# Guía de Reorganización del EDA (Bloque 4) y Puentes hacia la Sección 6

Documento de referencia operativa elaborado por **gera** (`20/11/2026`) sobre [`sales-revenue-jewery.ipynb`](../sales-revenue-jewery.ipynb).

Resume la reestructuración del **Bloque 4 (Análisis exploratorio)** en dos partes cronológicamente consistentes —**Parte I enfocada en el negocio (`4.1`–`4.4`)** y **Parte II centrada en propiedades estadísticas y temporales previas al modelado (`4.5`–`4.8`)**, sin incorporar métricas ni parámetros propios de la Sección 6 dentro del EDA— y explica fuera del EDA cómo esos hallazgos respaldan el diseño de los modelos en los **Bloques 5 y 6**.

---

## 1. Resumen de la Reorganización del Bloque 4

El Bloque 4 conserva `37` celdas dentro de un notebook de `110` celdas totales (`3,148,642` líneas y `$346,748,552.11 USD` en `2018–2025`, sin alterar `df`), separando primero el entendimiento comercial de la caracterización estadística de la serie semanal y manteniendo todo el diagnóstico agnóstico de una sucursal particular:

| Etapa | Sección | Qué analiza | Principio de diseño aplicado |
| :--- | :--- | :--- | :--- |
| **Base común** | **4.0 Base de análisis** | Define `2018–2025`, segmentos, `TIENDAS_FISICAS`, `tickets_venta`, `devoluciones_fin` y series semanales cerradas `W-SAT` (`Empresa`, `Tiendas físicas` y `Panel ubicación-semana`) | Prepara las vistas y series base una sola vez sin anticipar algoritmos futuros |
| **Parte I** (Negocio) | **4.1 Huella comercial y madurez de sedes** | Ventas netas acumuladas (`$237.6M` en `Web Warehouse` frente a `12` tiendas físicas), aperturas (`2018–2025`) y meses de historia observada | Ubica primero la comprensión de canales y la distinción entre `4` sedes maduras y `9` recientes |
| **Parte I** (Negocio) | **4.2 Productos, descuentos y rentabilidad** | Departamentos (`Jewelry`, `Home & Gifts`, `Beauty`), Pareto `80/20` y descuentos escalonados (`10%–50%`) | Muestra la mezcla comercial y define explícitamente `es_joyeria` en su propia celda |
| **Parte I** (Negocio) | **4.3 Comportamiento de las devoluciones** | Tasa por canal (`16.9%` tienda frente a `3.7%` web), efecto omnicanal (`42.6%`), pico de enero (`sem. 1–5`), rezagos y motivos | Explica el fenómeno comercial y su impacto contable en `net_sales` |
| **Parte I** (Negocio) | **4.4 Clientes y geografía de envíos** | Recurrencia (`CLIENTE_ANONIMO` excluido temporalmente) y concentración regional/`ZIP` en envíos web | Completa el diagnóstico del negocio antes de pasar al análisis estadístico |
| **Parte II** (Previo al modelado) | **4.5 Consistencia contable y calendario 4-5-4** | Cuadre contra cifras de control, correspondencia `retail_month`/`retail_quarter` y semana `53` de `2024` (`+$0.48M`) | Documenta por qué emparejar años por `retail_week` desfasa `371` frente a `364` días |
| **Parte II** (Previo al modelado) | **4.6 Distribución univariada semanal** | `boxplot` + histograma (`Total empresa` y `Tiendas físicas agregadas`) más tabla comparativa (`Web Warehouse` y `Panel ubicación-semana`) | Expone asimetría (`2.54` a `5.39`), cola navideña y mínimos negativos sin citar resultados de Bloque 6 |
| **Parte II** (Previo al modelado) | **4.7 Dinámica temporal multi-horizonte** | Serie mensual, semanas `1–53`, **`IVE` por Quarter (`Q1–Q4`)** por canal, serie desestacionalizada, dispersión anual, `CV %` (`2021–2025`), `ly_date_key` y `ACF/PACF` | Describe estacionalidad, heterocedasticidad multiplicativa y memoria serial sin referencias futuras |
| **Parte II** (Previo al modelado) | **4.8 Bivariado antecedentes y calendario** | *Lag plots* (`t-1` y `t-52` con `Tendencia lineal` y octiles), `barplot` por evento y `Quarter`, y correlaciones `Empresa` frente a `Mediana sedes maduras` | Analiza relación con rezagos conocidos antes de predecir, sin métricas ni hiperparámetros de Sección 6 |

---

## 2. Puentes hacia el Diseño Posterior del Modelado (Bloques 5 y 6)

Aunque el **Bloque 4** no incluye resultados ni métricas del Bloque 6, cada observación estadística de la **Parte II (`4.5`–`4.8`)** fundamenta las decisiones técnicas que se toman después al configurar `UBICACION_RL = 'Williamsburg'` en el Bloque 5 y evaluar los ensayos del Bloque 6:

### 2.1 Fundamento para modelos lineales (`OLS` en `6.1`–`6.5` y `6.8`)

1. **Indicadores de calendario frente a extremos estacionales (`4.6` y `4.8` $\rightarrow$ `6.1`–`6.2`):**

   * En `364` semanas del total empresa (`2019–2025`), el diagrama de dispersión entre `venta_neta` ($t$) y `t-1` sigue una trayectoria lineal clara en semanas normales (`Pearson = 0.814`, `Spearman = 0.888`, pendiente lineal `0.82`), mientras las `9` semanas de **`Previa Navidad`** (`media = $2,610,251 USD`) y `Black Friday` (`$1,993,580 USD`) saltan muy por encima de las `300` semanas normales (`$787,280 USD`) y las `27` semanas **`Post-evento`** caen por debajo.

   * Al llegar al Bloque 6, ese patrón explica por qué un modelo lineal base subestima campañas y sobreestima el inicio de enero, y por qué incorporar los `6` indicadores binarios de calendario reduce el error lineal (`MAE` `-20.27%` en `6.2` sobre la ubicación ejemplo).

2. **Construcción exacta de rezagos a `364` días (`4.5` $\rightarrow$ `Bloque 5` y `6.5`):**

   * Al comprobarse en `4.5` que `2024` contiene `53` semanas minoristas (`+$0.48M`), emparejar el año siguiente por `retail_week` introduce un corrimiento de `371` días.

   * En el Bloque 5 se opta por `shift(52)` (`364` días exactos), reduciendo el sesgo de la referencia anual en `6.5`.

3. **Selección por colinealidad (`4.8` $\rightarrow$ `6.3`–`6.4a`):**

   * La matriz de correlaciones bivariadas (`4.8`) muestra fuerte solapamiento entre `t-1` (`0.814`), `media_movil_4s` (`0.700`) y `t-2` (`0.699`) tanto a nivel empresa como en sedes maduras (`0.767`, `0.653` y `0.608`).

   * En la etapa de modelado, esa redundancia respalda aplicar una poda de multicolinealidad (`VIF`) sobre las medias móviles en `6.4a` para estabilizar los coeficientes.

### 2.2 Fundamento para árboles / `GradientBoostingRegressor` (`6.1`–`6.4b`)

1. **Asimetría, crecimiento y límites de extrapolación (`4.6` y `4.7`):**

   * La fuerte asimetría (`2.54` en empresa, `5.39` en el panel) y el crecimiento acumulado de escala (`$19.1M` en `2018` $\rightarrow$ `$72.5M` en `2025`) significan que las observaciones recientes alcanzan niveles nuevos fuera del rango de entrenamiento.

   * Como los ensambles de árboles promedian valores dentro de hojas finitas sin extrapolar tendencias, en el Bloque 6 presentan mayor brecha `Prueba / Entreno` que los modelos lineales cuando hay cambio de nivel.

2. **Baja frecuencia por evento anual (`4.8`):**

   * En siete años (`2019–2025`), cada campaña comercial aporta entre `7` y `9` observaciones (`Previa Navidad: 9`, `Cierre Navidad: 7`, `Black Friday: 7`, `Día de la Madre: 7`, `San Valentín: 7`).

   * Esa escasez muestral limita la capacidad de árboles poco profundos para aislar feriados puntuales frente a variables binarias aditivas.

### 2.3 Fundamento para Series Temporales, `Quarter` y Generalización (`6.4b`, `6.6`, `6.8`)

1. **Componentes autorregresivos y armónicos (`4.7` $\rightarrow$ `6.4b`):**

   * Las fuerzas de tendencia ($F_T = 0.664$) y estacionalidad ($F_S = 0.721$) junto con `ACF`/`PACF` (`t-1 = 0.823`, `t-2 = 0.681`, `t-4 = 0.405`, `t-52 = 0.720` / `PACF = 0.320`) justifican probar rezagos combinados con armónicos de Fourier en `6.4b`.

2. **Estacionalidad trimestral (`IVE`) y horizontes agregados (`4.7` $\rightarrow$ `6.8`):**

   * En `4.7`, `Q4` concentra un **`IVE = 1.461`** en la empresa (`1.587` en `Web Warehouse` frente a `1.225` en tiendas físicas), y el `CV (%)` desestacionalizado desciende de `23.39%` (semanal) a `21.52%` (*quarter*), mientras el total anual (`23.06%`) refleja el crecimiento de escala interanual.

   * Esto anticipa que al agregar predicciones de semanal a mensual y trimestral (`6.8`) se compensa el ruido semanal, mientras la precisión anual depende de capturar el nivel de tendencia vigente.

3. **Criterio objetivo de madurez para validación multi-ubicación (`4.1` y `4.8` $\rightarrow$ `6.6`):**

   * El diagnóstico de antigüedad de `4.1` delimita qué cuatro sedes acumulan `>= 100` semanas tras `t-52` (`Web Warehouse`, `Williamsburg`, `Wedding Annex`, `SOHO`), mientras el contraste de `4.8` en `t-52` (`r = 0.932` empresa frente a mediana `r = 0.332` en sedes maduras) explica por qué cada sucursal individual responde distinto al paso a generalización multi-ubicación (`6.6`).

---

## 3. Lista de Verificación Rápida para Experimentar en la Sección 6

1. **Antes de elegir o cambiar `UBICACION_RL` en el Bloque 5:** revisar en `4.1` que la sede cumpla `>= 100` semanas continuas tras `t-52` y verificar en `4.7`–`4.8` la amplitud estacional de su canal.

2. **Si probás nuevas variables en `6.1`–`6.4`:** validar su relación en `4.8`, medir `VIF` solo en entrenamiento y verificar `Prueba / Entreno` para descartar sobreajuste.

3. **Si ampliás el uso de `GradientBoostingRegressor`:** evaluar tasas de variación o transformación logarítmica sobre series con tendencia marcada (`Web Warehouse` o `Total empresa`).

4. **Si evaluás horizontes `Mensual`, `Quarter` o `Anual` (`6.8`):** revisar el `IVE` trimestral por canal y el `CV (%)` por horizonte en `4.7` para distinguir ruido compensable de cambios de nivel.
