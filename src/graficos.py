"""Funciones de visualización estandarizadas para limpieza, EDA y modelado."""

from typing import Any

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import seaborn as sns

from .config import (
    ANIOS_COMPLETOS,
    COLOR_ALERTA,
    COLOR_COSTO,
    COLOR_MARGEN,
    COLOR_NEUTRO,
    COLOR_NEUTRO_CLARO,
    COLOR_PRIMARIO,
    COLOR_WEB,
    DIAS_ES,
    ETIQUETAS_VARIABLES,
    MESES_ES,
    TONOS_ANIO,
    fmt_dolares,
    fmt_millones,
    fmt_porcentaje,
)


def _anotar_barras_horizontales(ax: Any, barras: Any, formato: str = "{:.1f}%") -> None:
    """Agrega etiquetas numéricas al final de barras horizontales si el ancho es positivo."""
    for p in barras.patches:
        ancho = p.get_width()
        if ancho > 0:
            ax.annotate(
                formato.format(ancho),
                (ancho + 1, p.get_y() + p.get_height() / 2),
                va="center",
                fontsize=9,
                color="#1f2937",
            )


def graficar_nulos_y_condicionales(df_nulos: pd.DataFrame, df_condicional: pd.DataFrame) -> None:
    """Visualiza el ranking de nulos por columna y los nulos condicionales por canal/tipo."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    sns.barplot(
        data=df_nulos.reset_index(), x="Porcentaje (%)", y="index",
        ax=axes[0], hue="index", palette="mako", legend=False,
    )
    axes[0].set_title("Valores faltantes por variable", fontsize=13, fontweight="bold", pad=10)
    axes[0].set_xlabel("Líneas con dato faltante (%)", fontsize=11)
    axes[0].set_ylabel("Variable", fontsize=11)
    axes[0].set_yticks(range(len(df_nulos)), [ETIQUETAS_VARIABLES.get(c, c) for c in df_nulos.index])
    axes[0].set_xlim(0, 115)
    _anotar_barras_horizontales(axes[0], axes[0])

    sns.barplot(
        data=df_condicional, x="% Nulos", y="Segmento Evaluado",
        hue="Variable", ax=axes[1], palette="Set2",
    )
    axes[1].set_title("Datos faltantes según canal y tipo de línea", fontsize=13, fontweight="bold", pad=10)
    axes[1].set_xlabel("Líneas con dato faltante (%)", fontsize=11)
    axes[1].set_ylabel("Segmento analizado", fontsize=11)
    axes[1].set_xlim(0, 115)
    leyenda = axes[1].legend(title="Variable", loc="upper right")
    for texto in leyenda.get_texts():
        texto.set_text(ETIQUETAS_VARIABLES.get(texto.get_text(), texto.get_text()))
    _anotar_barras_horizontales(axes[1], axes[1])

    plt.tight_layout()
    plt.show()


def graficar_contraste_hipotesis(control: pd.DataFrame, resumen_hip: dict[str, Any]) -> None:
    """Dibuja el panel 2x2 de contraste frente a las cifras y referencias del negocio."""
    cuota_web_anual = resumen_hip["cuota_web_anual"]
    tasa_mensual = resumen_hip["tasa_mensual"]
    tasa_tienda = resumen_hip["tasa_tienda"]

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))

    ax = axes[0, 0]
    anios = control.index.astype(str)
    posiciones = np.arange(len(anios))
    barras = ax.bar(posiciones, control["Año calendario (M USD)"], color=COLOR_PRIMARIO, width=0.6, label="Observado (año calendario)")
    ax.scatter(posiciones, control["Referencia (M USD)"], color=COLOR_COSTO, marker="D", s=70, zorder=3, label="Referencia contable")
    ax.bar_label(barras, labels=[f"${v:.1f}M" for v in control["Año calendario (M USD)"]], padding=4, fontsize=9)
    ax.set_xticks(posiciones, anios)
    ax.set_ylim(0, control["Año calendario (M USD)"].max() * 1.15)
    ax.set_title("Ventas netas anuales frente a las cifras de control", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Año calendario (2018-2025)")
    ax.set_ylabel("Ventas netas (millones de USD)")
    ax.legend(loc="upper left")

    ax = axes[0, 1]
    barras = ax.bar(cuota_web_anual.index.astype(str), cuota_web_anual.values, color=COLOR_WEB, width=0.6)
    ax.bar_label(barras, fmt="%.1f%%", padding=4, fontsize=9)
    ax.axhline(62, color=COLOR_NEUTRO, linestyle="--", linewidth=1.2, label="Referencia (62%)")
    ax.set_ylim(0, 108)
    ax.yaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Participación del canal web en la venta neta", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Año calendario (2018-2025)")
    ax.set_ylabel("Participación del canal web (%)")
    ax.legend(loc="upper right")

    ax = axes[1, 0]
    for anio in tasa_mensual.columns:
        serie = tasa_mensual[anio].dropna()
        ax.plot(serie.index, serie.values, marker="o", markersize=3.5, linewidth=1.8, color=TONOS_ANIO[anio], label=str(anio))
    ax.axhline(10, color=COLOR_NEUTRO, linestyle="--", linewidth=1.2, label="Referencia anual (10%)")
    ax.set_xticks(range(1, 13), MESES_ES)
    ax.set_ylim(0, tasa_mensual.max().max() * 1.15)
    ax.yaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Tasa de devolución por mes: enero concentra el pico", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Mes calendario")
    ax.set_ylabel("Devoluciones sobre venta bruta (%)")
    ax.legend(ncol=3, loc="upper center", fontsize=9)

    ax = axes[1, 1]
    destacadas = {"Williamsburg": COLOR_ALERTA, "BOSTON Newbury": COLOR_MARGEN}
    colores = [destacadas.get(u, COLOR_NEUTRO_CLARO) for u in tasa_tienda.index]
    barras = ax.barh(tasa_tienda.index, tasa_tienda.values, color=colores)
    ax.bar_label(barras, fmt="%.1f%%", padding=4, fontsize=9)
    ax.set_xlim(0, tasa_tienda.max() * 1.15)
    ax.xaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Tasa de devolución por ubicación donde se procesa", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Devoluciones sobre venta bruta (%)")
    ax.set_ylabel("Ubicación operativa")
    ax.grid(axis="y", visible=False)

    plt.tight_layout()
    plt.show()


def graficar_distribuciones_financieras(ventas_fin: pd.DataFrame, muestra_ventas: pd.DataFrame) -> None:
    """Dibuja histogramas KDE logarítmicos, boxplots y distribución discreta de cantidades."""
    paneles = [
        ("gross_sales", "Ventas brutas (USD)", COLOR_PRIMARIO),
        ("net_sales", "Ventas netas (USD)", COLOR_PRIMARIO),
        ("cogs", "Costo de mercancía (USD)", COLOR_COSTO),
        ("margin", "Margen registrado (USD)", COLOR_MARGEN),
        ("discount_total", "Descuento total (USD)", COLOR_ALERTA),
    ]
    fig = plt.figure(figsize=(17, 11))
    rejilla = fig.add_gridspec(2, 3, hspace=0.32, wspace=0.22)

    for i, (columna, etiqueta, color) in enumerate(paneles):
        celda = rejilla[i // 3, i % 3].subgridspec(2, 1, height_ratios=[5, 1], hspace=0.06)
        ax_hist = fig.add_subplot(celda[0])
        ax_caja = fig.add_subplot(celda[1], sharex=ax_hist)

        positivos = muestra_ventas.loc[muestra_ventas[columna] > 0, columna]
        pct_no_pos = (ventas_fin[columna] <= 0).mean() * 100
        mediana = ventas_fin.loc[ventas_fin[columna] > 0, columna].median()

        sns.histplot(x=positivos, bins=60, log_scale=True, kde=True, color=color, edgecolor="white", linewidth=0.3, ax=ax_hist)
        ax_hist.axvline(mediana, color="#1f2937", linestyle="--", linewidth=1.2)
        ax_hist.annotate(
            f"Mediana: ${mediana:,.0f}", (mediana, 0.93), xycoords=("data", "axes fraction"),
            xytext=(-6, 0), textcoords="offset points", ha="right", fontsize=9,
        )
        ax_hist.set_title(etiqueta, loc="left", fontsize=13, fontweight="bold")
        ax_hist.set_xlabel("")
        ax_hist.set_ylabel("Líneas de venta (muestra)")
        ax_hist.text(
            0.98, 0.93, f"{pct_no_pos:.1f}% de las líneas\ncon valor ≤ 0 (excluidas)",
            transform=ax_hist.transAxes, ha="right", va="top", fontsize=9, color="#555555",
        )
        ax_hist.xaxis.set_major_formatter(fmt_dolares)
        ax_hist.tick_params(axis="x", which="both", labelbottom=False)

        ax_caja.boxplot(
            positivos, vert=False, whis=(1, 99), showfliers=False, widths=0.5, patch_artist=True,
            boxprops={"facecolor": color, "alpha": 0.6}, medianprops={"color": "#1f2937"},
        )
        ax_caja.tick_params(axis="x", which="minor", labelbottom=False)
        ax_caja.set_xlabel(f"{etiqueta}, escala logarítmica (bigotes: p1 a p99)")
        ax_caja.set_yticks([])

    ax_qty = fig.add_subplot(rejilla[1, 2])
    tramos_qty = pd.cut(ventas_fin["qty"], bins=[0, 1, 2, 3, 4, np.inf], labels=["1 o menos", "2", "3", "4", "5 o más"])
    pct_qty = tramos_qty.value_counts(normalize=True).sort_index() * 100
    barras = ax_qty.bar(pct_qty.index.astype(str), pct_qty.values, color=COLOR_WEB)
    ax_qty.bar_label(barras, labels=[f"{v:.2f}%" for v in pct_qty.values], padding=3, fontsize=9)
    ax_qty.set_yscale("log")
    ax_qty.set_ylim(top=400)
    ax_qty.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:g}%"))
    ax_qty.tick_params(axis="y", which="minor", labelleft=False)
    ax_qty.set_title("Distribución de cantidades positivas", loc="left", fontsize=13, fontweight="bold")
    ax_qty.set_xlabel("Unidades por línea de venta")
    ax_qty.set_ylabel("Líneas con cantidad positiva (%), escala logarítmica")

    fig.suptitle("Distribución de las métricas financieras por línea de venta", x=0.125, ha="left", fontsize=15, fontweight="bold", y=0.95)
    plt.show()


def graficar_importe_ventas_vs_devoluciones(
    df_eda: pd.DataFrame, ventas_fin: pd.DataFrame, devoluciones_fin: pd.DataFrame, muestra_ventas: pd.DataFrame
) -> None:
    """Compara densidades logarítmicas de ventas vs devoluciones y muestra el boxplot lineal completo."""
    importe_venta = muestra_ventas.loc[muestra_ventas["net_sales"] > 0, "net_sales"]
    importe_devuelto = -devoluciones_fin.loc[devoluciones_fin["net_sales"] < 0, "net_sales"]
    serie_net_completa = df_eda["net_sales"].dropna()

    fig, axes = plt.subplots(1, 2, figsize=(17, 5.2), gridspec_kw={"width_ratios": [1.05, 1.0]})

    ax = axes[0]
    sns.kdeplot(x=importe_venta, log_scale=True, fill=True, alpha=0.25, linewidth=2, color=COLOR_PRIMARIO, label="Líneas de venta", ax=ax)
    sns.kdeplot(x=importe_devuelto, log_scale=True, fill=True, alpha=0.25, linewidth=2, color=COLOR_ALERTA, label="Líneas de devolución", ax=ax)
    for serie, color, desp in [
        (ventas_fin.loc[ventas_fin["net_sales"] > 0, "net_sales"], COLOR_PRIMARIO, -8),
        (importe_devuelto, COLOR_ALERTA, 8),
    ]:
        ax.axvline(serie.median(), color=color, linestyle="--", linewidth=1.2)
        ax.annotate(
            f"Mediana: ${serie.median():,.0f}", (serie.median(), 0.94), xycoords=("data", "axes fraction"),
            xytext=(desp, 0), textcoords="offset points", ha="right" if desp < 0 else "left", fontsize=9, color=color,
        )
    ax.set_xlim(5, 5000)
    ax.xaxis.set_major_formatter(fmt_dolares)
    ax.tick_params(axis="x", which="minor", labelbottom=False)
    ax.set_title("Importe por línea: ventas y devoluciones", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Importe neto por línea en valor absoluto (USD), escala logarítmica")
    ax.set_ylabel("Densidad")
    ax.legend(loc="upper right", bbox_to_anchor=(1, 0.88))

    ax_box = axes[1]
    ax_box.boxplot(
        serie_net_completa, orientation="horizontal", widths=0.30, patch_artist=True,
        boxprops=dict(facecolor=COLOR_NEUTRO_CLARO, edgecolor=COLOR_PRIMARIO, alpha=0.55, linewidth=1.2),
        medianprops=dict(color=COLOR_ALERTA, linewidth=2.0),
        whiskerprops=dict(color=COLOR_PRIMARIO, linewidth=1.2),
        capprops=dict(color=COLOR_PRIMARIO, linewidth=1.2),
        flierprops=dict(marker="o", markerfacecolor="none", markeredgecolor=COLOR_PRIMARIO, markersize=4.5, alpha=0.55),
    )
    q25, med, q75 = serie_net_completa.quantile([0.25, 0.50, 0.75])
    min_n, max_n = serie_net_completa.min(), serie_net_completa.max()
    ax_box.axvline(0, color=COLOR_NEUTRO, linestyle=":", linewidth=1.0)
    ax_box.annotate(f"Mínimo (devolución):\n-${abs(min_n):,.0f} USD", (min_n, 1), xytext=(0, 32), textcoords="offset points", ha="left", fontsize=9, color=COLOR_ALERTA)
    ax_box.annotate(f"Caja intercuartílica (p25-p75): {q25:,.0f} a {q75:,.0f} USD\nMediana global: {med:,.0f} USD", (med, 1), xytext=(18, -38), textcoords="offset points", ha="left", fontsize=9, color=COLOR_PRIMARIO)
    ax_box.annotate(f"Máximo (venta):\n${max_n:,.0f} USD", (max_n, 1), xytext=(0, 32), textcoords="offset points", ha="right", fontsize=9, color=COLOR_PRIMARIO)
    ax_box.xaxis.set_major_formatter(fmt_dolares)
    ax_box.set_yticks([1], ["net_sales"])
    ax_box.set_title("Boxplot de ventas netas en escala completa (valores extremos)", loc="left", fontsize=13, fontweight="bold")
    ax_box.set_xlabel("Ventas netas por línea (USD), escala lineal completa")
    ax_box.grid(axis="y", visible=False)

    plt.tight_layout()
    plt.show()


def graficar_participaciones_categoricas(paneles_categoricos: list[tuple[str, pd.DataFrame]]) -> None:
    """Dibuja los 6 gráficos horizontales de participación en líneas vs venta neta."""
    fig, axes = plt.subplots(2, 3, figsize=(19, 13), gridspec_kw={"height_ratios": [2.6, 1]})
    alto = 0.38
    for ax, (titulo, tabla) in zip(axes.flat, paneles_categoricos):
        y = np.arange(len(tabla))
        b_lin = ax.barh(y - alto / 2, tabla["% de líneas"], height=alto, color=COLOR_NEUTRO_CLARO, label="% de líneas")
        b_ven = ax.barh(y + alto / 2, tabla["% de venta neta"], height=alto, color=COLOR_PRIMARIO, label="% de venta neta")
        ax.bar_label(b_lin, fmt="%.1f%%", padding=3, fontsize=8, color="#555555")
        ax.bar_label(b_ven, fmt="%.1f%%", padding=3, fontsize=8)
        ax.set_yticks(y, tabla.index)
        ax.set_ylabel("")
        ax.invert_yaxis()
        ax.set_xlim(min(0, tabla.min().min() * 1.6), tabla.max().max() * 1.18)
        ax.axvline(0, color="#CCCCCC", linewidth=0.8)
        ax.xaxis.set_major_formatter(fmt_porcentaje)
        ax.set_title(titulo, loc="left", fontsize=13, fontweight="bold")
        ax.set_xlabel("Participación (%)")
        ax.grid(axis="y", visible=False)
        ax.legend(loc="lower right")
    plt.tight_layout()
    plt.show()


def graficar_matrices_correlacion(matrices: list[tuple[pd.DataFrame, str]]) -> None:
    """Dibuja el panel 2x2 de mapas de calor de correlación."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 13))
    for ax, (matriz, titulo) in zip(axes.flat, matrices):
        sns.heatmap(
            matriz.rename(index=ETIQUETAS_VARIABLES, columns=ETIQUETAS_VARIABLES),
            annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, center=0, square=True,
            linewidths=0.5, linecolor="white", annot_kws={"fontsize": 9},
            cbar_kws={"shrink": 0.8, "label": "Coeficiente de correlación"}, ax=ax,
        )
        ax.set_title(titulo, loc="left", fontsize=13, fontweight="bold")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_xlabel("")
        ax.set_ylabel("")
    plt.tight_layout()
    plt.show()


