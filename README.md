
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



## Data engineering and event reconstruction

### 1. Source ingestion

The project begins with three Gassco Excel files containing historical unplanned outage messages from 2024, 2025 and 2026.

The ingestion script reads the `Past Events` worksheet from each file and standardises 18 source columns.

The combined source dataset contains 376 outage messages.

The ingestion process:

- standardises text fields and removes surrounding whitespace;
- converts publication, start and stop fields to timestamps;
- converts capacity fields to numeric values;
- retains the source year, filename and original Excel row;
- exports the cleaned dataset as a CSV for database ingestion.

The original Excel files are preserved separately from the cleaned staging data.

### 2. Event reconstruction in PostgreSQL

A Gassco message is not necessarily a new outage.

Messages may contain revisions to previously reported events, changes in available capacity or updates to operational periods.

Consequently, the event study requires an event-selection process before market returns can be analysed.

The PostgreSQL workflow distinguishes initial announcements from later revisions and applies eligibility rules to identify the primary sample of first-revision unplanned capacity reductions.

The downstream event-alignment notebook queries:

`mart.gassco_primary_reduction_events`

This table contains 166 eligible first-revision reduction announcements.

The complete SQL used to construct this table is not yet included in the public repository. Its upstream selection rules therefore cannot currently be independently reproduced from the published code.

### 3. Event-universe validation

Before attaching market prices, the event-alignment notebook checks the resulting PostgreSQL table.

| Validation measure | Result |
|---|---:|
| Eligible event records | 166 |
| Distinct event keys | 166 |
| Distinct message IDs | 166 |
| Missing publication timestamps | 0 |
| Missing operational start timestamps | 0 |
| Missing outage-size values | 0 |

All 166 records are classified as revision 1.

The eligible publication dates run from 3 September 2024 to 31 August 2026.

### 4. Publication timing

The operational start of an outage is not necessarily the point at which the information becomes public.

The eligible announcements are classified as follows:

| Publication timing | Announcements |
|---|---:|
| After reported operational start | 110 |
| Before or at operational start | 56 |
| Total | 166 |

The analysis therefore retains two distinct timestamps:

- `publication_time`: when the outage information was reported;
- `event_start`: when the operational disruption reportedly began.

The first is used as the conceptual information-event timestamp for market alignment.

This distinction is necessary because an event study based only on operational start times could incorrectly associate earlier price movements with information that had not yet been published.

### 5. Data-quality boundary

The checks establish that the selected event table has unique identifiers and complete values for its principal analytical fields.

They do not independently prove that every underlying capacity value is economically correct or that the original SQL eligibility classifications are free from error.


## Event-study methodology

### 1. Aligning announcements with TTF observations

The eligible event dataset contains 166 first-revision Gassco outage announcements.

The analysis uses `publication_time` as the information-event timestamp, rather than the reported physical outage start.

The TTF dataset contains 591 unique daily observations between 1 July 2024 and 17 September 2026.

Each TTF observation is assigned a sequential index based on its position in the validated market series.

Announcements are aligned to the first observed TTF date on or after their publication date.

| Alignment outcome | Announcements |
|---|---:|
| Same-date TTF observation | 117 |
| Forward-aligned by 1 calendar day | 30 |
| Forward-aligned by 2 calendar days | 18 |
| Forward-aligned by 3 calendar days | 1 |
| **Total** | **166** |

The alignment uses the dates actually present in the vendor dataset rather than assuming a standard Monday-to-Friday trading calendar.

**Important limitation:** Calendar-date alignment does not establish whether an announcement occurred before or after the relevant market-price observation.

The vendor's price timestamp and the timezone of Gassco publication timestamps have not been independently verified.

Consequently, the resulting event windows measure movements around assigned market dates rather than isolated announcement-time price reactions.

### 2. Constructing return windows

For each aligned announcement, the notebook identifies the surrounding observed TTF prices.

Let:

- `P[-1]` denote the previous observed price;
- `P[0]` denote the assigned anchor-date price;
- `P[+1]` denote the next observed price;
- `P[+2]` denote the second subsequent observed price.

The following log-return windows are constructed:

| Window | Definition | Interpretation |
|---|---|---|
| [-1,0] | ln(P[0] / P[-1]) | Movement into the anchor observation |
| [0,+1] | ln(P[+1] / P[0]) | Movement after the anchor observation |
| [-1,+1] | ln(P[+1] / P[-1]) | Wider two-interval response |
| [0,+2] | ln(P[+2] / P[0]) | Extended post-anchor response |

