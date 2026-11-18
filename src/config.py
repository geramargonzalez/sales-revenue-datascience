"""Constantes de negocio, contratos de esquema, etiquetas y estilo visual del proyecto."""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

RUTA_DATASET_COMBINADO = "dataset/transactionRevenue_combined_2018-0926.csv"
RUTA_ARTEFACTOS_MODELOS = "artefactos_mlops"

VENTAS_NETAS_CONTROL = 392_170_429.26
FILAS_CONTABLES_ESPERADAS = 3_481_156
COLUMNAS_CONTABLES_ESPERADAS = 37
UMBRAL_POLITICA_DEVOLUCION = 90
UMBRAL_VIF = 5.0

FECHA_INICIO_EDA = "2018-01-01"
FECHA_FIN_EDA = "2026-01-01"
ANIOS_COMPLETOS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

CIFRAS_CONTROL = pd.Series({
    2018: 19.10,
    2019: 23.53,
    2020: 23.76,
    2021: 38.08,
    2022: 49.77,
    2023: 56.40,
    2024: 63.61,
    2025: 72.50,
})

COLUMNAS_REQUERIDAS = {
    "line_id", "receipt_id", "date", "hour", "retail_year", "retail_quarter",
    "retail_month", "retail_week", "ly_date_key", "date_key", "location_name",
    "loc_city", "loc_state", "is_web", "item_id", "department", "class",
    "subclass1", "brand", "item_season", "customer_id", "ship_to_postal",
    "associate_id", "qty", "net_sales", "gross_sales", "cogs", "margin",
    "discount_total", "markdown", "promo_name", "promo_amt", "is_return",
    "return_reason", "return_lag_days", "orig_location_name", "rpt_ignored",
    "txn_type", "is_employee_sale", "is_wholesale",
}

TIPOS_TRANSACCION_ESPERADOS = {"Sale", "Return", "Mixed", "Deposit", "Reversal", "Reversed"}
COLUMNAS_BOOLEANAS = ["is_web", "is_return", "rpt_ignored", "is_employee_sale", "is_wholesale"]
COLUMNAS_100_NULAS = ["item_season", "promo_name", "promo_amt"]
COLS_FINANCIERAS = ["gross_sales", "net_sales", "discount_total", "cogs", "margin", "qty", "markdown"]
DEPARTAMENTOS_MERCANCIA = ["Jewelry", "Home & Gifts", "Beauty"]

UBICACIONES_OPERATIVAS = [
    "Web Warehouse", "SOHO", "Williamsburg", "Rockefeller Center Store",
    "BOSTON Newbury", "San Francisco", "Georgetown", "Chicago",
    "Larchmont", "LA Culver City", "Philadelphia", "Atlanta",
    "Seattle", "Wedding Annex",
]

ETIQUETAS_VARIABLES = {
    "gross_sales": "Ventas brutas",
    "net_sales": "Ventas netas",
    "discount_total": "Descuento total",
    "markdown": "Rebaja de precio",
    "cogs": "Costo de mercancía",
    "margin": "Margen registrado",
    "qty": "Unidades",
    "return_lag_days": "Rezago original (días)",
    "return_lag_days_analisis": "Rezago hasta 90 días",
    "return_reason": "Motivo de devolución",
    "orig_location_name": "Ubicación de origen",
    "ship_to_postal": "Código postal de envío",
    "customer_id": "Cliente",
    "brand": "Marca",
    "subclass1": "Subclase",
    "class": "Clase",
    "department": "Departamento",
    "associate_id": "Vendedor",
    "item_season": "Temporada del artículo",
    "promo_name": "Promoción",
    "promo_amt": "Importe promocional",
}

# Grupos de variables para el modelado semanal por ubicación
VARIABLES_BASE_RL = ["venta_semana_anterior", "venta_hace_52_semanas"]
INDICADORES_EVENTOS_RL = [
    "es_black_friday",
    "es_previa_navidad",
    "es_cierre_navidad",
    "es_san_valentin",
    "es_dia_madre",
    "es_post_evento",
]
VARIABLES_HISTORIA_EXT_RL = [
    "venta_hace_2_semanas",
    "media_movil_4s",
    "media_movil_8s",
    "media_movil_12s",
    "volatilidad_4s",
    "impulso_4s_12s",
]
VARIABLES_FOURIER_RL = [
    "fourier_sin_1",
    "fourier_cos_1",
    "fourier_sin_2",
    "fourier_cos_2",
]
VARIABLES_CAL_RL = VARIABLES_BASE_RL + INDICADORES_EVENTOS_RL
VARIABLES_SOLO_HIST_RL = VARIABLES_BASE_RL + VARIABLES_HISTORIA_EXT_RL
VARIABLES_COMPLETO_SIN_FOURIER_RL = VARIABLES_CAL_RL + VARIABLES_HISTORIA_EXT_RL

# Paleta cromática institucional (visualization_standards.md)
COLOR_PRIMARIO = "#1E3A8A"
COLOR_WEB = "#0284C7"
COLOR_COSTO = "#D97706"
COLOR_ALERTA = "#DC2626"
COLOR_MARGEN = "#059669"
COLOR_NEUTRO = "#64748B"
COLOR_NEUTRO_CLARO = "#94A3B8"

TONOS_ANIO = {
    2018: "#E2E8F0",
    2019: "#CBD5E1",
    2020: "#94A3B8",
    2021: "#64748B",
    2022: "#475569",
    2023: "#3B82F6",
    2024: "#0284C7",
    2025: COLOR_PRIMARIO,
}

# Formateadores estándar de ejes
fmt_millones = FuncFormatter(lambda x, _: f"${x / 1e6:,.0f}M")
fmt_porcentaje = FuncFormatter(lambda x, _: f"{x:.0f}%")
fmt_dolares = FuncFormatter(lambda x, _: f"${x:,.0f}" if x == 0 or abs(x) >= 1 else f"${x:g}")


def configurar_estilo_graficos() -> None:
    """Aplica la configuración visual global definida en los estándares del proyecto."""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]
    plt.rcParams["axes.edgecolor"] = "#CCCCCC"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#EEEEEE"
    plt.rcParams["grid.linestyle"] = "--"
