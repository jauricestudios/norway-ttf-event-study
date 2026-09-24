# Norwegian Gas Outages and TTF

This project examines how near-term TTF gas prices behave around eligible Norwegian gas outage announcements published by Gassco.

The workflow combines PostgreSQL and Python to clean and validate outage data, align announcements to observed TTF market dates, construct event-return windows and test whether the resulting price movements show a consistent directional response.

The final analytical sample contains 166 eligible outage announcements mapped to 130 unique TTF market anchors. A reduced sample of 82 non-overlapping anchors is used for formal inference to reduce mechanical dependence between overlapping event windows.

The analysis does not find evidence of a common unconditional directional TTF response across the non-overlapping sample. This does not imply that Norwegian outages are irrelevant to TTF pricing. Individual reactions may depend on market expectations, outage size and duration, affected infrastructure, wider European gas conditions and contemporaneous information.
## Research question

How do near-term TTF prices behave around eligible first-revision Norwegian gas outage announcements, and do outage magnitude or publication timing help explain the observed response?

This matters because the physical start of an outage and the arrival of public information are not necessarily the same event. Some Gassco messages are published after the reported operational disruption has already begun, so the publication timestamp is used as the market-information event rather than the physical start time.

The market data are daily rather than intraday. The analysis therefore does not claim to measure an instantaneous price reaction. Instead, announcements are aligned to observed TTF trading dates and evaluated across daily event windows that allow for uncertainty about when information was incorporated into price.

## Tools

- **PostgreSQL** for storing, validating and querying the reconstructed Gassco event data.
- **Python** for cleaning, market-date alignment, event-window construction and statistical analysis.
- **pandas / NumPy** for data transformation and return calculations.
- **SciPy** for non-parametric statistical tests.
- **Jupyter** for validation, exploratory analysis and documenting the workflow.

## Data and workflow

The project is organised as a reproducible pipeline rather than a single analysis notebook:

1. **Gassco outage data** are cleaned, typed and validated before being loaded into PostgreSQL.
2. **TTF market data** are independently validated for numeric consistency, trading-date coverage and return construction.
3. **Event alignment** maps eligible first-revision outage announcements to observed TTF market dates and constructs alternative daily return windows.
4. **Event-study analysis** examines the 130 unique market anchors descriptively and uses the 82 non-overlapping anchors for formal inference.

The event universe is validated before market data are attached, including identifier uniqueness, missing analytical fields, revision composition and publication timing. 

Because the TTF data are daily rather than intraday, the analysis uses multiple event windows instead of pretending that one daily return perfectly isolates the announcement response. 

The final analysis then separates the full 130-anchor descriptive sample from the 82-anchor non-overlapping inferential sample. 
## Key findings

The 130 unique TTF market anchors have a descriptive median post-anchor \([0,+1]\) return of +0.279%.

Formal inference is based on the 82 non-overlapping anchors:

- the median post-anchor return is +0.057%, with no statistically detectable location shift away from zero (Wilcoxon W = 1615, p = 0.689);
- the largest individual outage magnitude shows little monotonic association with the subsequent return (Spearman rho = 0.050, p = 0.656);
- publication-timing groups do not show systematic rank separation (Mann-Whitney U = 612, p = 0.496).

The results therefore do not support a common unconditional directional TTF response across the sample. They are more consistent with market reactions depending on the unexpected component of the outage, affected infrastructure, duration, prevailing market conditions and other information arriving at the same time.
## Limitations

The study uses daily observations from a continuous TTF futures series rather than intraday transaction data or official ICE settlement prices. The exact market reaction to a timestamped announcement therefore cannot be isolated within the trading day.

The continuous futures series may also reflect contract-roll effects, so the return analysis should be interpreted as behaviour in the vendor-reported nearby continuous series rather than a fixed-maturity contract.

Outage size is measured using the largest individual communicated reduction within each market anchor. This is a useful severity measure, but it is not equivalent to the unexpected net supply shock perceived by the market.

Finally, event-window returns may contain other contemporaneous information. The analysis is therefore descriptive and inferential around observed announcement windows rather than a causal estimate of the isolated price effect of Norwegian outages.
## Repository structure

```text
norway-ttf-event-study/
├── README.md
├── notebooks/
│   ├── 02_ttf_validation.ipynb
│   ├── 03_event_alignment.ipynb
│   └── 04_event_study.ipynb
├── src/
│   ├── 01_ingest_gassco.py
│   └── 02_ingest_ttf.py
└── .gitignore
## Data sources

- **Gassco outage announcements**: Norwegian gas outage messages used to reconstruct the eligible event universe.
- **TTF market data**: Investing.com historical data for the ICE Dutch TTF Gas C1 continuous futures series.

The TTF source contains 591 daily observations in the validated sample. Raw source files are kept outside the public repository and are not redistributed here.
## Reproducing the analysis

The project depends on local source data and a PostgreSQL database, so the repository is intended to document the analytical workflow rather than provide a one-command reproduction from redistributed data.

The analysis should be followed in this order:

1. ingest and clean the Gassco outage records;
2. validate the TTF market series;
3. construct the eligible event universe in PostgreSQL;
4. align outage announcements to observed TTF market dates;
5. construct unique and non-overlapping event samples;
6. run the descriptive and inferential event-study analysis.

The notebooks are designed to be read sequentially from `02_ttf_validation.ipynb` through `04_event_study.ipynb`.
## Further work

The next extensions would focus on improving the measurement of the market shock rather than simply adding more statistical tests.

Potential improvements include:

- replacing the continuous TTF series with fixed-maturity contracts or an explicitly controlled roll methodology;
- incorporating the prompt TTF curve, such as the M1–M2 spread;
- separating communicated outage capacity from realised Norwegian gas-flow changes;
- constructing a better measure of the unexpected net supply shock rather than relying only on the largest individual outage;
- adding wider market controls such as storage, weather, LNG conditions and broader European gas fundamentals.
