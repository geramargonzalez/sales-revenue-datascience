"""Extrae un rango de fechas de BigQuery con el esquema de 40 columnas del dataset.

La tabla `transaction_revenue` solo contiene datos desde 2023, por lo que el
histórico previo se lee de `flat_SalesReceipt` (su tabla de origen) aplicando el
mismo mapeo de columnas de `documentation/query.sql`.

Requiere credenciales ADC con acceso al proyecto:
    gcloud auth application-default login

Uso:
    python scripts/extraer_historico_bigquery.py 2018-01-01 2021-12-31 dataset/transactionRevenue_2018-2021.csv
"""

import argparse
from decimal import Decimal

import pandas as pd
from google.cloud import bigquery

PROYECTO = "migrationdatanetsuite"
TABLA_ORIGEN = "migrationdatanetsuite.bigQueryToNetsuite.flat_SalesReceipt"

# Mismo mapeo que documentation/query.sql (orden de columnas idéntico al CSV actual)
CONSULTA = f"""
SELECT
  r.sale.DocumentLineId              AS line_id,
  r.sale.DocumentId                  AS receipt_id,
  r.sale.Date                        AS date,
  r.sale.Hour                        AS hour,
  r.retailcalendar.RetailYear        AS retail_year,
  r.retailcalendar.RetailQuarter     AS retail_quarter,
  r.retailcalendar.RetailMonth       AS retail_month,
  r.retailcalendar.RetailWeek        AS retail_week,
  r.retailcalendar.LYDateKey         AS ly_date_key,
  r.retailcalendar.DateKey           AS date_key,
  r.location.LocationName            AS location_name,
  r.location.City                    AS loc_city,
  r.location.State                   AS loc_state,
  r.sale.IsWebReceipt                AS is_web,
  r.sale.ItemId                      AS item_id,
  r.item.Department                  AS department,
  r.item.Class                       AS class,
  r.item.Subclass1                   AS subclass1,
  r.item.Brand                       AS brand,
  r.item.Season                      AS item_season,
  r.sale.CustomerId                  AS customer_id,
  r.sale.ShipToPostalCode            AS ship_to_postal,
  r.sale.AssociateId                 AS associate_id,
  r.sale.Qty                         AS qty,
  r.sale.NetSalesAmt                 AS net_sales,
  r.sale.GrossSalesAmt               AS gross_sales,
  r.sale.COGS                        AS cogs,
  r.sale.MarginAmt                   AS margin,
  r.sale.DiscountAmt                 AS discount_total,
  r.sale.Markdown                    AS markdown,
  r.sale.PromotionName               AS promo_name,
  r.sale.PromoAmount                 AS promo_amt,
  r.sale.IsReturn                    AS is_return,
  r.sale.ReturnReasonDescription     AS return_reason,
  DATE_DIFF(r.sale.Date, DATE(r.sale.OriginalReceiptDate), DAY) AS return_lag_days,
  r.location.OriginalLocationName    AS orig_location_name,
  r.sale.RptIgnored                  AS rpt_ignored,
  r.sale.TransactionTypeLabel        AS txn_type,
  r.sale.IsEmployeeSale              AS is_employee_sale,
  r.sale.SellToWholesaleCustomer     AS is_wholesale
FROM `{TABLA_ORIGEN}` r
WHERE r.sale.Date BETWEEN @desde AND @hasta
ORDER BY r.sale.Date, r.location.LocationName
"""


def formatear_valor(valor):
    """Replica el formato del CSV exportado: booleanos en minúscula, números sin ceros sobrantes."""
    if valor is None or valor is pd.NA or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, Decimal):
        texto = format(valor, "f")
        if "." in texto:
            texto = texto.rstrip("0").rstrip(".")
        return "0" if texto in ("-0", "") else texto
    return str(valor)


def main():
    parser = argparse.ArgumentParser(description="Extrae histórico de ventas desde BigQuery.")
    parser.add_argument("desde", help="Fecha inicial inclusive (AAAA-MM-DD)")
    parser.add_argument("hasta", help="Fecha final inclusive (AAAA-MM-DD)")
    parser.add_argument("salida", help="Ruta del CSV de salida")
    args = parser.parse_args()

    cliente = bigquery.Client(project=PROYECTO)
    config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("desde", "DATE", args.desde),
        bigquery.ScalarQueryParameter("hasta", "DATE", args.hasta),
    ])
    df = cliente.query(CONSULTA, job_config=config).result().to_dataframe()

    # Todas las columnas se escriben como texto ya formateado para no alterar decimales ni códigos postales
    df_texto = df.astype(object).apply(lambda col: col.map(formatear_valor))
    df_texto.to_csv(args.salida, index=False, lineterminator="\n")

    total = sum((v for v in df["net_sales"] if isinstance(v, Decimal)), Decimal("0"))
    print(f"Filas extraídas: {len(df):,}")
    print(f"Rango: {df['date'].min()} a {df['date'].max()}")
    print(f"net_sales: {total:,.2f}")


if __name__ == "__main__":
    main()
