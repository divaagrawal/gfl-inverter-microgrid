# Grid Forming Inverter Microgrid Stability Study

A synthetic dynamic benchmark comparing grid-following (GFL), droop-controlled grid-forming (GFM), and virtual-synchronous-machine (VSM) battery inverters during black start, islanding, a load step, and reconnection.

**Status:** educational portfolio project. All microgrid ratings, network equivalents, event timings, and controller parameters are synthetic. It is not hardware-in-the-loop validation, grid-code compliance evidence, or a real microgrid design.

## What it shows

- GFL needs an external voltage/frequency reference and cannot sustain the island alone.
- GFM establishes a voltage waveform, limits current, and shares frequency/voltage response through control laws.
- Droop and VSM responses trade speed, frequency nadir, damping, and current-limit exposure.

## Run

```bash
python3 -m pip install -r requirements.txt
python3 scripts/run_study.py
python3 scripts/make_dashboard.py
python3 -m pytest -q tests
```

The pinned requirements were exercised with Python 3.9 in this workspace; use Python 3.9+.

The commands write two reproducible inputs to the interactive dashboard:

- `results/tables/event_traces.csv` — time-series traces for all three cases.
- `results/tables/event_summary.csv` — one explicit status row per requested case.

Open `results/dashboard.html` locally after generation. Its mode selector and event rail update all four plots. The dashboard is intentionally labelled as a synthetic benchmark.

## Scenario boundary

| Window | Event | Model treatment |
| --- | --- | --- |
| 0–4 s | Black start | GFM establishes a synthetic voltage reference; GFL has none. |
| 4–10 s | Grid parallel | Stiff external reference is available. |
| 10–48 s | Islanded operation | The 22–35 s load step is applied; inverter power is capped at 0.45 pu. |
| 48–60 s | Reconnection | A synthetic stiff-grid restoration pulls each mode toward nominal; this is not a synchronisation study. |

The model omits network impedance, protection coordination, PLL dynamics, detailed converter switching, and test data. Therefore, its plots are illustrative controller comparisons, not design results.

## Provenance

Grid-forming and grid-following concepts are based on public technical literature, but no claim of IEEE compliance is made. The U.S. DOE notes that grid-forming inverters can black-start a grid, unlike grid-following inverters that need an external waveform reference. [DOE overview](https://www.energy.gov/cmei/systems/solar-integration-inverters-and-grid-services-basics)