def graficar_serie_mensual(serie_mensual: pd.DataFrame) -> None:
    """Grafica ventas netas y líneas de venta mensuales con franjas de nov-dic."""
    fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
    paneles = [
        ("venta_neta", "Ventas netas por mes (2018-2025)", "Ventas netas (USD)", COLOR_PRIMARIO, fmt_millones),
        ("lineas_venta", "Líneas de venta por mes (2018-2025)", "Número de líneas de venta", COLOR_NEUTRO,
         FuncFormatter(lambda x, _: f"{x / 1e3:,.0f} mil")),
    ]
    for ax, (col, titulo, etiq, color, formato) in zip(axes, paneles):
        ax.plot(serie_mensual.index, serie_mensual[col], marker="o", markersize=3.0, linewidth=1.8, color=color)
        for anio in serie_mensual.index.year.unique():
            ax.axvspan(pd.Timestamp(anio, 11, 1), pd.Timestamp(anio, 12, 31), color=COLOR_COSTO, alpha=0.10, linewidth=0)
        ax.set_xlim(serie_mensual.index.min() - pd.Timedelta(days=20), serie_mensual.index.max() + pd.Timedelta(days=20))
        ax.set_ylim(0, serie_mensual[col].max() * 1.12)
        ax.yaxis.set_major_formatter(formato)
        ax.set_title(titulo, loc="left", fontsize=13, fontweight="bold")
        ax.set_ylabel(etiq)
    axes[0].text(0.995, 0.93, "Franjas sombreadas: noviembre y diciembre", transform=axes[0].transAxes, ha="right", fontsize=9, color="#555555")
    axes[1].set_xlabel("Mes calendario (2018-2025)")
    plt.tight_layout()
    plt.show()


