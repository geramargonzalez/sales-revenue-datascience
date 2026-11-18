"""Vistas analíticas y cálculos del Análisis Exploratorio de Datos (Bloque 4, 2018-2025)."""

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .config import (
    ANIOS_COMPLETOS,
    CIFRAS_CONTROL,
    COLS_FINANCIERAS,
    COLUMNAS_CONTABLES_ESPERADAS,
    DEPARTAMENTOS_MERCANCIA,
    DIAS_ES,
    ETIQUETAS_VARIABLES,
    FECHA_FIN_EDA,
    FECHA_INICIO_EDA,
    FILAS_CONTABLES_ESPERADAS,
    MESES_ES,
    UBICACIONES_OPERATIVAS,
    UMBRAL_POLITICA_DEVOLUCION,
    VENTAS_NETAS_CONTROL,
)
from .datos import validar_nulos


@dataclass
class VistaEDA:
    """Contenedor inmutable de vistas derivadas del tramo 2018-2025 sin alterar df."""

    df_eda: pd.DataFrame
    fecha: pd.Series
    fecha_eda: pd.Series
    ventas_netas_eda: float
    filas_excluidas_2026: int
    ventas_excluidas_2026: float
    es_devolucion: pd.Series
    es_operativa: pd.Series
    ventas_fin: pd.DataFrame
    devoluciones_fin: pd.DataFrame
    aux: pd.DataFrame
    resumen_segmentos: pd.DataFrame


def construir_vista_eda(
    df: pd.DataFrame,
    nulos_rezago_esperados: int,
    fecha_inicio: str = FECHA_INICIO_EDA,
    fecha_fin: str = FECHA_FIN_EDA,
) -> VistaEDA:
    """Verifica el balance contable y construye las vistas y máscaras del EDA 2018-2025."""
    assert df.shape == (FILAS_CONTABLES_ESPERADAS, COLUMNAS_CONTABLES_ESPERADAS), (
        "Dimensiones inesperadas del dataset"
    )
    validar_nulos(df, nulos_rezago_esperados)
    assert abs(df["net_sales"].sum() - VENTAS_NETAS_CONTROL) < 0.01, "Descuadre de ventas netas"

    fecha = pd.to_datetime(df["date"])
    mascara_eda = fecha.ge(fecha_inicio) & fecha.lt(fecha_fin)
    df_eda = df.loc[mascara_eda]
    fecha_eda = fecha.loc[mascara_eda]
    ventas_netas_eda = float(df_eda["net_sales"].sum())
    filas_excluidas_2026 = int((~mascara_eda).sum())
    ventas_excluidas_2026 = float(df.loc[~mascara_eda, "net_sales"].sum())

    es_devolucion = df_eda["is_return"]
    es_operativa = df_eda["location_name"].isin(UBICACIONES_OPERATIVAS)

    ventas_fin = df_eda.loc[~es_devolucion, COLS_FINANCIERAS]
    devoluciones_fin = df_eda.loc[es_devolucion, COLS_FINANCIERAS + ["return_lag_days"]].copy()
    devoluciones_fin["return_lag_days_analisis"] = devoluciones_fin["return_lag_days"].clip(
        upper=UMBRAL_POLITICA_DEVOLUCION
    )

    aux = pd.DataFrame({
        "anio": fecha_eda.dt.year,
        "mes": fecha_eda.dt.month,
        "anio_minorista": df_eda["retail_year"],
        "semana_minorista": df_eda["retail_week"],
        "ubicacion": df_eda["location_name"],
        "es_web": df_eda["is_web"],
        "venta_neta": df_eda["net_sales"],
        "venta_bruta": df_eda["gross_sales"].where(~es_devolucion, 0.0),
        "devuelto": (-df_eda["net_sales"]).where(es_devolucion, 0.0),
    })

    segmentos = {
        "Líneas de devolución (is_return)": es_devolucion,
        "Ventas mayoristas (is_wholesale)": df_eda["is_wholesale"],
        "Departamento System (cargos y misceláneos)": df_eda["department"] == "System",
        "Ubicaciones no operativas (pop-ups y administrativas)": ~es_operativa,
        "Cliente anónimo (CLIENTE_ANONIMO)": df_eda["customer_id"] == "CLIENTE_ANONIMO",
        "Ventas con importe neto cero": ~es_devolucion & (df_eda["net_sales"] == 0),
        "Ventas con costo cero (cogs == 0)": ~es_devolucion & (df_eda["cogs"] == 0),
    }
    resumen_seg = pd.DataFrame({
        "Líneas": {k: int(m.sum()) for k, m in segmentos.items()},
        "% de líneas": {k: m.mean() * 100 for k, m in segmentos.items()},
        "Ventas netas (USD)": {k: df_eda.loc[m, "net_sales"].sum() for k, m in segmentos.items()},
    })
    resumen_seg["% de ventas netas"] = resumen_seg["Ventas netas (USD)"] / ventas_netas_eda * 100
    resumen_formateado = pd.DataFrame({
        "Líneas": resumen_seg["Líneas"].map("{:,.0f}".format),
        "% de líneas": resumen_seg["% de líneas"].map("{:.2f}%".format),
        "Ventas netas (USD)": resumen_seg["Ventas netas (USD)"].map("${:,.0f}".format),
        "% de ventas netas": resumen_seg["% de ventas netas"].map("{:.2f}%".format),
    })

    return VistaEDA(
        df_eda=df_eda,
        fecha=fecha,
        fecha_eda=fecha_eda,
        ventas_netas_eda=ventas_netas_eda,
        filas_excluidas_2026=filas_excluidas_2026,
        ventas_excluidas_2026=ventas_excluidas_2026,
        es_devolucion=es_devolucion,
        es_operativa=es_operativa,
        ventas_fin=ventas_fin,
        devoluciones_fin=devoluciones_fin,
        aux=aux,
        resumen_segmentos=resumen_formateado,
    )


def _tasa_devolucion(grupo: Any) -> pd.Series | float:
    totales = grupo[["devuelto", "venta_bruta"]].sum()
    return totales["devuelto"] / totales["venta_bruta"] * 100


