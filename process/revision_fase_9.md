# Fase 9: Revisión de código y propuestas de mejora

Autor: **gera**; fecha: **21/10/2026**.

## Alcance y referencias

Se revisaron `git diff main...HEAD` y los cambios locales de `git diff`, con `main` en `bf51b024ec757b7becda213d3d94d4d61b89c7b0` y `HEAD` en `24b4d63` al iniciar la revisión.

Los commits incluidos fueron `f26e432` (Fase 7, robustez del preprocesamiento y comparabilidad temporal) y `24b4d63` (Fase 8, textos y organización del notebook).

Se tomó esta referencia por defecto al no recibirse una selección alternativa durante la revisión.

La habilidad `mattpocock-skills:code-review` se aplicó mediante revisiones independientes de estándares y requisitos.

Los estándares consultados fueron `AGENTS.md`, la habilidad local de EDA y sus referencias de visualización y calendario; también se consultaron `README.md`, `process.md` e `ideas.md`.

No se identificó una incidencia original ni un gestor de incidencias configurado para la habilidad; los requisitos se contrastaron con las fases 7 y 8 de `process.md` y las reglas del repositorio, como especificación aproximada.

Para vincular futuras revisiones con incidencias, configurar la habilidad mediante `/setup-matt-pocock-skills`.

## Estándares

1. **P2 — Incumplimiento del entorno declarado, solo en el cambio local.** Los metadatos de `sales-revenue-jewery.ipynb`, líneas 6176 a 6191, seleccionan `python3` / `Python 3` y declaran Python 3.9.6.

   `AGENTS.md`, sección 1, requiere Python 3.11 en `.venv` y el kernel `sales-revenue-env`; la selección genérica puede resolver a otro entorno según la instalación.

   Propuesta: seleccionar el kernel del proyecto y guardar sus metadatos tras ejecutar; `HEAD` ya conserva la configuración correcta.

2. **Posible código duplicado — juicio de diseño.** Las validaciones del conteo de nulos se repiten en las celdas `e1b6d29c`, `eda_vistas_code` y `eda_control_final`, alrededor de las líneas 2233, 2490 y 6165.

   Propuesta: definir una función común dentro de una celda existente y llamarla en los tres puntos, manteniendo las comprobaciones intermedias y la estructura del notebook.

   Reutilizar el resumen de nulos por columna cuando ya está calculado también evita repetir recorridos innecesarios del dataset.

Se conservaron los tipos, identificadores y orden de las 72 celdas; no se observaron nuevas importaciones fuera de la celda inicial ni exclusiones adicionales de clientes anónimos.

## Requisitos

1. **P2 — Regresión local de reproducibilidad.** El mismo cambio de metadatos contradice el requisito registrado en la Fase 7 de `process.md`: «Los metadatos del notebook vuelven a declarar Python 3.11.16 y el kernel `sales-revenue-env`».

   Restaurar la selección del kernel satisface tanto el estándar como este requisito; se trata de un único problema observado en ambos ejes.

No se encontraron otros incumplimientos verificables en los cambios revisados: los rezagos originales se conservan, el recorte se aplica en vistas auxiliares, los acumulados comparten el corte semanal y el modelado permanece explícitamente pendiente.

**Mejora preventiva:** reemplazar la comprobación de preservación basada solo en máximo y cantidad de nulos por una comparación de la serie original completa con `pd.testing.assert_series_equal`, capturando una copia antes del tratamiento.

Cambios en valores intermedios o en la ubicación de los nulos pueden pasar los controles actuales; no se observó esa alteración en esta revisión.

**Mejora preventiva de carga:** validar que `line_id` no tenga nulos ni duplicados y que las columnas requeridas existan antes de transformar los datos; informar los registros problemáticos sin eliminarlos automáticamente.

Este control se propone como mejora adicional, no como regresión introducida por las fases revisadas.

## Verificación

Se ejecutaron las **38 celdas de código**, en orden, mediante un kernel nuevo `sales-revenue-env` con Python 3.11.16 de `.venv`, sin errores y sin guardar salidas en el notebook.

El control final confirmó **2,435,854 filas**, **37 columnas**, **2,239,455 nulos conservados en `return_lag_days`** y **$287,699,163.91 USD** de ventas netas.

Las semanas 1 a 38 de 2026 contienen siete fechas cada una; la semana 39 contiene tres y queda fuera de los acumulados comparables.

La sintaxis y la estructura de las 72 celdas se verificaron frente a `main`, `HEAD` y el árbol de trabajo.

La ejecución valida el código bajo el kernel del proyecto; no demuestra que el kernel genérico seleccionado en los metadatos locales resuelva al mismo intérprete.

## Próximos pasos

Revisar las propuestas de selección del kernel, centralización de validaciones, igualdad completa del rezago y contrato de carga antes de implementarlas.

La intervención registra la revisión; no aplica modificaciones al notebook ni al dataset.

Estándares: **2 hallazgos**, con el kernel como principal; requisitos: **1 hallazgo**, también el kernel local.
