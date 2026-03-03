# ISTVEL — Istanbul Simulation Tool for Vehicle Electrification

> **An open-source, end-to-end framework for microscopic EV fleet simulation using real-world traffic data.**

[![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-ff4b4b?logo=streamlit&logoColor=white)](https://streamlit.io)
[![SUMO](https://img.shields.io/badge/SUMO-≥1.20-00b4d8)](https://sumo.dlr.de)
[![License](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)

---

## Overview

ISTVEL bridges the gap between raw urban traffic sensor data and actionable fleet-electrification analysis. It ingests **hourly loop-detector records** from the Istanbul Metropolitan Municipality (IMM) open-data portal, synthesises a SUMO-ready simulation package, and delivers a multi-fleet comparison dashboard — all without requiring manual O-D matrix construction or route pre-processing.

The framework was developed and validated on the **Kadıköy district of Istanbul** (3.2 km², ~2,950 vehicles, January 2025 08:00–09:00) and independently replicated on the **Fatih district** under identical protocol. It is designed to generalise to any city whose road network is available on OpenStreetMap. Example simulation packages for both districts are included in the repository under `examples/`.

Simulations were conducted using **SUMO 1.25**.

```
IMM Loop Detectors  ──▶  ISTVEL  ──▶  SUMO Package (.zip)
                                           │
                              ┌────────────▼────────────┐
                              │  Run SUMO locally        │
                              └────────────┬────────────┘
                                           │ tripinfo.xml
                              ┌────────────▼────────────┐
                              │  ISTVEL Dashboard        │
                              │  BEV · ICEV · HEV · CS  │
                              └─────────────────────────┘
```

---

## Key Features

| Feature | Description |
|---|---|
| **Real traffic demand** | IMM inductive-loop counts mapped to OSM edges via geodesic snap |
| **Connection-aware BFS routing** | Zero-teleportation route synthesis using SUMO `<connection>` graph |
| **Physics-based BEV model** | Aerodynamic drag, rolling resistance, regenerative braking (SUMO battery device) |
| **Rigorous energy accounting** | Cumulative `tripinfo.xml` fields — immune to `emission-output` period bias |
| **Multi-fleet comparison** | BEV, ICEV (HBEFA3), HEV (50/50), BEV+CS scenarios in one run |
| **Charging station placement** | Automatic spacing-based placement with `chargeInTransit` support |
| **Multi-currency dashboard** | TRY / USD / EUR with live exchange rate inputs |
| **Plug-and-play for SUMO users** | Upload any `tripinfo.xml` — no re-simulation required |
| **Example scenarios included** | Ready-to-run Kadıköy and Fatih packages in `examples/` |

---

## Results (Kadıköy Case Study)

| Metric | BEV | BEV+CS | ICEV | HEV (50/50) |
|---|---|---|---|---|
| Vehicles arrived | 2,798 | 2,815 | 2,784 | 2,790 |
| Arrival rate | 94.7 % | 94.7 % | 94.2 % | 94.2 % |
| Net energy (kWh) | 848.1 | 851.7 | — | 441.6 |
| kWh / 100 km | 13.10 | 13.12 | — | 6.66 |
| Fuel (L) | — | — | 731.7 | 362.5 |
| Total CO₂ (kg) | 381.6 | 383.3 | 1,921.5 | 1,151.3 |
| CO₂ / 100 km (g) | 58.95 | 59.16 | 293.8 | 173.5 |
| TCO (TRY) | 3,816 | 3,833 | 41,795 | 22,693 |
| TCO / 100 km (TRY) | 59.0 | 59.2 | 638.8 | 341.8 |

> Grid carbon intensity: γ = 0.45 kg CO₂/kWh (Turkey 2023 average).  
> Fuel tariff: 57.12 TRY/L · Electricity tariff: 16.49 TRY/kWh.

**BEV achieves 80.1 % fewer lifecycle CO₂ emissions and 90.8 % lower TCO than ICEV** under current Turkish tariffs.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ISTVEL (app_v4.py)                    │
│                                                         │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐  │
│  │ IMM API     │   │ OSM / osmnx  │   │ Sidebar     │  │
│  │ Fetcher     │──▶│ Network      │──▶│ Parameters  │  │
│  └─────────────┘   └──────────────┘   └──────┬──────┘  │
│                                              │          │
│  ┌───────────────────────────────────────────▼──────┐  │
│  │            SUMO Package Generator                │  │
│  │  • connection-graph BFS route synthesis          │  │
│  │  • demand-weighted departure-edge sampling       │  │
│  │  • charging station placement (Δ_cs spacing)     │  │
│  │  • net.xml · routes.rou.xml · run.sumocfg        │  │
│  └───────────────────────────────────────────┬──────┘  │
│                                              │ .zip     │
│                    [User runs SUMO]          │          │
│                                              ▼          │
│  ┌───────────────────────────────────────────────────┐  │
│  │               Analysis Dashboard                  │  │
│  │  Tab 1: EV Fleet      Tab 4: Cross-Fleet Compare  │  │
│  │  Tab 2: Fuel Fleet    Tab 5: Charging Stations    │  │
│  │  Tab 3: Hybrid Fleet                              │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.12
- [SUMO ≥ 1.20](https://sumo.dlr.de/docs/Downloads.php) with `sumo`, `netconvert`, `dfrouter` on `PATH`  
  *(Simulations in this study were conducted using SUMO 1.25)*

### Setup

```bash
git clone https://github.com/emreakiskali/ISTVEL.git
cd ISTVEL

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Run

```bash
streamlit run app_v4.py
```

The app opens at `http://localhost:8501`.

---

## Usage

### Phase 1 — Generate a SUMO Package

1. **Select data** in the sidebar: choose month, day, and hour from the IMM portal (or upload your own OSM `.osm` file).
2. **Configure fleet parameters:**
   - Fleet mode: `EV`, `FUEL`, or `HYBRID`
   - Charging station toggle: interval (km), power (kW), efficiency, berth length (m)
   - Hybrid EV ratio (default 50 %)
3. **Click "Generate SUMO Package"** — the app fetches IMM traffic data, builds the OSM network, synthesises connection-valid routes, and packages everything as a `.zip`.
4. **Download the `.zip`**, unzip, and run SUMO:

```bash
cd sumo_package/
sumo -c simulation.sumocfg
```

SUMO writes outputs to `output/`:

| File | Contents |
|---|---|
| `tripinfo.xml` | Per-vehicle energy, emissions, route stats (primary analysis input) |
| `emission.xml` | Instantaneous emission rates (reference only) |
| `chargingstations_output.xml` | Per-station charging events (CS tab) |
| `summary.xml` | Simulation-wide aggregates |

### Phase 2 — Analyse Results

Upload the SUMO output files in the corresponding dashboard tabs:

| Tab | Required upload | Shows |
|---|---|---|
| **EV** | `tripinfo.xml` | Battery energy, regen, SoC, CO₂, TCO |
| **Fuel** | `tripinfo.xml` | Fuel consumption, tailpipe CO₂, TCO |
| **Hybrid** | `tripinfo.xml` | Mixed energy/fuel breakdown |
| **Compare** | — (uses uploaded fleets) | Cross-fleet normalised charts + savings metrics |
| **Charging Stations** | `chargingstations_output.xml` (+ optional `tripinfo.xml`) | Per-station energy, events, cost/100 km |

> **Tip for existing SUMO users:** If you already have a `tripinfo.xml` from any prior simulation, you can skip Phase 1 entirely and go straight to the analysis tabs. Just adjust the vehicle parameters (mass, drag, battery capacity) in the Python source to match your vType.

---

## Example Scenarios

Ready-to-run simulation packages for both validated districts are available in the `examples/` directory:

```
examples/
├── kadikoy_jan2025_0800/     # Kadıköy, 08:00–09:00, January 2025 (~2,950 vehicles)
│   ├── sumo_package.zip      # BEV, ICEV, MIX, BEV+CS configurations
│   └── tripinfo/             # Pre-computed tripinfo.xml outputs for all four fleets
└── fatih_jan2025_0800/       # Fatih, 08:00–09:00, January 2025 (~3,174 vehicles)
    ├── sumo_package.zip
    └── tripinfo/
```

These packages can be used to reproduce the paper results or as starting templates for new districts. Simply unzip and run with `sumo -c simulation.sumocfg`, or upload the included `tripinfo.xml` files directly to the dashboard without re-running SUMO.

---

## For Automotive Engineers & Fleet Operators

ISTVEL's analysis layer is decoupled from the simulation infrastructure. Vehicle specifications are exposed as plain Python constants in `app_v4.py`:

```python
# BEV vType parameters — replace with your vehicle's specs
VEHICLE_MASS_KG     = 1830      # kg (incl. rotational equiv. 40 kg)
BATTERY_CAPACITY_WH = 64_000    # Wh
DRAG_COEFF          = 0.35
FRONTAL_AREA_M2     = 2.6
ROLLING_RESIST      = 0.01
EFFICIENCY_PROP     = 0.98      # propulsion
EFFICIENCY_REGEN    = 0.96      # regeneration
AUX_POWER_W         = 100       # W
```

Substitute your values, upload a `tripinfo.xml` generated from any SUMO simulation of your target city, and obtain fuel consumption, electricity draw, tailpipe emissions, and total cost of ownership under realistic stop-and-go urban traffic — **no re-simulation required.**

---

## Charging Station Configuration

When the **Charging Stations** toggle is enabled, stations are placed on every eligible edge at a configurable interval:

```
K_e = floor(ℓ_e / Δ_cs),   ℓ_e ≥ 0.3 · Δ_cs
```

| Parameter | Default | Range | Description |
|---|---|---|---|
| Interval Δ_cs (km) | 1.0 | 0.2 – 5.0 | Spacing between stations |
| Power P_cs (kW) | 50 | 22 – 350 | Charging power per station |
| Efficiency η_cs | 0.95 | 0.80 – 0.99 | Charge transfer efficiency |
| Berth length b (m) | 10 | 5 – 1000 | Physical station length |
| chargeInTransit | ✓ | on/off | Charge while vehicle moves past |

The `sumocfg` automatically includes `<chargingstations-output>` when CS is enabled, writing per-event data to `output/chargingstations_output.xml`.

---

## Multi-Currency Support

All monetary outputs are computed internally in **TRY** and converted at display time:

| Currency | Default rate | Change in sidebar |
|---|---|---|
| TRY ₺ | 1.0 (base) | — |
| USD $ | 43.85 TRY/$ | ✓ |
| EUR € | 51.88 TRY/€ | ✓ |

Exchange rates reflect **February 2026** values and can be updated in the sidebar at any time without re-running the simulation.

---

## Project Structure

```
ISTVEL/
├── ISTVEL.py                  # Main Streamlit application (~2,900 lines)
├── requirements.txt           # Python dependencies
├── README.md
├── examples/
│   ├── kadikoy_jan2025_0800/  # Kadıköy example scenario
│   └── fatih_jan2025_0800/    # Fatih example scenario

---

## Data Sources

| Source | Description | Access |
|---|---|---|
| [IMM Open Data Portal](https://data.ibb.gov.tr) | Hourly loop-detector traffic records (speed, count) | Public API |
| [OpenStreetMap](https://openstreetmap.org) | Road network geometry and topology | Via `osmnx` |
| [SUMO](https://sumo.dlr.de) | Microscopic traffic simulation engine | Open-source (EPL 2.0) |

IMM data is fetched live via the CKAN datastore API:
```
https://data.ibb.gov.tr/api/3/action/datastore_search
```

---

## Authors

**Emre Akıskalıoğlu** — Research Assistant, Department of Mechanical Engineering, Faculty of Technology, Marmara University, Istanbul, Turkey  
✉ emre.akiskalioglu@marmara.edu.tr *(corresponding author)*  
🔗 [github.com/emreakiskali](https://github.com/emreakiskali)

---

## License

This project is released under the **MIT License** — see [LICENSE](LICENSE) for details.

Contributions, bug reports, and feature requests are welcome via [Issues](https://github.com/emreakiskali/ISTVEL/issues).
