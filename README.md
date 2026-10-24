# 🌙 Driving at night in France: what really makes it dangerous?

An interactive data-storytelling dashboard built with **Streamlit** on 10 years of French injury-accident data (2015-2024).

- **Live app:** https://night-road-safety-france.streamlit.app/
- **Repository:** https://github.com/manuela-GUE/night-road-safety
- **Author:** GUE Blé Manuela - BIA

## 1. The story

**Audience.** Drivers (cars and two-wheelers) who sometimes drive at night, and anyone who wants to understand where road-safety effort should go.

**Question.** Is night driving dangerous because it is dark, or because of the roads we drive on at night?

**Narrative arc.** Hook (why it matters) -> Context (how severity changes with light) -> Key insights (when, where, who, same-conditions comparison) -> Implications (what a driver can do, what-if scenario).

**Headline finding.** On roads with *no street lighting at night*, **13.5%** of injury accidents are fatal, against **4.9%** in daylight (about x2.8). These accidents are **10.6%** of all injury accidents but **25.8%** of deaths. The gap survives when comparing like with like (same area type, road type and speed limit), so it is not just an urban/rural effect.

| Lighting condition | Injury accidents | Fatal accidents | Share of accidents | Share of deaths |
|---|---|---|---|---|
| Daylight | 379,181 | 4.87% | 67.2% | 57.2% |
| Dawn / dusk | 36,573 | 6.34% | 6.5% | 7.3% |
| Night, street lighting on | 88,840 | 3.54% | 15.7% | 9.7% |
| Night, no street lighting | 59,595 | **13.45%** | 10.6% | **25.8%** |

| Same-conditions check (fatal accidents) | Daylight | Night, no lighting | Ratio |
|---|---|---|---|
| Built-up area | 2.47% | 7.87% | x3.2 |
| Outside built-up area | 9.30% | 14.92% | x1.6 |

Other findings: the fatal rate peaks between about 3 am and 5 am (11-12%, against about 4% at 8 am); Friday to Sunday carry about 56% of all night deaths; pedestrians, cyclists, mopeds and people aged 65+ are the most likely to die once an accident happens on an unlit night road (exact values are shown in the app).

> "Night, street lighting on" looks safer than daylight overall, but this is a composition effect: 91% of those accidents happen in built-up areas at low speed. The app therefore compares like with like instead of headlining that number.

## 2. The dashboard

| Page | What it answers |
|---|---|
| **Overview** | Headline insight, 4 KPIs tied to the filters, fatal rate by lighting, share of accidents vs share of deaths, yearly trend |
| **Deep dives** | When (hour x weekday heatmap), is it the dark or the road (comparison within area / road type / speed limit), who (vehicle, age band, trip purpose), which departments |
| **Map** | Fatal-accident rate by metropolitan department, for any lighting condition, with a top-10 |
| **What can I do?** | Six evidence-based tips and a what-if slider (deaths avoided per year if part of the unlit-night gap closed) |
| **Data & limits** | Per-year data-quality checks and the limits of the analysis |

Sidebar controls (years, departments, area type, trend/heatmap metric) apply to every page. Every chart has axis labels with units, hover tooltips and a text caption describing it.

## 3. Data

- **Source:** *Bases de donnees annuelles des accidents corporels de la circulation routiere* (BAAC), ONISR / Ministere de l'Interieur, on [data.gouv.fr](https://www.data.gouv.fr/datasets/53698f4ca3a729239d2036df/) (2005-2024; we use 2015-2024).
- **License:** Licence Ouverte (Etalab), attribution required. See the dataset page for the exact terms. The code is an academic project.
- **Tables:** four per year (`caracteristiques`, `lieux`, `vehicules`, `usagers`), joined on the accident id. Department outlines come from the open `gregoiredavid/france-geojson` repository.
- **Size:** 564,198 injury accidents after cleaning.

### Cleaning and validation (`utils/prep.py`, `utils/io.py`)

