# Reporte sobre la estructura de AGENTS.md y las habilidades

Fecha: 23/10/2026 · Autor: gera.

`AGENTS.md` establece las reglas transversales del proyecto y las habilidades describen procedimientos especializados que se consultan cuando la tarea los necesita.

En este repositorio, la habilidad disponible abarca el análisis exploratorio completo: validación del dataset, estadísticas descriptivas, comparación de canales, estacionalidad, correlaciones y conclusiones de negocio.

Las visualizaciones constituyen una parte de esa habilidad; sus detalles de presentación están concentrados en `references/visualization_standards.md`.

| Documento | Responsabilidad actual | Momento de consulta |
| :--- | :--- | :--- |
| [AGENTS.md](../AGENTS.md) | Entorno, Git, reglas de notebooks, protección contable y criterios de finalización. | Al trabajar en el repositorio. |
| [SKILL.md de EDA](../skills/exploratory-data-analysis/SKILL.md) | Secuencia de trabajo y criterios específicos del análisis exploratorio. | Al explorar datos, inspeccionar distribuciones o generar gráficos estadísticos. |
| [Estándares de visualización](../skills/exploratory-data-analysis/references/visualization_standards.md) | Tipografía, paleta, formatos monetarios, ejes, títulos y anotaciones. | Al crear o ajustar gráficos. |
| [Guía del calendario](../skills/exploratory-data-analysis/references/retail_calendar_guide.md) | Contexto de las variables temporales y de la estacionalidad. | Al interpretar o comparar períodos minoristas, considerando la discrepancia documentada. |
| [ideas.md](ideas.md) | Hipótesis y preguntas de negocio que orientan la exploración. | Al elegir preguntas analíticas; las hipótesis requieren validación. |
| [process.md](process.md) | Trabajo realizado, incidencias, decisiones y pendientes. | Para recuperar contexto y registrar resultados. |

La distribución actual de archivos expresa esas responsabilidades:

```text
AGENTS.md                              Reglas generales del proyecto
skills/
└── exploratory-data-analysis/
    ├── SKILL.md                        Procedimiento de análisis exploratorio
    └── references/
        ├── visualization_standards.md  Presentación de gráficos
        └── retail_calendar_guide.md    Contexto temporal del análisis
process/
├── ideas.md                            Hipótesis por investigar
└── process.md                          Historial y pendientes
```

Por ejemplo, para comparar ventas mensuales por canal, `AGENTS.md` establece las restricciones sobre el dataset y las convenciones del notebook.

La habilidad EDA orienta la selección de variables, las comparaciones y la explicación de resultados.

La referencia del calendario ayuda a interpretar los períodos y la referencia visual define cómo presentar importes, colores y etiquetas.

Finalmente, `process.md` registra el alcance, las comprobaciones y los hallazgos de la tarea.

La consolidación realizada en la Fase 14 sigue esta organización: la sección 1 de la habilidad remite a las secciones 3 y 4 de `AGENTS.md`, evitando mantener copias de las reglas generales.

Esa referencia específica no reduce el alcance del resto de `AGENTS.md`: las instrucciones de entorno, Git y registro de progreso siguen siendo aplicables al proyecto.

Para mantener la estructura, conviene ubicar cada contenido según su alcance:

- Una regla que afecta cualquier intervención pertenece a `AGENTS.md`.

- Una secuencia de análisis con condiciones de aplicación y resultados esperados pertenece a un `SKILL.md`.

- Los detalles técnicos extensos que respaldan ese procedimiento pertenecen a `references/`.

- Los hallazgos de una ejecución y los asuntos pendientes pertenecen a `process/`.

La estructura actual resulta suficiente para la habilidad EDA existente.

Si se documentan procedimientos recurrentes de modelado o validación de datos, pueden incorporarse como habilidades adicionales con sus propias referencias y un enlace a las reglas generales.

Una habilidad independiente de visualización sería útil si sus procedimientos se reutilizaran en varios contextos, como EDA, evaluación de modelos e informes; por ahora, mantenerla como referencia de EDA es coherente con la organización existente.

Queda una cuestión de contenido separada de esta estructura: `process.md` registra que la guía del calendario describe un inicio en febrero mientras que el dataset utiliza un inicio en enero.

El reporte conserva ese asunto como pendiente y no valida nuevamente el calendario ni las afirmaciones sectoriales de la guía.

Este documento describe el estado revisado y propone criterios de mantenimiento; no añade reglas operativas ni modifica el análisis, los datos o los documentos normativos.
