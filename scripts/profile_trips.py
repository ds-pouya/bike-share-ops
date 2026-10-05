"""Inspect the complete downloaded month without changing the project database."""

import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/citibike/2025-01"
ARCHIVE = RAW / "202501-citibike-tripdata.zip"
EXPECTED_COLUMNS = [
    "ride_id", "rideable_type", "started_at", "ended_at",
    "start_station_name", "start_station_id", "end_station_name",
    "end_station_id", "start_lat", "start_lng", "end_lat", "end_lng",
    "member_casual",
]


def main():
    files = []
    with ZipFile(ARCHIVE) as archive:
        for name in sorted(archive.namelist()):
            if not name.endswith(".csv") or name.startswith("__MACOSX/"):
                continue
            if Path(name).name != name:
                raise ValueError("Unexpected nested archive member; inspect it before extraction.")
            path = RAW / name
            # Re-extract from the preserved archive so modified CSVs cannot silently affect results.
            with archive.open(name) as source, path.open("wb") as output:
                shutil.copyfileobj(source, output)
            with path.open(newline="", encoding="utf-8-sig") as handle:
                if next(csv.reader(handle)) != EXPECTED_COLUMNS:
                    raise ValueError(f"Unexpected columns in {name}")
            files.append(str(path))
    if not files:
        raise ValueError("Archive contains no trip CSVs")
    con = duckdb.connect(":memory:")
    file_list = "[" + ", ".join("'" + name.replace("'", "''") + "'" for name in files) + "]"
    con.sql(f"SELECT * FROM read_csv({file_list}, all_varchar=true, header=true, nullstr='', strict_mode=true)").create_view("trips")
    counts = con.execute("""
        select count(*) as rows,
               count(distinct ride_id) as distinct_ride_ids,
               count(*) filter (where ride_id is null) as missing_ride_ids,
               min(try_cast(started_at as timestamp)) as first_start,
               max(try_cast(started_at as timestamp)) as last_start,
               min(try_cast(ended_at as timestamp)) as first_end,
               max(try_cast(ended_at as timestamp)) as last_end,
               count(*) filter (where try_cast(started_at as timestamp) is null) as invalid_start_times,
               count(*) filter (where try_cast(ended_at as timestamp) is null) as invalid_end_times,
               count(*) filter (where try_cast(ended_at as timestamp) <= try_cast(started_at as timestamp)) as nonpositive_durations,
               count(*) filter (where try_cast(ended_at as timestamp) - try_cast(started_at as timestamp) > interval '24 hours') as durations_over_24h,
               count(*) filter (where try_cast(ended_at as timestamp) - try_cast(started_at as timestamp) < interval '60 seconds') as durations_under_60s,
               count(*) filter (where try_cast(started_at as timestamp) < timestamp '2025-01-01'
                                  or try_cast(started_at as timestamp) >= timestamp '2025-02-01') as starts_outside_month
        from trips
    """)
    summary = dict(zip([item[0] for item in counts.description], counts.fetchone()))
    summary["duplicate_ride_id_rows"] = summary["rows"] - summary["missing_ride_ids"] - summary["distinct_ride_ids"]
    missing = {}
    for column in EXPECTED_COLUMNS:
        missing[column] = con.execute(f'SELECT count(*) FROM trips WHERE "{column}" IS NULL').fetchone()[0]
    categories = {}
    for column in ("rideable_type", "member_casual"):
        categories[column] = [{"value": value, "rows": count} for value, count in
            con.execute(f'SELECT "{column}", count(*) FROM trips GROUP BY 1 ORDER BY 2 DESC').fetchall()]
    files_summary = [{"file": Path(name).name, "rows": count} for name, count in
        con.execute("SELECT filename, count(*) FROM read_csv(?, all_varchar=true, header=true, filename=true, strict_mode=true) GROUP BY filename ORDER BY filename", [files]).fetchall()]
    result = {
        "source_url": "https://s3.amazonaws.com/tripdata/202501-citibike-tripdata.zip",
        "archive_sha256": json.loads((RAW / "download_manifest.json").read_text())["sha256"],
        "profiled_at_utc": datetime.now(timezone.utc).isoformat(),
        "duckdb_version": duckdb.__version__,
        "scope": "All CSV files in the January 2025 NYC archive; no sampling or row filtering",
        "inferred_grain": "One recorded trip per row; ride_id is the candidate key",
        "timestamp_note": "Source timestamps have no time-zone offsets; no time-zone conversion applied",
        "columns": EXPECTED_COLUMNS,
        "files": files_summary,
        "summary": summary,
        "missing_values": missing,
        "categories": categories,
    }
    output = ROOT / "docs/data_profile_2025_01.json"
    output.write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(output.read_text())
    con.close()


if __name__ == "__main__":
    main()