1. Files are located through the data.gouv.fr API, and **each download is validated** (the header must contain `Num_Acc` or `Accident_Id`), because the dataset also hosts unrelated "registered vehicles" files with similar names.
2. Separator (`,` before 2019, `;` after) and encoding (UTF-8 or Latin-1) are detected per file; column names are normalised (BOM, case, `Accident_Id` -> `Num_Acc`).
3. Department codes are harmonised: before 2019 metropolitan codes are stored x10 (`590` = Nord) and Corsica is `201`/`202`, converted to `2A`/`2B`.
4. Hours are parsed from both formats (`1730` and `17:30`); GPS coordinates stored as scaled integers are rescaled, and invalid or zero coordinates are set to missing.
5. Duplicate accident ids are dropped (none found); users are linked to vehicles on `Num_Acc` + `num_veh`.
6. Features: `lighting_group` (daylight, dawn/dusk, night lit, night unlit), `is_night`, `is_fatal`, age band, trip purpose, vehicle group, counts of killed / hospitalised / slightly injured per accident.
7. Per-year quality metrics are saved to `data/quality.json` and displayed in the app.

### Definitions

- **Night** = BAAC lighting codes 3, 4, 5. Code 4 (lighting present but switched off) is grouped with 3 as *unlit*.
- **Killed** = died within 30 days of the accident.
- **Fatal accident rate** = share of injury accidents with at least one person killed.
- **What-if** = deaths on unlit night roads minus the number expected at the daylight deaths-per-accident rate (computed separately for built-up and non-built-up areas), multiplied by the share of the gap the user chooses to close, per year. It is a scenario, not a forecast.

## 4. Data quality, limitations and ethics

- BAAC only contains **injury accidents recorded by the police**. There is no traffic data, so the app compares **severity**, not risk per kilometre. Night driving is much rarer than day driving, so the per-kilometre risk is probably higher than shown, but it cannot be quantified here.
- GPS coordinates are unusable for about half of the 2015 accidents (about 31% in 2016, 13% in 2017) and complete from 2019, so maps work at department level.
- Unknown user age rises from about 0% to about 2% from 2021; the speed limit exists only from 2019.
- National figures include overseas departments and territories; maps and rankings cover metropolitan France only (overseas samples are small).
- Results are associations. Fatigue, alcohol and actual speed also differ at night and are not in the data. The "who" comparisons should be read within a group (day vs night): pedestrians in injury accidents are rarely unhurt, which raises their base rate. Age results describe how often an accident is fatal for the person, not how often each age group has accidents.
- Privacy: the repository contains no personal data. Users are aggregated by categories (vehicle, age band, trip purpose, lighting, department); the source data are already anonymised by the publisher.
- Accessibility: charts have axis titles with units, hover text and a text caption; colours were chosen for contrast on a dark background. Colour is not the only cue (values appear as labels or axes), but the palette has not been formally tested for all forms of colour blindness.

## 5. Run it

Python 3.11 is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate        macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python build_data.py --years 2015 2024   # downloads the raw CSVs (cached in data/raw) and builds data/*.parquet
streamlit run app.py
```

- `python build_data.py --skip-download` rebuilds the processed files from `data/raw` without downloading anything.
- `python explore.py` prints the sanity checks and the figures quoted above.
- `make install`, `make data`, `make run` are shortcuts for the same commands.
- No random sampling is used, so the pipeline is deterministic and a `seeds.json` is not needed. Dependencies are pinned in `requirements.txt`.
- The small processed files in `data/` are committed so the deployed app starts fast; `data/raw/` is git-ignored.

## 6. Project structure

```
app.py                  page config, data loading, sidebar filters, navigation
build_data.py           download -> clean -> write data/*.parquet, quality.json, geojson
explore.py              sanity checks and first look at the hook
sections/               one module per page (overview, deep_dives, map_page, action, data_quality)
utils/io.py             API discovery, validated download, robust CSV reading, loaders
utils/prep.py           cleaning, validation, feature engineering, quality metrics
utils/viz.py            all charts (consistent dark theme and palette)
utils/theme.py          CSS, KPI and tip cards
data/                   accidents.parquet, users_agg.parquet, quality.json, departements.geojson
.streamlit/config.toml  theme
```

**Performance.** Data are pre-aggregated into two compact parquet files (categorical columns, zstd compression); the app loads them once with `st.cache_data` and filters in memory. Rates computed on very small samples are hidden (thresholds are shown in the captions).

## 7. Credits

Data: ONISR / Ministere de l'Interieur (data.gouv.fr). Department outlines: gregoiredavid/france-geojson. Built with Streamlit, pandas, Plotly and PyArrow.