Returns are stored as decimal log returns and multiplied by 100 when reported as percentages.

The primary reported outcome is the [0,+1] return.

This choice measures the movement after the assigned anchor price. It does not guarantee that the full market reaction to a disclosure is captured.

For example, if an announcement was already reflected in the anchor-date closing price, part of the price adjustment would occur before the [0,+1] window begins.

The wider windows are retained as complementary descriptive specifications.

### 3. Consolidating announcements into market anchors

Multiple eligible Gassco announcements can map to the same TTF price date.

The 166 announcements correspond to 130 unique market anchors.

Of these:

- 108 anchors contain one announcement;
- 13 anchors contain two announcements;
- 6 anchors contain three announcements;
- 2 anchors contain four announcements;
- 1 anchor contains six announcements.

In total, 22 anchors contain multiple announcements, representing 58 individual disclosures.

Because announcements assigned to the same anchor share the same TTF return window, treating them as independent market observations would duplicate price movements.

The analysis therefore separates:

**Announcement-level observations (166):** Used to examine outage characteristics, publication timing and event composition.

**Unique market anchors (130):** Used to examine distinct market-return observations without counting identical price windows repeatedly.

This distinction prevents announcement counts from being confused with independent market-price observations.

### 4. Identifying overlapping event windows

Even after consolidating announcements onto unique market dates, neighbouring event windows may overlap.

The wider [-1,+1] window uses the return intervals immediately before and after each anchor.

If two anchors are separated by only one or two observed TTF price intervals, their wider response windows share at least one return interval.

The notebook therefore constructs an additional spaced sample.

The selection algorithm:

1. Sort the 130 unique anchors by their TTF observation index.
2. Retain the earliest anchor.
3. Examine each subsequent anchor in chronological order.
4. Retain it only if its index is at least three observations after the previously retained anchor.
5. Continue until all 130 anchors have been evaluated.

This produces:

| Sample | Observations |
|---|---:|
| Unique market anchors | 130 |
| Retained spaced anchors | 82 |
| Excluded by spacing rule | 48 |

The rule removes mechanically shared return intervals between retained [-1,+1] windows.

It does not establish statistical independence between different outages or market periods.

### 5. Sample-selection implications

The 82-anchor sample is a robustness specification rather than a separate definition of a valid outage event.

Its composition depends on the chronological selection algorithm.

The earliest eligible anchor is retained when neighbouring event windows conflict, regardless of which announcement is more economically significant.

Consequently, the selected sample may differ from the full 130-anchor population in outage severity, infrastructure composition, publication timing or prevailing market conditions.

The analysis therefore retains both datasets:

- 130 unique anchors for descriptive market-response analysis;
- 82 spaced anchors for exploratory statistical inference with mechanical return-window overlap reduced.

Formal statistical tests on the 82 observations should not automatically be interpreted as representative of all Norwegian outage announcements.

### 6. Output datasets

The event-alignment notebook saves three processed datasets:

`data/processed/gassco_ttf_event_windows_announcement_level.csv`

`data/processed/gassco_ttf_event_windows_unique_anchors.csv`

`data/processed/gassco_ttf_event_windows_nonoverlap.csv`

These datasets provide the inputs for `notebooks/04_event_study.ipynb`.

The processed files are generated locally and are not all included in the public repository.


Publishing the complete SQL transformation and exclusion audit is therefore a remaining reproducibility task.


## Empirical results

The analysis examines whether Norwegian outage announcements are associated with systematic movements in near-term TTF futures prices.

Results are separated into the full 130-anchor descriptive sample and the 82-anchor spaced sample used for exploratory statistical inference.

### 1. Post-anchor return distribution

Across 130 unique market anchors, the median [0,+1] log return is +0.279%.

The 82-anchor spaced sample produces:

| Statistic | Result |
|---|---:|
| Observations | 82 |
| Mean return | +0.098% |
| Median return | +0.057% |
| Standard deviation | 3.107% |
| Reported 95% bootstrap interval for median | -0.526% to +0.925% |
| Wilcoxon signed-rank statistic | 1615 |
| Wilcoxon p-value | 0.689 |

The median is close to zero, while the distribution contains substantial positive and negative movements.

The percentile-bootstrap interval was calculated using 10,000 resamples of the 82 observations.

The Wilcoxon test does not reject its null hypothesis at conventional significance levels.

This does not prove that the true market response is zero. The test examines the distribution of selected daily returns, not an isolated causal announcement effect.

