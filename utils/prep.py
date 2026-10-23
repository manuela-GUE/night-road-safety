"""Cleaning, validation and feature engineering for the four BAAC tables."""
from __future__ import annotations

import numpy as np
import pandas as pd

LIGHTING_GROUP = {
    1: "Daylight",
    2: "Dawn / dusk",
    3: "Night, no street lighting",
    4: "Night, no street lighting",  # lighting exists but is switched off
    5: "Night, street lighting on",
}
LIGHTING_ORDER = ["Daylight", "Dawn / dusk", "Night, street lighting on", "Night, no street lighting"]
AREA = {1: "Outside built-up area", 2: "Built-up area"}
ROAD = {1: "Motorway", 2: "National road", 3: "Departmental road", 4: "Local road",
        5: "Off public network", 6: "Car park", 7: "Metropolitan urban road", 9: "Other"}
WEATHER = {1: "Normal", 2: "Light rain", 3: "Heavy rain", 4: "Snow / hail", 5: "Fog / smoke",
           6: "Strong wind / storm", 7: "Dazzling", 8: "Overcast", 9: "Other"}
SEVERITY = {1: "Unhurt", 2: "Killed", 3: "Hospitalised", 4: "Slightly injured"}
ROLE = {1: "Driver", 2: "Passenger", 3: "Pedestrian"}
TRIP = {1: "Home - work", 2: "Home - school", 3: "Shopping", 4: "Professional use",
        5: "Leisure / walk", 9: "Other"}
AGE_BINS = [-1, 17, 24, 34, 49, 64, 120]
AGE_LABELS = ["0-17", "18-24", "25-34", "35-49", "50-64", "65+"]

_VEH = {1: "Bicycle", 2: "Moped (<=50cc)", 30: "Moped (<=50cc)",
        4: "Motorcycle", 5: "Motorcycle", 6: "Motorcycle", 31: "Motorcycle", 32: "Motorcycle",
        33: "Motorcycle", 34: "Motorcycle",
        7: "Car", 8: "Car", 9: "Car", 10: "Van", 11: "Van", 12: "Van",
        13: "Truck", 14: "Truck", 15: "Truck", 16: "Truck", 17: "Truck",
        18: "Bus / coach", 37: "Bus / coach", 38: "Bus / coach"}

VALID_DEP = (
    {f"{i:02d}" for i in range(1, 96) if i != 20}
    | {"2A", "2B", "971", "972", "973", "974", "975", "976", "977", "978", "986", "987", "988"}
)


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.replace("\ufeff", "").strip().lower() for c in df.columns]
    df = df.rename(columns={"accident_id": "num_acc"})
    df["num_acc"] = df["num_acc"].astype(str).str.strip()
    return df


def parse_hour(hrmn: pd.Series) -> pd.Series:
    """'17:30' (2019+) or '1730' (older) -> 17. Invalid -> NaN."""
    s = hrmn.astype(str).str.strip().str.replace(":", "", regex=False).str.zfill(4)
    h = _num(s.str[:2])
    return h.where(h.between(0, 23))


def clean_dep(dep: pd.Series) -> pd.Series:
    """Normalise department codes. Older files store metropolitan codes x10 ('590' = Nord)."""
    d = dep.astype(str).str.strip().str.upper()
    is_dom = d.str.startswith("97")
    if (~is_dom).any() and d[~is_dom].str.endswith("0").mean() > 0.9:  # legacy x10 format
        d = d.replace({"201": "2A0", "202": "2B0"})  # Corsica was coded 201 / 202
        d = d.where(is_dom, d.str[:-1])
    return d.where(~d.str.fullmatch(r"\d"), d.str.zfill(2))


