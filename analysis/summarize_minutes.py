"""Summarize the public HR/EDA CSV using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def summarize(path: Path) -> dict:
    signals = {
        s: {"received": 0, "status_gated": 0, "minutes_with_values": 0,
            "above_nominal_minutes": 0}
        for s in ("hr", "eda")
    }
    first = previous = None
    rows = missing = gaps = largest_gap = joint_quality = 0
    required = {"elapsed_min"} | {
        f"{s}_{field}" for s in signals
        for field in ("received_n", "valid_n", "valid_fraction", "mean_bpm" if s == "hr" else "mean_scl")
    }
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Input is missing required HR/EDA columns")
        for line, row in enumerate(reader, 2):
            minute = int(row["elapsed_min"])
            if minute < 0 or (previous is not None and minute <= previous):
                raise ValueError(f"Line {line}: elapsed minutes must be nonnegative and strictly increasing")
            if first is None:
                first = minute
            if previous is not None and minute > previous + 1:
                gap = minute - previous - 1
                missing += gap
                gaps += 1
                largest_gap = max(largest_gap, gap)
            previous = minute
            good = True
            for signal, counts in signals.items():
                received = int(row[f"{signal}_received_n"])
                valid = int(row[f"{signal}_valid_n"])
                fraction = float(row[f"{signal}_valid_fraction"])
                if not 0 <= valid <= received:
                    raise ValueError(f"Line {line}: invalid callback counts for {signal}")
                if not math.isfinite(fraction) or abs(fraction - valid / 60) > 0.000051:
                    raise ValueError(f"Line {line}: {signal} fraction does not use the documented denominator")
                column = f"{signal}_mean_bpm" if signal == "hr" else f"{signal}_mean_scl"
                value = row[column]
                if bool(value) != bool(valid):
                    raise ValueError(f"Line {line}: {signal} mean/value count disagree")
                if value:
                    mean = float(value)
                    if not math.isfinite(mean) or mean < 0 or (signal == "hr" and mean == 0):
                        raise ValueError(f"Line {line}: invalid status-gated {signal} mean")
                    counts["minutes_with_values"] += 1
                counts["received"] += received
                counts["status_gated"] += valid
                counts["above_nominal_minutes"] += valid > 60
                good = good and received >= 54 and valid >= 48
            joint_quality += good
            rows += 1
    if not rows:
        raise ValueError("Input contains no observed minutes")
    span = previous - first + 1
    for counts in signals.values():
        counts["status_gated_fraction_of_received"] = (
            counts["status_gated"] / counts["received"] if counts["received"] else None
        )
        counts["received_fraction_of_nominal_span"] = counts["received"] / (span * 60)
        counts["status_gated_fraction_of_nominal_span"] = counts["status_gated"] / (span * 60)
    return {
        "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "observed_minutes": rows,
        "elapsed_span_minutes": span,
        "elapsed_span_days": span / 1440,
        "unobserved_minutes": missing,
        "collection_gaps": gaps,
        "largest_gap_minutes": largest_gap,
        "joint_quality_minutes": joint_quality,
        "joint_quality_rule": "Both sensors: received >= 54 and status-gated >= 48 per minute",
        "signals": signals,
    }


def report(summary: dict) -> str:
    h, e = (summary["signals"][s] for s in ("hr", "eda"))
    def percentage(value: float | None) -> str:
        return f"{value:.1%}" if value is not None else "n/a"

    metrics = [
        ("Received callbacks", f"{h['received']:,}", f"{e['received']:,}"),
        ("Status-gated callbacks", f"{h['status_gated']:,}", f"{e['status_gated']:,}"),
        ("Status-gated / received", percentage(h['status_gated_fraction_of_received']), percentage(e['status_gated_fraction_of_received'])),
        ("Received / nominal elapsed-span callbacks", percentage(h['received_fraction_of_nominal_span']), percentage(e['received_fraction_of_nominal_span'])),
        ("Status-gated / nominal elapsed-span callbacks", percentage(h['status_gated_fraction_of_nominal_span']), percentage(e['status_gated_fraction_of_nominal_span'])),
        ("Observed minutes with status-gated values", f"{h['minutes_with_values']:,}", f"{e['minutes_with_values']:,}"),
        ("Minutes with more than 60 status-gated callbacks", f"{h['above_nominal_minutes']:,}", f"{e['above_nominal_minutes']:,}"),
    ]
    lines = [
        "# Public data overview", "",
        "Generated by `python analysis/summarize_minutes.py` from the unchanged public CSV.", "",
        "## Collection and gaps", "",
        f"- Observed one-minute bins: **{summary['observed_minutes']:,}**.",
        f"- First-to-last elapsed span: **{summary['elapsed_span_minutes']:,} minutes** ({summary['elapsed_span_days']:.1f} days).",
        f"- Unobserved minutes within that span: **{summary['unobserved_minutes']:,}** across {summary['collection_gaps']:,} gaps.",
        f"- Largest gap: **{summary['largest_gap_minutes']:,} minutes** ({summary['largest_gap_minutes'] / 60:.1f} hours).", "",
        "Missing bins are collection gaps, not zero heart rate or zero EDA. An observed bin can also contain only invalid-status callbacks.", "",
        "## Received measurements and status gates", "",
        "| Measure | HR | EDA |", "|---|---:|---:|",
        *(f"| {name} | {a} | {b} |" for name, a, b in metrics), "",
        "The nominal denominator is 60 callbacks per elapsed minute, including gaps. The received-callback denominator excludes missing callbacks. Neither establishes independent physiological validity.", "",
        f"**{summary['joint_quality_minutes']:,} observed minutes** meet a simple joint coverage rule: at least 54 received and 48 status-gated callbacks for each sensor. This is a descriptive filter, not validated artifact removal. It uses the public export's bins, which differ from the raw-data windows in the earlier report.", "",
        "## What this supports", "",
        "The recordings support basic exploration of collection reliability and signal variation. A large callback count does not mean continuous usable data. Contact, movement, charging, activities, and sleep are not labeled in the public CSV.", "",
        "The public export covers the full recording span. Earlier local reports sometimes restricted analysis to more complete ambient dates, so their coverage percentages have different denominators.", "",
        "For examples of the earlier exploratory pattern work, see [the archived report](pattern-exploration.md). No stress, focus, sleep, or clinical prediction is validated here.", "",
        "## Reproduction", "",
        "The script checks ordered unique minutes, callback-count consistency, empty means, and the documented fraction denominator. It writes this report and [summary.json](summary.json) using only the Python standard library.", "",
        f"Input SHA-256: `{summary['input_sha256']}`.", "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/personal_sensor_minutes.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    summary = summarize(args.data)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    (args.output / "data-overview.md").write_text(report(summary), encoding="utf-8", newline="\n")
    print(f"Summarized {summary['observed_minutes']:,} observed minutes; wrote data-overview.md and summary.json")


if __name__ == "__main__":
    main()