def calcular_cifras_control_y_calendario(vista: VistaEDA) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula el contraste anual contra cifras de control y el mapeo de mes minorista."""
    aux = vista.aux
    control = pd.DataFrame({
        "Referencia (M USD)": CIFRAS_CONTROL,
        "Año calendario (M USD)": aux.groupby("anio")["venta_neta"].sum() / 1e6,
        "Año minorista 4-5-4 (M USD)": aux.groupby("anio_minorista")["venta_neta"].sum() / 1e6,
    })
    control["Diferencia calendario"] = control["Año calendario (M USD)"] - control["Referencia (M USD)"]
    control["Diferencia minorista"] = control["Año minorista 4-5-4 (M USD)"] - control["Referencia (M USD)"]
    control.index.name = "Año"

    mapa_meses = pd.crosstab(vista.df_eda["retail_month"], aux["mes"], normalize="index") * 100
    correspondencia = pd.DataFrame({
        "Trimestre minorista": vista.df_eda.groupby("retail_month")["retail_quarter"].first(),
        "Mes calendario dominante": mapa_meses.idxmax(axis=1),
        "% de líneas en ese mes": mapa_meses.max(axis=1).map("{:.1f}%".format),
    })
    correspondencia.index.name = "Mes minorista"
    return control, correspondencia.T


def calcular_contraste_hipotesis(vista: VistaEDA) -> dict[str, Any]:
    """Evalúa canal web, estacionalidad nov-dic, devoluciones y Wedding Annex (2018-2025)."""
    aux = vista.aux
    df_eda = vista.df_eda
    por_anio = aux.groupby("anio")

    cuota_web_anual = aux[aux["es_web"]].groupby("anio")["venta_neta"].sum() / por_anio["venta_neta"].sum() * 100
    cuota_web_total = float(aux.loc[aux["es_web"], "venta_neta"].sum() / aux["venta_neta"].sum() * 100)

    venta_mes = aux[aux["anio"].isin(ANIOS_COMPLETOS)].pivot_table(
        index="mes", columns="anio", values="venta_neta", aggfunc="sum"
    )
    cuota_nov_dic = venta_mes.loc[[11, 12]].sum() / venta_mes.sum() * 100

    tasa_global = float(aux["devuelto"].sum() / aux["venta_bruta"].sum() * 100)
    tasa_anual = _tasa_devolucion(por_anio)
    tasa_mensual = _tasa_devolucion(aux.groupby(["anio", "mes"])).unstack("anio")
    tasa_semanal = _tasa_devolucion(aux.groupby(["anio_minorista", "semana_minorista"]))
    tasa_tienda = _tasa_devolucion(aux[vista.es_operativa].groupby("ubicacion")).sort_values()

    annex = df_eda[df_eda["location_name"] == "Wedding Annex"]
    tickets_annex = annex.groupby("receipt_id").agg(
        importe=("net_sales", "sum"),
        mes=("date", lambda s: s.iloc[0][:7]),
        con_devolucion=("is_return", "any"),
    )
    tickets_annex = tickets_annex[~tickets_annex["con_devolucion"]]
    annex_mensual = tickets_annex.groupby("mes")["importe"].agg(tickets="size", importe="sum")
    annex_ultimos_12 = annex_mensual.tail(12)

    contraste = pd.DataFrame([
        [
            "Canal web sobre la venta neta",
            "~62%",
            f"{cuota_web_total:.1f}% en 2018-2025; pico de {cuota_web_anual.max():.1f}% (2020) "
            f"y {cuota_web_anual[2025]:.1f}% en 2025",
        ],
        [
            "Noviembre + diciembre sobre el año",
            "32%",
            f"entre {cuota_nov_dic.min():.1f}% y {cuota_nov_dic.max():.1f}% (2018-2025)",
        ],
        [
            "Devoluciones sobre la venta bruta",
            "~10% y creciente",
            f"{tasa_global:.1f}% en 2018-2025; de {tasa_anual[2018]:.1f}% (2018) a {tasa_anual[2025]:.1f}% (2025)",
        ],
        [
            "Pico de devoluciones en enero",
            "hasta 27%",
            f"enero entre {tasa_mensual.loc[1].min():.1f}% y {tasa_mensual.loc[1].max():.1f}%; "
            f"máximo semanal {tasa_semanal.max():.1f}%",
        ],
        [
            "Tasa de devolución Williamsburg vs. Boston",
            "17% vs. 7%",
            f"{tasa_tienda['Williamsburg']:.1f}% vs. {tasa_tienda['BOSTON Newbury']:.1f}%",
        ],
        [
            "Wedding Annex: tickets al mes",
            "~50",
            f"{annex_mensual['tickets'].mean():.0f} en 2018-2025; "
            f"{annex_ultimos_12['tickets'].mean():.0f} en 2025",
        ],
        [
            "Wedding Annex: ticket promedio",
            "~2,000 USD",
            f"${tickets_annex['importe'].mean():,.0f} en 2018-2025; "
            f"${annex_ultimos_12['importe'].sum() / annex_ultimos_12['tickets'].sum():,.0f} en 2025",
        ],
    ], columns=["Afirmación del negocio", "Referencia", "Observado en el dataset (2018-2025)"])

    return {
        "contraste": contraste,
        "cuota_web_anual": cuota_web_anual,
        "tasa_mensual": tasa_mensual,
        "tasa_tienda": tasa_tienda,
    }


def describir_variables_financieras(datos: pd.DataFrame) -> pd.DataFrame:
    """Devuelve estadísticas descriptivas con percentiles y asimetría en español."""
    resumen = datos.describe(percentiles=[0.25, 0.5, 0.75, 0.90, 0.99]).T
    resumen["asimetría"] = datos.skew()
    return resumen.rename(columns={
        "count": "líneas",
        "mean": "media",
        "std": "desv. estándar",
        "min": "mínimo",
        "25%": "p25",
        "50%": "mediana",
        "75%": "p75",
        "90%": "p90",
        "99%": "p99",
        "max": "máximo",
    }).rename(index=ETIQUETAS_VARIABLES)


def calcular_participaciones_categoricas(vista: VistaEDA) -> tuple[list[tuple[str, pd.DataFrame]], dict[str, int]]:
    """Calcula tablas de participación en líneas y en venta neta por dimensión categórica."""
    df_eda = vista.df_eda

    def participacion(serie: pd.Series, top: int | None = None) -> pd.DataFrame:
        tabla = pd.DataFrame({
            "% de líneas": serie.value_counts(normalize=True) * 100,
            "% de venta neta": df_eda.groupby(serie)["net_sales"].sum() / vista.ventas_netas_eda * 100,
        }).sort_values("% de venta neta", ascending=False)
        if top is not None and len(tabla) > top:
            resto = tabla.iloc[top:].sum().rename(f"Resto ({len(tabla) - top})")
            tabla = pd.concat([tabla.iloc[:top], resto.to_frame().T])
        return tabla

    canal = df_eda["is_web"].map({True: "Canal web", False: "Tienda física"})
    tipo_txn = df_eda["txn_type"].map({
        "Sale": "Venta", "Return": "Devolución", "Mixed": "Mixta", "Deposit": "Depósito"
    })
    ubicacion = df_eda["location_name"].where(vista.es_operativa, "Temporales y administrativas")

    paneles = [
        ("Clase de producto (10 principales)", participacion(df_eda["class"], top=10)),
        ("Marca (10 principales)", participacion(df_eda["brand"], top=10)),
        ("Ubicación", participacion(ubicacion)),
        ("Departamento", participacion(df_eda["department"])),
        ("Canal registrado", participacion(canal)),
        ("Tipo de transacción", participacion(tipo_txn)),
    ]
    cardinalidad = {
        "departamentos": int(df_eda["department"].nunique()),
        "clases": int(df_eda["class"].nunique()),
        "subclases": int(df_eda["subclass1"].nunique()),
        "marcas": int(df_eda["brand"].nunique()),
        "articulos": int(df_eda["item_id"].nunique()),
        "ubicaciones": int(df_eda["location_name"].nunique()),
    }
    return paneles, cardinalidad


def calcular_correlaciones_y_vif(vista: VistaEDA) -> dict[str, Any]:
    """Calcula matrices de correlación a nivel de línea y agregado semanal más VIF."""
    cols_corr = COLS_FINANCIERAS
    corr_pearson = vista.ventas_fin[cols_corr].corr(method="pearson")
    corr_spearman = vista.ventas_fin[cols_corr].corr(method="spearman")
    cols_dev = [c for c in cols_corr if c != "gross_sales"] + ["return_lag_days_analisis"]
    corr_dev = vista.devoluciones_fin[cols_dev].corr(method="pearson")

    semanal = (
        vista.df_eda[vista.es_operativa]
        .groupby(["retail_year", "retail_week", "location_name"])[cols_corr]
        .sum()
    )
    corr_semanal = semanal.corr(method="pearson")

    df_eda = vista.df_eda
    desvio_neto = (df_eda["gross_sales"] - df_eda["discount_total"] - df_eda["net_sales"]).abs() > 0.01
    desvio_margen = (df_eda["margin"] - (df_eda["net_sales"] - df_eda["cogs"])).abs() > 0.01

    cols_pred_sem = [c for c in cols_corr if c != "net_sales"]
    vif_completo = pd.Series(np.diag(np.linalg.inv(corr_semanal.values)), index=cols_corr).rename(ETIQUETAS_VARIABLES)
    vif_sin_neto = pd.Series(
        np.diag(np.linalg.inv(semanal[cols_pred_sem].corr().values)), index=cols_pred_sem
    ).rename(ETIQUETAS_VARIABLES)
    resumen_vif = pd.DataFrame({
        "VIF (7 variables)": vif_completo,
        "VIF (sin Ventas netas)": vif_sin_neto,
    }).round(1)

    return {
        "matrices": [
            (corr_pearson, "Pearson por línea de venta"),
            (corr_spearman, "Spearman por línea de venta"),
            (corr_dev, "Pearson por línea de devolución"),
            (corr_semanal, f"Pearson por semana y ubicación ({len(semanal):,} observaciones)"),
        ],
        "lineas_desvio_neto": int((desvio_neto & ~vista.es_devolucion).sum()),
        "lineas_desvio_margen": int(desvio_margen.sum()),
        "pct_desvio_margen": float(desvio_margen.mean() * 100),
        "lineas_cogs_cero": int((desvio_margen & (df_eda["cogs"] == 0) & (df_eda["margin"] == 0)).sum()),
        "ventas_desvio_margen": float(df_eda.loc[desvio_margen, "net_sales"].sum()),
        "resumen_vif": resumen_vif,
    }


def calcular_serie_mensual(vista: VistaEDA) -> pd.DataFrame:
    """Agrega líneas de venta y ventas netas por mes calendario."""
    periodo = vista.fecha_eda.dt.to_period("M")
    serie = pd.DataFrame({
        "lineas_venta": (~vista.es_devolucion).groupby(periodo).sum(),
        "venta_neta": vista.df_eda["net_sales"].groupby(periodo).sum(),
    })
    serie.index = serie.index.to_timestamp()
    return serie


def calcular_estacionalidad_mensual(vista: VistaEDA) -> dict[str, Any]:
    """Calcula participación mensual homologada y cascada bruta -> descuentos -> neta."""
    aux_comp = vista.aux[vista.aux["anio"].isin(ANIOS_COMPLETOS)]
    venta_mes_anio = aux_comp.pivot_table(index="mes", columns="anio", values="venta_neta", aggfunc="sum")
    cuota_mensual = venta_mes_anio / venta_mes_anio.sum() * 100
    cascada = aux_comp.groupby("mes")[["venta_bruta", "venta_neta", "devuelto"]].sum() / len(ANIOS_COMPLETOS)
    cascada["tras_descuentos"] = cascada["venta_neta"] + cascada["devuelto"]

    resumen = pd.DataFrame({
        "Participación media (%)": cuota_mensual.mean(axis=1),
        "Mínimo (%)": cuota_mensual.min(axis=1),
        "Máximo (%)": cuota_mensual.max(axis=1),
        "Descuentos sobre venta bruta (%)": (
            (cascada["venta_bruta"] - cascada["tras_descuentos"]) / cascada["venta_bruta"] * 100
        ),
        "Devoluciones sobre venta bruta (%)": cascada["devuelto"] / cascada["venta_bruta"] * 100,
    })
    resumen.index = MESES_ES
    return {"cuota_mensual": cuota_mensual, "cascada": cascada, "resumen_estacional": resumen.round(1).T}


def calcular_patron_dia_hora(vista: VistaEDA) -> dict[str, Any]:
    """Calcula distribución de ventas por día de la semana y hora del día según canal."""
    df_venta = vista.df_eda.loc[~vista.es_devolucion]
    canal_venta = df_venta["is_web"].map({True: "Canal web", False: "Tienda física"})

    venta_dia = (
        df_venta["net_sales"]
        .groupby([vista.fecha_eda[~vista.es_devolucion].dt.dayofweek, canal_venta])
        .sum()
        .unstack()
    )
    cuota_dia = venta_dia / venta_dia.sum() * 100
    cuota_dia.index = DIAS_ES

    lineas_hora = df_venta.groupby(["hour", canal_venta]).size().unstack(fill_value=0)
    cuota_hora = lineas_hora / lineas_hora.sum() * 100
    return {
        "cuota_dia": cuota_dia,
        "cuota_hora": cuota_hora,
        "web_hora_0": float(cuota_hora.loc[0, "Canal web"]),
        "hora_pico": cuota_hora.idxmax().to_dict(),
        "pct_11_19": cuota_hora.loc[11:19].sum().round(1).to_dict(),
    }


def calcular_ventas_semana_minorista(vista: VistaEDA) -> tuple[pd.DataFrame, int, pd.DataFrame]:
    """Agrega ventas netas por semana minorista 4-5-4 y resume semanas pico."""
    aux = vista.aux
    venta_semanal = aux.pivot_table(
        index="semana_minorista", columns="anio_minorista", values="venta_neta", aggfunc="sum"
    )
    dias_sem52_2025 = int(
        vista.fecha_eda[(aux["anio_minorista"] == 2025) & (aux["semana_minorista"] == 52)].dt.date.nunique()
    )
    pico_semanal = pd.DataFrame({
        "Semanas de mayor venta": {
            a: ", ".join(map(str, venta_semanal[a].nlargest(5).index.sort_values())) for a in ANIOS_COMPLETOS
        },
        "Peso de las 5 semanas en el año (%)": {
            a: venta_semanal[a].nlargest(5).sum() / venta_semanal[a].sum() * 100 for a in ANIOS_COMPLETOS
        },
        "Cuarto trimestre sobre el año (%)": {
            a: venta_semanal.loc[40:, a].sum() / venta_semanal[a].sum() * 100 for a in ANIOS_COMPLETOS
        },
    })
    pico_semanal.index.name = "Año minorista"
    return venta_semanal, dias_sem52_2025, pico_semanal


def calcular_interanual_y_descomposicion(vista: VistaEDA) -> dict[str, Any]:
    """Calcula crecimiento interanual homologado (ly_date_key), descomposición 52s y ACF/PACF."""
    aux = vista.aux
    df_eda = vista.df_eda
    venta_anual_cal = aux.groupby("anio")["venta_neta"].sum()
    venta_anual_min = aux.groupby("anio_minorista")["venta_neta"].sum()

    venta_por_date_key = df_eda.groupby("date_key")["net_sales"].sum()
    calendario_ly = (
        df_eda[["date_key", "ly_date_key"]]
        .assign(anio=vista.fecha_eda.dt.year)
        .drop_duplicates(subset=["date_key"])
    )
    calendario_ly["venta_actual"] = calendario_ly["date_key"].map(venta_por_date_key).fillna(0.0)
    calendario_ly["venta_ly"] = calendario_ly["ly_date_key"].map(venta_por_date_key)
    resumen_ly = (
        calendario_ly[calendario_ly["anio"] >= 2019]
        .groupby("anio")
        .agg(
            venta_actual_m=("venta_actual", lambda s: s.sum() / 1e6),
            venta_ly_m=("venta_ly", lambda s: s.sum() / 1e6),
            cobertura_ly_pct=("venta_ly", lambda s: s.notna().mean() * 100),
        )
    )
    resumen_ly["Variación ly_date_key (%)"] = (
        (resumen_ly["venta_actual_m"] - resumen_ly["venta_ly_m"]) / resumen_ly["venta_ly_m"] * 100
    )

    interanual = pd.DataFrame({
        "Año calendario (M USD)": venta_anual_cal / 1e6,
        "Variación calendario (%)": venta_anual_cal.pct_change() * 100,
        "Año minorista 4-5-4 (M USD)": venta_anual_min / 1e6,
        "Variación minorista (%)": venta_anual_min.pct_change() * 100,
        "Variación ly_date_key (%)": resumen_ly["Variación ly_date_key (%)"],
        "Fechas con par en ly_date_key (%)": resumen_ly["cobertura_ly_pct"],
    })
    interanual.index.name = "Año"

    periodo_estacional = 52
    max_rezago_acf = 56
    serie_sem = (
        df_eda.assign(fecha_ts=vista.fecha_eda)
        .set_index("fecha_ts")["net_sales"]
        .resample("W-SAT")
        .sum()
    )
    semanas_comp = (
        (serie_sem.index - pd.Timedelta(days=6) >= pd.Timestamp(FECHA_INICIO_EDA))
        & (serie_sem.index < pd.Timestamp(FECHA_FIN_EDA))
    )
    serie_sem = serie_sem.loc[semanas_comp].copy()

    pesos = np.ones(periodo_estacional + 1, dtype=float)
    pesos[0] = 0.5
    pesos[-1] = 0.5
    pesos /= periodo_estacional
    tendencia_vals = np.convolve(serie_sem.to_numpy(dtype=float), pesos, mode="valid")
    mitad = periodo_estacional // 2
    tendencia_ts = pd.Series(np.nan, index=serie_sem.index, dtype=float)
    tendencia_ts.iloc[mitad: len(serie_sem) - mitad] = tendencia_vals

    sin_tendencia = serie_sem - tendencia_ts
    pos_ciclo = np.arange(len(serie_sem)) % periodo_estacional
    patron_52 = pd.Series(sin_tendencia.to_numpy()).groupby(pos_ciclo).mean()
    patron_52 = patron_52 - patron_52.mean()
    estacional_ts = pd.Series([patron_52[pos] for pos in pos_ciclo], index=serie_sem.index, dtype=float)
    residuo_ts = serie_sem - tendencia_ts - estacional_ts

    mascara_valida = residuo_ts.notna()
    var_res = np.var(residuo_ts[mascara_valida], ddof=1)
    fuerza_tendencia = max(0.0, 1.0 - var_res / np.var((tendencia_ts + residuo_ts)[mascara_valida], ddof=1))
    fuerza_estacional = max(0.0, 1.0 - var_res / np.var((estacional_ts + residuo_ts)[mascara_valida], ddof=1))

    valores_ts = serie_sem.to_numpy(dtype=float)
    centrada = valores_ts - valores_ts.mean()
    n_sem = len(centrada)
    autocov = np.array([np.dot(centrada[: n_sem - k], centrada[k:]) / n_sem for k in range(max_rezago_acf + 1)])
    acf_vals = autocov / autocov[0]

    pacf_vals = np.zeros(max_rezago_acf + 1, dtype=float)
    pacf_vals[0] = 1.0
    phi_dl = np.zeros((max_rezago_acf + 1, max_rezago_acf + 1), dtype=float)
    var_dl = np.zeros(max_rezago_acf + 1, dtype=float)
    phi_dl[1, 1] = acf_vals[1]
    pacf_vals[1] = acf_vals[1]
    var_dl[1] = autocov[0] * (1.0 - acf_vals[1] ** 2)
    for k in range(2, max_rezago_acf + 1):
        num_dl = autocov[k] - np.dot(phi_dl[k - 1, 1:k], autocov[1:k][::-1])
        phi_dl[k, k] = num_dl / var_dl[k - 1]
        for j in range(1, k):
            phi_dl[k, j] = phi_dl[k - 1, j] - phi_dl[k, k] * phi_dl[k - 1, k - j]
        var_dl[k] = var_dl[k - 1] * (1.0 - phi_dl[k, k] ** 2)
        pacf_vals[k] = phi_dl[k, k]

    umbral_ic = 1.96 / np.sqrt(n_sem)
    rezagos_clave = [1, 2, 4, 13, 26, 52]
    tabla_acf_pacf = pd.DataFrame({
        "Rezago (semanas)": [f"t - {k}" for k in rezagos_clave],
        "Significado operativo": [
            "Semana inmediata anterior",
            "Hace 2 semanas",
            "Hace 1 mes minorista (4 sem.)",
            "Hace 1 trimestre (13 sem.)",
            "Hace 1 semestre (26 sem.)",
            "Misma semana del año previo (52 sem.)",
        ],
        "ACF (r_k)": [acf_vals[k] for k in rezagos_clave],
        "PACF (phi_kk)": [pacf_vals[k] for k in rezagos_clave],
        "Significativo al 95% (|r| > IC)": [
            "Sí" if abs(acf_vals[k]) > umbral_ic else "No" for k in rezagos_clave
        ],
    }).set_index("Rezago (semanas)")

    return {
        "interanual": interanual,
        "venta_anual_calendario": venta_anual_cal,
        "serie_semanal_ts": serie_sem,
        "tendencia_ts": tendencia_ts,
        "estacional_ts": estacional_ts,
        "residuo_ts": residuo_ts,
        "fuerza_tendencia": float(fuerza_tendencia),
        "fuerza_estacional": float(fuerza_estacional),
        "n_semanas_ts": n_sem,
        "umbral_ic_95": float(umbral_ic),
        "acf_vals": acf_vals,
        "pacf_vals": pacf_vals,
        "max_rezago_acf": max_rezago_acf,
        "tabla_acf_pacf": tabla_acf_pacf,
    }


def construir_tabla_tickets(vista: VistaEDA) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Agrega las líneas por receipt_id y separa los tickets sin devoluciones."""
    tickets = vista.df_eda.groupby("receipt_id").agg(
        importe=("net_sales", "sum"),
        lineas=("line_id", "size"),
        ubicacion=("location_name", "first"),
        es_web=("is_web", "first"),
        cliente=("customer_id", "first"),
        fecha_ticket=("date", "first"),
        con_devolucion=("is_return", "any"),
    )
    return tickets, tickets[~tickets["con_devolucion"]]