def clean_coords(car: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    lat = _num(car["lat"].astype(str).str.replace(",", ".", regex=False))
    lon = _num(car["long"].astype(str).str.replace(",", ".", regex=False))
    if lat.abs().median() > 90:  # legacy integer format scaled by 1e5
        lat, lon = lat / 1e5, lon / 1e5
    ok = lat.between(-90, 90) & lon.between(-180, 180) & (lat != 0) & (lon != 0)
    return lat.where(ok), lon.where(ok)


def process_year(raw: dict[str, pd.DataFrame], year: int):
    """Return (accidents, users_agg, quality) for one year."""
    car = _clean_columns(raw["caracteristiques"])
    lieux = _clean_columns(raw["lieux"])
    veh = _clean_columns(raw["vehicules"])
    usr = _clean_columns(raw["usagers"])
    for df in (veh, usr):
        df["num_veh"] = df["num_veh"].astype(str).str.strip() if "num_veh" in df else np.nan

    q = {"year": year, "accidents_raw": len(car), "users_raw": len(usr), "vehicles_raw": len(veh),
         "duplicate_accident_ids": int(car["num_acc"].duplicated().sum()),
         "users_orphan": int((~usr["num_acc"].isin(car["num_acc"])).sum())}
    car = car.drop_duplicates("num_acc").reset_index(drop=True)
    lieux = lieux.drop_duplicates("num_acc").set_index("num_acc")
    veh = veh.drop_duplicates(["num_acc", "num_veh"])

    # --- accident-level table -------------------------------------------------
    date = pd.to_datetime(pd.DataFrame({"year": year, "month": _num(car["mois"]),
                                        "day": _num(car["jour"])}), errors="coerce")
    lat, lon = clean_coords(car)
    lum = _num(car["lum"])
    acc = pd.DataFrame({
        "num_acc": car["num_acc"], "year": year, "month": date.dt.month, "dow": date.dt.dayofweek,
        "hour": parse_hour(car["hrmn"]), "dep": clean_dep(car["dep"]), "lum": lum,
        "lighting_group": lum.map(LIGHTING_GROUP), "is_night": lum.isin([3, 4, 5]),
        "area": _num(car["agg"]).map(AREA), "weather": _num(car["atm"]).map(WEATHER),
        "lat": lat.astype("float32"), "lon": lon.astype("float32"),
    })
    acc["road_type"] = acc["num_acc"].map(_num(lieux["catr"])).map(ROAD) if "catr" in lieux else np.nan
    acc["speed_limit"] = acc["num_acc"].map(_num(lieux["vma"])) if "vma" in lieux else np.nan

    # --- users ----------------------------------------------------------------
    usr["grav"] = _num(usr["grav"])
    age = year - _num(usr["an_nais"])
    usr["age_band"] = (pd.cut(age.where(age.between(0, 105)), AGE_BINS, labels=AGE_LABELS)
                       .astype("object").fillna("Unknown"))
    trip = _num(usr["trajet"]) if "trajet" in usr else pd.Series(np.nan, index=usr.index)
    usr["trip"] = trip.map(TRIP).fillna("Unknown")
    usr["role"] = _num(usr["catu"]).map(ROLE).fillna("Unknown")
    usr["severity"] = usr["grav"].map(SEVERITY).fillna("Unknown")

    counts = pd.crosstab(usr["num_acc"], usr["grav"]).reindex(columns=[1, 2, 3, 4], fill_value=0)
    counts.columns = ["n_unhurt", "n_killed", "n_hospitalised", "n_slight"]
    acc = acc.merge(counts, left_on="num_acc", right_index=True, how="left")
    acc[list(counts.columns)] = acc[list(counts.columns)].fillna(0).astype("int32")
    acc["is_fatal"] = acc["n_killed"] > 0

    veh["veh_group"] = _num(veh["catv"]).map(_VEH).fillna("Other")
    usr = usr.merge(veh[["num_acc", "num_veh", "veh_group"]], on=["num_acc", "num_veh"], how="left")
    usr.loc[usr["role"] == "Pedestrian", "veh_group"] = "Pedestrian"
    usr["veh_group"] = usr["veh_group"].fillna("Unknown")
    usr = usr.merge(acc[["num_acc", "dep", "lighting_group"]], on="num_acc", how="inner")
    users_agg = (usr.groupby(["dep", "lighting_group", "veh_group", "role", "age_band", "trip", "severity"],
                             observed=True).size().rename("n").reset_index())
    users_agg.insert(0, "year", year)

    # --- data-quality metrics -------------------------------------------------
    q.update({
        "accidents_clean": len(acc),
        "hour_missing_pct": round(100 * acc["hour"].isna().mean(), 2),
        "lum_missing_pct": round(100 * acc["lum"].isna().mean(), 2),
        "dep_invalid_pct": round(100 * (~acc["dep"].isin(VALID_DEP)).mean(), 2),
        "gps_invalid_pct": round(100 * acc["lat"].isna().mean(), 2),
        "users_age_unknown_pct": round(100 * (usr["age_band"] == "Unknown").mean(), 2),
    })
    return acc, users_agg, q
