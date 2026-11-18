"""Carga, anonimización, validación de contrato, limpieza e imputación sin pérdida contable."""

from typing import Any

import numpy as np
import pandas as pd

from .config import (
    COLUMNAS_100_NULAS,
    COLUMNAS_BOOLEANAS,
    COLUMNAS_REQUERIDAS,
    RUTA_DATASET_COMBINADO,
    TIPOS_TRANSACCION_ESPERADOS,
    UMBRAL_POLITICA_DEVOLUCION,
    VENTAS_NETAS_CONTROL,
)

CLASIFICACION_NULOS_NEGOCIO = {
    "return_reason": "No aplicable en ventas; puede faltar en devoluciones",
    "return_lag_days": "No aplicable o desconocido según la operación",
    "orig_location_name": "Origen no aplicable o no informado",
    "ship_to_postal": "Condicional por Canal (Físico vs Web)",
    "subclass1": "Jerarquía de Catálogo (Nivel 3)",
    "markdown": "Financiero (MSRP pleno, rebaja = $0)",
    "brand": "Jerarquía de Catálogo (Artículos genéricos/servicios)",
    "customer_id": "Identificación de Cliente (Venta anónima/Guest)",
    "class": "Jerarquía de Catálogo (Nivel 2)",
    "department": "Jerarquía de Catálogo (Nivel 1 residual)",
    "associate_id": "Operacional (Transacciones automáticas web)",
}


def cargar_y_anonimizar(ruta_csv: str = RUTA_DATASET_COMBINADO) -> pd.DataFrame:
    """Carga el CSV combinado y anonimiza el prefijo de empresa en ubicaciones y marca."""
    df = pd.read_csv(ruta_csv, low_memory=False)
    columnas_privadas = ["location_name", "orig_location_name", "brand"]
    columnas_ausentes = sorted(set(columnas_privadas) - set(df.columns))
    assert not columnas_ausentes, f"Columnas necesarias para anonimizar ausentes: {columnas_ausentes}"

    prefijos = (
        df["location_name"]
        .dropna()
        .drop_duplicates()
        .str.extract(r"^([^ ]+)\s+", expand=False)
        .value_counts()
    )
    token_cliente = prefijos.index[0]
    for columna in ["location_name", "orig_location_name"]:
        df[columna] = df[columna].str.replace(f"{token_cliente} ", "", regex=False)
    df["brand"] = (
        df["brand"]
        .str.replace(f"{token_cliente} Jewelry", "Marca propia", regex=False)
        .str.replace(token_cliente, "Marca propia", regex=False)
    )
    restante = any(
        df[col].astype("string").str.contains(token_cliente, case=False, regex=False, na=False).any()
        for col in columnas_privadas
    )
    assert not restante, "La anonimización dejó referencias al nombre de la empresa"
    return df