def analizar_canales_y_ubicaciones(vista: VistaEDA, tickets_venta: pd.DataFrame) -> dict[str, Any]:
    """Genera comparativas de canal, tiendas físicas, antigüedad y Wedding Annex."""
    df_eda = vista.df_eda

    def resumen_canal(mascara_lineas: pd.Series, mascara_tickets: pd.Series) -> dict[str, float]:
        lineas_v = df_eda[mascara_lineas & ~vista.es_devolucion]
        con_costo = lineas_v[lineas_v["cogs"] > 0]
        t = tickets_venta[mascara_tickets]
        a = vista.aux[mascara_lineas]
        return {
            "Ventas netas (M USD)": df_eda.loc[mascara_lineas, "net_sales"].sum() / 1e6,
            "Participación en la venta neta (%)": df_eda.loc[mascara_lineas, "net_sales"].sum() / vista.ventas_netas_eda * 100,
            "Tickets sin devoluciones (miles)": len(t) / 1e3,
            "Ticket promedio (USD)": t["importe"].mean(),
            "Ticket mediano (USD)": t["importe"].median(),
            "Líneas por ticket": t["lineas"].mean(),
            "Descuento sobre venta bruta (%)": lineas_v["discount_total"].sum() / lineas_v["gross_sales"].sum() * 100,
            "Margen sobre venta neta, líneas con costo (%)": con_costo["margin"].sum() / con_costo["net_sales"].sum() * 100,
            "Devoluciones sobre venta bruta (%)": a["devuelto"].sum() / a["venta_bruta"].sum() * 100,
        }

    comparativa_canal = pd.DataFrame({
        "Canal web": resumen_canal(df_eda["is_web"], tickets_venta["es_web"]),
        "Tienda física": resumen_canal(~df_eda["is_web"], ~tickets_venta["es_web"]),
    })

    tiendas_fisicas = [u for u in UBICACIONES_OPERATIVAS if u != "Web Warehouse"]
    es_tf = df_eda["location_name"].isin(tiendas_fisicas)
    venta_tienda = df_eda[es_tf].groupby("location_name")["net_sales"].sum().sort_values()
    ticket_tienda = (
        tickets_venta[tickets_venta["ubicacion"].isin(tiendas_fisicas)]
        .groupby("ubicacion")["importe"]
        .mean()
        .sort_values()
    )
    venta_estado = df_eda[es_tf].groupby("loc_state")["net_sales"].sum().sort_values()
    tiendas_estado = df_eda[es_tf].groupby("loc_state")["location_name"].nunique()

    fecha_corte = vista.fecha_eda.max()
    actividad = (
        df_eda[vista.es_operativa]
        .assign(_fecha=vista.fecha_eda[vista.es_operativa])
        .groupby("location_name")["_fecha"]
        .agg(primera_venta="min", ultima_venta="max", dias_con_ventas="nunique")
    )
    tickets_ub = tickets_venta.groupby("ubicacion").size()
    ficha_tiendas = pd.DataFrame({
        "Primera fecha registrada": actividad["primera_venta"].dt.date,
        "Historial observado (meses)": ((fecha_corte - actividad["primera_venta"]).dt.days / 30.44).round(0).astype(int),
        "Días con registros": actividad["dias_con_ventas"],
        "Tickets sin devoluciones por día con registros": (
            tickets_ub.reindex(actividad.index) / actividad["dias_con_ventas"]
        ).round(1),
        "Ventas netas por día con registros (USD)": (
            df_eda[vista.es_operativa].groupby("location_name")["net_sales"].sum() / actividad["dias_con_ventas"]
        ).round(0),
    }).sort_values("Primera fecha registrada")
    ficha_tiendas.index.name = "Ubicación"

    tickets_fisicos = tickets_venta[tickets_venta["ubicacion"].isin(tiendas_fisicas)]
    segmento = np.where(tickets_fisicos["ubicacion"] == "Wedding Annex", "Wedding Annex", "Resto de tiendas físicas")
    comp_annex = tickets_fisicos.groupby(segmento).agg(
        tickets=("importe", "size"),
        ticket_promedio=("importe", "mean"),
        ticket_mediano=("importe", "median"),
        lineas_por_ticket=("lineas", "mean"),
        venta=("importe", "sum"),
    )
    comp_annex["participacion_venta"] = comp_annex["venta"] / comp_annex["venta"].sum() * 100
    comp_annex["participacion_tickets"] = comp_annex["tickets"] / comp_annex["tickets"].sum() * 100
    comp_annex = comp_annex.drop(columns="venta").rename(columns={
        "tickets": "Tickets de venta",
        "ticket_promedio": "Ticket promedio (USD)",
        "ticket_mediano": "Ticket mediano (USD)",
        "lineas_por_ticket": "Líneas por ticket",
        "participacion_venta": "Importe de tickets físicos sin devoluciones (%)",
        "participacion_tickets": "Tickets físicos sin devoluciones (%)",
    })

    return {
        "comparativa_canal": comparativa_canal,
        "venta_tienda": venta_tienda,
        "ticket_tienda": ticket_tienda,
        "venta_estado": venta_estado,
        "tiendas_estado": tiendas_estado,
        "ficha_tiendas": ficha_tiendas,
        "comparativa_annex": comp_annex.round(1).T,
    }


