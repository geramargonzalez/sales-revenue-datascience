# Estándares de Visualización para el Análisis Exploratorio (EDA)

Este documento especifica las convenciones gráficas y de estilo para la elaboración de visualizaciones con `matplotlib` y `seaborn` en el proyecto de ingresos por ventas.

---

## 1. Configuración Global de Estilo

Para asegurar coherencia visual en todos los gráficos del notebook:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de tipografía y temas
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'Helvetica', 'Arial', 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#EEEEEE'
plt.rcParams['grid.linestyle'] = '--'
```

---

## 2. Paleta Cromática Institucional

Evitar colores saturados por defecto. Utilizar una paleta sobria adecuada para análisis financiero y de retail:

| Uso / Significado | Código Hexadecimal | Nombre Descriptivo |
| :--- | :--- | :--- |
| Color Principal (Ingresos / Primario) | `#1E3A8A` | Azul Marino Profundo |
| Color Secundario (Canal Web / Secundario) | `#0284C7` | Azul Océano |
| Color Terciario (Costos / COGS) | `#D97706` | Ámbar / Dorado |
| Alertas / Pérdidas / Devoluciones | `#DC2626` | Rojo Carmesí |
| Margen / Rentabilidad Positiva | `#059669` | Verde Esmeralda |
| Tonos Neutros de Apoyo | `#64748B`, `#94A3B8` | Gris Pizarra |

---

## 3. Formateo de Ejes y Números

- **Montos Monetarios**: Formatear siempre con símbolo de dólar y separadores de miles (ej. `$1,250,000 USD` o `$1.25M`).
- **Porcentajes**: Formatear con uno o dos decimales seguidos de `%` (ej. `24.5%`).
- **Etiquetas de Ejes**: Incluir siempre unidades explícitas entre paréntesis (ej. `Ventas Netas (USD)`, `Unidades (Cantidad)`).
- **Rotación de Etiquetas**: En categorías con nombres extensos, rotar a 45 grados (`rotation=45, ha='right'`) para evitar superposiciones.

---

## 4. Estructura de Encabezados y Leyendas

- **Título**: Claro, directo y en español, ubicado a la izquierda (`loc='left'`) o centrado, con peso tipográfico destacado (`fontsize=13, fontweight='bold'`).
- **Subtítulo contextual**: Opcional, describiendo brevemente la conclusión o cobertura temporal (`fontsize=10, color='#555555'`).
- **Anotaciones**: Destacar valores extremos o promedios con etiquetas de datos (`ax.bar_label` o `annotate`) cuando aporte claridad analítica.
