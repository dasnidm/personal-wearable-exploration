# Personal wearable data exploration

A small personal project collecting and exploring heart rate (HR) and electrodermal activity (EDA) with a Galaxy Watch-Android phone logging prototype. I collected my own recordings over approximately 11 weeks in May-August 2026, then explored collection gaps, signal quality, and recurring patterns.

I wanted to understand what the recordings could support before trying to interpret them as psychological states.

## Start here

- [Data overview](reports/data-overview.md): a short, reproducible summary of the public minute-level data.
- [Earlier pattern exploration](reports/pattern-exploration.md): an existing August 2026 report, selected aggregate results, and a figure from the original analyses.
- [Analysis code](analysis/summarize_minutes.py) and [data dictionary](data/README.md).

## What I tried

- Collected personal HR and EDA recordings using a watch-phone prototype.
- Checked missing intervals, SDK status flags, and differences between received and usable measurements.
- Tried exploratory analyses of signal direction, persistence, and repeated HR/EDA patterns.

The earlier pattern analysis mainly separated signal stability and availability. It did not establish stress, focus, sleep, or other physiological or psychological states.

![Existing exploratory cluster profiles](reports/assets/sequence-cluster-profiles.png)

*An example from the earlier analysis: the clusters differ substantially in flat-signal and unknown-EDA proportions. The figure is descriptive, not evidence of distinct physiological states.*

## Reproduce the public data overview

Python 3.10 or later; no third-party packages are needed:

```bash
python analysis/summarize_minutes.py
```

This regenerates `reports/data-overview.md` and `reports/summary.json` from [the public CSV](data/personal_sensor_minutes.csv). It does not rerun the earlier raw-signal models.

## Data and scope

The public CSV contains 87,469 observed one-minute bins. Gaps remain in the elapsed-minute index; absent minutes are not zero-valued measurements. Absolute timestamps, session/device IDs, activity labels, and free text are excluded.

The original recordings contained about 10.4 million HR/EDA callbacks. These are repeated measurements from **one person**, not independent observations or participants. SDK status gates are a quality filter, not independent physiological validation. IBI/HRV is excluded from this public dataset because the repeated/cumulative SDK bundles need further validation.

The raw recordings and phone metadata are not included. The earlier report uses inputs that cannot be reconstructed from one-minute aggregates; its published tables are aggregate results from that existing work.

## My contribution and assistance

I defined the project, collected the recordings, and used the outputs to explore questions about signal quality and patterns. Coding, analysis implementation, and report drafting were extensively assisted by Codex. This is an early learning project with no formal lab supervision or validated state-prediction result.

The repository name `cs130` comes from its original coursework use.