def _agrupar_motivo(motivo: str) -> str:
    texto = motivo.lower()
    reglas = [
        ("warranty", "Garantía"),
        ("damage", "Dañado o defectuoso"),
        ("defect", "Dañado o defectuoso"),
        ("quality", "Dañado o defectuoso"),
        ("size", "Cambio de talla"),
        ("fit", "Cambio de talla"),
        ("mind", "Cambio de opinión"),
        ("not as exp", "No era lo esperado"),
        ("gift", "Devolución de regalo"),
        ("style", "Cambio de estilo o color"),
        ("color", "Cambio de estilo o color"),
        ("discount", "Ajuste de precio o impuesto"),
        ("price", "Ajuste de precio o impuesto"),
        ("tax", "Ajuste de precio o impuesto"),
        ("lost", "Extravío o artículo incorrecto"),
        ("incorrect item", "Extravío o artículo incorrecto"),
        ("wrong item", "Extravío o artículo incorrecto"),
        ("no especificado", "No especificado"),
    ]
    return next((grupo for clave, grupo in reglas if clave in texto), "Otros motivos")


def analizar_devoluciones(vista: VistaEDA) -> dict[str, Any]:
    """Calcula balance, canal de procesamiento, estacionalidad semanal y perfil de devoluciones."""
    df_eda = vista.df_eda
    aux = vista.aux
    es_dev = vista.es_devolucion
    tiendas_fisicas = [u for u in UBICACIONES_OPERATIVAS if u != "Web Warehouse"]

    balance = pd.DataFrame({
        "Líneas": es_dev.map({False: "Venta", True: "Devolución"}).value_counts(),
        "% de líneas": es_dev.map({False: "Venta", True: "Devolución"}).value_counts(normalize=True) * 100,
    })

    dev_canal = (
        aux.assign(canal=aux["es_web"].map({True: "Canal web", False: "Tienda física"}), es_devolucion=es_dev)
        .groupby("canal")
        .agg(
            devuelto=("devuelto", "sum"),
            venta_bruta=("venta_bruta", "sum"),
            lineas_devolucion=("es_devolucion", "sum"),
            lineas=("es_devolucion", "size"),
        )
    )
    tabla_canal = pd.DataFrame({
        "Importe devuelto (M USD)": dev_canal["devuelto"] / 1e6,
        "Tasa en importe (%)": dev_canal["devuelto"] / dev_canal["venta_bruta"] * 100,
        "Proporción de líneas (%)": dev_canal["lineas_devolucion"] / dev_canal["lineas"] * 100,
    })

    origen_web = df_eda[es_dev & (df_eda["orig_location_name"] == "Web Warehouse")]
    texto_origen_web = (
        f"Devoluciones de compras web procesadas en una tienda física: {(~origen_web['is_web']).mean() * 100:.1f}% "
        f"de {len(origen_web):,} líneas con origen web registrado"
    )

    sem_dev = (
        aux.assign(es_dev=es_dev)
        .groupby("semana_minorista")
        .agg(
            devuelto=("devuelto", "sum"),
            venta_bruta=("venta_bruta", "sum"),
            lineas_dev=("es_dev", "sum"),
            lineas=("es_dev", "size"),
        )
        .loc[1:52]
    )
    sem_dev["tasa_importe"] = sem_dev["devuelto"] / sem_dev["venta_bruta"] * 100
    sem_dev["tasa_lineas"] = sem_dev["lineas_dev"] / sem_dev["lineas"] * 100

    es_tf = df_eda["location_name"].isin(tiendas_fisicas)
    tf_dev = aux[es_tf].assign(origen_web=(df_eda.loc[es_tf, "orig_location_name"] == "Web Warehouse"))
    tf_dev["dev_web"] = np.where(tf_dev["origen_web"], tf_dev["devuelto"], 0.0)
    tf_dev["dev_tienda"] = tf_dev["devuelto"] - tf_dev["dev_web"]
    por_tienda = tf_dev.groupby("ubicacion")[["venta_bruta", "devuelto", "dev_tienda", "dev_web"]].sum()
    por_tienda = por_tienda[por_tienda["venta_bruta"] >= 1e6].copy()
    por_tienda["tasa_total"] = por_tienda["devuelto"] / por_tienda["venta_bruta"] * 100
    por_tienda["tasa_tienda"] = por_tienda["dev_tienda"] / por_tienda["venta_bruta"] * 100
    por_tienda["tasa_web"] = por_tienda["dev_web"] / por_tienda["venta_bruta"] * 100
    por_tienda["pct_origen_web"] = por_tienda["dev_web"] / por_tienda["devuelto"] * 100
    por_tienda = por_tienda.sort_values("tasa_total")

    lineas_dev = df_eda[es_dev]
    rezago_analisis = vista.devoluciones_fin["return_lag_days_analisis"].dropna()
    motivos = lineas_dev["return_reason"].map(_agrupar_motivo).value_counts(normalize=True).sort_values() * 100

    es_joyeria = df_eda["department"] == "Jewelry"
    por_clase = aux[es_joyeria].assign(clase=df_eda.loc[es_joyeria, "class"]).groupby("clase")[["devuelto", "venta_bruta"]].sum()
    por_clase = por_clase[por_clase["venta_bruta"] >= 1e6]
    tasa_clase = (por_clase["devuelto"] / por_clase["venta_bruta"] * 100).sort_values()

    rangos = pd.cut(
        df_eda["net_sales"].abs(),
        bins=[0, 25, 50, 100, 200, 400, 800, np.inf],
        labels=["Hasta $25", "$25-50", "$50-100", "$100-200", "$200-400", "$400-800", "Más de $800"],
    )
    tasa_rango = es_dev.groupby(rangos, observed=True).mean() * 100
    canal_proc = df_eda["is_web"].map({False: "Tienda física", True: "Canal web"})
    tasa_rango_canal = es_dev.groupby([rangos, canal_proc], observed=True).mean().unstack() * 100

    return {
        "balance": balance,
        "tabla_canal": tabla_canal,
        "texto_origen_web": texto_origen_web,
        "sem_dev": sem_dev,
        "tasa_enero_imp": float(sem_dev.loc[1:5, "devuelto"].sum() / sem_dev.loc[1:5, "venta_bruta"].sum() * 100),
        "tasa_resto_imp": float(sem_dev.loc[6:52, "devuelto"].sum() / sem_dev.loc[6:52, "venta_bruta"].sum() * 100),
        "tasa_enero_lin": float(sem_dev.loc[1:5, "lineas_dev"].sum() / sem_dev.loc[1:5, "lineas"].sum() * 100),
        "tasa_resto_lin": float(sem_dev.loc[6:52, "lineas_dev"].sum() / sem_dev.loc[6:52, "lineas"].sum() * 100),
        "por_tienda_dev": por_tienda,
        "rezago_analisis": rezago_analisis,
        "motivos": motivos,
        "tasa_clase": tasa_clase,
        "tasa_global": float(aux["devuelto"].sum() / aux["venta_bruta"].sum() * 100),
        "tasa_rango": tasa_rango,
        "tasa_rango_canal": tasa_rango_canal,
        "sin_rezago_n": int(lineas_dev["return_lag_days"].isna().sum()),
        "sin_rezago_pct": float(lineas_dev["return_lag_days"].isna().mean() * 100),
    }


