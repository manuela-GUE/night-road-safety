"""Quick sanity checks + first look at the hook. Run: python explore.py"""
import pandas as pd

from utils.io import load_processed
from utils.prep import VALID_DEP

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
acc, users, quality = load_processed()

print("\n=== 1. Rows per year ===")
print(acc.groupby("year").size().to_string())

print("\n=== 2. Data quality (per year) ===")
cols = ["duplicate_accident_ids", "hour_missing_pct", "lum_missing_pct", "dep_invalid_pct",
        "gps_invalid_pct", "users_age_unknown_pct", "users_orphan"]
print(pd.DataFrame(quality).set_index("year")[cols].to_string())
print("Invalid department codes:", sorted(set(acc["dep"].astype(str)) - VALID_DEP))

print("\n=== 3. Hook: severity by lighting condition (all years) ===")
g = acc.groupby("lighting_group", observed=True).agg(
    accidents=("num_acc", "size"), killed=("n_killed", "sum"), fatal_pct=("is_fatal", lambda s: round(100 * s.mean(), 2)))
g["share_of_accidents_%"] = (100 * g["accidents"] / g["accidents"].sum()).round(1)
g["share_of_killed_%"] = (100 * g["killed"] / g["killed"].sum()).round(1)
print(g.to_string())

print("\n=== 4. Night share per year (checks for coding changes) ===")
y = acc.groupby("year").agg(night_share_pct=("is_night", lambda s: round(100 * s.mean(), 1)),
                            fatal_pct_night=("is_fatal", lambda s: None))
y["fatal_pct_night"] = acc[acc["is_night"]].groupby("year")["is_fatal"].mean().mul(100).round(2)
y["fatal_pct_day"] = acc[~acc["is_night"]].groupby("year")["is_fatal"].mean().mul(100).round(2)
print(y.to_string())

print("\n=== 5. Fatal-accident rate by hour ===")
h = acc.groupby("hour").agg(accidents=("num_acc", "size"), fatal_pct=("is_fatal", lambda s: round(100 * s.mean(), 2)))
print(h.T.to_string())

print("\n=== 6. Fatal-accident rate (%) by lighting x area / road type (controls for confounders) ===")
for col in ["area", "road_type"]:
    g = (acc.groupby(["lighting_group", col], observed=True)
         .agg(accidents=("num_acc", "size"), fatal_pct=("is_fatal", lambda s: round(100 * s.mean(), 2))).unstack(col))
    print(g["fatal_pct"].to_string(), "\n")
    print(g["accidents"].to_string(), "\n")

print("\n=== 7. Fatal-accident rate (%) by lighting x speed limit (2019+ only) ===")
v = acc[(acc["year"] >= 2019) & acc["speed_limit"].isin([30, 50, 80, 90, 110, 130])]
print(v.pivot_table(index="lighting_group", columns="speed_limit", values="is_fatal", aggfunc="mean", observed=True)
      .mul(100).round(2).to_string())

print("\n=== 8. Night accidents by weekday (0 = Monday) ===")
w = acc[acc["is_night"]].groupby("dow").agg(accidents=("num_acc", "size"), killed=("n_killed", "sum"),
    fatal_pct=("is_fatal", lambda s: round(100 * s.mean(), 2)))
print(w.T.to_string())
