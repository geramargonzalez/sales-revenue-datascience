# Guía del Calendario Minorista NRF 4-5-4 en Joyería

Este documento describe la estructura y lógica de negocio del calendario minorista 4-5-4 utilizado en las variables temporales del dataset (`retail_year`, `retail_quarter`, `retail_month`, `retail_week`).

---

## 1. ¿Qué es el Calendario 4-5-4?

El calendario 4-5-4 es un estándar internacional impulsado por la *National Retail Federation* (NRF) para la industria de venta al por menor (*retail*):
- Divide cada trimestre de 13 semanas en tres bloques mensuales: el primer mes tiene **4 semanas**, el segundo **5 semanas** y el tercero **4 semanas** (4 + 5 + 4 = 13 semanas por trimestre).
- Un año minorista cuenta con exactamente 52 semanas (364 días), agrupadas en 4 trimestres idénticos.
- Asegura que los mismos días de la semana y fines de semana coincidan exactamente año contra año, facilitando la comparación contable de ventas comparables (*Like-for-Like* / *Comp-Store Sales*).

---

## 2. Variables Disponibles en el Dataset

| Variable | Tipo | Descripción y Rango |
| :--- | :--- | :--- |
| `retail_year` | Entero | Año fiscal minorista (ej. 2022, 2023, 2024, 2025, 2026). |
| `retail_quarter` | Entero | Trimestre fiscal minorista (1, 2, 3, 4). Cada trimestre comprende 13 semanas. |
| `retail_month` | Entero | Mes minorista (1 a 12). Corresponde al ciclo de 4 o 5 semanas. |
| `retail_week` | Entero | Semana del año minorista (1 a 52). |

---

## 3. Estacionalidad Característica del Sector Joyería

Al interpretar las tendencias del calendario 4-5-4 en este dataset, tener en cuenta los siguientes picos de demanda característicos:

1. **Trimestre 1 (Q1: Meses 1 a 3 - Febrero a Abril aprox.):**
   - Pico clave en febrero por la festividad de **San Valentín** (alta demanda en anillos, colgantes y joyería fina de regalo).
2. **Trimestre 2 (Q2: Meses 4 a 6 - Mayo a Julio aprox.):**
   - Pico significativo en mayo impulsado por el **Día de la Madre** y temporada temprana de bodas.
3. **Trimestre 3 (Q3: Meses 7 a 9 - Agosto a Octubre aprox.):**
   - Período de menor actividad transaccional relativa (*valle de verano*), habitualmente compensado con campañas de promociones y descuentos.
4. **Trimestre 4 (Q4: Meses 10 a 12 - Noviembre a Enero aprox.):**
   - El período más crítico del año (*Holiday Season*, *Black Friday*, *Cyber Monday*, Navidad y Fin de Año).
   - Históricamente concentra entre el **35% y el 45% del margen y los ingresos anuales** de joyería.
