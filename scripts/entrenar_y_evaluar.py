"""Pipeline CLI reutilizable para entrenar, evaluar y guardar modelos semanales."""

import argparse
from pathlib import Path
import sys

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from src import config, datos, evaluacion, modelos, variables  # noqa: E402


def ejecutar_pipeline(ubicacion: str, guardar_artefactos: bool) -> None:
    """Ejecuta carga, limpieza, ingeniería incremental, evaluación y guardado de modelos."""
    df_raw = datos.cargar_y_anonimizar(config.RUTA_DATASET_COMBINADO)
    datos.validar_contrato_carga(df_raw)
    df_filtrado, _ = datos.filtrar_registros_contables(df_raw)
    df, control = datos.imputar_valores_faltantes(df_filtrado)

    semanal, datos_rl, _ = variables.construir_serie_semanal_base(df, ubicacion=ubicacion)
    particion = modelos.particionar_cronologico(datos_rl, config.VARIABLES_BASE_RL)
    idx_train, idx_test = particion["idx_train"], particion["idx_test"]

    registro = []
    tabla_e1, _, _ = modelos.ejecutar_ensayo(
        datos_rl, idx_train, idx_test, config.VARIABLES_BASE_RL, "1. Base (t-1 y t-52)", registro
    )

    semanal, datos_rl = variables.agregar_calendario_comercial(semanal, datos_rl)
    _, pred_e2, modelos_e2 = modelos.ejecutar_ensayo(
        datos_rl, idx_train, idx_test, config.VARIABLES_CAL_RL, "2. Base + Calendario", registro
    )

    semanal, datos_rl = variables.agregar_historia_extendida(semanal, datos_rl)
    modelos.ejecutar_ensayo(
        datos_rl, idx_train, idx_test, config.VARIABLES_SOLO_HIST_RL, "3a. Base + Historia (sin cal.)", registro
    )
    modelos.ejecutar_ensayo(
        datos_rl, idx_train, idx_test, config.VARIABLES_COMPLETO_SIN_FOURIER_RL, "3b. Base + Cal. + Historia", registro
    )

    vars_sin_vif, _, _ = variables.podar_por_vif(datos_rl.loc[idx_train], config.VARIABLES_COMPLETO_SIN_FOURIER_RL)
    _, pred_e4a, modelos_e4a = modelos.ejecutar_ensayo(
        datos_rl, idx_train, idx_test, vars_sin_vif, "4a. Reducido (VIF <= 5)", registro
    )

    semanal, datos_rl = variables.agregar_fourier(semanal, datos_rl)
    vars_red_fourier = vars_sin_vif + config.VARIABLES_FOURIER_RL
    _, pred_e4b, modelos_e4b = modelos.ejecutar_ensayo(
        datos_rl, idx_train, idx_test, vars_red_fourier, "4b. Reducido + Fourier", registro
    )

    res_cv = modelos.evaluar_comparativa_y_tscv(
        datos_rl, idx_test, pred_e2, pred_e4a, pred_e4b,
        config.VARIABLES_CAL_RL, vars_sin_vif, vars_red_fourier,
    )
    evaluacion.verificar_cierre_contable(
        df, control["nulos_rezago_previos"], datos_rl.loc[idx_train], datos_rl.loc[idx_test]
    )

    print(f"Ubicación: {ubicacion} | Base contable net_sales: ${df['net_sales'].sum():,.2f}")
    print("\n--- Resultados en prueba (80/20 cronológico) ---")
    print(res_cv["resultados_modelos"].round(2).to_string())
    print("\n--- Validación cruzada temporal (TimeSeriesSplit 5 pliegues) ---")
    print(res_cv["resumen_tscv"].round(2).to_string())

    if guardar_artefactos:
        slug = ubicacion.lower().replace(" ", "_")
        modelos.guardar_modelo(
            modelos_e2["OLS"],
            f"ols_base_calendario_{slug}.joblib",
            {"ubicacion": ubicacion, "variables": config.VARIABLES_CAL_RL},
        )
        modelos.guardar_modelo(
            modelos_e4b["OLS"],
            f"ols_reducido_fourier_{slug}.joblib",
            {"ubicacion": ubicacion, "variables": vars_red_fourier},
        )
        print(f"\nModelos guardados en {config.RUTA_ARTEFACTOS_MODELOS}/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena y evalúa los modelos semanales por ubicación.")
    parser.add_argument("--ubicacion", default="Williamsburg", help="Nombre de ubicación operativa.")
    parser.add_argument("--guardar", action="store_true", help="Guarda modelos entrenados con joblib.")
    args = parser.parse_args()
    ejecutar_pipeline(args.ubicacion, args.guardar)


if __name__ == "__main__":
    main()
