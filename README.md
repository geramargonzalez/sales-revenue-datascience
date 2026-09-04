# Jewelry Sales Transactions Dataset

This repository contains sales revenue transaction data extracted from BigQuery (`migrationdatanetsuite.bigQueryToNetsuite.flat_SalesReceipt`, Teamwork Commerce POS system). 

Each record represents an individual receipt item line (item sold or returned) along with store location, product hierarchy, customer attributes, and detailed financial line items. The dataset spans from **January 2022 to August 2026** across physical retail stores and the e-commerce channel.

---

## 1. Dataset Files & Volume

Due to dataset size, the extraction is partitioned into two files. Both files share the identical 40-column schema:

| File Name | Start Date | End Date | Row Count |
| :--- | :--- | :--- | :--- |
| `transactionRevenueSO0124.csv` | 2022-01-02 | 2024-01-01 | 990,369 |
| `transactionRevenueSO24-0826.csv` | 2024-01-01 | 2026-08-31 | 1,446,775 |
| **Combined Total** | **2022-01-02** | **2026-08-31** | **2,437,144** |

---

## 2. Data Dictionary

### Identifiers
| Column | Type | Description |
| :--- | :--- | :--- |
| `line_id` | String | Unique line item ID. One row = one ticket line. Primary key for deduplication. |
| `receipt_id` | String | Transaction/Receipt identifier. Shared across lines within the same receipt. |

### Date & Time (4-5-4 Retail Calendar)
| Column | Type | Description |
| :--- | :--- | :--- |
| `date` | Date | Sale date (store local time). |
| `hour` | Integer | Hour of the day (0–23). |
| `retail_year` | Integer | 4-5-4 Retail calendar year (differs slightly from calendar year). |
| `retail_quarter` | Integer | Retail quarter (1–4). |
| `retail_month` | Integer | Retail month (1–12, structured into 4 or 5 full weeks). |
| `retail_week` | Integer | Retail week of year (1–52, or 53 in leap retail years like 2024). |
| `ly_date_key` | Integer | Equivalent date key from last year (YYYYMMDD) for direct YoY comparison. |
| `date_key` | Integer | Numeric date key in YYYYMMDD format. |

### Location & Channel
| Column | Type | Description |
| :--- | :--- | :--- |
| `location_name` | String | Store or warehouse name (`Web Warehouse` = E-commerce channel). |
| `loc_city` | String | Store city. |
| `loc_state` | String | Store state. |
| `is_web` | Boolean | `TRUE` if sale originated online. Primary reliable channel indicator. |

### Product Hierarchy
| Column | Type | Description |
| :--- | :--- | :--- |
| `item_id` | String | Item SKU identifier. |
| `department` | String | Top-level department (`Jewelry`, `Home & Gifts`, `Beauty`, `System`). |
| `class` | String | Product class (sub-level of department). |
| `subclass1` | String | Product subclass (third tier in product hierarchy). |
| `brand` | String | Brand name. |
| `item_season` | String | Assigned product season. |

### Customer & Associate
| Column | Type | Description |
| :--- | :--- | :--- |
| `customer_id` | String | Unique customer identifier. Key for cohort and retention analysis. |
| `ship_to_postal` | String | Shipping postal code. |
| `associate_id` | String | Sales associate ID tied to the transaction line. |

### Financial Metrics (USD)
| Column | Type | Description |
| :--- | :--- | :--- |
| `qty` | Decimal | Units count (negative for returns). |
| `net_sales` | Decimal | Net sales amount (after discounts and net of returns). Main KPI. |
| `gross_sales` | Decimal | Gross sales amount before discounts. |
| `cogs` | Decimal | Cost of Goods Sold. |
| `margin` | Decimal | Gross margin amount (`net_sales - cogs`). |
| `discount_total` | Decimal | Total line discount applied. |
| `markdown` | Decimal | Price markdown from original MSRP. |

### Promotions
| Column | Type | Description |
| :--- | :--- | :--- |
| `promo_name` | String | Name of applied promotion (null/blank if no promo applied). |
| `promo_amt` | Decimal | Discount amount attributed to the promotion. |