![Distribution of post-anchor TTF returns](https://raw.githubusercontent.com/jauricestudios/jauricestudios.github.io/main/norway_ttf_event_study/charts/ttf_post_announcement_return_distribution.png)

*Figure 1. Distribution of post-anchor TTF returns in the spaced event sample.*

### 2. Outage magnitude and TTF returns

The second analysis examines whether the largest individual announced capacity reduction at each market anchor is associated with subsequent signed returns.

The analysis uses Spearman's rank correlation to measure monotonic association.

| Sample | Spearman correlation |
|---|---:|
| 130 unique anchors | -0.006 |
| 82 spaced anchors | +0.050 |

For the 82-anchor sample, the reported p-value is 0.656.

The estimated monotonic association is close to zero in both samples.

![Outage magnitude versus TTF returns](https://raw.githubusercontent.com/jauricestudios/jauricestudios.github.io/main/norway_ttf_event_study/charts/outage_magnitude_vs_ttf_return.png)

*Figure 2. Largest individual communicated outage magnitude against the subsequent signed TTF return.*

Announced unavailable capacity is not necessarily the unexpected reduction in aggregate Norwegian gas supply.

The results therefore cannot establish whether market prices respond to genuinely unexpected supply shocks.

### 3. Publication timing

The third analysis compares market returns according to whether the largest outage announcement associated with an anchor was published before or after the reported operational start.

For the 82-anchor sample:

| Publication timing | Observations | Median return |
|---|---:|---:|
| Published after operational start | 59 | -0.246% |
| Published before or at operational start | 23 | +0.753% |

The Mann–Whitney U statistic is 612, with a p-value of 0.496.

This provides little evidence of systematic rank separation between the two groups.

The comparison concerns publication relative to operational start, not publication relative to the verified TTF market closing time.

### 4. Event versus non-event market movements

The analysis also investigates whether returns around outage-associated market dates are unusually large compared with selected non-event observations.

For the primary [0,+1] return window:

| Sample | Observations | Mean absolute return |
|---|---:|---:|
| Unique event anchors | 130 | 2.398% |
| Selected non-event observations | 301 | 2.719% |

The non-event sample excludes observations whose return windows overlap the event-date contamination rule.

In this exploratory comparison, event-associated dates do not show larger average absolute returns.

However, the comparison is not a matched counterfactual.

The event and non-event samples differ in calendar composition and may experience different volatility regimes or contemporaneous market information.

The result therefore does not establish that Norwegian outage announcements reduce volatility.

A separate local-control exercise also identified repeated use of benchmark dates, with some control observations assigned as many as 12 times. Such reuse creates additional dependence that must be considered before formal event-versus-control inference.

### 5. Interpretation

The analysis does not detect a consistent unconditional directional return across the selected event windows.

It also finds little evidence of a monotonic relationship between the largest communicated outage and the subsequent signed return.

These findings are compatible with market responses depending on information that the present dataset does not directly measure, including:

- the unexpected change in net Norwegian supply;
- whether the outage was anticipated;
- affected infrastructure and alternative supply routes;
- prevailing European gas balances;
- wider LNG, storage and weather conditions;
- other information arriving during the return window.

These explanations remain hypotheses rather than demonstrated drivers of the observed returns.

The principal contribution of the project is therefore its structured reconstruction and alignment of operational disclosures with market observations, together with an explicit assessment of what the resulting daily returns can and cannot establish.

### Statistical qualifications

The formal tests are exploratory.

The 82-anchor selection removes mechanically shared return intervals but does not guarantee independent observations.

The reported percentile-bootstrap interval resamples individual observations and is not adjusted for possible dependence across market regimes or related outage episodes.

The Wilcoxon signed-rank test is not automatically a pure median test without additional assumptions. The Mann–Whitney test assesses rank-based differences and does not automatically test equality of medians.

All results should be interpreted as observational associations, not causal estimates.


## Reproducing the analysis

### Current reproducibility status

The repository documents the Python processing and statistical-analysis workflow.

However, it is not currently a fully self-contained reproduction package.

The raw Gassco and TTF source files are stored locally and excluded from Git. The SQL transformations that construct the eligible event universe are also not yet included in the public repository.

A reader can inspect the published code and saved notebook results, but reproducing the complete analysis requires additional data and database preparation.

### 1. Software requirements

The published Python scripts and notebooks use:

- Python
- pandas
- NumPy
- SciPy
- Matplotlib
- Jupyter
- openpyxl for reading Excel files

PostgreSQL and the `psql` command-line client are required for event-database queries.

The repository does not yet provide a tested, version-pinned Python environment.

For an initial local setup, install the required Python packages:

```bash
python -m pip install pandas numpy scipy matplotlib jupyter openpyxl
```

This is an installation example, not a verified dependency lockfile.

### 2. Required local input files

The Gassco ingestion script expects:

```text
data/raw/gassco/
├── gassco_umm_unplanned_2024.xlsx
├── gassco_umm_unplanned_2025.xlsx
└── gassco_umm_unplanned_2026.xlsx
```

The TTF ingestion script and validation notebook expect:

```text
data/raw/ttf/
└── ice_dutch_ttf_futures_2024-07-01_to_2026-09-17.csv
```

The exact input filenames and folder structure are currently defined in the code.

The TTF CSV is expected to contain the vendor fields:

`Date`, `Price`, `Open`, `High`, `Low`, `Vol.`, `Change %`.

These input files are not redistributed in this repository.

The `.gitignore` file excludes the local `data/` directory.

### 3. Gassco data ingestion

From the project root, run:

```bash
python src/01_ingest_gassco.py
```

The script reads the three Excel source files, standardises the analytical fields and writes:

`data/staging/gassco_umm_import.csv`

The staging file is an input to the local database workflow.

**Current limitation:** The public repository does not yet provide the complete SQL needed to load, reconstruct and validate the final eligible event universe from this staging file.

### 4. TTF data validation

The initial source-validation script can be run using:

```bash
python src/02_ingest_ttf.py
```

This script checks the expected source columns, date parsing, duplicate dates and missing values.

It does not currently create the final processed TTF dataset.

The full validation and processing workflow is contained in:

`notebooks/02_ttf_validation.ipynb`

That notebook produces:

`data/processed/ttf_daily_validated.csv`

The saved analysis reports 591 validated daily observations.

### 5. PostgreSQL event universe

The event-alignment notebook connects to the local PostgreSQL database:

`norway_ttf`

It queries the existing relation:

`mart.gassco_primary_reduction_events`

The published notebook expects this table to contain the reconstructed and eligible first-revision Gassco announcements.

In the saved analysis, the table contains:

- 166 records;
- 166 distinct event keys;
- 166 distinct message IDs;
- no missing publication timestamps;
- no missing operational start timestamps;
- no missing outage-size values.

These checks establish the properties of the existing analytical table. They do not independently reproduce its upstream construction.

Rebuilding this database table from the original source files remains a separate task.

### 6. Event alignment

Once the validated TTF dataset and PostgreSQL event table are available, run:

`notebooks/03_event_alignment.ipynb`

The notebook queries PostgreSQL through the `psql` command-line client and aligns eligible announcements to observed market dates.

It generates:

```text
data/processed/
├── gassco_ttf_event_windows_announcement_level.csv
├── gassco_ttf_event_windows_unique_anchors.csv
└── gassco_ttf_event_windows_nonoverlap.csv
```

The saved notebook outputs report:

- 166 announcement-level observations;
- 130 unique market anchors;
- 82 chronologically spaced anchors.

### 7. Statistical analysis

Run:

`notebooks/04_event_study.ipynb`

The notebook requires the processed event-alignment datasets and the original TTF CSV for benchmark construction.

It calculates descriptive return statistics, event-versus-non-event comparisons, outage-size relationships, publication-timing comparisons and non-parametric tests.

The saved analysis reports:

| Check | Expected saved result |
|---|---:|
| Unique event anchors | 130 |
| Spaced event anchors | 82 |
| Median [0,+1] return (spaced sample) | +0.057% |
| Wilcoxon p-value | 0.689 |
| Spearman correlation | +0.050 |
| Mann-Whitney p-value | 0.496 |

These values are reference results from the existing notebooks, not guarantees that an independently reconstructed input dataset will produce identical outputs.

### 8. Remaining reproducibility work

Before the repository can support a complete independent rerun, the following work is required:

1. Publish the SQL schema, event-reconstruction transformations and eligibility rules.
2. Provide an input-data dictionary and documented source requirements.
3. Add a tested, version-pinned Python dependency file.
4. Add executable validation checks for the 166, 130 and 82 observation counts.
5. Record the Python, PostgreSQL and package versions used for the final analysis.
6. Archive the source-data versions and processing assumptions, subject to redistribution rights.

The current repository should therefore be treated as a documented research workflow with partially reproducible components, rather than a fully automated end-to-end pipeline.

