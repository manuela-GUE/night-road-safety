# Dataset used

**Bases de donnees annuelles des accidents corporels de la circulation routiere** (BAAC), years 2005-2024 (we use 2015-2024).

- Publisher: ONISR / Ministere de l'Interieur
- Portal: data.gouv.fr (approved portal)
- Link: https://www.data.gouv.fr/datasets/53698f4ca3a729239d2036df/
- API used by `build_data.py`: https://www.data.gouv.fr/api/1/datasets/53698f4ca3a729239d2036df/
- License: Licence Ouverte (Etalab) - attribution required; check the dataset page for the exact version.

Tables per year: `caracteristiques`, `lieux`, `vehicules`, `usagers`, joined on the accident id.

Department outlines (for the map): https://github.com/gregoiredavid/france-geojson (simplified departments file).

The raw files are not bundled: `python build_data.py --years 2015 2024` downloads them and caches them in `data/raw`.