### Returns Management
| Column | Type | Description |
| :--- | :--- | :--- |
| `is_return` | Boolean | `TRUE` if line item is a return (`net_sales` is negative). |
| `return_reason` | String | Stated customer return reason. |
| `return_lag_days` | Integer | Elapsed days between original sale and return processing. |
| `orig_location_name` | String | Original store where item was purchased (helps track cross-store returns). |

### Filtering Flags
| Column | Type | Description |
| :--- | :--- | :--- |
| `rpt_ignored` | Boolean | `TRUE` = exclude from accounting reports (gift cards). Always filter out. |
| `txn_type` | String | Transaction category (`Sale`, `Return`, `Mixed`, `Reversal`, `Reversed`). |
| `is_employee_sale` | Boolean | `TRUE` for employee purchase discount transactions. |
| `is_wholesale` | Boolean | `TRUE` for B2B / wholesale accounts. |

---

## 3. Recommended Data Filtering Rules

To align revenue calculations with official financial accounting, apply the following filters:

1. **Exclude Gift Cards:** Filter out `rpt_ignored = TRUE` (gift card liability entries with $0 COGS; ~$4.62M in 2025).
2. **Exclude Transaction Voids:** Filter out `txn_type IN ('Reversal', 'Reversed')`.
3. **Include Returns:** Retain `is_return = TRUE` rows. Return rows already contain negative values in `net_sales`.
4. **Filter Active Retail Locations:** When evaluating physical store performance, filter out administrative and temporary pop-up locations (`Returns and Holds`, `Non-Sellable Webs`, `Jewelry Studio`).

> [!NOTE]
> **Active Operational Locations (14):**
> Web Warehouse, SOHO, Williamsburg, Rockefeller Center, Boston Newbury, San Francisco, Georgetown, Chicago, Larchmont, LA Culver City, Philadelphia, Atlanta, Seattle, and Wedding Annex.

---

## 4. Control Totals Benchmark

Validate data loading pipelines by matching Net Sales (in Millions USD) after applying filtering rules 1 & 2:

| Retail Year | Net Sales ($M) | YoY Growth | Status |
| :--- | :--- | :--- | :--- |
| **2022** | $49.77M | — | Baseline |
| **2023** | $56.40M | +13.3% | Full Year |
| **2024** | $63.61M | +12.8% | Full Year (53 weeks) |
| **2025** | $72.50M | +14.0% | Full Year |
| **2026** | $41.11M | Partial | Jan – Aug |

---

## 5. Domain Notes & Analytical Considerations

> [!IMPORTANT]
> **E-Commerce Channel Identification:**
> Do **NOT** use `loc_ecommerce_flag` from legacy data sources (it incorrectly flags Williamsburg and Wedding Annex as online stores). Always use the **`is_web`** boolean column as the authoritative channel indicator.

- **4-5-4 Retail Calendar Alignment:** The `retail_*` fields align weeks year-over-year (ensuring Holiday / Black Friday weeks match exact comparative weeks). Note that 2024 is a 53-week retail year.
- **Return Dynamics:** Customer returns account for ~10% of gross revenue annually, peaking in January (up to 27%). Return rates vary significantly by store (e.g., Williamsburg ~17% vs. Boston ~7%).
- **Seasonality & Concentration:** Q4 (November & December) accounts for approximately 32% of total annual sales volume. E-commerce (`is_web = TRUE`) represents ~62% of overall net sales.
- **Wedding Annex Outlier Segment:** The *Wedding Annex* location represents high-ticket custom transactions (approx. 50 orders/month with an average order value of ~$2,000 USD). It is recommended to segment this location separately from standard retail store analytics.

---

## 6. Dataset Technical Metadata

- **Source System:** Teamwork Commerce POS / BigQuery `migrationdatanetsuite.bigQueryToNetsuite.flat_SalesReceipt`
- **Data Granularity:** One row per ticket line (`line_id`)
- **Currency:** USD ($)
