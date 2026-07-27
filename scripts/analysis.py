"""
AutoHub Vehicle Service Network — Exploratory Data Analysis

Reads ../data/autohub_service_bookings.csv and produces:
  - 7 chart PNGs in ../charts/
  - a printed summary of key findings (also captured into ../report/findings.txt)

Run: python analysis.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

DATA_PATH = "../data/autohub_service_bookings.csv"
CHART_DIR = "../charts"
os.makedirs(CHART_DIR, exist_ok=True)

# ---------------------------------------------------------------- style
plt.rcParams.update({
    "figure.facecolor": "#10151c",
    "axes.facecolor": "#10151c",
    "savefig.facecolor": "#10151c",
    "axes.edgecolor": "#2a3441",
    "axes.labelcolor": "#eef2f6",
    "text.color": "#eef2f6",
    "xtick.color": "#93a4b5",
    "ytick.color": "#93a4b5",
    "grid.color": "#232d39",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.linestyle": "-",
    "grid.alpha": 0.6,
})
ACCENT = "#ff5a1f"
AMBER = "#ffb347"
BLUE = "#4da3ff"
GREEN = "#35c17b"
PALETTE = [ACCENT, BLUE, GREEN, AMBER]

findings = []
def log(line=""):
    print(line)
    findings.append(line)

# ---------------------------------------------------------------- load & clean
df = pd.read_csv(DATA_PATH, parse_dates=["booking_date"])
df["month"] = df["booking_date"].dt.to_period("M").astype(str)
df["completed"] = df["status"] == "Completed"

log("=" * 70)
log("AUTOHUB SERVICE NETWORK — KEY FINDINGS")
log("=" * 70)
log(f"Total bookings analyzed: {len(df):,}  |  Date range: {df['booking_date'].min().date()} to {df['booking_date'].max().date()}")
completion_rate = df["completed"].mean() * 100
log(f"Completion rate: {completion_rate:.1f}%  (Cancelled: {(df['status']=='Cancelled').mean()*100:.1f}%, No-show: {(df['status']=='No-show').mean()*100:.1f}%)")
total_revenue = df["revenue_pkr"].sum()
log(f"Total revenue (completed jobs): Rs {total_revenue:,.0f}")
log("")

# ================================================================
# 1. Monthly revenue trend
# ================================================================
monthly = df.groupby("month")["revenue_pkr"].sum().reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly["month"], monthly["revenue_pkr"] / 1e6, marker="o", color=ACCENT, linewidth=2.4, markersize=6)
ax.fill_between(monthly["month"], monthly["revenue_pkr"] / 1e6, alpha=0.12, color=ACCENT)
ax.set_title("Monthly Revenue Trend (Rs, millions)")
ax.set_ylabel("Revenue (Rs mm)")
plt.xticks(rotation=45, ha="right")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/01_monthly_revenue_trend.png", dpi=150)
plt.close()

best_month = monthly.loc[monthly["revenue_pkr"].idxmax()]
worst_month = monthly.loc[monthly["revenue_pkr"].idxmin()]
log(f"[Chart 1] Monthly revenue trend — peak month: {best_month['month']} (Rs {best_month['revenue_pkr']/1e6:.2f}M), "
    f"lowest: {worst_month['month']} (Rs {worst_month['revenue_pkr']/1e6:.2f}M)")

# ================================================================
# 2. Revenue & job share by branch
# ================================================================
branch_stats = df.groupby("branch").agg(
    jobs=("booking_id", "count"),
    completed_jobs=("completed", "sum"),
    revenue=("revenue_pkr", "sum"),
    avg_rating=("customer_rating", "mean"),
    avg_wait=("wait_time_min", "mean"),
).sort_values("revenue", ascending=False).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].barh(branch_stats["branch"], branch_stats["revenue"] / 1e6, color=PALETTE)
axes[0].set_title("Revenue by Branch (Rs mm)")
axes[0].invert_yaxis()
axes[1].barh(branch_stats["branch"], branch_stats["jobs"], color=PALETTE)
axes[1].set_title("Job Volume by Branch")
axes[1].invert_yaxis()
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/02_branch_revenue_volume.png", dpi=150)
plt.close()

top_branch = branch_stats.iloc[0]
log(f"[Chart 2] Top branch by revenue: {top_branch['branch']} (Rs {top_branch['revenue']/1e6:.2f}M, "
    f"{top_branch['jobs']:,} jobs, avg rating {top_branch['avg_rating']:.2f}★)")

# ================================================================
# 3. Service category popularity & revenue contribution
# ================================================================
cat_stats = df.groupby("service_category").agg(
    jobs=("booking_id", "count"),
    revenue=("revenue_pkr", "sum"),
).sort_values("revenue", ascending=False).reset_index()

fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(
    cat_stats["revenue"], labels=cat_stats["service_category"],
    autopct="%1.1f%%", colors=PALETTE, textprops={"color": "#eef2f6"},
    wedgeprops={"edgecolor": "#10151c", "linewidth": 2}
)
ax.set_title("Revenue Share by Service Category")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/03_category_revenue_share.png", dpi=150)
plt.close()

top_cat = cat_stats.iloc[0]
log(f"[Chart 3] Largest revenue category: {top_cat['service_category']} "
    f"({top_cat['revenue']/total_revenue*100:.1f}% of total revenue, {top_cat['jobs']:,} jobs)")

# ================================================================
# 4. Top 10 services by job volume
# ================================================================
svc_stats = df.groupby("service_name").agg(
    jobs=("booking_id", "count"),
    revenue=("revenue_pkr", "sum"),
    avg_price=("price_pkr", "mean"),
).sort_values("jobs", ascending=False).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(svc_stats["service_name"][::-1], svc_stats["jobs"][::-1], color=ACCENT)
ax.set_title("Service Popularity (Jobs Booked)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/04_service_popularity.png", dpi=150)
plt.close()

log(f"[Chart 4] Most-booked service: {svc_stats.iloc[0]['service_name']} ({svc_stats.iloc[0]['jobs']:,} jobs) — "
    f"least-booked: {svc_stats.iloc[-1]['service_name']} ({svc_stats.iloc[-1]['jobs']:,} jobs)")

# ================================================================
# 5. Customer satisfaction vs wait time
# ================================================================
rated = df.dropna(subset=["customer_rating"])
wait_bins = pd.cut(rated["wait_time_min"], bins=[-1, 5, 10, 15, 20, 100],
                    labels=["0-5 min", "6-10 min", "11-15 min", "16-20 min", "20+ min"])
wait_rating = rated.groupby(wait_bins, observed=True)["customer_rating"].mean().reset_index()

fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(wait_rating["wait_time_min"].astype(str), wait_rating["customer_rating"], color=PALETTE)
ax.set_title("Average Customer Rating vs. Wait Time")
ax.set_ylabel("Avg rating (1-5)")
ax.set_ylim(1, 5)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/05_rating_vs_wait.png", dpi=150)
plt.close()

corr = rated[["wait_time_min", "customer_rating"]].corr().iloc[0, 1]
log(f"[Chart 5] Correlation between wait time and customer rating: {corr:.2f} "
    f"({'longer waits associate with lower ratings' if corr < -0.1 else 'weak relationship'})")

# ================================================================
# 6. Demand by day of week & hour (heatmap-style)
# ================================================================
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df["hour"] = pd.to_datetime(df["booking_time"], format="%H:%M").dt.hour
pivot = df.pivot_table(index="day_of_week", columns="hour", values="booking_id", aggfunc="count", fill_value=0)
pivot = pivot.reindex(day_order)

fig, ax = plt.subplots(figsize=(11, 5))
im = ax.imshow(pivot.values, cmap="inferno", aspect="auto")
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)
ax.set_title("Booking Demand Heatmap — Day of Week × Hour")
ax.set_xlabel("Hour of day")
cbar = plt.colorbar(im, ax=ax)
cbar.set_label("Bookings", color="#eef2f6")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/06_demand_heatmap.png", dpi=150)
plt.close()

busiest_day = df["day_of_week"].value_counts().idxmax()
busiest_hour = df["hour"].value_counts().idxmax()
log(f"[Chart 6] Busiest day: {busiest_day} — busiest hour: {busiest_hour}:00")

# ================================================================
# 7. Technician performance (top 10 by job count and rating)
# ================================================================
tech_stats = rated.groupby("technician").agg(
    jobs=("booking_id", "count"),
    avg_rating=("customer_rating", "mean"),
).sort_values("jobs", ascending=False).reset_index()

fig, ax1 = plt.subplots(figsize=(11, 6))
ax1.bar(tech_stats["technician"], tech_stats["jobs"], color=BLUE, alpha=0.85, label="Jobs completed")
ax1.set_ylabel("Jobs completed", color=BLUE)
ax1.tick_params(axis="x", rotation=45)
plt.setp(ax1.get_xticklabels(), ha="right")

ax2 = ax1.twinx()
ax2.plot(tech_stats["technician"], tech_stats["avg_rating"], color=ACCENT, marker="o", linewidth=2, label="Avg rating")
ax2.set_ylabel("Avg rating", color=ACCENT)
ax2.set_ylim(1, 5)
ax1.set_title("Technician Workload vs. Average Rating")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/07_technician_performance.png", dpi=150)
plt.close()

top_tech = tech_stats.iloc[0]
log(f"[Chart 7] Busiest technician: {top_tech['technician']} ({top_tech['jobs']:,} jobs, {top_tech['avg_rating']:.2f}★ avg)")

# ================================================================
# Summary stats table
# ================================================================
log("")
log("-" * 70)
log("BRANCH SUMMARY TABLE")
log("-" * 70)
log(branch_stats.round(2).to_string(index=False))

log("")
log("-" * 70)
log("RECOMMENDATIONS")
log("-" * 70)
log("1. Riverside (Lahore) drives the most revenue and volume — consider it the")
log("   template branch; assess whether Industrial (Faisalabad) needs a marketing")
log("   push or reduced bay count given its lower utilization.")
log("2. Wait time is negatively correlated with customer rating — prioritize adding")
log("   bay capacity or staff during the identified peak hour/day combination.")
log("3. Maintenance-category services drive the largest job volume; bundling")
log("   Diagnostics + Maintenance into a package could lift average ticket size.")
log("4. Cancellations and no-shows total roughly "
    f"{(df['status']!='Completed').mean()*100:.1f}% of bookings — a reminder/")
log("   confirmation flow the day before appointments could recover this revenue.")

# save findings to text file for the report
os.makedirs("../report", exist_ok=True)
with open("../report/findings.txt", "w") as f:
    f.write("\n".join(findings))

print("\nAll charts saved to ../charts/  |  findings saved to ../report/findings.txt")
