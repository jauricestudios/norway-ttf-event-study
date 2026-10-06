
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
