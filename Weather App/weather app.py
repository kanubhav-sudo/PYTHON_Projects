# analysis.py
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# Config
# -----------------------------
DATA_PATH = "data/india_weather.csv"        # set your CSV path
OUTPUT_DIR = "outputs"
CITY_FILTER = "Delhi"                        # set None to analyze all cities
SEED = 42

os.makedirs(OUTPUT_DIR, exist_ok=True)
np.random.seed(SEED)
sns.set(style="whitegrid", context="notebook")

# -----------------------------
# Task 1: Data acquisition & loading
# -----------------------------
import kagglehub

# Download latest version
path = kagglehub.dataset_download("zaraavagyan/weathercsv")

print("Path to dataset files:", path)
df = pd.read_csv(path)

print("\n=== Head ===")
print(df.head())
print("\n=== Info ===")
print(df.info())
print("\n=== Describe ===")
print(df.describe(include="all"))

# -----------------------------
# Task 2: Cleaning & processing
# -----------------------------
# Standardize column names (lowercase, underscores)
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

# Identify possible date & metric columns (adjust to your CSV)
candidate_date_cols = [c for c in df.columns if "date" in c or "time" in c]
date_col = candidate_date_cols[0] if candidate_date_cols else None
if date_col is None:
    raise ValueError("No date column found. Please rename your date column to 'date'.")

# Convert date to datetime and set index
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.dropna(subset=[date_col]).sort_values(by=date_col)
df = df.set_index(date_col)

# Choose relevant columns (edit names to match your file)
# Try common variants: temperature max/min, rainfall, humidity
col_map_candidates = {
    "tmax": ["temperature_2m_max", "tmax", "temp_max", "max_temp"],
    "tmin": ["temperature_2m_min", "tmin", "temp_min", "min_temp"],
    "rain": ["rain_sum", "rainfall", "precipitation", "precip_sum"],
    "humidity": ["relative_humidity_2m_mean", "humidity", "rh_mean", "avg_humidity"],
}

def pick_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

col_tmax = pick_column(df, col_map_candidates["tmax"])
col_tmin = pick_column(df, col_map_candidates["tmin"])
col_rain = pick_column(df, col_map_candidates["rain"])
col_hum  = pick_column(df, col_map_candidates["humidity"])

selected_cols = [c for c in [col_tmax, col_tmin, col_rain, col_hum, "city"] if c is not None and c in df.columns]
df = df[selected_cols]

# Handle missing values: strategy
# - For temperature/humidity: forward-fill then backward-fill
# - For rainfall: fill NaN with 0 (common for missing rain)
numeric_cols = [c for c in df.columns if c != "city"]
rain_like = [col_rain] if col_rain else []
non_rain = [c for c in numeric_cols if c not in rain_like]

# Forward/backward fill for non-rain metrics
df[non_rain] = df[non_rain].ffill().bfill()

# Fill rainfall NaNs with 0
if col_rain:
    df[col_rain] = df[col_rain].fillna(0)

# Optional: filter by city
if "city" in df.columns and CITY_FILTER is not None:
    df = df[df["city"].str.lower() == CITY_FILTER.lower()]

# -----------------------------
# Task 3: Statistics with NumPy
# -----------------------------
def summarize_array(arr):
    arr = np.asarray(arr, dtype=float)
    return {
        "mean": float(np.nanmean(arr)),
        "min": float(np.nanmin(arr)),
        "max": float(np.nanmax(arr)),
        "std": float(np.nanstd(arr, ddof=1)) if len(arr) > 1 else float("nan"),
    }

daily_stats = {col: summarize_array(df[col].values) for col in numeric_cols}

# Monthly and yearly resamples
monthly = df.resample("M").agg({
    col_tmax: "mean",
    col_tmin: "mean",
    col_rain: "sum" if col_rain else "mean",
    col_hum:  "mean" if col_hum else "mean"
})
yearly = df.resample("Y").agg({
    col_tmax: "mean",
    col_tmin: "mean",
    col_rain: "sum" if col_rain else "mean",
    col_hum:  "mean" if col_hum else "mean"
})

monthly_stats = {col: summarize_array(monthly[col].values) for col in monthly.columns}
yearly_stats  = {col: summarize_array(yearly[col].values)  for col in yearly.columns}

print("\n=== Daily stats (NumPy) ===")
print(daily_stats)
print("\n=== Monthly stats (NumPy) ===")
print(monthly_stats)
print("\n=== Yearly stats (NumPy) ===")
print(yearly_stats)

