"""Data access layer: download BAAC files from the data.gouv.fr API (cached on disk),
read raw CSVs robustly, and load the processed parquet files used by the app."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import requests

DATASET_ID = "53698f4ca3a729239d2036df"  # BAAC annual databases (ONISR), 2005-2024
API_URL = f"https://www.data.gouv.fr/api/1/datasets/{DATASET_ID}/"
GEOJSON_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/"
    "departements-version-simplifiee.geojson"
)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_DIR / "raw"
KINDS = ("caracteristiques", "lieux", "vehicules", "usagers")
TIMEOUT = 60

SOURCE_TEXT = (
    "Source: ONISR / Ministère de l'Intérieur - 'Bases de données annuelles des accidents "
    "corporels de la circulation routière' (BAAC), data.gouv.fr. "
    "License: Licence Ouverte (Etalab) - check the dataset page for the exact version."
)


def _classify(name: str) -> str | None:
    t = name.lower()
    if "lieux" in t:
        return "lieux"
    if "vehicule" in t:
        return "vehicules"
    if "usager" in t:
        return "usagers"
    if t.startswith("car"):  # also matches the 'carcteristiques' typo used in some years
        return "caracteristiques"
    return None


def list_resources() -> dict[tuple[int, str], list[tuple[str, str]]]:
    """Return {(year, kind): [(title, url), ...]} by querying the data.gouv.fr API."""
    r = requests.get(API_URL, timeout=TIMEOUT)
    r.raise_for_status()
    found: dict[tuple[int, str], list[tuple[str, str]]] = {}
    for res in r.json().get("resources", []):
        url = res.get("url")
        if not url:
            continue
        title = res.get("title") or ""
        fname = url.rsplit("/", 1)[-1]
        is_csv = (res.get("format") or "").lower() == "csv" or fname.lower().endswith(".csv")
        if not is_csv:
            continue
        kind = _classify(title) or _classify(fname)
        m = re.search(r"(20\d{2})", title) or re.search(r"(20\d{2})", fname)
        if kind and m:
            found.setdefault((int(m.group(1)), kind), []).append((title or fname, url))
    return found


def looks_like_baac(path: Path) -> bool:
    """True if the CSV header has the BAAC accident key (Num_Acc, or Accident_Id in some years)."""
    with open(path, "rb") as f:
        first = f.readline().decode("latin-1").lower()
    return "num_acc" in first or "accident_id" in first


def _fetch(url: str, dest: Path) -> None:
    with requests.get(url, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)


def download_year(year: int, resources: dict, force: bool = False) -> None:
    """Download the 4 BAAC tables of a year. Several resources can match a name, so each
    candidate is checked (header must contain the BAAC accident key) before it is accepted."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for kind in KINDS:
        dest = RAW_DIR / f"{kind}-{year}.csv"
        if dest.exists() and not force and looks_like_baac(dest):
            continue
        candidates = resources.get((year, kind), [])
        if not candidates:
            raise RuntimeError(f"No resource found for {kind} {year}.")
        tmp = dest.with_suffix(".part")
        for title, url in candidates:
            print(f"  downloading {kind} {year}: {title}")
            _fetch(url, tmp)
            if looks_like_baac(tmp):
                tmp.replace(dest)
                break
            print("    -> not a BAAC table (no Num_Acc / Accident_Id column), trying next candidate")
        else:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(f"None of the {len(candidates)} candidate files for {kind} {year} is a BAAC table: "
                               f"{[t for t, _ in candidates]}")


def download_geojson(force: bool = False) -> Path:
    dest = DATA_DIR / "departements.geojson"
    if dest.exists() and not force:
        return dest
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(GEOJSON_URL, timeout=TIMEOUT)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest


def read_raw(kind: str, year: int) -> pd.DataFrame:
    """Read a raw BAAC CSV. Separator (',' before 2019, ';' after) and encoding vary by year."""
    path = RAW_DIR / f"{kind}-{year}.csv"
    with open(path, "rb") as f:
        first = f.readline().decode("latin-1")
    sep = ";" if first.count(";") > first.count(",") else ","
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(path, sep=sep, encoding=enc, dtype=str, low_memory=False)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Cannot decode {path}")


def load_processed():
    """Load the pre-aggregated files produced by build_data.py (used by the app)."""
    acc = pd.read_parquet(DATA_DIR / "accidents.parquet")
    users = pd.read_parquet(DATA_DIR / "users_agg.parquet")
    quality = json.loads((DATA_DIR / "quality.json").read_text(encoding="utf-8"))
    return acc, users, quality


def load_geojson() -> dict:
    return json.loads((DATA_DIR / "departements.geojson").read_text(encoding="utf-8"))
