# Lincoln Flight Prices

A flight price comparison tool tracking round-trip fares out of Lincoln,
NE (LNK) on Breeze Airways, to Las Vegas (LAS) and Orange County/Santa
Ana (SNA).

## How it works

- **`VegasFlights.py`** pulls LNK→LAS nonstop round-trip fares from
  SerpApi (Google Flights data), picks the cheapest option per date, and
  writes results to `lnk_las_6months.json` (with `lnk_las_test.json` as a
  smaller test-run output)
- **`LAFlights.py`** does the same for LNK→SNA, writing
  `lnk_sna_6months.json` / `lnk_sna_test.json`
- **`index.html`** displays fares ranked cheapest to most expensive, with
  adjustable cost calculators for seat selection, baggage fees, and promo
  codes layered on top of the base fare

## GitHub secrets required

`.github/workflows/Bi-Monthly Flight Tracker.yaml` runs on the 1st of
each month and needs this added under repo → Settings → Secrets and
variables → Actions:

| Secret | Used for |
|---|---|
| `SERPAPI_KEY` | Google Flights data via SerpApi, used by both `VegasFlights.py` and `LAFlights.py` |

## Setup

Requires a SerpApi key:

```bash
export SERPAPI_KEY="your_serpapi_key"
```

## Running locally

```bash
pip install serpapi

python VegasFlights.py
python LAFlights.py
```

Then open `index.html` (or serve the folder with
`python -m http.server`) to browse fares.

## Structure

```
BreezeLincolnFlights-main/
├── VegasFlights.py         # LNK -> LAS fares via SerpApi
├── LAFlights.py             # LNK -> SNA fares via SerpApi
├── lnk_las_6months.json / lnk_las_test.json   # generated LAS fare data
├── lnk_sna_6months.json / lnk_sna_test.json   # generated SNA fare data
└── index.html                # fare comparison + cost calculator front-end
```
