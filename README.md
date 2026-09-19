# Autumn Atlas

An interactive map of ten autumn tree species in the contiguous United States.

**Website:** https://yeyekuailai.github.io/fall-foliage-map/

- Distinct tree-crown illustrations, colored independently through September–November.
- Relative grove density and species mix derived from historical USFS FHTET abundance models.
- Lightweight state and urban outlines, with city/state search.
- English interface and bilingual English–Chinese botanical descriptions.
- On-demand weather, GBIF observations and external foliage forecasts.

## Run locally

```sh
python3 -m http.server 8000
```

Open http://localhost:8000. No build step, API key or package installation is needed to view the map. All paths are relative so the site works under the GitHub Pages repository path.

## Publishing

GitHub Pages serves the root of the `main` branch. `.nojekyll` publishes the static files without Jekyll processing.

## Data and limitations

The tree illustrations represent groups, not surveyed individual-tree positions. Density is based on modeled forest conditions circa 2002. Seven species have historical seasonal calibration at Harvard Forest only; geographic transfer remains unvalidated and three species retain illustrative parameters. The timeline is not a live foliage observation or a current-season forecast.

Read [full methodology and provenance](data/MODEL-NOTES.md). Source attribution and reference links are also available in **Data & Models**.

The included data and libraries retain their original terms: Harvard Forest HF003 is CC0; Natural Earth is public domain; Leaflet is BSD-2-Clause (see `data/leaflet-LICENSE.txt`). Open-Meteo and other external services have their own usage terms. The tree illustrations were generated specifically for this project.

## Source layout

`index.html`, `app.js`, `forest.js`, `city-search.js`, `model.js` and `style.css` contain the application. `assets/` holds the tree atlas; `data/` contains display rasters, species metadata, calibration and provenance. `scripts/` contains data preparation and calibration checks. Large temporary downloads and private hosting configuration are excluded.
