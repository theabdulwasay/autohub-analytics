# AutoHub Analytics — Data Analyst Project

A complete data analyst portfolio project built on top of the AutoHub
multi-branch vehicle service network: a synthetic-but-realistic dataset,
a full exploratory data analysis in Python, and a formula-driven Excel
dashboard — the three artifacts a hiring manager expects to see.

---

## 📦 What's included

```
autohub-analytics/
├── README.md                          # this file
├── AutoHub_Analytics_Dashboard.xlsx    # Excel dashboard (KPIs, pivots, charts — all formulas)
├── data/
│   └── autohub_service_bookings.csv    # 6,500-row synthetic dataset (12 months, 4 branches)
├── scripts/
│   ├── generate_dataset.py            # reproducibly generates the CSV dataset
│   ├── analysis.py                    # pandas + matplotlib EDA — produces all 7 charts
│   └── build_excel_dashboard.py        # builds the Excel workbook from the CSV
├── charts/
│   ├── 01_monthly_revenue_trend.png
│   ├── 02_branch_revenue_volume.png
│   ├── 03_category_revenue_share.png
│   ├── 04_service_popularity.png
│   ├── 05_rating_vs_wait.png
│   ├── 06_demand_heatmap.png
│   └── 07_technician_performance.png
└── report/
    └── findings.txt                   # key findings & recommendations, plain text
```

---

## 🗂 The dataset

`data/autohub_service_bookings.csv` — **6,500 rows**, one per service booking,
covering **12 months** (Aug 2025 – Jul 2026) across AutoHub's 4 branches.

| Column | Description |
|---|---|
| `booking_id` | Unique job ID |
| `booking_date`, `booking_time`, `day_of_week` | When the booking happened |
| `branch`, `branch_city` | Which AutoHub location |
| `service_name`, `service_category` | What was serviced (10 service types, 5 categories) |
| `technician` | Assigned technician (12 staff) |
| `customer_name`, `vehicle_make`, `vehicle_model`, `vehicle_year` | Customer/vehicle info |
| `payment_method` | Card / Cash / Mobile Wallet / Bank Transfer |
| `status` | Completed / Cancelled / No-show |
| `price_pkr`, `duration_min` | Job price and estimated duration |
| `wait_time_min` | Minutes between arrival and bay assignment |
| `customer_rating` | 1–5 star rating (blank if not completed) |
| `revenue_pkr` | Realized revenue (0 for non-completed jobs) |

The data is **synthetic** (generated with a seeded random model, so it's
reproducible), but built with realistic seasonality — busier around
monsoon-prep months and Dec, busier Fri/Sat, a lunchtime peak, higher-revenue
branches getting proportionally more volume, and customer ratings that
genuinely correlate with wait time — so the analysis below reflects patterns
worth practicing on, not noise.

To regenerate it: `cd scripts && python generate_dataset.py`

---

## 📊 The analysis

`scripts/analysis.py` loads the CSV with pandas and produces 7 charts plus a
console/`findings.txt` summary. Run it with:

```bash
cd scripts
pip install pandas numpy matplotlib   # if not already installed
python analysis.py
```

### Key findings (from this run of the data)

- **6,500 bookings** analyzed, **92.9% completion rate** (4.0% cancelled, 3.1% no-show)
- **Total revenue (completed jobs): Rs 28,621,620**
- **AutoHub Riverside** (Lahore) is the top branch — Rs 9.79M revenue, 2,238 jobs, 4.19★ average rating
- **Maintenance** is the largest revenue category (38.1% of total, led by Oil & Filter Change at 1,440 jobs)
- **Wait time and customer rating are negatively correlated (r = -0.32)** — longer waits mean lower ratings
- **Friday at 12:00** is the single busiest day/hour combination network-wide
- Busiest technician: **Imran Qureshi** (543 jobs, 4.26★ average)

### Recommendations

1. Use Riverside's operating pattern as a template; investigate whether Industrial (Faisalabad) needs a marketing push or a smaller bay footprint given its lower utilization.
2. Add bay capacity or staff around the Friday-lunchtime peak — wait time is the clearest lever on customer satisfaction found in this data.
3. Bundle Diagnostics with Maintenance visits to lift average ticket size, since Maintenance already drives the highest job volume.
4. Cancellations + no-shows are ~7.1% of bookings — a day-before reminder/confirmation flow could recover meaningful revenue.

Full findings text (mirrors the console output): `report/findings.txt`

---

## 📈 The Excel dashboard

`AutoHub_Analytics_Dashboard.xlsx` has 5 sheets:

| Sheet | Contents |
|---|---|
| **Dashboard** | KPI cards (total bookings, completed jobs, revenue, avg rating, avg wait) + 4 charts, all formula-driven |
| **Raw Data** | The full 6,500-row dataset, with a `month` helper column |
| **Branch Summary** | Bookings, completion rate, revenue, avg rating, avg wait — one row per branch, computed with `COUNTIF`/`COUNTIFS`/`SUMIFS`/`AVERAGEIFS` |
| **Category Summary** | Same rollups by service category |
| **Monthly Trend** | Jobs and revenue by month |

**Every number is a live formula** referencing the Raw Data sheet — nothing is
hardcoded, so if you edit or extend the raw data, the summaries and charts
recalculate. The workbook has already been recalculated with LibreOffice and
verified to have **zero formula errors**.

To rebuild it from scratch:
```bash
cd scripts
python build_excel_dashboard.py
```

---

## 🛠 Tech stack

- **Python 3** — `pandas`, `numpy`, `matplotlib` for data generation and EDA
- **openpyxl** — for the formula-driven Excel workbook and native Excel charts
- No external services or paid tools required

---

## 🔁 Reproducing everything from scratch

```bash
cd scripts
python generate_dataset.py          # -> ../data/autohub_service_bookings.csv
python analysis.py                  # -> ../charts/*.png, ../report/findings.txt
python build_excel_dashboard.py     # -> ../AutoHub_Analytics_Dashboard.xlsx
```

---

## 💡 Ways to extend this project

- Swap the synthetic CSV for real booking data (same column names → the
  Excel formulas and Python script work unchanged)
- Add a `PowerPoint`/PDF executive summary from the `charts/` folder
- Build a small Streamlit or Dash app on top of `analysis.py` for an
  interactive filter-by-branch/date dashboard
- Add cohort analysis (repeat customers) once real customer IDs are available
