"""Definición, entrenamiento, validación temporal, inferencia y persistencia de modelos."""

from pathlib import Path
from typing import Any, Callable

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit, train_test_split

from .config import RUTA_ARTEFACTOS_MODELOS, UBICACIONES_OPERATIVAS, VARIABLES_BASE_RL, VARIABLES_CAL_RL
from .evaluacion import metricas_por_horizonte, resumir_metricas_modelo
from .variables import (
    calcular_armonicos_fourier,
    calcular_indicadores_calendario_fecha,
    construir_calendario_minorista,
    construir_dataset_proyeccion_anual,
    construir_todas_las_variables_semanales,
)

# Fábricas por defecto: agregar aquí nuevos candidatos (p. ej. LightGBM) sin tocar el notebook
FABRICAS_MODELOS_DEFECTO: dict[str, Callable[[], Any]] = {
    "Regresión lineal (OLS)": LinearRegression,
    "Boosting de árboles": lambda: GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=2,
        min_samples_leaf=5,
        loss="squared_error",
        random_state=42,
    ),
}


def construir_modelo(nombre: str, fabricas: dict[str, Callable[[], Any]] | None = None) -> Any:
    """Instancia un modelo candidato por nombre a partir del registro configurado."""
    catalogo = fabricas or FABRICAS_MODELOS_DEFECTO
    if nombre not in catalogo:
        raise ValueError(f"Modelo no registrado: {nombre}. Disponibles: {list(catalogo)}")
    return catalogo[nombre]()


def particionar_cronologico(
    datos: pd.DataFrame,
    columnas_iniciales: list[str] = VARIABLES_BASE_RL,
    test_size: float = 0.20,
) -> dict[str, Any]:
    """Divide la serie semanal cronológicamente sin mezclar orden temporal (80/20)."""
    datos_train, datos_test = train_test_split(datos, test_size=test_size, shuffle=False)
    idx_train = datos_train.index
    idx_test = datos_test.index
    y_train = datos.loc[idx_train, "venta_neta"]
    y_test = datos.loc[idx_test, "venta_neta"]
    return {
        "datos_train": datos_train,
        "datos_test": datos_test,
        "idx_train": idx_train,
        "idx_test": idx_test,
        "X_train": datos.loc[idx_train, columnas_iniciales],
        "X_test": datos.loc[idx_test, columnas_iniciales],
        "y_train": y_train,
        "y_test": y_test,
        "media_prueba": float(y_test.mean()),
    }


