"""Construcción de series semanales W-SAT e ingeniería incremental de variables."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from .config import (
    FECHA_FIN_EDA,
    FECHA_INICIO_EDA,
    INDICADORES_EVENTOS_RL,
    UBICACIONES_OPERATIVAS,
    UMBRAL_VIF,
    VARIABLES_BASE_RL,
    VARIABLES_FOURIER_RL,
    VARIABLES_HISTORIA_EXT_RL,
)


def construir_calendario_minorista(df: pd.DataFrame, fecha: pd.Series | None = None) -> pd.DataFrame:
    """Extrae la tabla de correspondencia semanal W-SAT -> (retail_year, retail_week)."""
    fecha_ser = pd.to_datetime(df["date"]) if fecha is None else fecha
    calendario_diario = pd.DataFrame({
        "date": fecha_ser,
        "retail_year": df["retail_year"],
        "retail_week": df["retail_week"],
    }).drop_duplicates()
    assert not calendario_diario["date"].duplicated().any(), (
        "Una fecha pertenece a más de una semana minorista"
    )
    return calendario_diario.sort_values("date").set_index("date").resample("W-SAT").last()


def construir_serie_semanal_base(
    df: pd.DataFrame,
    ubicacion: str,
    fecha: pd.Series | None = None,
    calendario_minorista: pd.DataFrame | None = None,
    fecha_inicio: str = FECHA_INICIO_EDA,
    fecha_fin: str = FECHA_FIN_EDA,
    validar_ubicacion: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Construye la serie semanal W-SAT de una ubicación y la vista base con t-1 y t-52."""
    if validar_ubicacion:
        assert ubicacion in UBICACIONES_OPERATIVAS, "Elegí una ubicación válida de UBICACIONES_OPERATIVAS"

    fecha_ser = pd.to_datetime(df["date"]) if fecha is None else fecha
    if calendario_minorista is None:
        calendario_minorista = construir_calendario_minorista(df, fecha=fecha_ser)

    mascara = df["location_name"].eq(ubicacion) & fecha_ser.ge(fecha_inicio) & fecha_ser.lt(fecha_fin)
    ventas_loc = df.loc[mascara, ["date", "net_sales"]].copy()
    ventas_loc["date"] = pd.to_datetime(ventas_loc["date"])

    semanal = (
        ventas_loc.set_index("date")["net_sales"]
        .resample("W-SAT")
        .sum(min_count=1)
        .to_frame("venta_neta")
    )
    semanas_cerradas = (
        (semanal.index - pd.Timedelta(days=6) >= pd.Timestamp(fecha_inicio))
        & (semanal.index < pd.Timestamp(fecha_fin))
    )
    semanal = semanal.loc[semanas_cerradas].copy().join(calendario_minorista, how="left")
    assert semanal[["retail_year", "retail_week"]].notna().all().all(), (
        "Faltan claves del calendario minorista"
    )

    semanal["venta_semana_anterior"] = semanal["venta_neta"].shift(1)
    semanal["venta_hace_52_semanas"] = semanal["venta_neta"].shift(52)

    historico_anual = (
        semanal.assign(rw_52=semanal["retail_week"].clip(upper=52), fecha_ref_rw=semanal.index)
        .groupby(["retail_year", "rw_52"])[["venta_neta", "fecha_ref_rw"]]
        .last()
        .reset_index()
    )
    historico_anual["retail_year"] = historico_anual["retail_year"] + 1
    historico_anual = historico_anual.rename(columns={"venta_neta": "venta_anio_anterior"})
    semanal["rw_52"] = semanal["retail_week"].clip(upper=52)
    semanal = (
        semanal.reset_index()
        .merge(
            historico_anual[["retail_year", "rw_52", "venta_anio_anterior", "fecha_ref_rw"]],
            on=["retail_year", "rw_52"],
            how="left",
            validate="many_to_one",
        )
        .drop(columns=["rw_52"])
        .set_index("date")
        .sort_index()
    )

    continuidad = semanal["venta_neta"].shift(1).rolling(4).count().eq(4)
    datos_base = semanal.loc[continuidad].dropna(subset=VARIABLES_BASE_RL + ["venta_neta"]).copy()
    return semanal, datos_base, int(len(ventas_loc))