# -----------------------------
# Task 4: Visualization with Matplotlib
# -----------------------------
# 1) Line chart: daily temperature trend (use max temp if available)
plot_temp_col = col_tmax or col_tmin
if plot_temp_col:
    plt.figure(figsize=(10, 4))
    df[plot_temp_col].plot(color="tomato", linewidth=1)
    plt.title(f"Daily {plot_temp_col.replace('_',' ').title()} Trend")
    plt.xlabel("Date")
    plt.ylabel("°C")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "daily_temperature_trend.png"), dpi=200)
    plt.close()

# 2) Bar chart: monthly rainfall totals
if col_rain:
    monthly_rain = df[col_rain].resample("M").sum()
    plt.figure(figsize=(10, 4))
    monthly_rain.plot(kind="bar", color="steelblue")
    plt.title("Monthly Rainfall Totals")
    plt.xlabel("Month")
    plt.ylabel("Rainfall")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "monthly_rainfall_totals.png"), dpi=200)
    plt.close()

# 3) Scatter: humidity vs temperature (use mean temp if both exist)
if col_hum and (col_tmax or col_tmin):
    # Create a derived daily mean temperature if both exist
    if col_tmax and col_tmin:
        df["temp_mean"] = (df[col_tmax] + df[col_tmin]) / 2.0
        x_col = "temp_mean"
    else:
        x_col = plot_temp_col

    plt.figure(figsize=(6, 6))
    sns.scatterplot(x=df[x_col], y=df[col_hum], s=20, alpha=0.7)
    plt.title("Humidity vs Temperature")
    plt.xlabel("Temperature (°C)")
    plt.ylabel("Relative Humidity (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "humidity_vs_temperature.png"), dpi=200)
    plt.close()

# 4) Combined figure: line + bar (temp & rainfall)
if plot_temp_col and col_rain:
    fig, ax1 = plt.subplots(figsize=(12, 5))
    df[plot_temp_col].rolling(7).mean().plot(ax=ax1, color="darkred", label="7-day mean temp")
    ax1.set_xlabel("Date"); ax1.set_ylabel("Temperature (°C)")
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    df[col_rain].resample("W").sum().plot(ax=ax2, kind="bar", color="skyblue", alpha=0.5)
    ax2.set_ylabel("Weekly Rainfall")
    plt.title("Weekly Rainfall vs 7-Day Mean Temperature")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "combined_figure.png"), dpi=200)
    plt.close()

# -----------------------------
# Task 5: Grouping & aggregation
# -----------------------------
# Group by month number
df["month"] = df.index.month
df["year"] = df.index.year

grouped_by_month = df.groupby("month").agg({
    col_tmax: ["mean", "min", "max"],
    col_tmin: ["mean", "min", "max"],
    col_rain: ["sum", "mean"] if col_rain else ["mean"],
    col_hum:  ["mean", "min", "max"] if col_hum else ["mean"],
})

print("\n=== Grouped by month ===")
print(grouped_by_month)

# Optional: define seasons for India
def season_of_month(m):
    # DJF (Winter): 12,1,2; Pre-monsoon: 3-5; Monsoon: 6-9; Post-monsoon: 10-11
    if m in (12, 1, 2): return "Winter"
    if m in (3, 4, 5):  return "Pre-monsoon"
    if m in (6, 7, 8, 9): return "Monsoon"
    return "Post-monsoon"

df["season"] = df["month"].apply(season_of_month)

grouped_by_season = df.groupby("season").agg({
    col_tmax: ["mean", "min", "max"],
    col_tmin: ["mean", "min", "max"],
    col_rain: ["sum", "mean"] if col_rain else ["mean"],
    col_hum:  ["mean", "min", "max"] if col_hum else ["mean"],
}).sort_index()

print("\n=== Grouped by season ===")
print(grouped_by_season)

# Resample examples: monthly/yearly aggregates
monthly_agg = df.resample("M").agg({
    col_tmax: "mean",
    col_tmin: "mean",
    col_rain: "sum" if col_rain else "mean",
    col_hum:  "mean" if col_hum else "mean",
})
yearly_agg = df.resample("Y").agg({
    col_tmax: "mean",
    col_tmin: "mean",
    col_rain: "sum" if col_rain else "mean",
    col_hum:  "mean" if col_hum else "mean",
})

# -----------------------------
# Task 6: Export & storytelling
# -----------------------------
# Export cleaned data
clean_cols = [c for c in df.columns if c not in ["month", "year", "season"]]
df[clean_cols].to_csv(os.path.join(OUTPUT_DIR, "cleaned_weather.csv"))

print("\n=== Exported cleaned data to outputs/cleaned_weather.csv ===")

# Done: plots saved to outputs/
print("Saved plots: daily_temperature_trend.png, monthly_rainfall_totals.png, humidity_vs_temperature.png, combined_figure.png")
