from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data_exports" / "combined" / "combined_raw.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "data" / "personal_sensor_minutes.csv"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

query = """
WITH bounds AS (
    SELECT MIN(timestamp_ms) AS first_timestamp_ms
    FROM raw_samples
),
heart AS (
    SELECT
        FLOOR((timestamp_ms - first_timestamp_ms) / 60000)::BIGINT AS elapsed_min,
        COUNT(*) AS hr_received_n,
        COUNT(*) FILTER (WHERE hr_status = 1 AND hr_bpm > 0) AS hr_valid_n,
        AVG(hr_bpm) FILTER (WHERE hr_status = 1 AND hr_bpm > 0) AS hr_mean_bpm,
        MEDIAN(hr_bpm) FILTER (WHERE hr_status = 1 AND hr_bpm > 0) AS hr_median_bpm,
        STDDEV_SAMP(hr_bpm) FILTER (WHERE hr_status = 1 AND hr_bpm > 0) AS hr_sd_bpm
    FROM raw_heart, bounds
    GROUP BY elapsed_min
),
eda AS (
    SELECT
        FLOOR((timestamp_ms - first_timestamp_ms) / 60000)::BIGINT AS elapsed_min,
        COUNT(*) AS eda_received_n,
        COUNT(*) FILTER (WHERE eda_status = 0) AS eda_valid_n,
        AVG(eda_scl) FILTER (WHERE eda_status = 0) AS eda_mean_scl,
        MEDIAN(eda_scl) FILTER (WHERE eda_status = 0) AS eda_median_scl,
        STDDEV_SAMP(eda_scl) FILTER (WHERE eda_status = 0) AS eda_sd_scl
    FROM raw_eda, bounds
    GROUP BY elapsed_min
)
SELECT
    COALESCE(h.elapsed_min, e.elapsed_min) AS elapsed_min,
    COALESCE(h.hr_received_n, 0) AS hr_received_n,
    COALESCE(h.hr_valid_n, 0) AS hr_valid_n,
    ROUND(COALESCE(h.hr_valid_n, 0) / 60.0, 4) AS hr_valid_fraction,
    ROUND(h.hr_mean_bpm, 4) AS hr_mean_bpm,
    ROUND(h.hr_median_bpm, 4) AS hr_median_bpm,
    ROUND(h.hr_sd_bpm, 4) AS hr_sd_bpm,
    COALESCE(e.eda_received_n, 0) AS eda_received_n,
    COALESCE(e.eda_valid_n, 0) AS eda_valid_n,
    ROUND(COALESCE(e.eda_valid_n, 0) / 60.0, 4) AS eda_valid_fraction,
    ROUND(e.eda_mean_scl, 6) AS eda_mean_scl,
    ROUND(e.eda_median_scl, 6) AS eda_median_scl,
    ROUND(e.eda_sd_scl, 6) AS eda_sd_scl
FROM heart h
FULL OUTER JOIN eda e USING (elapsed_min)
ORDER BY elapsed_min
"""

with duckdb.connect(str(DB_PATH), read_only=True) as connection:
    connection.execute(
        f"COPY ({query}) TO '{OUT_PATH.as_posix()}' (HEADER, DELIMITER ',')"
    )
    rows = connection.execute(f"SELECT COUNT(*) FROM ({query})").fetchone()[0]

print(f"wrote={OUT_PATH}")
print(f"rows={rows}")
print(f"bytes={OUT_PATH.stat().st_size}")
