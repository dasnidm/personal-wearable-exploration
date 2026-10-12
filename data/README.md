# Public minute-level data

`personal_sensor_minutes.csv` contains one row per minute with at least one HR or EDA callback. The elapsed-minute index preserves collection gaps. Missing rows must not be treated as recorded zeros.

| Column | Description |
|---|---|
| `elapsed_min` | Whole minutes since the first recorded sample; not calendar time |
| `hr_received_n` | HR callbacks received in this minute |
| `hr_valid_n` | HR callbacks passing `hr_status = 1` and `hr_bpm > 0` |
| `hr_valid_fraction` | `hr_valid_n / 60`, rounded to four decimals |
| `hr_mean_bpm` | Mean status-gated heart rate, in beats/minute |
| `hr_median_bpm` | Median status-gated heart rate, in beats/minute |
| `hr_sd_bpm` | Sample standard deviation of status-gated HR values |
| `eda_received_n` | EDA callbacks received in this minute |
| `eda_valid_n` | EDA callbacks passing `eda_status = 0` |
| `eda_valid_fraction` | `eda_valid_n / 60`, rounded to four decimals |
| `eda_mean_scl` | Mean device-reported skin conductance level after the status gate |
| `eda_median_scl` | Median status-gated skin conductance level |
| `eda_sd_scl` | Sample standard deviation of status-gated EDA values |

The `*_valid_fraction` columns use a **nominal 60 callbacks/minute**, not the number of received callbacks. They can occasionally exceed 1 because callback counts can exceed that nominal rate. They are approximate nominal coverage measures, not probabilities. Validity among received callbacks is `valid_n / received_n`, with zero-received bins excluded from that ratio.

Empty mean/median cells indicate no status-gated values. Empty standard-deviation cells can also mean only one value passed the gate. SDK-valid measurements can still contain contact effects, motion artifacts, or device processing effects. EDA values have not been independently calibrated here and must not be treated as stress scores.

## Export provenance

- Source period: approximately May-August 2026; about 11 weeks.
- Original scale: 10,381,795 HR/EDA callback rows from one person's recordings.
- Transformation: status-gated one-minute aggregates; see [the original exporter](../export_public_dataset.py).
- Removed: absolute timestamps, session/device IDs, source filenames, labels, free text, and phone metadata.
- Omitted: IBI bundles and derived HRV.

The exporter is retained as provenance. It requires DuckDB and the private local source database, so it is not part of the public reproduction command. The public data overview needs only this CSV.