def calcular_indicadores_calendario_fecha(fecha_objetivo: pd.Timestamp) -> dict[str, int]:
    """Calcula los 6 indicadores de calendario comercial para una fecha puntual de cierre."""
    mes, dia = fecha_objetivo.month, fecha_objetivo.day
    fecha_prev = fecha_objetivo - pd.Timedelta(days=7)
    es_post = int(
        (fecha_prev.month == 11 and 24 <= fecha_prev.day <= 30)
        or (fecha_prev.month == 12 and fecha_prev.day >= 25)
        or (fecha_prev.month == 2 and 10 <= fecha_prev.day <= 16)
        or (fecha_prev.month == 5 and 7 <= fecha_prev.day <= 13)
    )
    return {
        "es_black_friday": int(mes == 11 and 24 <= dia <= 30),
        "es_previa_navidad": int(mes == 12 and 15 <= dia <= 24),
        "es_cierre_navidad": int(mes == 12 and dia >= 25),
        "es_san_valentin": int(mes == 2 and 10 <= dia <= 16),
        "es_dia_madre": int(mes == 5 and 7 <= dia <= 13),
        "es_post_evento": es_post,
    }


def _sincronizar_columnas(semanal: pd.DataFrame, datos: pd.DataFrame | None, columnas: list[str]) -> pd.DataFrame | None:
    if datos is None:
        return None
    datos_act = datos.copy()
    for col in columnas:
        datos_act[col] = semanal.loc[datos_act.index, col]
    return datos_act


def agregar_calendario_comercial(
    semanal: pd.DataFrame, datos: pd.DataFrame | None = None
) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    """Agrega los 6 indicadores de eventos comerciales conocidos de antemano."""
    sem = semanal.copy()
    mes = sem.index.month
    dia = sem.index.day
    sem["es_black_friday"] = ((mes == 11) & (dia >= 24) & (dia <= 30)).astype(int)
    sem["es_previa_navidad"] = ((mes == 12) & (dia >= 15) & (dia <= 24)).astype(int)
    sem["es_cierre_navidad"] = ((mes == 12) & (dia >= 25)).astype(int)
    sem["es_san_valentin"] = ((mes == 2) & (dia >= 10) & (dia <= 16)).astype(int)
    sem["es_dia_madre"] = ((mes == 5) & (dia >= 7) & (dia <= 13)).astype(int)
    sem["es_post_evento"] = (
        sem["es_black_friday"].shift(1, fill_value=0)
        | sem["es_cierre_navidad"].shift(1, fill_value=0)
        | sem["es_san_valentin"].shift(1, fill_value=0)
        | sem["es_dia_madre"].shift(1, fill_value=0)
    ).astype(int)
    return sem, _sincronizar_columnas(sem, datos, INDICADORES_EVENTOS_RL)


def agregar_historia_extendida(
    semanal: pd.DataFrame, datos: pd.DataFrame | None = None
) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    """Agrega rezago t-2, medias móviles, volatilidad e impulso usando solo información <= t-1."""
    sem = semanal.copy()
    venta_pasada = sem["venta_neta"].shift(1)
    sem["venta_hace_2_semanas"] = sem["venta_neta"].shift(2)
    sem["media_movil_4s"] = venta_pasada.rolling(4).mean()
    sem["media_movil_8s"] = venta_pasada.rolling(8, min_periods=4).mean()
    sem["media_movil_12s"] = venta_pasada.rolling(12, min_periods=4).mean()
    sem["volatilidad_4s"] = venta_pasada.rolling(4).std()
    sem["impulso_4s_12s"] = sem["media_movil_4s"] - sem["media_movil_12s"]
    return sem, _sincronizar_columnas(sem, datos, VARIABLES_HISTORIA_EXT_RL)


def calcular_armonicos_fourier(retail_week: int) -> dict[str, float]:
    """Calcula los 4 armónicos de Fourier de 52 semanas para una semana minorista puntual."""
    angulo = 2.0 * np.pi * min(int(retail_week), 52) / 52.0
    return {
        "fourier_sin_1": float(np.sin(angulo)),
        "fourier_cos_1": float(np.cos(angulo)),
        "fourier_sin_2": float(np.sin(2.0 * angulo)),
        "fourier_cos_2": float(np.cos(2.0 * angulo)),
    }


def agregar_fourier(
    semanal: pd.DataFrame, datos: pd.DataFrame | None = None
) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    """Agrega 2 pares de armónicos estacionales continuos (período = 52 semanas)."""
    sem = semanal.copy()
    angulo = 2.0 * np.pi * sem["retail_week"].clip(upper=52) / 52.0
    sem["fourier_sin_1"] = np.sin(angulo)
    sem["fourier_cos_1"] = np.cos(angulo)
    sem["fourier_sin_2"] = np.sin(2.0 * angulo)
    sem["fourier_cos_2"] = np.cos(2.0 * angulo)
    return sem, _sincronizar_columnas(sem, datos, VARIABLES_FOURIER_RL)