def graficar_estacionalidad_mensual(cuota_mensual: pd.DataFrame, cascada: pd.DataFrame) -> None:
    """Dibuja la participación mensual por año y la cascada venta bruta -> venta neta."""
    fig, axes = plt.subplots(1, 2, figsize=(17, 6))
    ax = axes[0]
    for anio in ANIOS_COMPLETOS:
        ax.plot(range(1, 13), cuota_mensual[anio], marker="o", markersize=3.5, linewidth=1.8, color=TONOS_ANIO[anio], label=str(anio))
    ax.axhline(100 / 12, color=COLOR_COSTO, linestyle="--", linewidth=1.2, label="Reparto uniforme (8.3%)")
    ax.set_xticks(range(1, 13), MESES_ES)
    ax.set_ylim(0, cuota_mensual.max().max() * 1.12)
    ax.yaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Participación de cada mes en la venta neta anual", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Mes calendario")
    ax.set_ylabel("Participación en el año (%)")
    ax.legend(ncol=3, loc="upper left", fontsize=9)

    ax = axes[1]
    ax.plot(range(1, 13), cascada["venta_bruta"], marker="o", markersize=4, linewidth=2, color=COLOR_NEUTRO, label="Venta bruta")
    ax.plot(range(1, 13), cascada["tras_descuentos"], marker="o", markersize=4, linewidth=2, color=COLOR_WEB, label="Tras descuentos")
    ax.plot(range(1, 13), cascada["venta_neta"], marker="o", markersize=4, linewidth=2, color=COLOR_PRIMARIO, label="Venta neta (tras devoluciones)")
    ax.fill_between(range(1, 13), cascada["venta_neta"], cascada["tras_descuentos"], color=COLOR_ALERTA, alpha=0.18, label="Devoluciones")
    ax.set_xticks(range(1, 13), MESES_ES)
    ax.set_ylim(0, cascada["venta_bruta"].max() * 1.12)
    ax.yaxis.set_major_formatter(fmt_millones)
    ax.set_title("De la venta bruta a la neta: promedio mensual 2018-2025", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Mes calendario")
    ax.set_ylabel("Importe mensual promedio (USD)")
    ax.legend(loc="upper left")

    plt.tight_layout()
    plt.show()


def graficar_patron_dia_hora(cuota_dia: pd.DataFrame, cuota_hora: pd.DataFrame) -> None:
    """Dibuja el patrón semanal y horario separado por canal."""
    colores_canal = {"Canal web": COLOR_WEB, "Tienda física": COLOR_PRIMARIO}
    fig, axes = plt.subplots(1, 2, figsize=(17, 6))

    ax = axes[0]
    posiciones = np.arange(7)
    for i, canal_nom in enumerate(["Tienda física", "Canal web"]):
        barras = ax.bar(posiciones + (i - 0.5) * 0.4, cuota_dia[canal_nom], width=0.4, color=colores_canal[canal_nom], label=canal_nom)
        ax.bar_label(barras, fmt="%.1f%%", padding=2, fontsize=9)
    ax.set_xticks(posiciones, DIAS_ES)
    ax.set_ylim(0, cuota_dia.max().max() * 1.15)
    ax.yaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Importe de líneas de venta por día registrado", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Día de la semana")
    ax.set_ylabel("Importe de ventas sin devoluciones del canal (%)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left")

    ax = axes[1]
    for canal_nom in ["Tienda física", "Canal web"]:
        ax.plot(cuota_hora.index, cuota_hora[canal_nom], marker="o", markersize=4, linewidth=2, color=colores_canal[canal_nom], label=canal_nom)
    ax.set_xticks(range(0, 24, 2))
    ax.set_ylim(0, cuota_hora.max().max() * 1.12)
    ax.yaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Líneas de venta por hora registrada", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Hora registrada (0 a 23, hora local)")
    ax.set_ylabel("Participación en las líneas del canal (%)")
    ax.legend(loc="upper left")

    plt.tight_layout()
    plt.show()