def validar_contrato_carga(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    """Valida el contrato de columnas, clave primaria, fechas, categorías e importes."""
    columnas_ausentes = sorted(COLUMNAS_REQUERIDAS - set(df.columns))
    line_id_nulos = int(df["line_id"].isna().sum())
    line_id_duplicados = int(df["line_id"].duplicated(keep=False).sum())
    fecha_validada = pd.to_datetime(df["date"], errors="coerce")
    fechas_invalidas = int(fecha_validada.isna().sum())
    tipos_inesperados = sorted(set(df["txn_type"].dropna()) - TIPOS_TRANSACCION_ESPERADOS)
    booleanos_invalidos = {
        col: int((~df[col].isin([True, False])).sum()) for col in COLUMNAS_BOOLEANAS
    }
    net_sales_validada = pd.to_numeric(df["net_sales"], errors="coerce")
    importes_no_finitos = int((~np.isfinite(net_sales_validada)).sum())

    assert not columnas_ausentes, f"Faltan columnas requeridas: {columnas_ausentes}"
    assert line_id_nulos == 0, f"line_id contiene {line_id_nulos:,} nulos"
    assert line_id_duplicados == 0, f"line_id contiene {line_id_duplicados:,} registros duplicados"
    assert fechas_invalidas == 0, f"date contiene {fechas_invalidas:,} valores inválidos"
    assert not tipos_inesperados, f"Tipos de transacción inesperados: {tipos_inesperados}"
    assert sum(booleanos_invalidos.values()) == 0, f"Valores booleanos inválidos: {booleanos_invalidos}"
    assert importes_no_finitos == 0, f"net_sales contiene {importes_no_finitos:,} valores no finitos"

    resumen = pd.DataFrame({
        "Control": [
            "Columnas requeridas ausentes",
            "line_id nulos",
            "line_id duplicados",
            "Fechas inválidas",
            "Categorías txn_type inesperadas",
            "Valores booleanos inválidos",
            "net_sales no finitos",
        ],
        "Resultado": [
            len(columnas_ausentes),
            line_id_nulos,
            line_id_duplicados,
            fechas_invalidas,
            len(tipos_inesperados),
            sum(booleanos_invalidos.values()),
            importes_no_finitos,
        ],
    })
    return resumen, fecha_validada.min(), fecha_validada.max()


def obtener_esquema_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve la tabla vertical de columnas y tipos de dato del dataset."""
    return pd.DataFrame({"Nombre de Columna": df.columns, "Tipo de Dato": df.dtypes.values})


def filtrar_registros_contables(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Excluye tarjetas de regalo (rpt_ignored) y anulaciones (Reversal/Reversed)."""
    filtro_tarjetas = df["rpt_ignored"] == True
    filtro_anulaciones = df["txn_type"].isin(["Reversal", "Reversed"])
    resumen = {
        "total_inicial": int(len(df)),
        "total_tarjetas": int(filtro_tarjetas.sum()),
        "total_anulaciones": int(filtro_anulaciones.sum()),
        "total_excluidas": int((filtro_tarjetas | filtro_anulaciones).sum()),
    }
    df_limpio = df[~filtro_tarjetas & ~filtro_anulaciones].copy()
    resumen["total_final"] = int(len(df_limpio))
    return df_limpio, resumen


def diagnosticar_rezago_devoluciones(
    df: pd.DataFrame, umbral_politica: int = UMBRAL_POLITICA_DEVOLUCION
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Diagnostica return_lag_days y crea la vista acotada sin alterar df."""
    lag_serie = df.loc[df["is_return"], "return_lag_days"]
    lag_informado = lag_serie.dropna()
    metricas = {
        "lineas_devolucion": int(len(lag_serie)),
        "rezagos_informados": int(len(lag_informado)),
        "sin_rezago": int(lag_serie.isna().sum()),
        "ceros_explicitos": int((lag_informado == 0).sum()),
        "media": float(lag_informado.mean()),
        "mediana": float(lag_informado.median()),
        "p75": float(lag_informado.quantile(0.75)),
        "p90": float(lag_informado.quantile(0.90)),
        "maximo": float(lag_informado.max()),
        "superan_umbral": int((lag_informado > umbral_politica).sum()),
        "pct_superan_umbral": float((lag_informado > umbral_politica).mean() * 100),
    }
    vista = df.loc[df["is_return"], ["return_lag_days"]].copy()
    vista["return_lag_days_analisis"] = vista["return_lag_days"].clip(upper=umbral_politica)
    vista["rezago_recortado"] = vista["return_lag_days"] > umbral_politica
    assert df["return_lag_days"].max() == lag_informado.max(), "Se modificó el rezago original"
    return metricas, vista


def diagnosticar_nulos(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula la tabla de columnas con nulos y los porcentajes de nulos condicionales."""
    total_filas = len(df)
    nulos_conteo = df.isnull().sum()
    df_nulos = pd.DataFrame({
        "Tipo de Dato": df.dtypes,
        "Valores Nulos": nulos_conteo,
        "Porcentaje (%)": ((nulos_conteo / total_filas) * 100).round(2),
    })
    df_nulos = df_nulos[df_nulos["Valores Nulos"] > 0].sort_values(by="Valores Nulos", ascending=False)
    df_nulos["Clasificación de Negocio"] = df_nulos.index.map(CLASIFICACION_NULOS_NEGOCIO)

    df_condicional = pd.DataFrame({
        "Segmento Evaluado": [
            "Web (is_web=True)",
            "Tienda Física (is_web=False)",
            "Devoluciones (is_return=True)",
            "Ventas (is_return=False)",
        ],
        "Variable": ["ship_to_postal", "ship_to_postal", "return_reason", "return_reason"],
        "% Nulos": [
            df[df["is_web"] == True]["ship_to_postal"].isnull().mean() * 100,
            df[df["is_web"] == False]["ship_to_postal"].isnull().mean() * 100,
            df[df["is_return"] == True]["return_reason"].isnull().mean() * 100,
            df[df["is_return"] == False]["return_reason"].isnull().mean() * 100,
        ],
    })
    return df_nulos, df_condicional


def validar_nulos(datos: pd.DataFrame, nulos_rezago_esperados: int) -> pd.Series:
    """Valida los nulos permitidos tras imputación y devuelve su conteo por columna."""
    nulos = datos.isna().sum()
    assert nulos.drop("return_lag_days").sum() == 0, "Quedan nulos fuera de return_lag_days"
    assert nulos["return_lag_days"] == nulos_rezago_esperados, "Se alteraron los nulos originales del rezago"
    return nulos


def imputar_valores_faltantes(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Elimina columnas 100% vacías y aplica imputación semántica conservando todas las filas."""
    filas_previas = len(df)
    columnas_previas = df.shape[1]
    net_sales_previo = float(df["net_sales"].sum())

    columnas_ausentes = sorted(set(COLUMNAS_100_NULAS) - set(df.columns))
    assert not columnas_ausentes, f"Columnas esperadas ausentes: {columnas_ausentes}"
    conteo_no_nulos = df[COLUMNAS_100_NULAS].notna().sum()
    assert conteo_no_nulos.eq(0).all(), (
        f"Columnas con datos que no deben eliminarse: {conteo_no_nulos[conteo_no_nulos > 0].to_dict()}"
    )

    df_tratado = df.drop(columns=COLUMNAS_100_NULAS)
    nulos_rezago_previos = int(df_tratado["return_lag_days"].isna().sum())

    columnas_num_imputadas = ["markdown"]
    for col in columnas_num_imputadas:
        df_tratado[col] = df_tratado[col].fillna(0.0)

    imputaciones_catalogo = {
        "customer_id": "CLIENTE_ANONIMO",
        "brand": "Sin Marca / Genérico",
        "subclass1": "Sin Subclase",
        "class": "Sin Clase",
        "department": "Sin Departamento",
        "associate_id": "SISTEMA_WEB",
    }
    for col, valor in imputaciones_catalogo.items():
        df_tratado[col] = df_tratado[col].fillna(valor)

    df_tratado["ship_to_postal"] = np.where(
        df_tratado["ship_to_postal"].notna(),
        df_tratado["ship_to_postal"],
        np.where(~df_tratado["is_web"], "COMPRA_EN_TIENDA", "NO_DISPONIBLE"),
    )
    df_tratado["return_reason"] = np.where(
        df_tratado["return_reason"].notna(),
        df_tratado["return_reason"],
        np.where(~df_tratado["is_return"], "No aplica (Venta)", "No especificado"),
    )
    df_tratado["orig_location_name"] = np.where(
        df_tratado["orig_location_name"].notna(),
        df_tratado["orig_location_name"],
        np.where(~df_tratado["is_return"], "No aplica (Venta)", "No registrada / Misma tienda"),
    )

    nulos_por_columna = validar_nulos(df_tratado, nulos_rezago_previos)
    resumen_num_cero = pd.DataFrame({
        "Columna": columnas_num_imputadas,
        "Valores Nulos": [int(df_tratado[c].isnull().sum()) for c in columnas_num_imputadas],
        "Mínimo": [float(df_tratado[c].min()) for c in columnas_num_imputadas],
        "Media": [float(df_tratado[c].mean()) for c in columnas_num_imputadas],
        "Máximo": [float(df_tratado[c].max()) for c in columnas_num_imputadas],
    })

    control = {
        "filas_previas": filas_previas,
        "filas_posteriores": len(df_tratado),
        "columnas_previas": columnas_previas,
        "columnas_posteriores": df_tratado.shape[1],
        "net_sales_previo": net_sales_previo,
        "net_sales_posterior": float(df_tratado["net_sales"].sum()),
        "nulos_rezago_previos": nulos_rezago_previos,
        "nulos_por_columna": nulos_por_columna,
        "resumen_num_cero": resumen_num_cero,
    }
    assert abs(control["net_sales_posterior"] - VENTAS_NETAS_CONTROL) < 0.01, "Descuadre de ventas netas"
    return df_tratado, control