def calcular_vif_tabla(df_vars: pd.DataFrame) -> pd.Series:
    """Calcula el Factor de Inflación de la Varianza (VIF) para cada variable explicativa."""
    vif_vals = {}
    for col in df_vars.columns:
        otras = [c for c in df_vars.columns if c != col]
        r2_col = LinearRegression().fit(df_vars[otras], df_vars[col]).score(df_vars[otras], df_vars[col])
        vif_vals[col] = np.inf if r2_col >= 0.999999 else 1.0 / (1.0 - r2_col)
    return pd.Series(vif_vals, name="VIF")


def podar_por_vif(
    datos_entrenamiento: pd.DataFrame,
    columnas_candidatas: list[str],
    columnas_protegidas: list[str] = VARIABLES_BASE_RL,
    umbral_vif: float = UMBRAL_VIF,
) -> tuple[list[str], pd.DataFrame, list[tuple[str, float]]]:
    """Elimina iterativamente la variable no protegida con mayor VIF hasta cumplir <= umbral."""
    X_ent = datos_entrenamiento[columnas_candidatas].astype(float)
    vif_inicial = calcular_vif_tabla(X_ent)
    restantes = list(columnas_candidatas)
    eliminadas: list[tuple[str, float]] = []

    while True:
        vif_actual = calcular_vif_tabla(X_ent[restantes])
        candidatas = vif_actual[[v for v in restantes if v not in columnas_protegidas]]
        if candidatas.empty or candidatas.max() <= umbral_vif:
            break
        peor_var = str(candidatas.idxmax())
        eliminadas.append((peor_var, float(vif_actual[peor_var])))
        restantes.remove(peor_var)

    vif_final = calcular_vif_tabla(X_ent[restantes])
    tabla_comparativa = pd.DataFrame({
        f"VIF inicial ({len(columnas_candidatas)} var.)": vif_inicial,
        "VIF depurado": vif_final,
    })
    return restantes, tabla_comparativa, eliminadas


def construir_todas_las_variables_semanales(
    df: pd.DataFrame,
    ubicacion: str,
    fecha: pd.Series | None = None,
    calendario_minorista: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Genera serie semanal completa con calendario, historia extendida y Fourier (para multi-ubicación)."""
    semanal, _, _ = construir_serie_semanal_base(
        df,
        ubicacion=ubicacion,
        fecha=fecha,
        calendario_minorista=calendario_minorista,
        validar_ubicacion=False,
    )
    semanal, _ = agregar_calendario_comercial(semanal)
    semanal, _ = agregar_historia_extendida(semanal)
    semanal, _ = agregar_fourier(semanal)
    continuidad = semanal["venta_neta"].shift(1).rolling(4).count().eq(4)
    return semanal, semanal.loc[continuidad].copy()


def construir_dataset_proyeccion_anual(semanal: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Prepara variables conocidas al cierre anual previo para proyectar todo un año sin fuga."""
    anual = semanal.copy()
    anual["media_movil_4s_hace_52s"] = anual["venta_neta"].shift(52).rolling(4, min_periods=1).mean()
    anual["anio_calendario"] = anual.index.year
    cierre_anual = anual.groupby("anio_calendario")["venta_neta"].agg(media_ult12=lambda s: s.tail(12).mean())
    cierre_prev_1 = cierre_anual.copy()
    cierre_prev_1.index += 1
    cierre_prev_2 = cierre_anual.copy()
    cierre_prev_2.index += 2
    anual["ratio_cierre_anual"] = anual["anio_calendario"].map(
        cierre_prev_1["media_ult12"] / cierre_prev_2["media_ult12"]
    ).clip(0.8, 1.2)
    anual["venta_52s_ajustada"] = anual["venta_hace_52_semanas"] * (0.65 + 0.35 * anual["ratio_cierre_anual"])

    vars_anual = ["venta_52s_ajustada", "media_movil_4s_hace_52s"] + INDICADORES_EVENTOS_RL
    vars_anual_fourier = vars_anual + VARIABLES_FOURIER_RL
    datos_anual = anual.dropna(subset=vars_anual_fourier + ["venta_neta"]).copy()
    return datos_anual, vars_anual, vars_anual_fourier