def graficar_ventas_semana_minorista(venta_semanal: pd.DataFrame) -> None:
    """Dibuja las ventas netas por semana minorista 4-5-4 entre 2018 y 2025."""
    fig, ax = plt.subplots(figsize=(16, 6.5))
    ax.axvspan(39.5, 53.5, color=COLOR_COSTO, alpha=0.10, linewidth=0)
    for anio in ANIOS_COMPLETOS:
        serie = venta_semanal[anio].dropna()
        ax.plot(serie.index, serie.values, linewidth=2.2 if anio == 2025 else 1.5, color=TONOS_ANIO[anio], label=str(anio))
    semana_pico = venta_semanal[2025].idxmax()
    ax.annotate(
        f"Semana {semana_pico} de 2025: ${venta_semanal[2025].max() / 1e6:.1f}M",
        (semana_pico, venta_semanal[2025].max()), xytext=(-12, 0), textcoords="offset points", ha="right", va="center", fontsize=9,
    )
    ax.text(39.8, venta_semanal.max().max() * 1.06, "Cuarto trimestre minorista", fontsize=9, color=COLOR_COSTO, va="center")
    ax.set_xlim(1, 53)
    ax.set_ylim(0, venta_semanal.max().max() * 1.12)
    ax.set_xticks(range(1, 54, 4))
    ax.yaxis.set_major_formatter(fmt_millones)
    ax.set_title("Ventas netas por semana minorista y año (2018-2025)", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Semana minorista (calendario 4-5-4)")
    ax.set_ylabel("Ventas netas (USD)")
    ax.legend(title="Año minorista", ncol=4, loc="upper left")
    plt.tight_layout()
    plt.show()


def graficar_interanual_y_descomposicion(res: dict[str, Any]) -> None:
    """Dibuja evolución interanual y el panel 2x2 de descomposición temporal más ACF/PACF."""
    interanual = res["interanual"]
    venta_anual_cal = res["venta_anual_calendario"]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    barras = ax.bar(interanual.index.astype(str), venta_anual_cal / 1e6, color=[COLOR_NEUTRO_CLARO] * 7 + [COLOR_PRIMARIO], width=0.6)
    etiquetas = [
        f"${v / 1e6:.2f}M" if pd.isna(c) else f"${v / 1e6:.2f}M\n({c:+.1f}%)"
        for v, c in zip(venta_anual_cal, interanual["Variación calendario (%)"])
    ]
    ax.bar_label(barras, labels=etiquetas, padding=4, fontsize=9)
    ax.set_ylim(0, venta_anual_cal.max() / 1e6 * 1.2)
    ax.set_title("Evolución interanual de las ventas netas (2018-2025)", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Año calendario")
    ax.set_ylabel("Ventas netas (millones de USD)")
    ax.grid(axis="x", visible=False)
    plt.tight_layout()
    plt.show()

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    ax = axes[0, 0]
    ax.plot(res["serie_semanal_ts"].index, res["serie_semanal_ts"], color=COLOR_NEUTRO_CLARO, linewidth=1.2, label="Serie semanal observada")
    ax.plot(res["tendencia_ts"].index, res["tendencia_ts"], color=COLOR_PRIMARIO, linewidth=2.4, label="Tendencia (media móvil 52 sem.)")
    ax.yaxis.set_major_formatter(fmt_millones)
    ax.set_title(f"Descomposición semanal: serie y tendencia (F_T = {res['fuerza_tendencia']:.2f})", loc="left", fontsize=12, fontweight="bold")
    ax.set_xlabel("Sábado de cierre semanal (2018-2025)")
    ax.set_ylabel("Ventas netas (USD)")
    ax.legend(loc="upper left")

    ax = axes[0, 1]
    ax.plot(res["estacional_ts"].index, res["estacional_ts"], color=COLOR_WEB, linewidth=1.3, label="Componente estacional (52 sem.)")
    ax.plot(res["residuo_ts"].index, res["residuo_ts"], color=COLOR_ALERTA, linewidth=0.9, alpha=0.65, label="Residuo")
    ax.axhline(0, color="#555555", linestyle="--", linewidth=0.9)
    ax.yaxis.set_major_formatter(fmt_millones)
    ax.set_title(f"Componente estacional y residuo (F_S = {res['fuerza_estacional']:.2f})", loc="left", fontsize=12, fontweight="bold")
    ax.set_xlabel("Sábado de cierre semanal (2018-2025)")
    ax.set_ylabel("Desviación frente a tendencia (USD)")
    ax.legend(loc="upper left")

    rezagos_eje = np.arange(1, res["max_rezago_acf"] + 1)
    umbral_ic = res["umbral_ic_95"]
    for ax, vals_c, tit_c in [
        (axes[1, 0], res["acf_vals"][1:], "Función de Autocorrelación (ACF) semanal (rezagos 1 a 56)"),
        (axes[1, 1], res["pacf_vals"][1:], "Función de Autocorrelación Parcial (PACF) semanal (rezagos 1 a 56)"),
    ]:
        colores_b = [COLOR_ALERTA if r in (1, 4, 52) else COLOR_PRIMARIO for r in rezagos_eje]
        ax.bar(rezagos_eje, vals_c, width=0.65, color=colores_b, alpha=0.88)
        ax.axhline(umbral_ic, color=COLOR_COSTO, linestyle="--", linewidth=1.1, label=f"IC 95% (±{umbral_ic:.2f})")
        ax.axhline(-umbral_ic, color=COLOR_COSTO, linestyle="--", linewidth=1.1)
        ax.axhline(0, color="#333333", linewidth=0.8)
        ax.set_xlim(0, res["max_rezago_acf"] + 1)
        ax.set_xticks([1, 4, 13, 26, 39, 52])
        ax.set_title(tit_c, loc="left", fontsize=12, fontweight="bold")
        ax.set_xlabel("Rezago en semanas (en rojo: t-1, t-4 y t-52)")
        ax.set_ylabel("Correlación")
        ax.legend(loc="upper right")

    plt.tight_layout()
    plt.show()


def graficar_desempeno_tiendas_fisicas(res_canales: dict[str, Any]) -> None:
    """Dibuja ventas netas, ticket promedio y ventas por estado de tiendas físicas."""
    venta_tienda = res_canales["venta_tienda"]
    ticket_tienda = res_canales["ticket_tienda"]
    venta_estado = res_canales["venta_estado"]
    tiendas_estado = res_canales["tiendas_estado"]

    fig, axes = plt.subplots(1, 3, figsize=(19, 6.5), gridspec_kw={"width_ratios": [1.2, 1.2, 0.9]})

    ax = axes[0]
    barras = ax.barh(venta_tienda.index, venta_tienda.values, color=COLOR_PRIMARIO)
    ax.bar_label(barras, labels=[f"${v / 1e6:.1f}M" for v in venta_tienda.values], padding=4, fontsize=9)
    ax.set_xlim(0, venta_tienda.max() * 1.15)
    ax.xaxis.set_major_formatter(fmt_millones)
    ax.set_title("Ventas netas por tienda física", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Ventas netas acumuladas 2018-2025 (USD)")
    ax.grid(axis="y", visible=False)

    ax = axes[1]
    colores_t = [COLOR_COSTO if "Wedding Annex" in u else COLOR_MARGEN for u in ticket_tienda.index]
    barras = ax.barh(ticket_tienda.index, ticket_tienda.values, color=colores_t)
    ax.bar_label(barras, labels=[f"${v:,.0f}" for v in ticket_tienda.values], padding=4, fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(100, ticket_tienda.max() * 1.6)
    ax.xaxis.set_major_formatter(fmt_dolares)
    ax.tick_params(axis="x", which="minor", labelbottom=False)
    ax.set_title("Ticket promedio por tienda física", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Ticket promedio (USD), escala logarítmica")
    ax.grid(axis="y", visible=False)

    ax = axes[2]
    barras = ax.barh(venta_estado.index, venta_estado.values, color=COLOR_NEUTRO)
    ax.bar_label(
        barras,
        labels=[
            f"${v / 1e6:.1f}M ({tiendas_estado[e]} tiendas)" if tiendas_estado[e] > 1 else f"${v / 1e6:.1f}M (1 tienda)"
            for e, v in venta_estado.items()
        ],
        padding=4, fontsize=9,
    )
    ax.set_xlim(0, venta_estado.max() * 1.45)
    ax.xaxis.set_major_formatter(fmt_millones)
    ax.set_title("Ventas netas por estado", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Ventas netas de tiendas físicas (USD)")
    ax.set_ylabel("Estado")
    ax.grid(axis="y", visible=False)

    plt.tight_layout()
    plt.show()


def graficar_estacionalidad_y_tienda_devoluciones(res_dev: dict[str, Any]) -> None:
    """Dibuja la curva semanal de devoluciones (semanas 1-52) y la tasa apilada por tienda."""
    sem_dev = res_dev["sem_dev"]
    por_tienda = res_dev["por_tienda_dev"]
    tasa_enero_imp = res_dev["tasa_enero_imp"]
    tasa_resto_imp = res_dev["tasa_resto_imp"]
    tasa_enero_lin = res_dev["tasa_enero_lin"]
    tasa_resto_lin = res_dev["tasa_resto_lin"]

    fig, axes = plt.subplots(1, 2, figsize=(17, 5.6), gridspec_kw={"width_ratios": [1.05, 1.05]})

    ax = axes[0]
    ax.axvspan(1, 5, color=COLOR_ALERTA, alpha=0.12, label="Pico post-navideño (semanas 1 a 5: enero)")
    ax.plot(sem_dev.index, sem_dev["tasa_importe"], color=COLOR_ALERTA, marker="o", markersize=4, linewidth=2.0, label="Tasa en importe (% de venta bruta)")
    ax.plot(sem_dev.index, sem_dev["tasa_lineas"], color=COLOR_PRIMARIO, marker="s", markersize=3.5, linewidth=1.8, linestyle="--", label="Proporción de líneas devueltas (%)")
    ax.axhline(tasa_resto_imp, color=COLOR_NEUTRO, linestyle=":", linewidth=1.2, label=f"Promedio semanas 6-52 en importe ({tasa_resto_imp:.1f}%)")
    ax.annotate(
        f"Semana 1: {sem_dev.loc[1, 'tasa_importe']:.1f}% en importe\n({sem_dev.loc[1, 'tasa_lineas']:.1f}% de las líneas)",
        (1, sem_dev.loc[1, "tasa_importe"]), xytext=(14, -4), textcoords="offset points", ha="left", va="top", fontsize=9, color=COLOR_ALERTA, fontweight="bold",
    )
    ax.annotate(
        f"Promedio semanas 1-5 (enero):\n{tasa_enero_imp:.1f}% en importe ({tasa_enero_lin:.1f}% de líneas)\nfrente a {tasa_resto_imp:.1f}% ({tasa_resto_lin:.1f}%) en semanas 6-52",
        (3, tasa_enero_imp), xytext=(8.5, 15.2), arrowprops=dict(arrowstyle="->", color=COLOR_PRIMARIO, lw=1.0),
        ha="left", va="center", fontsize=9, color=COLOR_PRIMARIO,
    )
    ax.set_xlim(0.5, 52.5)
    ax.set_ylim(0, sem_dev["tasa_importe"].max() * 1.16)
    ax.yaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Estacionalidad semanal de las devoluciones (semanas 1 a 52)", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Semana minorista (calendario 4-5-4, acumulado 2018-2025)")
    ax.set_ylabel("Tasa de devolución (%)")
    ax.legend(loc="upper right", frameon=True)

    ax = axes[1]
    ax.barh(por_tienda.index, por_tienda["tasa_tienda"], color=COLOR_ALERTA, label="Compra original en tienda física")
    b_web = ax.barh(por_tienda.index, por_tienda["tasa_web"], left=por_tienda["tasa_tienda"], color=COLOR_WEB, label="Compra original en canal web")
    etiq_t = [f"{tot:.1f}% ({pw:.0f}% web)" for tot, pw in zip(por_tienda["tasa_total"], por_tienda["pct_origen_web"])]
    ax.bar_label(b_web, labels=etiq_t, padding=4, fontsize=9)
    ax.set_xlim(0, por_tienda["tasa_total"].max() * 1.26)
    ax.xaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Tasa de devolución en importe por tienda física y origen", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Devoluciones procesadas en tienda sobre su venta bruta (%)")
    ax.set_ylabel("Tienda física operativa (venta bruta >= $1M)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", frameon=True)

    plt.tight_layout()
    plt.show()


def graficar_perfil_devoluciones(res_dev: dict[str, Any]) -> None:
    """Dibuja el panel 2x2 de rezago, motivos, tasa por clase y rango de importe."""
    rezago = res_dev["rezago_analisis"]
    motivos = res_dev["motivos"]
    tasa_clase = res_dev["tasa_clase"]
    tasa_rango = res_dev["tasa_rango"]
    tasa_rango_canal = res_dev["tasa_rango_canal"]

    fig, axes = plt.subplots(2, 2, figsize=(17, 12))

    ax = axes[0, 0]
    conteo_rez = rezago.round().astype(int).value_counts().reindex(range(0, 91), fill_value=0)
    colores_rez = [COLOR_NEUTRO if d in (0, 90) else COLOR_ALERTA for d in conteo_rez.index]
    ax.bar(conteo_rez.index, conteo_rez.values / len(rezago) * 100, color=colores_rez, width=1.0)
    for dia, texto in [(0, "Día 0: cero explícito"), (90, "90 días o más\n(vista analítica)")]:
        pct = conteo_rez[dia] / len(rezago) * 100
        ax.annotate(
            f"{pct:.1f}%\n{texto}", (dia, pct),
            xytext=(14 if dia == 0 else -14, -6), textcoords="offset points",
            ha="left" if dia == 0 else "right", va="top", fontsize=9,
        )
    ax.set_xlim(-2, 92)
    ax.yaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Días entre la venta y la devolución", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Rezago de la devolución (días)")
    ax.set_ylabel("Devoluciones con rezago informado (%)")

    ax = axes[0, 1]
    barras = ax.barh(motivos.index, motivos.values, color=COLOR_ALERTA)
    ax.bar_label(barras, fmt="%.1f%%", padding=4, fontsize=9)
    ax.set_xlim(0, motivos.max() * 1.15)
    ax.xaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Motivos de devolución agrupados", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Líneas de devolución (%)")
    ax.grid(axis="y", visible=False)

    ax = axes[1, 0]
    barras = ax.barh(tasa_clase.index, tasa_clase.values, color=COLOR_ALERTA)
    ax.bar_label(barras, fmt="%.1f%%", padding=4, fontsize=9)
    ax.axvline(res_dev["tasa_global"], color=COLOR_NEUTRO, linestyle="--", linewidth=1.2, label="Tasa global")
    ax.set_xlim(0, tasa_clase.max() * 1.15)
    ax.xaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Tasa de devolución en importe por clase de joyería", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Devoluciones sobre venta bruta (%)")
    ax.set_ylabel("Clase de joyería (venta bruta de al menos $1M)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right")

    ax = axes[1, 1]
    pos_r = np.arange(len(tasa_rango))
    b_t = ax.bar(pos_r - 0.2, tasa_rango_canal["Tienda física"], width=0.38, color=COLOR_ALERTA, label="Procesada en tienda física")
    b_w = ax.bar(pos_r + 0.2, tasa_rango_canal["Canal web"], width=0.38, color=COLOR_WEB, label="Procesada en canal web")
    ax.plot(pos_r, tasa_rango.values, color=COLOR_PRIMARIO, marker="o", markersize=5, linewidth=1.8, linestyle="--", label="Total del tramo")
    ax.bar_label(b_t, fmt="%.1f%%", padding=3, fontsize=9)
    ax.bar_label(b_w, fmt="%.1f%%", padding=3, fontsize=9)
    ax.set_xticks(pos_r, tasa_rango.index.astype(str))
    ax.set_ylim(0, tasa_rango_canal["Tienda física"].max() * 1.18)
    ax.yaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Proporción de líneas devueltas según importe y canal", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Importe de la línea en valor absoluto (USD)")
    ax.set_ylabel("Líneas que son devolución (%)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", frameon=True)

    plt.tight_layout()
    plt.show()


