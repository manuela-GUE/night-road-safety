# Driving at night in France - a data-storytelling dashboard

Streamlit dashboard for drivers on night-time road safety, built on the French BAAC injury-accident database.

## Data
ONISR / Ministry of the Interior, *Bases de donnees annuelles des accidents corporels de la circulation routiere*
(2005-2024) on data.gouv.fr (dataset id `53698f4ca3a729239d2036df`). Licence Ouverte (Etalab) - verify on the dataset page.
Department boundaries: `gregoiredavid/france-geojson`. No sampling is used, so the pipeline is deterministic.

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build_data.py --years 2015 2024   # downloads raw CSVs (cached in data/raw), writes data/*.parquet
streamlit run app.py
```
`data/raw/` is git-ignored; the small processed files in `data/` are committed so the deployed app starts fast.

## Structure
`app.py` (filters + layout) | `sections/` (story parts) | `utils/io.py` (download/read/load) |
`utils/prep.py` (cleaning, features, quality metrics) | `utils/viz.py` (charts) | `build_data.py` (pipeline)

## Limitations
Injury accidents only (no traffic exposure data); older GPS data are unreliable; night = BAAC lighting codes 3-5.
