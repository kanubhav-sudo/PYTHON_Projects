import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# -------------------------------
# Task 1: Data Ingestion & Validation
# -------------------------------
def load_data(data_dir="data"):
    all_files = Path(data_dir).glob("*.csv")
    df_list = []
    for file in all_files:
        try:
            df = pd.read_csv(file, on_bad_lines="skip")
            # Add metadata if missing
            if "Building" not in df.columns:
                df["Building"] = file.stem
            if "Date" not in df.columns:
                raise ValueError("Missing Date column")
            df["Date"] = pd.to_datetime(df["Date"])
            df_list.append(df)
        except FileNotFoundError:
            print(f"Missing file: {file}")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    df_combined = pd.concat(df_list, ignore_index=True)
    return df_combined

# -------------------------------
# Task 2: Core Aggregation Logic
# -------------------------------
def calculate_daily_totals(df):
    return df.groupby(["Building", pd.Grouper(key="Date", freq="D")])["kWh"].sum().reset_index()

def calculate_weekly_aggregates(df):
    return df.groupby(["Building", pd.Grouper(key="Date", freq="W")])["kWh"].sum().reset_index()

def building_wise_summary(df):
    return df.groupby("Building")["kWh"].agg(["mean", "min", "max", "sum"]).reset_index()

# -------------------------------
# Task 3: Object-Oriented Modeling
# -------------------------------
class MeterReading:
    def __init__(self, timestamp, kwh):
        self.timestamp = timestamp
        self.kwh = kwh

class Building:
    def __init__(self, name):
        self.name = name
        self.meter_readings = []

    def add_reading(self, reading):
        self.meter_readings.append(reading)

    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.meter_readings)

    def generate_report(self):
        total = self.calculate_total_consumption()
        return f"Building {self.name} consumed {total:.2f} kWh in total."

class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def add_building(self, building):
        self.buildings[building.name] = building

# -------------------------------
# Task 4: Visualization
# -------------------------------
def create_dashboard(df_daily, df_weekly, summary):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Trend Line
    for building in df_daily["Building"].unique():
        subset = df_daily[df_daily["Building"] == building]
        axes[0].plot(subset["Date"], subset["kWh"], label=building)
    axes[0].set_title("Daily Consumption Trend")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("kWh")
    axes[0].legend()

    # Bar Chart
    weekly_avg = df_weekly.groupby("Building")["kWh"].mean()
    axes[1].bar(weekly_avg.index, weekly_avg.values)
    axes[1].set_title("Average Weekly Usage")
    axes[1].set_ylabel("kWh")

    # Scatter Plot
    axes[2].scatter(summary["mean"], summary["max"])
    for i, b in enumerate(summary["Building"]):
        axes[2].text(summary["mean"][i], summary["max"][i], b)
    axes[2].set_title("Peak vs Average Consumption")
    axes[2].set_xlabel("Average kWh")
    axes[2].set_ylabel("Peak kWh")

    plt.tight_layout()
    plt.savefig("dashboard.png")

# -------------------------------
# Task 5: Persistence & Summary
# -------------------------------
def export_results(df_combined, summary):
    df_combined.to_csv("cleaned_energy_data.csv", index=False)
    summary.to_csv("building_summary.csv", index=False)

    total_consumption = df_combined["kWh"].sum()
    highest_building = summary.loc[summary["sum"].idxmax(), "Building"]
    peak_load_time = df_combined.loc[df_combined["kWh"].idxmax(), "Date"]

    with open("summary.txt", "w") as f:
        f.write(f"Total Campus Consumption: {total_consumption:.2f} kWh\n")
        f.write(f"Highest Consuming Building: {highest_building}\n")
        f.write(f"Peak Load Time: {peak_load_time}\n")

# -------------------------------
# Main Execution
# -------------------------------
if __name__ == "__main__":
    df = load_data("data")
    df_daily = calculate_daily_totals(df)
    df_weekly = calculate_weekly_aggregates(df)
    summary = building_wise_summary(df)

    create_dashboard(df_daily, df_weekly, summary)
    export_results(df, summary)

    print("Pipeline executed successfully!")