def ejecutar_ensayo(
    datos: pd.DataFrame,
    idx_train: pd.DatetimeIndex,
    idx_test: pd.DatetimeIndex,
    columnas: list[str],
    nombre_ensayo: str,
    registro_ensayos: list[dict[str, Any]] | None = None,
    fabricas_modelos: dict[str, Callable[[], Any]] | None = None,
    registrar: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Entrena los modelos candidatos sobre el mismo corte cronológico y evalúa métricas."""
    assert datos[columnas].isna().sum().sum() == 0, f"Existen nulos inesperados en {nombre_ensayo}"
    assert datos.index.equals(idx_train.append(idx_test)), "Cambió el universo de semanas"

    X_tr = datos.loc[idx_train, columnas]
    X_te = datos.loc[idx_test, columnas]
    y_train = datos.loc[idx_train, "venta_neta"]
    y_test = datos.loc[idx_test, "venta_neta"]

    mod_ols = construir_modelo("Regresión lineal (OLS)", fabricas_modelos).fit(X_tr, y_train)
    mod_gb = construir_modelo("Boosting de árboles", fabricas_modelos).fit(X_tr, y_train)

    pred_df = pd.DataFrame({
        "Venta real": y_test,
        "Referencia: año anterior": datos.loc[idx_test, "venta_hace_52_semanas"],
        "Referencia: semana anterior": datos.loc[idx_test, "venta_semana_anterior"],
        "Regresión lineal (OLS)": mod_ols.predict(X_te),
        "Boosting de árboles": mod_gb.predict(X_te),
    }, index=idx_test)

    filas = [
        resumir_metricas_modelo("Referencia: año anterior", y_test, pred_df["Referencia: año anterior"]),
        resumir_metricas_modelo("Referencia: semana anterior", y_test, pred_df["Referencia: semana anterior"]),
        resumir_metricas_modelo(
            "Regresión lineal (OLS)", y_test, pred_df["Regresión lineal (OLS)"], y_train, mod_ols.predict(X_tr)
        ),
        resumir_metricas_modelo(
            "Boosting de árboles", y_test, pred_df["Boosting de árboles"], y_train, mod_gb.predict(X_tr)
        ),
    ]
    tabla = pd.DataFrame(filas).set_index("Modelo")

    if registrar and registro_ensayos is not None:
        for modelo_nom, row in tabla.iterrows():
            if modelo_nom.startswith("Referencia:"):
                continue
            registro_ensayos.append({
                "Ensayo": nombre_ensayo,
                "N° var.": len(columnas),
                "Modelo": modelo_nom,
                "MAE (USD)": row["MAE (USD)"],
                "MAE (% media)": row["MAE (% media)"],
                "RMSE (USD)": row["RMSE (USD)"],
                "R²": row["R²"],
                "Sesgo (USD)": row["Sesgo (USD)"],
                "MAE entreno (USD)": row.get("MAE entreno (USD)", np.nan),
                "Prueba / Entreno": row.get("Prueba / Entreno", np.nan),
            })

    return tabla, pred_df, {"OLS": mod_ols, "Boosting": mod_gb}


def evaluar_comparativa_y_tscv(
    datos: pd.DataFrame,
    idx_prueba: pd.DatetimeIndex,
    pred_e2: pd.DataFrame,
    pred_e4a: pd.DataFrame,
    pred_e4b: pd.DataFrame,
    variables_cal: list[str],
    variables_sin_vif: list[str],
    variables_red_fourier: list[str],
    n_splits: int = 5,
    test_size: int = 40,
) -> dict[str, Any]:
    """Evalúa los modelos seleccionados en prueba fija y en validación cruzada temporal."""
    y_test = datos.loc[idx_prueba, "venta_neta"]
    metodos = [
        "Regresión lineal (Base + Cal.)",
        "Modelo Reducido (VIF <= 5)",
        "OLS Reducido + Fourier",
        "Boosting de árboles",
        "Referencia anual",
    ]
    predicciones_prueba = pd.DataFrame({
        "Venta real": y_test,
        "Regresión lineal (Base + Cal.)": pred_e2["Regresión lineal (OLS)"],
        "Modelo Reducido (VIF <= 5)": pred_e4a["Regresión lineal (OLS)"],
        "OLS Reducido + Fourier": pred_e4b["Regresión lineal (OLS)"],
        "Boosting de árboles": pred_e2["Boosting de árboles"],
        "Referencia anual": datos.loc[idx_prueba, "venta_hace_52_semanas"],
    }, index=idx_prueba)

    resultados_modelos = pd.DataFrame([
        resumir_metricas_modelo(nombre, y_test, predicciones_prueba[nombre]) for nombre in metodos
    ]).set_index("Modelo")

    espec_cv = {
        "Regresión lineal (Base + Cal.)": (variables_cal, construir_modelo("Regresión lineal (OLS)")),
        "Modelo Reducido (VIF <= 5)": (variables_sin_vif, construir_modelo("Regresión lineal (OLS)")),
        "OLS Reducido + Fourier": (variables_red_fourier, construir_modelo("Regresión lineal (OLS)")),
        "Boosting de árboles": (variables_cal, construir_modelo("Boosting de árboles")),
    }

    tscv = TimeSeriesSplit(n_splits=n_splits, test_size=test_size)
    registros_tscv = []
    for pliegue, (idx_ent, idx_val) in enumerate(tscv.split(datos), start=1):
        y_ent_cv = datos["venta_neta"].iloc[idx_ent]
        y_val_cv = datos["venta_neta"].iloc[idx_val]
        pred_cv = {
            nombre: clone(estimador).fit(datos[cols].iloc[idx_ent], y_ent_cv).predict(datos[cols].iloc[idx_val])
            for nombre, (cols, estimador) in espec_cv.items()
        }
        pred_cv["Referencia anual"] = datos["venta_hace_52_semanas"].iloc[idx_val].to_numpy()

        for metodo, y_hat in pred_cv.items():
            mae_cv = float(mean_absolute_error(y_val_cv, y_hat))
            registros_tscv.append({
                "Pliegue": f"Pliegue {pliegue}",
                "Método": metodo,
                "MAE (USD)": mae_cv,
                "MAE (% media)": mae_cv / float(y_val_cv.mean()) * 100,
                "RMSE (USD)": float(np.sqrt(mean_squared_error(y_val_cv, y_hat))),
                "R²": float(r2_score(y_val_cv, y_hat)),
            })

    df_tscv = pd.DataFrame(registros_tscv)
    resumen_tscv = (
        df_tscv.groupby("Método", sort=False)
        .agg(
            MAE_medio=("MAE (USD)", "mean"),
            MAE_pct_medio=("MAE (% media)", "mean"),
            MAE_std=("MAE (USD)", "std"),
            RMSE_medio=("RMSE (USD)", "mean"),
            R2_medio=("R²", "mean"),
        )
        .rename(columns={
            "MAE_medio": "MAE medio (USD)",
            "MAE_pct_medio": "MAE medio (% media)",
            "MAE_std": "Desv. MAE (USD)",
            "RMSE_medio": "RMSE medio (USD)",
            "R2_medio": "R² medio",
        })
    )
    return {
        "metodos_comparados": metodos,
        "predicciones_prueba": predicciones_prueba,
        "resultados_modelos": resultados_modelos,
        "df_tscv": df_tscv,
        "resumen_tscv": resumen_tscv,
    }


def evaluar_multiubicacion(
    df: pd.DataFrame,
    variables_cal: list[str],
    variables_red_fourier: list[str],
    ubicaciones: list[str] = UBICACIONES_OPERATIVAS,
    min_semanas: int = 100,
) -> pd.DataFrame:
    """Evalúa la generalización frente a la referencia anual en sucursales con >= min_semanas."""
    fecha = pd.to_datetime(df["date"])
    calendario = construir_calendario_minorista(df, fecha=fecha)
    registros = []

    for loc_nom in ubicaciones:
        _, dat_loc_raw = construir_todas_las_variables_semanales(df, loc_nom, fecha=fecha, calendario_minorista=calendario)
        dat_loc = dat_loc_raw.dropna(subset=variables_red_fourier + ["venta_neta"]).copy()
        if len(dat_loc) < min_semanas:
            continue

        tr_loc, te_loc = train_test_split(dat_loc, test_size=0.20, shuffle=False)
        y_tr, y_te = tr_loc["venta_neta"], te_loc["venta_neta"]
        mu_te = float(y_te.mean())

        p_ref = te_loc["venta_hace_52_semanas"]
        p_cal = construir_modelo("Regresión lineal (OLS)").fit(tr_loc[variables_cal], y_tr).predict(te_loc[variables_cal])
        p_rf = construir_modelo("Regresión lineal (OLS)").fit(tr_loc[variables_red_fourier], y_tr).predict(
            te_loc[variables_red_fourier]
        )
        p_gb = construir_modelo("Boosting de árboles").fit(tr_loc[variables_cal], y_tr).predict(te_loc[variables_cal])

        registros.append({
            "Ubicación": loc_nom,
            "Semanas totales": len(dat_loc),
            "Semanas prueba": len(te_loc),
            "Media prueba (USD)": mu_te,
            "MAE Ref. anual (% media)": mean_absolute_error(y_te, p_ref) / mu_te * 100,
            "MAE OLS Base+Cal. (% media)": mean_absolute_error(y_te, p_cal) / mu_te * 100,
            "MAE OLS Red.+Fourier (% media)": mean_absolute_error(y_te, p_rf) / mu_te * 100,
            "MAE Boosting (% media)": mean_absolute_error(y_te, p_gb) / mu_te * 100,
            "R² OLS Base+Cal.": r2_score(y_te, p_cal),
            "R² OLS Red.+Fourier": r2_score(y_te, p_rf),
        })

    return pd.DataFrame(registros).set_index("Ubicación")


def predecir_semana_puntual(
    fecha_objetivo: pd.Timestamp,
    retail_week: int,
    entradas_rezagos: dict[str, float],
    modelos_entrenados: dict[str, tuple[Any, list[str]]],
    resultados_modelos: pd.DataFrame,
    media_prueba: float,
    datos: pd.DataFrame,
    predicciones_prueba: pd.DataFrame,
    metodos_comparados: list[str],
    retail_year_contraste: int = 2025,
) -> dict[str, Any]:
    """Genera el pronóstico puntual reutilizando calendario y Fourier y contrasta con la semana real."""
    assert 1 <= retail_week <= 53, "La semana minorista debe estar entre 1 y 53"
    fila = {
        **entradas_rezagos,
        **calcular_indicadores_calendario_fecha(fecha_objetivo),
        **calcular_armonicos_fourier(retail_week),
    }
    nueva_semana = pd.DataFrame([fila])

    predicciones = {
        nombre: float(modelo.predict(nueva_semana[cols])[0])
        for nombre, (modelo, cols) in modelos_entrenados.items()
    }
    resumen_puntual = pd.DataFrame([
        {
            "Modelo": nom,
            "Pronóstico puntual (USD)": val,
            "MAE prueba (USD)": resultados_modelos.loc[nom, "MAE (USD)"],
            "MAE prueba (% media)": resultados_modelos.loc[nom, "MAE (% media)"],
            "RMSE prueba (USD)": resultados_modelos.loc[nom, "RMSE (USD)"],
            "RMSE prueba (% media)": resultados_modelos.loc[nom, "RMSE (USD)"] / media_prueba * 100,
            "R² prueba": resultados_modelos.loc[nom, "R²"],
            "Rango ±MAE (USD)": (
                f"${val - resultados_modelos.loc[nom, 'MAE (USD)']:,.0f} a "
                f"${val + resultados_modelos.loc[nom, 'MAE (USD)']:,.0f}"
            ),
            "Rango ±RMSE (USD)": (
                f"${val - resultados_modelos.loc[nom, 'RMSE (USD)']:,.0f} a "
                f"${val + resultados_modelos.loc[nom, 'RMSE (USD)']:,.0f}"
            ),
        }
        for nom, val in predicciones.items()
    ]).set_index("Modelo")

    contraste_real = None
    info_real = None
    sem_real = datos[(datos["retail_year"] == retail_year_contraste) & (datos["retail_week"] == retail_week)]
    if not sem_real.empty and sem_real.index[0] in predicciones_prueba.index:
        fecha_real = sem_real.index[0]
        fila_obs = sem_real.iloc[0]
        fila_pred = predicciones_prueba.loc[fecha_real]
        venta_real = float(fila_pred["Venta real"])
        info_real = {
            "fecha": fecha_real,
            "t_1": float(fila_obs["venta_semana_anterior"]),
            "mm4s": float(fila_obs["media_movil_4s"]),
            "t_52": float(fila_obs["venta_hace_52_semanas"]),
            "venta_real": venta_real,
        }
        contraste_real = pd.DataFrame([
            {
                "Modelo": m,
                "Pronóstico 2025 (USD)": fila_pred[m],
                "Venta real 2025 (USD)": venta_real,
                "Diferencia (USD)": fila_pred[m] - venta_real,
                "Error abs. (USD)": abs(fila_pred[m] - venta_real),
                "Error semana (%)": abs(fila_pred[m] - venta_real) / venta_real * 100,
                "MAE prueba (USD)": resultados_modelos.loc[m, "MAE (USD)"],
                "MAE prueba (% media)": resultados_modelos.loc[m, "MAE (% media)"],
                "RMSE prueba (USD)": resultados_modelos.loc[m, "RMSE (USD)"],
                "Dentro de ±MAE": "Sí" if abs(fila_pred[m] - venta_real) <= resultados_modelos.loc[m, "MAE (USD)"] else "No",
            }
            for m in metodos_comparados
        ]).set_index("Modelo")

    return {
        "nueva_semana": nueva_semana,
        "resumen_puntual": resumen_puntual,
        "contraste_real": contraste_real,
        "info_real": info_real,
    }


def proyectar_horizonte_anual_2025(
    semanal: pd.DataFrame, fecha_corte: str = "2025-01-01"
) -> dict[str, Any]:
    """Entrena hasta el cierre de 2024 y proyecta todo 2025 a escala semanal, mensual y trimestral."""
    datos_anual, vars_anual, vars_anual_fourier = construir_dataset_proyeccion_anual(semanal)
    train_anual = datos_anual.loc[datos_anual.index < fecha_corte]
    test_anual = datos_anual.loc[datos_anual.index >= fecha_corte].copy()

    mod_ols = construir_modelo("Regresión lineal (OLS)").fit(train_anual[vars_anual], train_anual["venta_neta"])
    mod_ols_fourier = construir_modelo("Regresión lineal (OLS)").fit(
        train_anual[vars_anual_fourier], train_anual["venta_neta"]
    )
    test_anual["Proyección anual (OLS)"] = mod_ols.predict(test_anual[vars_anual])
    test_anual["Proyección anual (OLS + Fourier)"] = mod_ols_fourier.predict(test_anual[vars_anual_fourier])

    cols_comp = ["venta_neta", "Proyección anual (OLS)", "Proyección anual (OLS + Fourier)"]
    mensual = test_anual.resample("ME")[cols_comp].sum()
    trimestral = test_anual.resample("QE")[cols_comp].sum()

    real_tot = float(test_anual["venta_neta"].sum())
    pred_ols_tot = float(test_anual["Proyección anual (OLS)"].sum())
    pred_four_tot = float(test_anual["Proyección anual (OLS + Fourier)"].sum())

    media_sem = float(test_anual["venta_neta"].mean())
    media_mes = float(mensual["venta_neta"].mean())
    media_trim = float(trimestral["venta_neta"].mean())

    resumen = pd.DataFrame([
        metricas_por_horizonte("1. Semanal: 52 semanas (OLS)", test_anual["venta_neta"], test_anual["Proyección anual (OLS)"], media_sem),
        metricas_por_horizonte(
            "1. Semanal: 52 semanas (OLS + Fourier)", test_anual["venta_neta"], test_anual["Proyección anual (OLS + Fourier)"], media_sem
        ),
        metricas_por_horizonte("2. Mensual: 12 meses agregados (OLS)", mensual["venta_neta"], mensual["Proyección anual (OLS)"], media_mes),
        metricas_por_horizonte(
            "2. Mensual: 12 meses agregados (OLS + Fourier)", mensual["venta_neta"], mensual["Proyección anual (OLS + Fourier)"], media_mes
        ),
        metricas_por_horizonte(
            "3. Trimestral: 4 trimestres agregados (OLS)", trimestral["venta_neta"], trimestral["Proyección anual (OLS)"], media_trim
        ),
        metricas_por_horizonte(
            "3. Trimestral: 4 trimestres agregados (OLS + Fourier)",
            trimestral["venta_neta"],
            trimestral["Proyección anual (OLS + Fourier)"],
            media_trim,
        ),
    ]).set_index("Horizonte y modelo en 2025")

    return {
        "test_anual": test_anual,
        "mensual": mensual,
        "trimestral": trimestral,
        "real_total_2025": real_tot,
        "pred_total_2025_ols": pred_ols_tot,
        "pred_total_2025_fourier": pred_four_tot,
        "error_pct_ols": (pred_ols_tot - real_tot) / real_tot,
        "error_pct_fourier": (pred_four_tot - real_tot) / real_tot,
        "resumen_horizontes": resumen,
        "modelos_anuales": {"OLS": mod_ols, "OLS + Fourier": mod_ols_fourier},
    }


def guardar_modelo(
    modelo: Any,
    nombre_archivo: str,
    metadatos: dict[str, Any] | None = None,
    directorio: str = RUTA_ARTEFACTOS_MODELOS,
) -> Path:
    """Serializa un modelo entrenado junto con sus metadatos usando joblib."""
    destino_dir = Path(directorio)
    destino_dir.mkdir(parents=True, exist_ok=True)
    ruta = destino_dir / nombre_archivo
    joblib.dump({"modelo": modelo, "metadatos": metadatos or {}}, ruta)
    return ruta


def cargar_modelo(ruta: str | Path) -> tuple[Any, dict[str, Any]]:
    """Carga un modelo serializado con joblib y devuelve (modelo, metadatos)."""
    paquete = joblib.load(ruta)
    return paquete["modelo"], paquete.get("metadatos", {})