def graficar_productos_y_descuentos(res_prod: dict[str, Any]) -> None:
    """Dibuja el panel 2x2 de subclases/clases/marcas/descuentos y la dispersión de descuento."""
    venta_sub = res_prod["venta_subclase"]
    margen_clase = res_prod["margen_clase"]
    margen_marca = res_prod["margen_marca"]
    margen_marca_pct = res_prod["margen_marca_pct"]
    por_tramo = res_prod["por_tramo"]
    muestra_desc = res_prod["muestra_desc"]

    fig, axes = plt.subplots(2, 2, figsize=(17, 13))

    ax = axes[0, 0]
    barras = ax.barh(venta_sub.index, venta_sub.values, color=COLOR_PRIMARIO)
    ax.bar_label(barras, labels=[f"${v / 1e6:.1f}M" for v in venta_sub.values], padding=4, fontsize=9)
    ax.set_xlim(0, venta_sub.max() * 1.15)
    ax.xaxis.set_major_formatter(fmt_millones)
    ax.set_title(f"Ventas netas por subclase (12 principales: {res_prod['peso_top12_subclase']:.1f}% del total)", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Ventas netas (USD)")
    ax.grid(axis="y", visible=False)

    ax = axes[0, 1]
    barras = ax.barh(margen_clase.index, margen_clase.values, color=COLOR_MARGEN)
    ax.bar_label(barras, fmt="%.1f%%", padding=4, fontsize=9)
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title(f"Margen por clase de joyería (7 líderes: {res_prod['peso_top7_clase']:.1f}% de joyería)", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Margen sobre venta neta, líneas con costo (%)")
    ax.grid(axis="y", visible=False)

    ax = axes[1, 0]
    barras = ax.barh(margen_marca.index, margen_marca.values, color=COLOR_MARGEN)
    ax.bar_label(
        barras,
        labels=[f"${v / 1e6:.1f}M ({p:.0f}% en ventas con costo)" for v, p in zip(margen_marca.values, margen_marca_pct.values)],
        padding=4, fontsize=9,
    )
    ax.set_xscale("log")
    ax.set_xlim(margen_marca.min() * 0.7, margen_marca.max() * 6)
    ax.xaxis.set_major_formatter(fmt_millones)
    ax.tick_params(axis="x", which="minor", labelbottom=False)
    ax.set_title(f"Margen registrado por marca (12 principales: {res_prod['peso_top12_marca']:.1f}% del margen)", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Margen registrado (USD), escala logarítmica")
    ax.grid(axis="y", visible=False)

    ax = axes[1, 1]
    posiciones = np.arange(len(por_tramo))
    b1 = ax.bar(posiciones - 0.2, por_tramo["% de líneas"], width=0.4, color=COLOR_NEUTRO_CLARO, label="% de líneas de venta")
    b2 = ax.bar(posiciones + 0.2, por_tramo["% de venta neta"], width=0.4, color=COLOR_PRIMARIO, label="% de venta neta")
    ax.bar_label(b1, fmt="%.1f%%", padding=3, fontsize=9, color="#555555")
    ax.bar_label(b2, fmt="%.1f%%", padding=3, fontsize=9)
    ax.plot(posiciones, por_tramo["Margen (%)"], marker="D", markersize=7, linewidth=2, color=COLOR_MARGEN, label="Margen en ventas con costo (%)")
    for x, m in zip(posiciones, por_tramo["Margen (%)"]):
        ax.annotate(f"{m:.0f}%", (x, m), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9, color=COLOR_MARGEN)
    ax.set_xticks(posiciones, por_tramo.index.astype(str))
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Profundidad de descuento: peso y margen de cada tramo", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Descuento sobre la venta bruta de la línea")
    ax.set_ylabel("Participación o margen (%)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.show()

    fig_desc, ax_desc = plt.subplots(figsize=(11.5, 5.2))
    ax_desc.scatter(muestra_desc["gross_sales"], muestra_desc["discount_total"], alpha=0.30, s=22, color=COLOR_PRIMARIO, edgecolors="none", label="Muestra de líneas de venta (n = 5,000)")
    for pct_ref, x_fin in [(10, 4500), (15, 3600), (20, 3900), (30, 2650), (50, 1450)]:
        x_vals = np.array([0, x_fin])
        y_vals = x_vals * (pct_ref / 100.0)
        ax_desc.plot(x_vals, y_vals, color=COLOR_NEUTRO, linestyle="--", linewidth=0.9, alpha=0.65)
        ax_desc.annotate(f"{pct_ref}%", (x_fin, y_vals[1]), xytext=(4, 2), textcoords="offset points", fontsize=9, color=COLOR_NEUTRO, fontweight="bold")
    ax_desc.annotate(
        "Base sin descuento ($0 USD):\n68.2% de las líneas de venta", (2400, 0), xytext=(2400, 130),
        arrowprops=dict(arrowstyle="->", color=COLOR_ALERTA, lw=1.0), fontsize=9, color=COLOR_ALERTA, fontweight="bold",
    )
    ax_desc.xaxis.set_major_formatter(fmt_dolares)
    ax_desc.yaxis.set_major_formatter(fmt_dolares)
    ax_desc.set_title("Relación entre descuento total y venta bruta (muestra de líneas de venta)", loc="left", fontsize=13, fontweight="bold")
    ax_desc.set_xlabel("Venta bruta por línea (USD)")
    ax_desc.set_ylabel("Descuento total por línea (USD)")
    ax_desc.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    plt.show()


def graficar_clientes_y_geografia(res_cli: dict[str, Any]) -> None:
    """Dibuja recurrencia de clientes, mapa postal de EE. UU. y mapa NYC top 15 ZIP."""
    resumen_frec = res_cli["resumen_frecuencia"]
    cuota_region_dig = res_cli["cuota_region_dig"]
    top_zip = res_cli["top_zip"]

    fig, axes = plt.subplots(1, 3, figsize=(19, 6.5))

    ax = axes[0]
    posiciones = np.arange(len(resumen_frec))
    b1 = ax.bar(posiciones - 0.2, resumen_frec["% de clientes"], width=0.4, color=COLOR_NEUTRO_CLARO, label="% de clientes")
    b2 = ax.bar(posiciones + 0.2, resumen_frec["% de la venta"], width=0.4, color=COLOR_PRIMARIO, label="% del importe analizado")
    ax.bar_label(b1, fmt="%.1f%%", padding=3, fontsize=9, color="#555555")
    ax.bar_label(b2, fmt="%.1f%%", padding=3, fontsize=9)
    ax.set_xticks(posiciones, resumen_frec.index.astype(str))
    ax.set_ylim(0, resumen_frec[["% de clientes", "% de la venta"]].max().max() * 1.15)
    ax.yaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Clientes e importe de tickets sin devoluciones", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Tickets sin devoluciones por cliente identificado")
    ax.set_ylabel("Participación (%)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right")

    ax = axes[1]
    us_lon = [
        -124.7, -124.0, -122.5, -120.5, -117.1, -114.6, -111.0, -108.2, -106.5, -104.0, -101.0, -99.1, -97.1, -97.0,
        -94.0, -91.0, -89.0, -88.0, -85.0, -83.0, -82.5, -81.0, -80.1, -80.5, -81.4, -78.5, -75.5, -76.0, -74.0, -72.0,
        -70.0, -70.7, -67.0, -67.8, -70.0, -71.5, -73.4, -75.0, -76.3, -79.0, -82.4, -83.5, -84.8, -87.5, -87.8, -84.5,
        -88.0, -90.5, -92.0, -95.2, -104.0, -117.0, -122.8, -124.7,
    ]
    us_lat = [
        48.4, 43.0, 37.8, 34.5, 32.5, 32.7, 31.3, 31.3, 31.8, 29.0, 29.8, 26.4, 25.9, 27.8, 29.7, 29.1, 30.2, 30.2,
        29.7, 29.1, 27.5, 25.2, 25.8, 28.5, 30.7, 33.9, 35.2, 37.0, 39.0, 41.0, 41.7, 43.1, 44.8, 47.1, 46.5, 45.0,
        45.0, 44.8, 43.6, 42.9, 43.0, 42.3, 45.8, 41.8, 45.1, 46.5, 48.2, 48.0, 46.8, 49.0, 49.0, 49.0, 49.0, 48.4,
    ]
    ax.fill(us_lon, us_lat, facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.2, zorder=1)
    coords_region = {
        "0": (-71.2, 42.6, "0 · Noreste", 18, 16),
        "1": (-75.5, 41.8, "1 · NY, PA", -36, 26),
        "2": (-78.2, 36.8, "2 · Atl. medio", 22, -4),
        "3": (-83.2, 31.8, "3 · Sureste", 18, -16),
        "4": (-83.8, 40.3, "4 · Medio oeste E", -38, 14),
        "5": (-96.0, 45.5, "5 · Medio oeste N", 0, 16),
        "6": (-91.5, 39.0, "6 · Centro", -8, -22),
        "7": (-98.5, 32.2, "7 · Sur centro", 0, -22),
        "8": (-109.0, 39.2, "8 · Montaña", 0, 16),
        "9": (-120.2, 38.5, "9 · Pacífico", 18, -4),
    }
    for dig, pct in cuota_region_dig.items():
        lon, lat, etiq, dx, dy = coords_region[dig]
        es_p = dig in ("1", "9", "0")
        ax.scatter(lon, lat, s=pct * 42, color=COLOR_PRIMARIO if es_p else COLOR_WEB, alpha=0.82, edgecolors="white", linewidth=1.5, zorder=3)
        ax.annotate(
            f"{etiq}\n({pct:.1f}%)", xy=(lon, lat), xytext=(dx, dy), textcoords="offset points",
            ha="center", va="center", fontsize=9, fontweight="bold" if es_p else "normal",
            color="#1E293B", arrowprops=dict(arrowstyle="-", color="#94A3B8", lw=0.6),
            bbox=dict(boxstyle="round,pad=0.16", facecolor="white", edgecolor="none", alpha=0.82), zorder=4,
        )
    ax.set_xlim(-128, -62)
    ax.set_ylim(23.5, 51.5)
    ax.set_title("Importe web por región de envío (ZIP válido)", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Longitud (°O) · Burbujas según % del importe web")
    ax.set_ylabel("Latitud (°N)")

    ax = axes[2]
    manhattan_lon = [-74.018, -74.011, -73.978, -73.971, -73.942, -73.927, -73.910, -73.922, -73.934, -73.960, -73.993, -74.009, -74.018]
    manhattan_lat = [40.701, 40.705, 40.711, 40.742, 40.776, 40.808, 40.873, 40.878, 40.852, 40.810, 40.765, 40.725, 40.701]
    brooklyn_lon = [-74.042, -74.015, -74.000, -73.985, -73.968, -73.956, -73.938, -73.895, -73.885, -73.950, -74.035, -74.042]
    brooklyn_lat = [40.640, 40.675, 40.688, 40.703, 40.708, 40.738, 40.733, 40.710, 40.640, 40.610, 40.615, 40.640]
    ax.fill(manhattan_lon, manhattan_lat, facecolor="#F1F5F9", edgecolor="#94A3B8", linewidth=1.1, zorder=1)
    ax.fill(brooklyn_lon, brooklyn_lat, facecolor="#F8FAFC", edgecolor="#94A3B8", linewidth=1.1, zorder=1)
    ax.text(-73.952, 40.812, "MANHATTAN", fontsize=9, fontweight="bold", color="#64748B", ha="center")
    ax.text(-73.935, 40.642, "BROOKLYN", fontsize=9, fontweight="bold", color="#64748B", ha="center")
    coords_zip = {
        "10013": (-74.003, 40.720, "10013 SoHo", -50, -4),
        "11249": (-73.962, 40.716, "11249 Wburg.", -24, 24),
        "11215": (-73.982, 40.667, "11215 Park Slope", -8, -18),
        "11201": (-73.990, 40.694, "11201 Bklyn Hts.", -56, 4),
        "11238": (-73.963, 40.679, "11238 Prospect", 48, -12),
        "11222": (-73.951, 40.728, "11222 Greenpoint", 54, 14),
        "11211": (-73.951, 40.712, "11211", 42, 0),
        "11217": (-73.979, 40.682, "11217", -28, -12),
        "10024": (-73.975, 40.786, "10024", -44, 2),
        "11205": (-73.966, 40.694, "11205", 42, 2),
        "11231": (-74.002, 40.678, "11231", -44, 2),
        "10025": (-73.967, 40.798, "10025", -44, 6),
        "10023": (-73.982, 40.776, "10023", -44, -4),
        "10011": (-74.000, 40.742, "10011", -44, 2),
        "11216": (-73.949, 40.681, "11216", 42, -1),
    }
    for z, val in top_zip.items():
        lon, lat, nombre_z, dx, dy = coords_zip[z]
        es_top2 = z in ("10013", "11249")
        monto_z = f"${val / 1e6:.1f}M" if val >= 1e6 else f"${val / 1e3:,.0f}k"
        ax.scatter(lon, lat, s=(val / 1e6) * 165, color=COLOR_PRIMARIO if es_top2 else COLOR_WEB, alpha=0.82, edgecolors="white", linewidth=1.3, zorder=3)
        ax.annotate(
            f"{nombre_z} ({monto_z})", xy=(lon, lat), xytext=(dx, dy), textcoords="offset points",
            ha="center", va="center", fontsize=9, fontweight="bold" if es_top2 else "normal",
            color="#1E293B", arrowprops=dict(arrowstyle="-", color="#94A3B8", lw=0.6),
            bbox=dict(boxstyle="round,pad=0.14", facecolor="white", edgecolor="none", alpha=0.82), zorder=4,
        )
    ax.set_xlim(-74.075, -73.860)
    ax.set_ylim(40.625, 40.835)
    ax.xaxis.set_major_locator(plt.MultipleLocator(0.05))
    ax.set_title("Códigos postales con mayor importe web (NYC)", loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel("Longitud (°O) · Los 15 principales están en Nueva York")
    ax.set_ylabel("Latitud (°N)")

    plt.tight_layout()
    plt.show()


def graficar_panel_4_metricas(tabla_metricas: pd.DataFrame, titulo_panel: str) -> None:
    """Dibuja un panel horizontal 1x4 con MAE, RMSE, R² y Sesgo en prueba."""
    colores_modelos = {
        "Referencia: año anterior": COLOR_ALERTA,
        "Referencia: semana anterior": COLOR_NEUTRO,
        "Regresión lineal (OLS)": COLOR_PRIMARIO,
        "Regresión lineal (Base + Cal.)": COLOR_PRIMARIO,
        "Modelo Reducido (VIF <= 5)": COLOR_WEB,
        "OLS Reducido + Fourier": COLOR_MARGEN,
        "Boosting de árboles": COLOR_COSTO,
        "Referencia anual": COLOR_ALERTA,
    }
    cols_pal = [colores_modelos.get(m, COLOR_WEB) for m in tabla_metricas.index]
    fig, axes = plt.subplots(1, 4, figsize=(17, 3.8))
    espec_metricas = [
        ("MAE (USD)", "MAE semanal (USD)", fmt_dolares),
        ("RMSE (USD)", "RMSE semanal (USD)", fmt_dolares),
        ("R²", "R² en prueba", None),
        ("Sesgo (USD)", "Sesgo medio (USD)", fmt_dolares),
    ]
    for ax, (col_m, tit_m, fmt_m) in zip(axes, espec_metricas):
        vals = tabla_metricas[col_m]
        bars = ax.barh(tabla_metricas.index, vals.values, color=cols_pal)
        ax.invert_yaxis()
        ax.set_title(tit_m, loc="left", fontsize=11, fontweight="bold")
        ax.grid(axis="y", visible=False)
        ax.locator_params(axis="x", nbins=4)
        if fmt_m is not None:
            ax.xaxis.set_major_formatter(fmt_m)
        ax.tick_params(axis="both", labelsize=9)
        if col_m == "Sesgo (USD)":
            ax.axvline(0, color="#334155", linewidth=1.0)
            lim_abs = max(abs(vals.min()), abs(vals.max()), 500) * 1.40
            ax.set_xlim(-lim_abs, lim_abs)
            for b, v in zip(bars, vals.values):
                offset = lim_abs * 0.03 if v >= 0 else -lim_abs * 0.03
                ha = "left" if v >= 0 else "right"
                ax.text(v + offset, b.get_y() + b.get_height() / 2, f"{v:+,.0f}", va="center", ha=ha, fontsize=9)
        else:
            max_v = max(vals.max(), 0.1)
            min_v = min(0.0, vals.min() * 1.18)
            ax.set_xlim(min_v, max_v * 1.26)
            for b, v in zip(bars, vals.values):
                txt = f"${v:,.0f}" if "USD" in col_m else f"{v:.2f}"
                xpos = max(v, 0) + max_v * 0.025 if v >= 0 else v - max_v * 0.025
                ha = "left" if v >= 0 else "right"
                ax.text(xpos, b.get_y() + b.get_height() / 2, txt, va="center", ha=ha, fontsize=9)
    for ax in axes[1:]:
        ax.set_yticklabels([])
    fig.suptitle(titulo_panel, x=0.01, ha="left", fontsize=13, fontweight="bold", y=1.03)
    plt.tight_layout()
    plt.show()


def graficar_curva_e_importancia(
    pred_df: pd.DataFrame,
    cols_curva: list[str],
    imp_serie: pd.Series,
    titulo_curva: str,
    titulo_imp: str,
    xlabel_imp: str = "Importancia (%)",
) -> None:
    """Grafica Real vs. Predicho en prueba junto con la importancia o impacto de variables."""
    fig, axes = plt.subplots(1, 2, figsize=(17, 4.4), gridspec_kw={"width_ratios": [1.35, 1.0]})
    ax = axes[0]
    estilos = {
        "Venta real": {"color": "#0F172A", "lw": 2.1, "ls": "-"},
        "Regresión lineal (OLS)": {"color": COLOR_PRIMARIO, "lw": 1.8, "ls": "-"},
        "OLS Reducido + Fourier": {"color": COLOR_MARGEN, "lw": 1.8, "ls": "-"},
        "Boosting de árboles": {"color": COLOR_COSTO, "lw": 1.8, "ls": "--"},
        "Referencia: año anterior": {"color": COLOR_ALERTA, "lw": 1.4, "ls": ":"},
    }
    for col in cols_curva:
        est = estilos.get(col, {"color": COLOR_WEB, "lw": 1.5, "ls": "-"})
        ax.plot(pred_df.index, pred_df[col], label=col, color=est["color"], linewidth=est["lw"], linestyle=est["ls"])
    y_max_curva = float(pred_df[cols_curva].max().max())
    ax.set_ylim(top=y_max_curva * 1.18)
    ax.set_title(titulo_curva, loc="left", fontsize=12, fontweight="bold")
    ax.set_xlabel("Sábado de cierre de la semana", fontsize=10)
    ax.xaxis.set_major_formatter(DateFormatter("%m/%Y"))
    ax.set_ylabel("Ventas netas (USD)", fontsize=10)
    ax.yaxis.set_major_formatter(fmt_dolares)
    ax.legend(ncol=2, loc="upper left", fontsize=9, frameon=True)

    ax2 = axes[1]
    s_ord = imp_serie.sort_values()
    col_imp = [COLOR_ALERTA if v < 0 else COLOR_PRIMARIO for v in s_ord.values]
    bars = ax2.barh(s_ord.index, s_ord.values, color=col_imp)
    if (s_ord.values < 0).any():
        ax2.axvline(0, color="#334155", linewidth=1.0)
        span = max(abs(s_ord.min()), abs(s_ord.max()), 1.0)
        ax2.set_xlim(s_ord.min() - span * 0.28, s_ord.max() + span * 0.28)
    else:
        ax2.set_xlim(0, max(s_ord.max(), 1.0) * 1.24)
        ax2.xaxis.set_major_formatter(fmt_porcentaje)
    for b, v in zip(bars, s_ord.values):
        txt = f"{v:+.0f}" if (s_ord.values < 0).any() else f"{v:.1f}%"
        offset = (ax2.get_xlim()[1] - ax2.get_xlim()[0]) * 0.015
        xpos = v + offset if v >= 0 else v - offset
        ha = "left" if v >= 0 else "right"
        ax2.text(xpos, b.get_y() + b.get_height() / 2, txt, va="center", ha=ha, fontsize=9)
    ax2.set_title(titulo_imp, loc="left", fontsize=12, fontweight="bold")
    ax2.set_xlabel(xlabel_imp, fontsize=10)
    ax2.grid(axis="y", visible=False)
    plt.tight_layout()
    plt.show()


def graficar_evolucion_ensayos_y_sobreajuste(
    df_evolucion: pd.DataFrame, mae_ref_364_pct: float, orden_ensayos: list[str]
) -> None:
    """Dibuja la evolución de MAE (% media) por ensayo y el control de sobreajuste."""
    pivot_mae_pct = df_evolucion.pivot(index="Ensayo", columns="Modelo", values="MAE (% media)").reindex(orden_ensayos)
    fig, axes = plt.subplots(1, 2, figsize=(17, 4.8), gridspec_kw={"width_ratios": [1.25, 1.0]})

    ax = axes[0]
    ypos = np.arange(len(pivot_mae_pct))
    h_bar = 0.34
    ax.barh(ypos - h_bar / 2, pivot_mae_pct["Regresión lineal (OLS)"], height=h_bar, color=COLOR_PRIMARIO, label="Regresión lineal (OLS)")
    ax.barh(ypos + h_bar / 2, pivot_mae_pct["Boosting de árboles"], height=h_bar, color=COLOR_COSTO, label="Boosting de árboles")
    ax.axvline(mae_ref_364_pct, color=COLOR_ALERTA, linestyle="--", linewidth=1.2, label=f"Referencia año anterior ({mae_ref_364_pct:.1f}%)")
    for y_i, v_ols, v_gb in zip(ypos, pivot_mae_pct["Regresión lineal (OLS)"], pivot_mae_pct["Boosting de árboles"]):
        ax.text(v_ols + 0.3, y_i - h_bar / 2, f"{v_ols:.2f}%", va="center", fontsize=9, fontweight="bold", color=COLOR_PRIMARIO)
        ax.text(v_gb + 0.3, y_i + h_bar / 2, f"{v_gb:.2f}%", va="center", fontsize=9)
    ax.set_yticks(ypos, pivot_mae_pct.index)
    ax.invert_yaxis()
    ax.set_xlim(0, 29)
    ax.xaxis.set_major_formatter(fmt_porcentaje)
    ax.set_title("Evolución del MAE (% media) a través de todos los ensayos", loc="left", fontsize=12, fontweight="bold")
    ax.set_xlabel("MAE semanal en prueba (% sobre la venta media)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=9, frameon=True)

    ax2 = axes[1]
    sub_ov = df_evolucion[df_evolucion["Ensayo"].isin([
        "1. Base (t-1 y t-52)", "2. Base + Calendario", "4a. Reducido (VIF <= 5)", "4b. Reducido + Fourier"
    ])].copy()
    etiq_cortas = {"Regresión lineal (OLS)": "OLS", "Boosting de árboles": "Boosting"}
    etiq_ov = [f"{r['Ensayo'].split('.')[0]} | {etiq_cortas.get(r['Modelo'], r['Modelo'])}" for _, r in sub_ov.iterrows()]
    yp2 = np.arange(len(sub_ov))
    ax2.barh(yp2 - 0.18, sub_ov["MAE entreno (USD)"], height=0.34, color=COLOR_NEUTRO_CLARO, label="MAE entrenamiento")
    ax2.barh(yp2 + 0.18, sub_ov["MAE (USD)"], height=0.34, color=COLOR_PRIMARIO, label="MAE prueba (ciega)")
    for i, (_, r) in enumerate(sub_ov.iterrows()):
        ax2.text(max(r["MAE entreno (USD)"], r["MAE (USD)"]) + 280, yp2[i], f"Ratio: {r['Prueba / Entreno']:.2f}x", va="center", fontsize=9)
    ax2.set_yticks(yp2, etiq_ov)
    ax2.invert_yaxis()
    ax2.set_xlim(0, max(sub_ov["MAE (USD)"].max(), sub_ov["MAE entreno (USD)"].max()) * 1.32)
    ax2.xaxis.set_major_formatter(fmt_dolares)
    ax2.set_title("Control de sobreajuste: MAE Entrenamiento vs. Prueba", loc="left", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Error medio absoluto semanal (USD)")
    ax2.grid(axis="y", visible=False)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=9, frameon=True)

    plt.tight_layout()
    plt.show()


def graficar_comparativa_y_tscv(
    predicciones_prueba: pd.DataFrame, df_tscv: pd.DataFrame, metodos_comparados: list[str], ubicacion: str
) -> None:
    """Dibuja curvas finales en prueba y MAE por pliegue en TimeSeriesSplit."""
    fig, axes = plt.subplots(2, 1, figsize=(15, 8.2))
    ax = axes[0]
    predicciones_prueba[
        ["Venta real", "OLS Reducido + Fourier", "Regresión lineal (Base + Cal.)", "Boosting de árboles", "Referencia anual"]
    ].plot(
        ax=ax, x_compat=True, linewidth=1.8,
        color=["#0F172A", COLOR_MARGEN, COLOR_PRIMARIO, COLOR_COSTO, COLOR_ALERTA],
    )
    ax.set_ylim(top=predicciones_prueba.max().max() * 1.18)
    ax.set_title(f"Comparativa final en prueba ({ubicacion}): Venta real vs. modelos seleccionados", loc="left", fontsize=12, fontweight="bold")
    ax.set_xlabel("Sábado de cierre de la semana")
    ax.xaxis.set_major_formatter(DateFormatter("%m/%Y"))
    ax.set_ylabel("Ventas netas (USD)")
    ax.yaxis.set_major_formatter(fmt_dolares)
    ax.legend(ncol=3, loc="upper left", fontsize=9, frameon=True)

    ax2 = axes[1]
    tabla_pliegues = df_tscv.pivot(index="Pliegue", columns="Método", values="MAE (USD)")[metodos_comparados]
    tabla_pliegues.plot(
        kind="bar", ax=ax2, width=0.78, rot=0,
        color=[COLOR_PRIMARIO, COLOR_WEB, COLOR_MARGEN, COLOR_COSTO, COLOR_ALERTA],
    )
    ax2.set_title(f"Estabilidad histórica (MAE por pliegue en TimeSeriesSplit - {ubicacion})", loc="left", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Ventana cronológica de validación (40 semanas cada una)")
    ax2.set_ylabel("MAE (USD)")
    ax2.yaxis.set_major_formatter(fmt_dolares)
    ax2.grid(axis="x", visible=False)
    ax2.legend(ncol=3, loc="upper right", fontsize=9, frameon=True)

    plt.tight_layout()
    plt.show()


def graficar_proyeccion_2025(res_anual: dict[str, Any], ubicacion: str) -> None:
    """Dibuja el horizonte semanal y el horizonte mensual agregado para la proyección 2025."""
    test_anual = res_anual["test_anual"]
    mensual = res_anual["mensual"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.4), gridspec_kw={"width_ratios": [1.35, 1.0]})
    ax = axes[0]
    test_anual.rename(columns={"venta_neta": "Venta real 2025"})[
        ["Venta real 2025", "Proyección anual (OLS)", "Proyección anual (OLS + Fourier)"]
    ].plot(ax=ax, x_compat=True, linewidth=1.8, color=["#0F172A", COLOR_PRIMARIO, COLOR_MARGEN])
    ax.set_title(f"Horizonte semanal 2025 ({len(test_anual)} semanas - {ubicacion})", loc="left", fontsize=12, fontweight="bold")
    ax.set_xlabel("Sábado de cierre (2025)")
    ax.xaxis.set_major_formatter(DateFormatter("%m/%Y"))
    ax.set_ylabel("Ventas netas (USD)")
    ax.yaxis.set_major_formatter(fmt_dolares)
    ax.legend(loc="upper left", fontsize=9, frameon=True)

    ax2 = axes[1]
    meses_lbl = [MESES_ES[d.month - 1] for d in mensual.index]
    xm = np.arange(len(meses_lbl))
    ax2.bar(xm - 0.2, mensual["venta_neta"], width=0.38, color="#0F172A", label="Venta real 2025")
    ax2.bar(xm + 0.2, mensual["Proyección anual (OLS + Fourier)"], width=0.38, color=COLOR_MARGEN, label="OLS + Fourier")
    ax2.set_xticks(xm, meses_lbl)
    ax2.set_title("Horizonte mensual agregado 2025 (12 meses)", loc="left", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Mes de cierre (2025)")
    ax2.set_ylabel("Ventas netas mensuales (USD)")
    ax2.yaxis.set_major_formatter(fmt_dolares)
    ax2.grid(axis="x", visible=False)
    ax2.legend(loc="upper left", fontsize=9, frameon=True)

    plt.tight_layout()
    plt.show()
