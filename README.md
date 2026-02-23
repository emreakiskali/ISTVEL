# ISTVEL
**Istanbul Simulation Tool for Vehicle Electrification**

An open-source, three-phase framework that converts [IBB](https://data.ibb.gov.tr) open traffic data into ready-to-run [SUMO](https://eclipse.dev/sumo) microscopic simulation packages with configurable EV/ICE/hybrid fleet scenarios — accessible through a Streamlit web interface.

---

## Overview

| Phase | What it does |
|-------|-------------|
| **1 — Visualise** | Fetches 5 years of hourly geohash traffic records from IBB CKAN API and renders heat maps, speed overlays, and summary metrics |
| **2 — Generate** | Converts IBB records to a SUMO-ready ZIP: OSM network → `netconvert` → edge matching → vehicle/route XML → `.sumocfg` |
| **3 — Electrify** | Adds BEV scenario (Kia Soul EV 64 kWh), automatic charging station placement, and fleet composition control |

Post-simulation dashboard parses `tripinfo.xml`, `emission.xml`, and `battery.xml` and produces per-vehicle energy, emission, and fuel-vs-electricity comparisons.

---

## Features

- **Node-anchored edge matching** — reliably resolves OSM way IDs ↔ SUMO integer edge IDs
- **Manual region selector** — click 3–8 points on a map to define a custom bounding box
- **Fleet modes** — EV-only · FUEL-only · HYBRID (adjustable EV penetration ratio)
- **Fuel conversion** — EN 590 diesel density (820 kg/m³, 9.96 kWh/L) for accurate volume reporting
- **Bilingual UI** — Turkish / English toggle
- **One-click export** — complete SUMO package as a ZIP archive

---

## Quick Start

```bash
# 1. Install dependencies
pip install streamlit osmnx folium streamlit-folium pandas numpy requests

# 2. Install SUMO (≥ 1.20)
# https://sumo.dlr.de/docs/Installing/index.html

# 3. Run
streamlit run app.py
```

---

## Repository Structure

```
istvel/
├── app.py                  # Main Streamlit application
├── ibb_trafik_indir.py     # Bulk CSV backup script for IBB data
├── .gitlab-ci.yml          # Monthly auto-backup pipeline
├── data/                   # IBB CSV backups (Git LFS)
├── LICENSE
└── NOTICE                  # Third-party attributions
```

---

## Data Backup

All 60 monthly IBB datasets (Jan 2020 – Dec 2024) can be downloaded locally as CSV:

```bash
pip install requests

python ibb_trafik_indir.py                              # all months
python ibb_trafik_indir.py --baslat "Ocak 2022" --bitis "Aralık 2022"
python ibb_trafik_indir.py --aylar "Mayıs 2022" "Ekim 2023"
```

> **Note:** CSV files are tracked with Git LFS. Run `git lfs install` before cloning.

---

## Output Files

| File | Description |
|------|-------------|
| `network.net.xml` | SUMO network (netconvert output) |
| `routes.rou.xml` | Vehicle routes with EV/ICE vTypes |
| `charging_stations.add.xml` | Charging station definitions |
| `edgedata.add.xml` | IBB traffic stats per edge |
| `simulation.sumocfg` | Ready-to-run SUMO configuration |
| `snap_report.csv` | Geohash-to-edge mapping report |

---

## Citation

If you use ISTVEL in your research, please cite:

```bibtex
@article{istvel2026,
  title   = {ISTVEL: A Three-Phase Framework for Urban Traffic Modeling
             and Electric Vehicle Energy Analysis in Istanbul},
  author  = {[Author(s)]},
  journal = {[Venue]},
  year    = {2026}
}
```

---

## Third-Party Notices

- **OpenStreetMap** © OpenStreetMap contributors — [ODbL](https://www.openstreetmap.org/copyright)
- **IBB Traffic Density Dataset** © Istanbul Metropolitan Municipality — [CC BY](https://data.ibb.gov.tr)
- **SUMO** © German Aerospace Center DLR — [EPL-2.0](https://eclipse.dev/sumo)

---

## License

Apache-2.0 © [Author(s)]
