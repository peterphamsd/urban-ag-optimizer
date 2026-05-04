# Urban Agriculture Site Optimizer
### San Diego, CA — Probabilistic Site Viability Assessment

A GIS-based decision support tool that identifies and ranks urban parcels for agricultural viability using FAO-56 Penman-Monteith evapotranspiration modeling and Monte Carlo simulation.

![Urban Agriculture Site Map](outputs/screenshot_output_map.png)

---

## What It Does

This tool answers a precise question:

> **Given real climate data, soil conditions, and urban infrastructure — which parcels of land in San Diego are most viable for urban agriculture, and what is the probability of success across a range of future climate scenarios?**

Rather than using arbitrary scoring weights, viability is derived from physical first principles — atmospheric physics, crop science, and hydrology — then quantified probabilistically across 1,000 simulated growing seasons per site.

---

## Who It's For

- **City planners** — prioritize vacant and open space land for food production programs
- **Urban agriculture nonprofits** — identify and make the case for specific sites to city councils
- **Project finance professionals** — assess irrigation cost ranges and yield stability before committing capital
- **Green infrastructure consultants** — integrate water demand modeling into site feasibility studies

---

## Methodology

### 1. Site Eligibility Screening

Parcels are filtered by land use classification — vacant land and open space are flagged as eligible. Commercial and industrial parcels are classified as rooftop farm candidates with height-adjusted wind modeling.

### 2. FAO-56 Penman-Monteith Evapotranspiration

Daily reference evapotranspiration (ETo) is computed using the UN FAO-56 Penman-Monteith equation — the global standard for crop water requirement estimation. Inputs are sourced from the NASA POWER API (real historical climate data):

$$
ETo = \frac{0.408\Delta(R_n - G) + \gamma\frac{900}{T+273}u_2(e_s - e_a)}{\Delta + \gamma(1 + 0.34u_2)}
$$

Where:
- $\Delta$ = slope of saturation vapour pressure curve (kPa/°C)
- $R_n$ = net radiation at crop surface (MJ/m²/day)
- $G$ = soil heat flux density (MJ/m²/day)
- $\gamma$ = psychrometric constant (kPa/°C)
- $T$ = mean daily air temperature (°C)
- $u_2$ = wind speed at 2m height (m/s)
- $e_s - e_a$ = vapour pressure deficit (kPa)

Rooftop farms receive wind speed adjustment for measurement height per FAO-56 Equation 47.

### 3. Lettuce Crop Coefficient Curves

Crop-specific water demand is modeled using FAO-56 Table 12 Kc values for lettuce across 4 growth stages over a 75-day season:

$$ETc = K_c \times ETo$$

| Stage | Days | Kc |
|-------|------|----|
| Initial | 1-20 | 0.70 |
| Development | 21-50 | 0.70 → 1.00 |
| Mid-season | 51-65 | 1.00 |
| Late season | 66-75 | 1.00 → 0.95 |

### 4. Soil Water Balance

Daily root zone depletion is tracked against soil hydraulic thresholds (sandy loam parameters for San Diego):

$$TAW = (\theta_{FC} - \theta_{WP}) \times Z_e \times 1000 = 13mm$$

$$RAW = p \times TAW = 3.9mm$$

When depletion exceeds RAW, the stress coefficient activates:

$$K_s = \frac{TAW - D_r}{TAW - RAW}$$

$$ETc_{adj} = K_s \times K_c \times ETo$$

An irrigation trigger refills the root zone when depletion exceeds RAW, modeling a managed drip irrigation system.

### 5. Monte Carlo Simulation

Each site runs 1,000 growing season simulations with sampled climate uncertainty:

| Variable | Distribution | Range |
|----------|-------------|-------|
| Temperature variation | Normal(0, 1.5°C) | Year-to-year climate shift |
| Rainfall multiplier | Triangular(0.5, 1.0, 1.5) | 50-150% of average |
| Wind variation | Uniform(0.8, 1.2) | ±20% of baseline |
| Water rate | Uniform($4.50, $8.00/HCF) | San Diego tiered pricing |

Outputs per site:
- **P(viable)** — probability of successful growing season
- **Avg irrigation cost** — expected seasonal cost per 100m²
- **Cost P05/P95** — best and worst case cost range
- **Yield stability index** — production consistency across scenarios

### 6. Weighted Scoring

$$Score = P(viable) \times 30 + FoodDesert \times 25 + Transit \times 20 + LotSize \times 25$$

Transit distances are calculated using real San Diego MTS stop locations via GeoPandas spatial joins. Food desert scores are derived from USDA Food Access Research Atlas data.

---

## Technical Stack

| Category | Tools |
|----------|-------|
| Language | Python 3.x |
| Geospatial | GeoPandas, Shapely, Folium |
| Data | Pandas, NumPy |
| APIs | NASA POWER, NREL PVWatts, San Diego Open Data |
| Modeling | FAO-56 Penman-Monteith, Monte Carlo Simulation |
| Visualization | Folium (interactive HTML map) |