def analizar_productos_y_rentabilidad(vista: VistaEDA) -> dict[str, Any]:
    """Calcula resumen por departamento, Pareto 80/20, márgenes y tramos de descuento."""
    df_eda = vista.df_eda
    lineas_venta = df_eda[~vista.es_devolucion]
    con_costo = lineas_venta[lineas_venta["cogs"] > 0]

    def margen_pct(grupo_col: str) -> pd.Series:
        g = con_costo.groupby(grupo_col)[["margin", "net_sales"]].sum()
        return g["margin"] / g["net_sales"] * 100

    def descuento_pct(grupo_col: str) -> pd.Series:
        g = lineas_venta.groupby(grupo_col)[["discount_total", "gross_sales"]].sum()
        return g["discount_total"] / g["gross_sales"] * 100

    resumen_dept = pd.DataFrame({
        "Ventas netas (M USD)": df_eda.groupby("department")["net_sales"].sum() / 1e6,
        "Unidades vendidas (miles)": lineas_venta.groupby("department")["qty"].sum() / 1e3,
        "Precio neto por unidad (USD)": (
            lineas_venta.groupby("department")["net_sales"].sum() / lineas_venta.groupby("department")["qty"].sum()
        ),
        "Margen total (M USD)": df_eda.groupby("department")["margin"].sum() / 1e6,
        "Margen, líneas con costo (%)": margen_pct("department"),
        "Descuento sobre venta bruta (%)": descuento_pct("department"),
    }).loc[DEPARTAMENTOS_MERCANCIA]
    resumen_dept.index.name = "Departamento"

    venta_sub_tot = df_eda.groupby("subclass1")["net_sales"].sum().sort_values()
    venta_subclase = venta_sub_tot.tail(12)
    peso_top12_subclase = float(venta_subclase.sum() / venta_sub_tot.sum() * 100)

    es_joyeria = df_eda["department"] == "Jewelry"
    venta_clase_j = df_eda[es_joyeria].groupby("class")["net_sales"].sum()
    clases_top7 = venta_clase_j.nlargest(7).index
    peso_top7_clase = float(venta_clase_j.loc[clases_top7].sum() / venta_clase_j.sum() * 100)
    margen_clase = margen_pct("class").reindex(clases_top7).sort_values()

    margen_marca_tot = df_eda.groupby("brand")["margin"].sum()
    margen_marca = margen_marca_tot.nlargest(12).sort_values()
    peso_top12_marca = float(margen_marca.sum() / margen_marca_tot[margen_marca_tot > 0].sum() * 100)
    margen_marca_pct = margen_pct("brand").reindex(margen_marca.index)

    filas_pareto = []
    for col_p, etiq_p, met_p in [
        ("subclass1", "Subclase (ventas netas)", "net_sales"),
        ("class", "Clase (ventas netas)", "net_sales"),
        ("brand", "Marca (ventas netas)", "net_sales"),
        ("brand", "Marca (margen registrado)", "margin"),
    ]:
        serie_p = df_eda.groupby(col_p)[met_p].sum().sort_values(ascending=False)
        serie_pos = serie_p[serie_p > 0]
        acum_p = serie_pos.cumsum() / serie_pos.sum() * 100
        n_80 = int((acum_p < 80).sum() + 1)
        filas_pareto.append({
            "Dimensión": etiq_p,
            "Categorías activas": len(serie_pos),
            "Categorías para el 80% (Pareto)": f"{n_80} ({n_80 / len(serie_pos) * 100:.1f}%)",
            "Acumulado exacto (%)": round(float(acum_p.iloc[n_80 - 1]), 1),
        })
    resumen_pareto = pd.DataFrame(filas_pareto).set_index("Dimensión")

    con_bruta = lineas_venta[lineas_venta["gross_sales"] > 0]
    profundidad = con_bruta["discount_total"] / con_bruta["gross_sales"] * 100
    tramos = pd.cut(
        profundidad,
        bins=[-np.inf, 0, 10, 20, 30, np.inf],
        labels=["Sin descuento", "Hasta 10%", "10% a 20%", "20% a 30%", "Más de 30%"],
    )
    por_tramo = con_bruta.groupby(tramos, observed=True).agg(lineas=("line_id", "size"), venta=("net_sales", "sum"))
    por_tramo["% de líneas"] = por_tramo["lineas"] / por_tramo["lineas"].sum() * 100
    por_tramo["% de venta neta"] = por_tramo["venta"] / por_tramo["venta"].sum() * 100
    costo_tramo = (
        con_bruta[con_bruta["cogs"] > 0]
        .groupby(tramos[con_bruta["cogs"] > 0], observed=True)[["margin", "net_sales"]]
        .sum()
    )
    por_tramo["Margen (%)"] = costo_tramo["margin"] / costo_tramo["net_sales"] * 100

    return {
        "resumen_departamento": resumen_dept,
        "venta_subclase": venta_subclase,
        "peso_top12_subclase": peso_top12_subclase,
        "margen_clase": margen_clase,
        "peso_top7_clase": peso_top7_clase,
        "margen_marca": margen_marca,
        "margen_marca_pct": margen_marca_pct,
        "peso_top12_marca": peso_top12_marca,
        "por_tramo": por_tramo,
        "muestra_desc": con_bruta.sample(n=5_000, random_state=42),
        "resumen_pareto": resumen_pareto,
    }


