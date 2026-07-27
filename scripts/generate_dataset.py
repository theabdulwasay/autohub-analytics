"""
Generates a realistic synthetic dataset for the AutoHub multi-branch vehicle
service network: one row per completed/in-progress service booking over a
12-month period across 4 branches.

Run: python generate_dataset.py
Output: ../data/autohub_service_bookings.csv
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(42)

# ---------------------------------------------------------------- reference data
branches = [
    {"name": "AutoHub Downtown",   "city": "Rawalpindi", "bays": 8,  "base_demand": 1.15},
    {"name": "AutoHub Northgate",  "city": "Islamabad",  "bays": 6,  "base_demand": 0.90},
    {"name": "AutoHub Riverside",  "city": "Lahore",     "bays": 10, "base_demand": 1.35},
    {"name": "AutoHub Industrial", "city": "Faisalabad", "bays": 5,  "base_demand": 0.60},
]

services = [
    {"name": "Diagnostic Scan",                  "category": "Diagnostics", "price": 1500,  "duration_min": 30,  "weight": 14},
    {"name": "Oil & Filter Change",               "category": "Maintenance", "price": 4200,  "duration_min": 45,  "weight": 22},
    {"name": "Brake Service",                     "category": "Safety",      "price": 8900,  "duration_min": 90,  "weight": 12},
    {"name": "AC Performance Check",               "category": "Comfort",     "price": 3000,  "duration_min": 60,  "weight": 10},
    {"name": "Battery & Charging Test",            "category": "Electrical",  "price": 800,   "duration_min": 20,  "weight": 9},
    {"name": "Wheel Alignment & Balancing",        "category": "Maintenance", "price": 3500,  "duration_min": 75,  "weight": 13},
    {"name": "Full Inspection (Pre-Purchase)",      "category": "Diagnostics", "price": 6000,  "duration_min": 120, "weight": 5},
    {"name": "Detailing & Paint Protection",       "category": "Comfort",     "price": 12000, "duration_min": 180, "weight": 4},
    {"name": "Transmission Fluid Service",         "category": "Maintenance", "price": 7200,  "duration_min": 90,  "weight": 6},
    {"name": "Suspension Repair",                  "category": "Safety",      "price": 9800,  "duration_min": 110, "weight": 5},
]

technicians = [
    "Kamran Yousuf", "Waqas Ali", "Hina Sultana", "Danish Iqbal", "Aliya Baig",
    "Faisal Mehmood", "Sana Rafiq", "Tariq Jameel", "Nadeem Shah", "Rabia Yousaf",
    "Imran Qureshi", "Mehwish Khan",
]

payment_methods = ["Card", "Cash", "Mobile Wallet", "Bank Transfer"]
payment_weights = [0.42, 0.28, 0.22, 0.08]

vehicle_makes = [
    ("Honda", "Civic"), ("Honda", "City"), ("Toyota", "Corolla"), ("Toyota", "Yaris"),
    ("Suzuki", "Alto"), ("Suzuki", "Cultus"), ("Kia", "Sportage"), ("Hyundai", "Tucson"),
    ("Hyundai", "Elantra"), ("MG", "HS"), ("Suzuki", "WagonR"), ("Toyota", "Fortuner"),
]

first_names = ["Hamza", "Fatima", "Ali", "Zainab", "Bilal", "Ayesha", "Usman", "Sara",
               "Ahmed", "Mahnoor", "Umar", "Komal", "Hassan", "Sadia", "Kashif", "Rimsha",
               "Adeel", "Nida", "Farhan", "Iqra", "Shahid", "Warda", "Junaid", "Amina"]
last_names = ["Riaz", "Sheikh", "Raza", "Malik", "Ahmed", "Noor", "Tariq", "Khalid",
              "Farooq", "Iqbal", "Baig", "Yousaf", "Rafiq", "Jameel", "Shah", "Qureshi"]

statuses = ["Completed", "Completed", "Completed", "Completed", "Cancelled", "No-show"]
status_weights = [0.80, 0.05, 0.05, 0.03, 0.04, 0.03]  # will renormalize below

N_ROWS = 6500
START_DATE = datetime(2025, 8, 1)
END_DATE = datetime(2026, 7, 25)
total_days = (END_DATE - START_DATE).days

def weighted_choice(options, weights, size=None):
    weights = np.array(weights, dtype=float)
    weights /= weights.sum()
    idx = rng.choice(len(options), size=size, p=weights)
    return idx

# ---------------------------------------------------------------- date distribution
# Seasonal effect: more services in monsoon/winter prep months, dip around major holidays.
day_offsets = rng.integers(0, total_days, size=N_ROWS * 2)  # oversample, trim later
dates = [START_DATE + timedelta(days=int(d)) for d in day_offsets]

def seasonal_weight(d):
    month = d.month
    # Higher demand: March-April (post-winter checkup), July-Sep (monsoon prep), Dec (year-end)
    month_factor = {1: 0.85, 2: 0.85, 3: 1.15, 4: 1.2, 5: 1.0, 6: 0.95,
                    7: 1.25, 8: 1.2, 9: 1.1, 10: 0.95, 11: 0.9, 12: 1.1}[month]
    weekday_factor = 0.55 if d.weekday() == 6 else (1.15 if d.weekday() in (4, 5) else 1.0)  # Sun slow, Fri/Sat busy
    return month_factor * weekday_factor

weights = np.array([seasonal_weight(d) for d in dates])
weights /= weights.sum()
chosen_idx = rng.choice(len(dates), size=N_ROWS, replace=False, p=weights)
chosen_dates = [dates[i] for i in chosen_idx]

# ---------------------------------------------------------------- build rows
branch_names = [b["name"] for b in branches]
branch_demand_w = [b["base_demand"] for b in branches]
branch_idx = weighted_choice(branch_names, branch_demand_w, size=N_ROWS)

service_names = [s["name"] for s in services]
service_w = [s["weight"] for s in services]
service_idx = weighted_choice(service_names, service_w, size=N_ROWS)

rows = []
booking_id_start = 100000

for i in range(N_ROWS):
    b = branches[branch_idx[i]]
    s = services[service_idx[i]]
    d = chosen_dates[i]

    hour = int(np.clip(rng.normal(13, 3.2), 7, 20))
    minute = int(rng.choice([0, 15, 30, 45]))
    booking_dt = d.replace(hour=hour, minute=minute)

    technician = rng.choice(technicians)
    payment = payment_methods[weighted_choice(payment_methods, payment_weights)]
    make, model = vehicle_makes[rng.integers(0, len(vehicle_makes))]
    vehicle_year = int(rng.integers(2014, 2025))
    customer = f"{rng.choice(first_names)} {rng.choice(last_names)}"

    status = rng.choice(statuses, p=np.array(status_weights) / sum(status_weights))

    # price varies slightly around base (+/-10%), duration varies +/-15%
    price = round(s["price"] * rng.uniform(0.92, 1.08), -1)
    duration = int(round(s["duration_min"] * rng.uniform(0.85, 1.2)))

    # wait time (minutes from arrival to bay assignment) - busier branches wait longer
    base_wait = 8 if b["name"] != "AutoHub Riverside" else 14
    wait_minutes = max(0, int(rng.normal(base_wait + (5 if hour in (11, 12, 13, 17) else 0), 6)))

    # satisfaction rating (1-5): correlated with wait time and inversely with cancellations
    if status == "Completed":
        base_rating = 4.6 - (wait_minutes / 40) - (0.15 if s["category"] == "Safety" else 0)
        rating = float(np.clip(rng.normal(base_rating, 0.45), 1, 5))
        rating = round(rating * 2) / 2  # round to nearest 0.5
    else:
        rating = np.nan

    revenue = price if status == "Completed" else 0

    rows.append({
        "booking_id": f"JOB-{booking_id_start + i}",
        "booking_date": booking_dt.strftime("%Y-%m-%d"),
        "booking_time": booking_dt.strftime("%H:%M"),
        "day_of_week": booking_dt.strftime("%A"),
        "branch": b["name"],
        "branch_city": b["city"],
        "service_name": s["name"],
        "service_category": s["category"],
        "technician": technician,
        "customer_name": customer,
        "vehicle_make": make,
        "vehicle_model": model,
        "vehicle_year": vehicle_year,
        "payment_method": payment,
        "status": status,
        "price_pkr": round(price, 0),
        "duration_min": duration,
        "wait_time_min": wait_minutes,
        "customer_rating": rating,
        "revenue_pkr": round(revenue, 0),
    })

df = pd.DataFrame(rows)
df = df.sort_values("booking_date").reset_index(drop=True)

out_path = "/home/claude/autohub-analytics/data/autohub_service_bookings.csv"
df.to_csv(out_path, index=False)
print(f"Wrote {len(df):,} rows to {out_path}")
print(df.head())
print("\nStatus breakdown:\n", df["status"].value_counts())
print("\nDate range:", df["booking_date"].min(), "to", df["booking_date"].max())