---

## Project Structure

```
urban-ag-optimizer/
├── src/
│   ├── scoring.py          # master pipeline — runs end to end
│   ├── fao56.py            # FAO-56 Penman-Monteith implementation
│   ├── monte_carlo.py      # Monte Carlo simulation engine
│   ├── weather.py          # NASA POWER API integration
│   ├── solar.py            # NREL PVWatts API integration
│   ├── spatial.py          # GeoPandas transit distance calculations
│   ├── map_output.py       # Folium interactive map builder
│   └── transit.py          # San Diego MTS transit data loader
├── data/
│   ├── parcels.csv             # parcel dataset
│   ├── generate_parcels.py     # synthetic data generator
│   └── transit_stops.geojson   # San Diego MTS stop locations
├── tests/
│   └── test_fao56.py       # FAO-56 validation suite (5/5 passing)
├── outputs/
│   └── urban_ag_map.html   # interactive map output
├── .env                    # API keys (not tracked)
├── requirements.txt        # dependencies
└── README.md
```

---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/peterphamsd/urban-ag-optimizer.git
cd urban-ag-optimizer
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API keys
Create a `.env` file in the root directory:
```
NREL_API_KEY=your_key_here
```
Get a free key at: https://developer.nrel.gov/signup/

### 5. Run the pipeline
```bash
python src/scoring.py
```

### 6. Open the map
Open `outputs/urban_ag_map.html` in any browser.

### 7. Run FAO-56 validation suite
```bash
python tests/test_fao56.py
```

---

## Validation

The FAO-56 Penman-Monteith implementation is validated against published benchmarks:

| Test | Result | Value |
|------|--------|-------|
| FAO-56 Annex 2 (Cabinda, Angola) | ✅ PASS | 2.84 mm/day (tol: ±1.1) |
| California Summer (Davis, CA) | ✅ PASS | 6.59 mm/day (range: 6-8) |
| San Diego Coastal Summer | ✅ PASS | 3.99 mm/day (range: 3.5-6.5) |
| Lettuce Kc Curve (8 checkpoints) | ✅ PASS | All within 0.01 tolerance |
| Rooftop vs Ground ETo | ✅ PASS | 0.33 mm/day difference |
| **Overall** | **5/5 PASSING** | |

---

## Sample Output

Current analysis of San Diego eligible parcels:

| Rank | Address | P(viable) | Avg Cost | Stability | Score |
|------|---------|-----------|----------|-----------|-------|
| #1 | 376 National City Blvd | 100% | $4.74 | 98.97% | 92.97 |
| #2 | 847 Main St | 100% | $4.76 | 98.94% | 92.90 |
| #3 | 905 El Cajon Blvd | 100% | $4.69 | 98.99% | 84.04 |
| #4 | 869 Harbor Dr | 100% | $4.70 | 98.97% | 68.39 |
| #5 | 485 University Ave | 100% | $4.74 | 98.94% | 65.58 |

Average seasonal irrigation cost: **$4.72 per 100m²**
Average yield stability: **98.97%**

---

## Potential Improvements & Next Steps

### Phase 3 — Real Parcel Data Integration
Replace synthetic parcels with real San Diego County Assessor data (~700,000 parcels). Filter to eligible land use codes and scale the pipeline to handle thousands of candidate sites with marker clustering.

### Real Soil Data
Integrate USDA Web Soil Survey API to replace assumed sandy loam parameters with measured soil hydraulic properties per parcel location. This improves TAW/RAW calculations and irrigation demand accuracy.

### Building Footprint Integration
Spatial join San Diego building footprint data to identify parcels with existing rooftop structures. Extract real building heights for more accurate rooftop wind adjustment per FAO-56 Equation 47.

### Expanded Crop Library
Extend beyond lettuce to model tomatoes, herbs, and leafy greens with their respective FAO-56 Kc curves and stress thresholds. Allow crop selection as a pipeline input parameter.

### Economic Layer
Add full cost-benefit analysis — land lease costs, infrastructure investment, expected yield value, and payback period — to produce a financial viability score alongside the agronomic one.

### Climate Change Scenarios
Replace historical NASA POWER baselines with CMIP6 climate projections to model site viability under 2050 and 2100 warming scenarios. Assess which sites remain viable under different emissions pathways.

### Dashboard Interface
Build a Streamlit or Dash web application to replace the static HTML map — allowing users to adjust crop type, farm size, scoring weights, and climate scenarios interactively.

---

## Background

Built as a personal project to bridge business intelligence and sustainability analytics — applying financial portfolio assessment thinking to urban green infrastructure site selection.

Inspired by the integrated sustainability consulting work of firms like Arup, WSP, and Jacobs — where data-driven decision support meets urban systems thinking.

---

## Author

**Peter Pham**
Business Intelligence Analyst | San Diego, CA
[github.com/peterphamsd](https://github.com/peterphamsd)
