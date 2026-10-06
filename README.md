
# Norwegian Gas Outages & TTF

**Python · PostgreSQL · European Gas Markets · Event Study**

## Project overview

This project investigates how near-term Dutch TTF natural gas futures prices behave around first public disclosures of unplanned Norwegian gas infrastructure outages.

The central challenge is distinguishing an operational disruption from new information reaching the market. An outage may have begun before it is reported, while its expected effect on gas supply may already be reflected in prices.

I developed a Python and PostgreSQL workflow to reconstruct Gassco outage announcements, validate a daily TTF futures price series, align disclosures with market observations and analyse subsequent returns.

### Research question

How do near-term TTF prices behave around eligible first-revision Norwegian gas outage announcements, and are the observed returns associated with outage magnitude or publication timing?

### Key results

| Measure | Result |
|---|---:|
| Raw Gassco messages | 376 |
| Eligible first-revision reduction announcements | 166 |
| Unique TTF market-date anchors | 130 |
| Chronologically spaced analytical anchors | 82 |
| Median post-anchor return (82 anchors) | +0.057% |
| Reported 95% bootstrap interval | -0.526% to +0.925% |
| Wilcoxon signed-rank p-value | 0.689 |

The selected 82-anchor sample does not show a statistically detectable common directional shift in post-anchor TTF returns. The analysis also finds little evidence of a monotonic relationship between the largest communicated outage and subsequent signed returns.

These are observational findings, not estimates of the causal price impact of Norwegian gas disruptions. The daily price series does not establish the exact price observed immediately before each disclosure.

### What the project demonstrates

- Reconstruction of operational announcements from revision-based source data.
- Data-quality validation and event eligibility rules in PostgreSQL.
- Alignment of timestamped disclosures with an observed financial-market calendar.
- Construction of announcement-level, market-anchor and spaced event samples.
- Statistical analysis with explicit attention to selection, market-price timing and identification limitations.



## Repository structure

```text
norway-ttf-event-study/
├── README.md
├── src/
│   ├── 01_ingest_gassco.py
│   └── 02_ingest_ttf.py
├── notebooks/
│   ├── 02_ttf_validation.ipynb
│   ├── 03_event_alignment.ipynb
│   └── 04_event_study.ipynb
└── .gitignore
```

### Python ingestion scripts

**`src/01_ingest_gassco.py`**

Reads the 2024–2026 Gassco Excel files, extracts the relevant columns and standardises text, numeric and timestamp fields.

It retains source-year, filename and Excel-row information for traceability.

The cleaned records are exported to:

`data/staging/gassco_umm_import.csv`

**`src/02_ingest_ttf.py`**

Reads the raw vendor-provided TTF CSV and performs initial structural checks, including expected columns, valid dates, duplicate observations and missing values.

Further market-data validation and preparation take place in the first notebook.

### Analysis notebooks

**`notebooks/02_ttf_validation.ipynb`**

Validates the TTF market-price series, including OHLC relationships, calendar coverage, reported percentage changes and calculated returns.

Produces:

`data/processed/ttf_daily_validated.csv`

**`notebooks/03_event_alignment.ipynb`**

Queries the local PostgreSQL database to examine the eligible Gassco event universe.

Maps announcements to observed TTF dates, constructs daily return windows and identifies shared or overlapping market anchors.

Produces processed event-window, unique-anchor and spaced-anchor datasets.

**`notebooks/04_event_study.ipynb`**

Analyses the resulting event samples.

This includes:
- descriptive return distributions;
- overlapping-event sensitivity;
- exploratory non-event comparisons;
- outage magnitude and publication timing;
- non-parametric statistical inference;
- extreme-return diagnostics.

### PostgreSQL dependency

The event-alignment notebook queries the local `norway_ttf` PostgreSQL database.

The public repository currently documents the downstream analysis but does not contain all SQL transformations needed to reconstruct the eligible event universe from the original staged records.

This is an important reproducibility limitation and will be addressed separately.
