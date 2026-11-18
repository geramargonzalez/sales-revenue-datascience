"""Cálculo de métricas, comparativas de ensayos y verificaciones de cierre."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .config import (
    COLUMNAS_CONTABLES_ESPERADAS,
    FILAS_CONTABLES_ESPERADAS,
    INDICADORES_EVENTOS_RL,
    VENTAS_NETAS_CONTROL,
)
from .datos import validar_nulos


def resumir_metricas_modelo(
    nombre_modelo: str,
    y_real: pd.Series,
    y_pred: np.ndarray | pd.Series,
    y_ent_real: pd.Series | None = None,
    y_ent_pred: np.ndarray | pd.Series | None = None,
) -> dict[str, float | str]:
    """Calcula MAE, MAPE, RMSE, R², sesgo medio y razón de generalización Prueba/Entreno."""
    mae_prueba = float(mean_absolute_error(y_real, y_pred))
    fila: dict[str, float | str] = {
        "Modelo": nombre_modelo,
        "MAE (USD)": mae_prueba,
        "MAE (% media)": mae_prueba / float(y_real.mean()) * 100,
        "MAPE (%)": float((np.abs(y_real - y_pred) / y_real).mean() * 100),
        "RMSE (USD)": float(np.sqrt(mean_squared_error(y_real, y_pred))),
        "R²": float(r2_score(y_real, y_pred)),
        "Sesgo (USD)": float(np.mean(y_pred - y_real)),
    }
    if y_ent_real is not None and y_ent_pred is not None:
        mae_ent = float(mean_absolute_error(y_ent_real, y_ent_pred))
        fila["MAE entreno (USD)"] = mae_ent
        fila["Prueba / Entreno"] = mae_prueba / mae_ent if mae_ent > 0 else np.nan
    return fila


def metricas_por_horizonte(
    nombre: str, real: pd.Series, pred: pd.Series | np.ndarray, media_ref: float
) -> dict[str, float | str]:
    """Calcula MAE, MAPE, RMSE y R² para cada horizonte temporal de 2025."""
    mae = float(mean_absolute_error(real, pred))
    return {
        "Horizonte y modelo en 2025": nombre,
        "MAE (USD)": mae,
        "MAE (% media)": mae / float(media_ref) * 100,
        "MAPE (%)": float((np.abs(real - pred) / real).mean() * 100),
        "RMSE (USD)": float(np.sqrt(mean_squared_error(real, pred))),
        "R²": float(r2_score(real, pred)),
    }


def comparar_contra_referencia(
    tabla_base: pd.DataFrame, tabla_nueva: pd.DataFrame, sufijo_nuevo: str = "+ Calendario"
) -> pd.DataFrame:
    """Construye la tabla comparativa de MAE y R² entre dos ensayos consecutivos."""
    modelos = ["Regresión lineal (OLS)", "Boosting de árboles"]
    return pd.DataFrame({
        "MAE Base (USD)": tabla_base.loc[modelos, "MAE (USD)"],
        f"MAE {sufijo_nuevo} (USD)": tabla_nueva.loc[modelos, "MAE (USD)"],
        "Cambio MAE (%)": (tabla_nueva.loc[modelos, "MAE (USD)"] / tabla_base.loc[modelos, "MAE (USD)"] - 1) * 100,
        "R² Base": tabla_base.loc[modelos, "R²"],
        f"R² {sufijo_nuevo}": tabla_nueva.loc[modelos, "R²"],
    })


def resumir_ensayos_1_a_3(etapas: list[tuple[str, int, pd.DataFrame]]) -> pd.DataFrame:
    """Agrupa las métricas clave de los ensayos 1 a 3b en una sola tabla comparativa."""
    filas = [
        {
            "Ensayo": nombre,
            "N° var.": n_vars,
            "MAE Lineal (USD)": tabla.loc["Regresión lineal (OLS)", "MAE (USD)"],
            "R² Lineal": tabla.loc["Regresión lineal (OLS)", "R²"],
            "MAE Boosting (USD)": tabla.loc["Boosting de árboles", "MAE (USD)"],
            "R² Boosting": tabla.loc["Boosting de árboles", "R²"],
        }
        for nombre, n_vars, tabla in etapas
    ]
    return pd.DataFrame(filas).set_index("Ensayo")


def comparar_rezago_364_vs_retail_week(
    datos: pd.DataFrame,
    idx_entrenamiento: pd.DatetimeIndex,
    idx_prueba: pd.DatetimeIndex,
    tabla_e2: pd.DataFrame,
) -> tuple[pd.DataFrame, float, float]:
    """Compara la alineación por 364 días (shift 52) frente al emparejamiento por retail_week."""
    sub_prueba = datos.loc[idx_prueba]
    y_test = datos.loc[idx_prueba, "venta_neta"]
    media_prueba = float(y_test.mean())
    dias_desfase_rw = (sub_prueba.index - pd.to_datetime(sub_prueba["fecha_ref_rw"])).dt.days
    dias_2025 = int(dias_desfase_rw[sub_prueba.index.year == 2025].mode().iloc[0])

    cols_cal_rw = ["venta_semana_anterior", "venta_anio_anterior"] + INDICADORES_EVENTOS_RL
    idx_tr_rw = datos.loc[idx_entrenamiento].dropna(subset=["venta_anio_anterior"]).index
    mod_ols_rw = LinearRegression().fit(datos.loc[idx_tr_rw, cols_cal_rw], datos.loc[idx_tr_rw, "venta_neta"])
    pred_ols_rw = mod_ols_rw.predict(datos.loc[idx_prueba, cols_cal_rw])

    verificacion = pd.DataFrame([
        {
            "Criterio de rezago anual": "Referencia ingenua por retail_week (371 días en 2025)",
            "Días en 2025": dias_2025,
            "MAE prueba (USD)": mean_absolute_error(y_test, sub_prueba["venta_anio_anterior"]),
            "MAE (% media)": mean_absolute_error(y_test, sub_prueba["venta_anio_anterior"]) / media_prueba * 100,
            "R² prueba": r2_score(y_test, sub_prueba["venta_anio_anterior"]),
        },
        {
            "Criterio de rezago anual": "Referencia ingenua por 364 días exactos (shift 52)",
            "Días en 2025": 364,
            "MAE prueba (USD)": mean_absolute_error(y_test, sub_prueba["venta_hace_52_semanas"]),
            "MAE (% media)": mean_absolute_error(y_test, sub_prueba["venta_hace_52_semanas"]) / media_prueba * 100,
            "R² prueba": r2_score(y_test, sub_prueba["venta_hace_52_semanas"]),
        },
        {
            "Criterio de rezago anual": "Regresión lineal (Base + Calendario) con retail_week",
            "Días en 2025": dias_2025,
            "MAE prueba (USD)": mean_absolute_error(y_test, pred_ols_rw),
            "MAE (% media)": mean_absolute_error(y_test, pred_ols_rw) / media_prueba * 100,
            "R² prueba": r2_score(y_test, pred_ols_rw),
        },
        {
            "Criterio de rezago anual": "Regresión lineal (Base + Calendario) con 364 días (elegido)",
            "Días en 2025": 364,
            "MAE prueba (USD)": tabla_e2.loc["Regresión lineal (OLS)", "MAE (USD)"],
            "MAE (% media)": tabla_e2.loc["Regresión lineal (OLS)", "MAE (% media)"],
            "R² prueba": tabla_e2.loc["Regresión lineal (OLS)", "R²"],
        },
    ]).set_index("Criterio de rezago anual")

    mejora_ref = float((verificacion.iloc[1]["MAE prueba (USD)"] / verificacion.iloc[0]["MAE prueba (USD)"] - 1) * 100)
    mejora_ols = float((verificacion.iloc[3]["MAE prueba (USD)"] / verificacion.iloc[2]["MAE prueba (USD)"] - 1) * 100)
    return verificacion, mejora_ref, mejora_ols


def verificar_cierre_contable(
    df: pd.DataFrame,
    nulos_rezago_previos: int,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
) -> dict[str, int | float]:
    """Ejecuta las aserciones de integridad contable y partición cronológica del Bloque 10."""
    assert df.shape == (FILAS_CONTABLES_ESPERADAS, COLUMNAS_CONTABLES_ESPERADAS), "Dimensiones inesperadas del dataset"
    validar_nulos(df, nulos_rezago_previos)
    assert abs(df["net_sales"].sum() - VENTAS_NETAS_CONTROL) < 0.01, "Descuadre de ventas netas"
    assert X_train.index.max() < X_test.index.min(), "La partición debe ser cronológica"
    assert X_test.index.max() < pd.Timestamp("2026-01-01"), "La prueba excede 2025"
    return {
        "filas": int(df.shape[0]),
        "columnas": int(df.shape[1]),
        "ventas_netas": float(df["net_sales"].sum()),
    }
