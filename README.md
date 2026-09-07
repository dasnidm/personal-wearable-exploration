# CS130 Personal Sensor Dataset

This repository contains a privacy-reduced, one-minute dataset derived from personal Galaxy Watch sensor recordings.

## Data

`data/personal_sensor_minutes.csv` contains one row per observed minute. Absolute timestamps, session identifiers, device identifiers, source filenames, task names, and phone models are excluded. Time is represented as minutes elapsed from the beginning of the dataset.

The dataset is descriptive and is not a medical dataset. Heart rate and EDA are wearable measurements with missingness and SDK quality flags. EDA must not be interpreted directly as stress, and the data must not be used for diagnosis.

### Columns

| Column | Description |
|---|---|
| `elapsed_min` | Minutes since the first recorded sample |
| `hr_received_n` | HR callbacks received during the minute |
| `hr_valid_n` | HR values passing the SDK status/value gate |
| `hr_valid_fraction` | Valid HR count divided by the nominal 60 samples |
| `hr_mean_bpm` | Mean valid heart rate |
| `hr_median_bpm` | Median valid heart rate |
| `hr_sd_bpm` | Within-minute standard deviation of valid heart rate |
| `eda_received_n` | EDA callbacks received during the minute |
| `eda_valid_n` | EDA values passing the SDK status gate |
| `eda_valid_fraction` | Valid EDA count divided by the nominal 60 samples |
| `eda_mean_scl` | Mean valid skin conductance level |
| `eda_median_scl` | Median valid skin conductance level |
| `eda_sd_scl` | Within-minute standard deviation of valid EDA |

## R

```r
sensor <- read.csv(
  "https://raw.githubusercontent.com/dasnidm/cs130/main/data/personal_sensor_minutes.csv"
)
head(sensor)
```

## Python

```python
import pandas as pd

sensor = pd.read_csv(
    "https://raw.githubusercontent.com/dasnidm/cs130/main/data/personal_sensor_minutes.csv"
)
print(sensor.head())
```

## Provenance and privacy

- Source period: approximately May-August 2026.
- Original scale: about 10.4 million HR/EDA callback rows.
- Public transformation: status-gated one-minute aggregates.
- Removed: absolute time, IDs, file provenance, labels, free text, and device metadata.
- IBI bundles are omitted because their cumulative/repeated SDK format requires additional validation.

The raw personal dataset is intentionally not included.
