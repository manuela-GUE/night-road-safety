"""Download the BAAC files, clean them and write the light parquet files used by the app.

Usage:  python build_data.py --years 2015 2024 [--force] [--skip-download]
Run once locally, then commit data/*.parquet, data/quality.json and data/departements.geojson.
"""
from __future__ import annotations

import argparse
import json

import pandas as pd

from utils import io as dio
from utils.prep import LIGHTING_ORDER, process_year


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--years", nargs=2, type=int, default=[2015, 2024], metavar=("START", "END"))
    p.add_argument("--force", action="store_true", help="re-download raw files")
    p.add_argument("--skip-download", action="store_true", help="use files already in data/raw")
    args = p.parse_args()
    years = list(range(args.years[0], args.years[1] + 1))

    resources = {} if args.skip_download else dio.list_resources()
    accs, users, quality = [], [], []
    for y in years:
        print(f"Year {y}")
        if not args.skip_download:
            dio.download_year(y, resources, force=args.force)
        raw = {k: dio.read_raw(k, y) for k in dio.KINDS}
        a, u, q = process_year(raw, y)
        accs.append(a), users.append(u), quality.append(q)

    acc = pd.concat(accs, ignore_index=True)
    usr = pd.concat(users, ignore_index=True)
    for c in ["dep", "lighting_group", "area", "weather", "road_type"]:
        acc[c] = acc[c].astype("category")
    acc["lighting_group"] = acc["lighting_group"].cat.set_categories(LIGHTING_ORDER)
    for c in ["dep", "lighting_group", "veh_group", "role", "age_band", "trip", "severity"]:
        usr[c] = usr[c].astype("category")

    dio.DATA_DIR.mkdir(exist_ok=True)
    acc.to_parquet(dio.DATA_DIR / "accidents.parquet", compression="zstd", index=False)
    usr.to_parquet(dio.DATA_DIR / "users_agg.parquet", compression="zstd", index=False)
    (dio.DATA_DIR / "quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    dio.download_geojson()
    print(f"Done: {len(acc):,} accidents, {len(usr):,} aggregated user rows.")


if __name__ == "__main__":
    main()