def analizar_clientes_y_geografia(vista: VistaEDA, tickets_venta: pd.DataFrame) -> dict[str, Any]:
    """Calcula recurrencia en vista temporal sin CLIENTE_ANONIMO y geografía web por ZIP."""
    df_eda = vista.df_eda
    es_anonimo = df_eda["customer_id"] == "CLIENTE_ANONIMO"
    pct_filas_excl = float(es_anonimo.mean() * 100)
    pct_ventas_excl = float(df_eda.loc[es_anonimo, "net_sales"].sum() / vista.ventas_netas_eda * 100)

    tickets_ident = tickets_venta[tickets_venta["cliente"] != "CLIENTE_ANONIMO"]
    clientes = tickets_ident.groupby("cliente").agg(compras=("importe", "size"), gasto=("importe", "sum"))

    frecuencia = pd.cut(clientes["compras"], bins=[0, 1, 2, 5, np.inf], labels=["1", "2", "3 a 5", "6 o más"])
    resumen_frec = clientes.groupby(frecuencia, observed=True).agg(clientes=("compras", "size"), gasto=("gasto", "sum"))
    resumen_frec["% de clientes"] = resumen_frec["clientes"] / resumen_frec["clientes"].sum() * 100
    resumen_frec["% de la venta"] = resumen_frec["gasto"] / resumen_frec["gasto"].sum() * 100
    resumen_frec["Gasto promedio por cliente (USD)"] = resumen_frec["gasto"] / resumen_frec["clientes"]

    envios_web = df_eda.loc[df_eda["is_web"] & ~vista.es_devolucion, ["ship_to_postal", "net_sales"]]
    zip5 = envios_web["ship_to_postal"].str.extract(r"^(\d{5})(?:-\d{4})?$")[0]
    venta_zip = envios_web.groupby(zip5)["net_sales"].sum()
    top_zip = venta_zip.nlargest(15).sort_values()
    venta_region = envios_web.groupby(zip5.str[0])["net_sales"].sum()
    cuota_region_dig = venta_region / venta_region.sum() * 100

    tabla_clientes = resumen_frec[["clientes", "% de clientes", "% de la venta", "Gasto promedio por cliente (USD)"]].rename(
        columns={
            "clientes": "Clientes identificados",
            "% de la venta": "% del importe de tickets sin devoluciones",
            "Gasto promedio por cliente (USD)": "Importe medio de tickets sin devoluciones por cliente (USD)",
        }
    )

    return {
        "pct_filas_excluidas": pct_filas_excl,
        "pct_ventas_excluidas": pct_ventas_excl,
        "n_clientes": int(len(clientes)),
        "pct_recurrentes": float((clientes["compras"] > 1).mean() * 100),
        "resumen_frecuencia": resumen_frec,
        "tabla_clientes": tabla_clientes,
        "cuota_region_dig": cuota_region_dig,
        "top_zip": top_zip,
        "pct_zip_valido": float(zip5.notna().mean() * 100),
        "zips_distintos": int(zip5.nunique()),
        "peso_top15_zip": float(top_zip.sum() / venta_zip.sum() * 100),
    }
